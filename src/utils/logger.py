# Sistema de logging aprimorado
import logging

def setup_logger(name: str, level: str = "INFO", log_file: str = None):
    """Configura o logger.

    Args:
        name (str): Nome do logger.
        level (str): Nível de log (INFO, DEBUG, etc.).
        log_file (str): Arquivo para salvar os logs (opcional).

    Returns:
        logging.Logger: Instância configurada do logger.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger