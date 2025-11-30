# Implementação de um limitador de taxa
import time

class RateLimiter:
    """Implementação de um limitador de taxa.

    Attributes:
        max_calls (int): Número máximo de chamadas permitidas.
        period (float): Período de tempo em segundos.
        calls (list): Lista de timestamps das chamadas.
    """
    def __init__(self, max_calls: int, period: float):
        """Inicializa o limitador de taxa.

        Args:
            max_calls (int): Número máximo de chamadas permitidas.
            period (float): Período de tempo em segundos.
        """
        self.max_calls = max_calls
        self.period = period
        self.calls = []

    def is_allowed(self) -> bool:
        """Verifica se uma nova chamada é permitida.

        Returns:
            bool: True se a chamada for permitida, False caso contrário.
        """
        now = time.time()
        self.calls = [call for call in self.calls if call > now - self.period]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False