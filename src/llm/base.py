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