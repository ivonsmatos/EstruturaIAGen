import openai
from transformers import pipeline

class GPTIntegration:
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key

    def generate_openai(self, prompt, model="gpt-4"):
        """Gera texto usando o modelo GPT da OpenAI."""
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response['choices'][0]['message']['content']

    def train_custom_model(self, data):
        """Treinar um modelo personalizado com os dados fornecidos."""
        # Simulação de treinamento
        return f"Modelo treinado com {len(data)} exemplos."

    def recommend(self, context):
        """Gerar recomendações com base no contexto."""
        return f"Recomendações geradas para o contexto: {context}"

class HuggingFaceIntegration:
    def __init__(self):
        self.generator = pipeline("text-generation", model="gpt2")

    def generate_huggingface(self, prompt, max_length=50):
        """Gera texto usando um modelo do Hugging Face."""
        result = self.generator(prompt, max_length=max_length, num_return_sequences=1)
        return result[0]['generated_text']