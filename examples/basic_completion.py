# Exemplo básico de geração de texto
from src.llm.base import BaseModel

class ExampleModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Resposta gerada para: {prompt}"

if __name__ == "__main__":
    model = ExampleModel("modelo_exemplo")
    prompt = "Qual é a capital da França?"
    print(model.generate(prompt))