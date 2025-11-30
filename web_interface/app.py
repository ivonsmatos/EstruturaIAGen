# Interface Web usando Flask
from flask import Flask, request, jsonify, session
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.llm.base import BaseModel
import pandas as pd
from web_interface.database import Database

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessário para usar sessões

class ExampleModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Resposta gerada para: {prompt}"

model = ExampleModel("modelo_exemplo")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    response = model.generate(prompt)
    return jsonify({"response": response})

@app.route('/')
def home():
    return "Bem-vindo à aplicação!", 200

# Adicionar suporte para configurações dinâmicas e perfis de usuário
@app.route('/settings', methods=['POST'])
def update_settings():
    data = request.json
    session['settings'] = data
    return jsonify({"message": "Configurações atualizadas!"})

@app.route('/profile', methods=['GET'])
def get_profile():
    return jsonify({"profile": session.get('profile', {})})

if __name__ == '__main__':
    app.run(debug=True)