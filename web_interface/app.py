# Interface Web usando Flask
from flask import Flask, request, jsonify
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

if __name__ == '__main__':
    app.run(debug=True)