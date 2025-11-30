from src.llm.base import BaseModel

class ClaudeClient(BaseModel):
    def __init__(self, model_name: str):
        super().__init__(model_name)

    def generate(self, prompt: str) -> str:
        return f"Claude gerou uma resposta para: {prompt}"