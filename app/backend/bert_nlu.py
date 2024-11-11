import torch
from transformers import BertTokenizer, BertModel
import torch.nn as nn
from torch.nn import Dropout, Linear, BatchNorm1d
import pickle

def get_device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")

class BertWithRegularization(nn.Module):
    def __init__(self, bert_model, num_labels):
        super(BertWithRegularization, self).__init__()
        self.bert = bert_model
        self.dropout = Dropout(0.75)
        self.batchnorm = BatchNorm1d(768)
        self.classifier = Linear(768, num_labels, bias=True)
        self.l1 = 1e-07
        self.l2 = 1e-08
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs[1]  # Obter o embedding do token [CLS]
        cls_output = self.batchnorm(cls_output)
        cls_output = self.dropout(cls_output)
        logits = self.classifier(cls_output)
        return logits
    
def load_model(model_path, num_labels, device):
    bert_model = BertModel.from_pretrained('neuralmind/bert-base-portuguese-cased')
    model = BertWithRegularization(bert_model=bert_model, num_labels=num_labels)
    model.load_state_dict(torch.load(model_path, map_location=device))
    return model

def load_tokenizer(tokenizer_path):
    return BertTokenizer.from_pretrained(tokenizer_path)

def load_label_encoder(label_encoder_path):
    with open(label_encoder_path, 'rb') as f:
        label_encoder = pickle.load(f)
    return label_encoder

model_path = 'models/nlu/modelo_bert_classificacao.pt'
tokenizer_path = 'models/nlu/tokenizer_bert.pt'
label_encoder_path = 'models/nlu/label_encoder.pkl'

device = get_device()

label_encoder = load_label_encoder(label_encoder_path)

model = load_model(model_path, num_labels=len(label_encoder.classes_), device=device)
model.to(device)
tokenizer = load_tokenizer(tokenizer_path)

def predict_intention(input_text):
    encoded = tokenizer.encode_plus(
        input_text,
        add_special_tokens=True,
        max_length=128,
        truncation=True,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt'
    )
    input_ids = encoded['input_ids'].to(device)
    attention_mask = encoded['attention_mask'].to(device)
    model.eval()
    with torch.no_grad():
        logits = model(input_ids=input_ids, attention_mask=attention_mask)

    top_k = torch.topk(logits, k=5, dim=1)

    top_k_indices = top_k.indices.cpu().numpy()[0]

    top_k_labels = label_encoder.inverse_transform(top_k_indices)
    return top_k_labels