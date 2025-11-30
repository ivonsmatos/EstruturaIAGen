# Testes para o módulo base
import pytest
from src.llm.base import BaseModel

class TestModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Teste: {prompt}"

def test_generate():
    model = TestModel("modelo_teste")
    result = model.generate("Teste de prompt")
    assert result == "Teste: Teste de prompt"