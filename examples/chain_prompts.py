# Exemplo de encadeamento de prompts
from src.prompt_engineering.templates import PromptTemplate

if __name__ == "__main__":
    template = PromptTemplate("Explique o conceito de {conceito} em termos simples.")
    prompt = template.format(conceito="Inteligência Artificial")
    print(prompt)