# Autenticação e Controle de Acesso
from functools import wraps
from flask import request, jsonify

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