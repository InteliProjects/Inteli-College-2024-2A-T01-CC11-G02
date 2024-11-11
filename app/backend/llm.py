import os
from dotenv import load_dotenv
import torch
from peft import PeftModel
import pandas as pd
import requests
import re
from sklearn.metrics.pairwise import cosine_similarity
import threading

from textwrap import dedent
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    pipeline,
    TextIteratorStreamer,
    AutoModel
)
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.prompts import ChatPromptTemplate
from huggingface_hub import login

load_dotenv()

token = os.getenv("HUGGINGFACE_TOKEN") 

login(token=token)

# Defina o caminho do PDF
DOC_PATH = ""
CHROMA_PATH = "db_brastel"

# Carregue seu documento PDF
loader = PyPDFLoader(DOC_PATH)
pages = loader.load()

# Divida o documento em partes menores
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(pages)

# Obtenha o modelo de incorporação do Hugging Face
embeddings = HuggingFaceEmbeddings(model_name="distilbert-base-nli-stsb-mean-tokens")

# Incorpore os chunks como vetores e carregue-os no banco de dados
db_chroma = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_PATH)

# Definições de configuração
PAD_TOKEN = "<|pad|>"
MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"
HUGGINGFACE_TOKEN = "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"

# Carregar o tokenizer
tokenizer_llm = AutoTokenizer.from_pretrained(
    "/content/drive/MyDrive/Dados/models/nlg/Llama-3-BB-Instruct-Brastel",
    use_fast=True,
    token=HUGGINGFACE_TOKEN
)
tokenizer_llm.add_special_tokens({'pad_token': PAD_TOKEN})
tokenizer_llm.padding_side = "right"

# Carregar o modelo base
llm_model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype=torch.float16,
    token=HUGGINGFACE_TOKEN,
)

llm_model.resize_token_embeddings(len(tokenizer_llm), pad_to_multiple_of=8)

# Carregar o modelo PEFT
model_llm = PeftModel.from_pretrained(
    llm_model,
    model_id="/content/drive/MyDrive/Dados/models/nlg/Llama-3-BB-Instruct-Brastel",
    token=HUGGINGFACE_TOKEN,
)

df = pd.read_parquet('/content/drive/MyDrive/Dados/embeddings_data.parquet')

def replace_numbers(text):
    return re.sub(r'\d+', lambda x: 'X' * len(x.group()), text)

df['Resposta'] = df.apply(lambda row: replace_numbers(row['Resposta']) if row['Intencao'] == 'Confirmacao de cambio/taxas' else row['Resposta'], axis=1)

def get_exchange_rate():
    url = 'https://economia.awesomeapi.com.br/last/BRL-JPY'

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        rate = data['BRLJPY']['bid']
        return f"Taxa de conversão de BRL para JPY hoje: {rate}"
    else:
        return f"Falha ao obter taxa de conversão. Status code: {response.status_code}"

def create_test_prompt(question, context_text, tokenizer):
    # Obter as 5 respostas mais similares com a mesma 'Intencao'
    most_similar_rows = find_most_similar(question, context_text)

    additional_context = ''

    if context_text == 'Confirmacao de cambio/taxas':
        additional_context += f"\n {get_exchange_rate()}"

    prompt = dedent(
        f"""
        ## OBJETIVO ##
        Faça uma resposta para a pergunta utilizando o contexto fornecido.
        ## INFORMAÇÕES CRUCIAIS ##
        {additional_context}
        ## EXEMPLOS DE RESPOSTAS ##
        {most_similar_rows['Resposta']}
        ## TAREFA ##
        A pergunta foi a seguinte:
        {question}
        A resposta é:
        """
    )
    messages = [
        {
            "role": "system",
            "content": "Responda à pergunta considerando o contexto fornecido."
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)


# Função test_prompt modificada
def test_prompt(input_text, predicted_intention):
    test_prompt = create_test_prompt(input_text, predicted_intention, tokenizer_llm)

    # Preparar a entrada
    input_ids = tokenizer_llm.encode(test_prompt, return_tensors='pt')

    # Mover o modelo e a entrada para o dispositivo apropriado
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_llm.to(device)
    input_ids = input_ids.to(device)

    # Inicializar o streamer
    streamer = TextIteratorStreamer(tokenizer_llm, skip_prompt=True, skip_special_tokens=True)

    # Iniciar a geração em uma thread separada
    generation_kwargs = dict(
        input_ids=input_ids,
        max_new_tokens=128,
        do_sample=True,
        temperature=0.8,
        streamer=streamer
    )

    generation_thread = threading.Thread(target=model_llm.generate, kwargs=generation_kwargs)
    generation_thread.start()

    # Fazer o streaming do texto gerado
    generated_text = ""
    for new_text in streamer:
        print(new_text, end='', flush=True)
        generated_text += new_text

    # Aguardar a thread de geração terminar
    generation_thread.join()

    return generated_text

def get_embedding(text):
    tokenizer = AutoTokenizer.from_pretrained('neuralmind/bert-base-portuguese-cased')
    model = AutoModel.from_pretrained('neuralmind/bert-base-portuguese-cased')
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().numpy()

def find_most_similar(string, context_text, dataframe=df):
    filtered_df = dataframe[dataframe['Intencao'] == context_text]

    if filtered_df.empty:
        raise ValueError(f"Nenhuma entrada encontrada com Intencao == {context_text}")

    string_embedding = get_embedding(string)

    similarities = filtered_df['coluna_embedding'].apply(
        lambda emb: cosine_similarity([string_embedding], [emb])[0][0]
    )

    filtered_df = filtered_df.copy()
    filtered_df['similarity'] = similarities

    most_similar_rows = filtered_df.nlargest(5, 'similarity')

    return most_similar_rows