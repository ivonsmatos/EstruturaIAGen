# Autenticação e Controle de Acesso
from functools import wraps
from flask import request, jsonify, Flask
from flask_oauthlib.provider import OAuth2Provider
import jwt

app = Flask(__name__)
oauth = OAuth2Provider(app)

API_KEY = "minha_chave_secreta"

def require_api_key(f):
    """Decorator para exigir autenticação por chave API."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("x-api-key")
        if api_key != API_KEY:
            return jsonify({"error": "Acesso negado: chave API inválida."}), 403
        return f(*args, **kwargs)
    return decorated_function

# Configuração de exemplo para OAuth2
@app.route('/token', methods=['POST'])
def generate_token():
    data = request.json
    user_id = data.get('user_id')
    token = jwt.encode({'user_id': user_id}, 'secret_key', algorithm='HS256')
    return jsonify({'token': token})