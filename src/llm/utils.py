# Funções utilitárias para modelos de linguagem
import re

def clean_text(text: str) -> str:
    """Remove caracteres indesejados de um texto."""
    return re.sub(r'[^\w\s]', '', text)