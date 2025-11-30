import requests

class OllamaIntegration:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def generate(self, prompt, model="llama-2"):
        """Gera texto usando o Ollama."""
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt
        }
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json().get("text", "")
        else:
            raise Exception(f"Erro ao se comunicar com o Ollama: {response.status_code}, {response.text}")