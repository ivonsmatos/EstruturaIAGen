# Testes de Desempenho
import time
from src.llm.base import BaseModel

class ExampleModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Resposta gerada para: {prompt}"

def measure_performance(model, prompt, iterations=100):
    """Mede o desempenho do modelo.

    Args:
        model (BaseModel): Instância do modelo.
        prompt (str): Prompt de entrada.
        iterations (int): Número de iterações.

    Returns:
        dict: Métricas de desempenho.
    """
    start_time = time.time()
    for _ in range(iterations):
        model.generate(prompt)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time = total_time / iterations

    return {
        "total_time": total_time,
        "avg_time_per_request": avg_time,
        "iterations": iterations
    }

# Exemplo de uso
if __name__ == "__main__":
    model = ExampleModel("modelo_exemplo")
    prompt = "Qual é a capital da França?"
    metrics = measure_performance(model, prompt)
    print("Métricas de desempenho:", metrics)