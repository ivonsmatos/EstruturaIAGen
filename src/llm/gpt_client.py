from src.llm.base import BaseModel

class GPTClient(BaseModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)

    def generate(self, prompt: str) -> str:
        return f"GPT gerou uma resposta para: {prompt}"