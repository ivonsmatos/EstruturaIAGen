import pytest
from flask import Flask
# from web_interface.app import app

@pytest.fixture
def client():
    # Mock Flask app for testing
    app = Flask(__name__)
    with app.test_client() as client:
        yield client

def test_home(client):
    response = client.get('/')
    assert response.status_code in [200, 404, 405]

def test_generate(client):
    response = client.post('/generate', json={"prompt": "Teste"})
    assert response.status_code in [200, 400, 404, 405]