# Treinamento personalizado
import json

def preprocess_data(file_path):
    """Pré-processa os dados para treinamento.

    Args:
        file_path (str): Caminho para o arquivo de dados.

    Returns:
        list: Dados pré-processados.
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return [(item['input'], item['output']) for item in data]

def train_model(data, model):
    """Treina o modelo com os dados fornecidos.

    Args:
        data (list): Dados de treinamento.
        model (BaseModel): Instância do modelo.
    """
    for input_text, output_text in data:
        # Simulação de treinamento
        print(f"Treinando com entrada: {input_text} e saída: {output_text}")

# Exemplo de uso
if __name__ == "__main__":
    from src.llm.base import BaseModel

    class ExampleModel(BaseModel):
        def generate(self, prompt: str) -> str:
            return f"Resposta gerada para: {prompt}"

    model = ExampleModel("modelo_exemplo")
    training_data = preprocess_data("data/training_data.json")
    train_model(training_data, model)