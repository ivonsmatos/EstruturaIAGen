# Interface Web usando Flask
from flask import Flask, request, jsonify
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.llm.base import BaseModel

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)