# API REST usando Flask
from flask import Flask, request, jsonify
from src.llm.base import BaseModel, ModelFactory
from web_interface.database import Database
from web_interface.auth import require_api_key
from web_interface.export import export_to_csv, export_to_json
from web_interface.cloud_integration import upload_to_s3

app = Flask(__name__)

class ExampleModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Resposta gerada para: {prompt}"

model = ExampleModel("modelo_exemplo")
db = Database()

@app.route('/api/generate', methods=['POST'])
@require_api_key
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    response = model.generate(prompt)
    db.insert_log(prompt, response)
    return jsonify({"response": response})

@app.route('/api/analyze', methods=['POST'])
@require_api_key
def analyze():
    data = request.json
    response = data.get('response', '')
    analysis = {
        "length": len(response),
        "words": len(response.split()),
        "uppercase_count": sum(1 for c in response if c.isupper())
    }
    return jsonify({"analysis": analysis})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    logs = db.fetch_logs()
    return jsonify({"logs": logs})

@app.route('/api/select_model', methods=['POST'])
def select_model():
    data = request.json
    model_type = data.get('model_type', 'gpt')
    try:
        global model
        model = ModelFactory.create_model(model_type)
        return jsonify({"message": f"Modelo {model_type} selecionado com sucesso."})
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/export/csv', methods=['GET'])
@require_api_key
def export_csv():
    file_path = "data/logs.csv"
    export_to_csv(file_path)
    return jsonify({"message": f"Logs exportados para {file_path}"})

@app.route('/api/export/json', methods=['GET'])
@require_api_key
def export_json():
    file_path = "data/logs.json"
    export_to_json(file_path)
    return jsonify({"message": f"Logs exportados para {file_path}"})

@app.route('/api/upload/s3', methods=['POST'])
@require_api_key
def upload_logs_to_s3():
    data = request.json
    bucket_name = data.get('bucket_name', 'default-bucket')
    file_path = "data/logs.json"
    try:
        upload_to_s3(file_path, bucket_name)
        return jsonify({"message": f"Logs enviados para o bucket {bucket_name}."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)