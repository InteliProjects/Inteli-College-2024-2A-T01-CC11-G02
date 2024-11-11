from flask import Flask, request, jsonify
import dill
import numpy as np
import tensorflow as tf
import os
from flask_cors import CORS
from bert_nlu import predict_intention
from llm import test_prompt

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)
CORS(app)

@app.route('/predict_bert', methods=['POST'])
def predict_bert():
    print('-------------------------------------')
    print('------- PREDICAO MODELO BERT --------')
    print('-------------------------------------')
    data = request.get_json()

    text = data['input_data']
    print('Frase recebida: ' + text)
    
    prediction = predict_intention(text)

    return jsonify({'predicted_labels': prediction.tolist()})

@app.route('/test_prompt', methods=['POST'])
def test_prompt():
    print('-------------------------------------')
    print('---------- TEST PROMPT --------------')
    print('-------------------------------------')
    data = request.get_json()

    text = data['text']
    print('Texto recebido: ' + text)

    intent = data['intent']
    print('Intenção do texto: ' + intent)

    result = test_prompt(text, intent)
    print('Result: ' + result)

    return jsonify({'result': result})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)