# Base para integração com modelos de linguagem
class BaseModel:
    """Classe base para integração com modelos de linguagem.

    Attributes:
        model_name (str): Nome do modelo.
    """
    def __init__(self, model_name: str):
        """Inicializa a classe BaseModel.

        Args:
            model_name (str): Nome do modelo.
        """
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        """Gera uma resposta com base no prompt fornecido.

        Args:
            prompt (str): Texto de entrada para o modelo.

        Returns:
            str: Resposta gerada pelo modelo.
        """
        raise NotImplementedError("Este método deve ser implementado pelas subclasses.")

class ModelFactory:
    """Fábrica para criar instâncias de diferentes modelos de linguagem."""
    @staticmethod
    def create_model(model_type: str):
        """Cria uma instância do modelo com base no tipo fornecido.

        Args:
            model_type (str): Tipo do modelo (ex.: "gpt", "claude").

        Returns:
            BaseModel: Instância do modelo correspondente.
        """
        if model_type == "gpt":
            from src.llm.gpt_client import GPTClient
            return GPTClient("GPT")
        elif model_type == "claude":
            from src.llm.claude_client import ClaudeClient
            return ClaudeClient("Claude")
        else:
            raise ValueError(f"Modelo desconhecido: {model_type}")