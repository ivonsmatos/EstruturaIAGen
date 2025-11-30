# EstruturaIAGen

## Visão Geral

Um modelo estruturado de projeto de IA generativa para construir aplicações robustas de IA, seguindo as melhores práticas de manutenção e escalabilidade.

## Como Começar

1. Clone o repositório.
2. Instale as dependências a partir do `requirements.txt`.
3. Configure as definições do modelo.
4. Revise o código de exemplo.
5. Comece com notebooks para testes.

## Estrutura do Projeto

- `config/`: Configuração separada do código.
- `src/`: Código-fonte principal com organização modular.
- `data/`: Armazenamento organizado para diferentes tipos de dados.
- `examples/`: Referências de implementação.
- `notebooks/`: Experimentação e análise.

## Melhores Práticas

- Use YAML para arquivos de configuração.
- Implemente tratamento adequado de erros.
- Use limitação de taxa para APIs.
- Separe os dados do modelo.
- Armazene resultados em cache apropriadamente.
- Mantenha documentação.
- Use notebooks para testes.

## Exemplos de Uso

### Geração de Texto Básica

```python
from src.llm.base import BaseModel

class ExampleModel(BaseModel):
    def generate(self, prompt: str) -> str:
        return f"Resposta gerada para: {prompt}"

model = ExampleModel("modelo_exemplo")
prompt = "Qual é a capital da França?"
print(model.generate(prompt))
```

### Encadeamento de Prompts

```python
from src.prompt_engineering.templates import PromptTemplate

template = PromptTemplate("Explique o conceito de {conceito} em termos simples.")
prompt = template.format(conceito="Inteligência Artificial")
print(prompt)
```

## Configuração do Ambiente

1. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

2. Execute os exemplos:

   ```bash
   python examples/basic_completion.py
   ```

3. Experimente os notebooks:
   Abra os arquivos na pasta `notebooks/` usando Jupyter Notebook ou VS Code.
