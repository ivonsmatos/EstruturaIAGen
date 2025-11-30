# EstruturaIAGen

## Visão Geral

EstruturaIAGen é um projeto modular desenvolvido em Python, utilizando Flask para a interface web e API, Dash para o painel de monitoramento, SQLite para o banco de dados e integração com AWS S3 para armazenamento em nuvem. O objetivo do projeto é fornecer uma estrutura escalável para aplicações de IA generativa.

## Funcionalidades

- **Interface Web**: Interface desenvolvida com Flask para interação com o usuário.
- **API REST**: Endpoints para geração de texto, análise, exportação de resultados e integração com a nuvem.
- **Painel de Monitoramento**: Painel interativo criado com Dash para visualização de métricas e desempenho.
- **Autenticação**: Sistema de autenticação para proteger os endpoints da API.
- **Banco de Dados**: Integração com SQLite para armazenamento local de dados.
- **Integração com Nuvem**: Upload de arquivos para o AWS S3.
- **Testes de Desempenho**: Scripts para medir o desempenho dos modelos de IA.

## Estrutura do Projeto

```
EstruturaIAGen/
│
├── web_interface/
│   ├── app.py               # Arquivo principal para iniciar a aplicação Flask
│   ├── api.py               # Endpoints da API
│   ├── dashboard.py         # Painel de monitoramento com Dash
│   ├── auth.py              # Sistema de autenticação
│   └── cloud_integration.py # Integração com AWS S3
│
├── src/
│   ├── llm/                 # Modelos de linguagem
│   │   ├── base.py          # Classe base para os modelos
│   │   ├── gpt_client.py    # Cliente para GPT
│   │   └── claude_client.py # Cliente para Claude
│
├── tests/
│   └── performance_test.py  # Testes de desempenho
│
├── config/                  # Arquivos de configuração
│
└── README.md                # Documentação do projeto
```

## Requisitos

- Python 3.10 ou superior
- Pacotes Python:
  - Flask
  - Dash
  - SQLite
  - boto3

## Como Executar

1. Clone o repositório:
   ```bash
   git clone https://github.com/ivonsmatos/EstruturaIAGen.git
   ```
2. Navegue até o diretório do projeto:
   ```bash
   cd EstruturaIAGen
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicie a aplicação:
   ```bash
   python web_interface/app.py
   ```
5. Acesse a aplicação em seu navegador:
   ```
   http://127.0.0.1:5000
   ```

## Exemplos de Uso

### Chamadas à API

#### Exemplo: Geração de Texto

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Escreva um poema sobre o céu."}'
```

#### Exemplo: Upload para AWS S3

```bash
curl -X POST http://127.0.0.1:5000/api/upload \
     -F "file=@caminho/do/arquivo.txt"
```

### Painel de Monitoramento

Acesse o painel em `http://127.0.0.1:5000/dashboard` para visualizar métricas e desempenho.

## Configuração do Ambiente

Certifique-se de configurar as seguintes variáveis de ambiente antes de executar a aplicação:

- `AWS_ACCESS_KEY_ID`: Chave de acesso da AWS.
- `AWS_SECRET_ACCESS_KEY`: Chave secreta da AWS.
- `AWS_BUCKET_NAME`: Nome do bucket S3.

## Testes

Para executar os testes de desempenho:

```bash
python tests/performance_test.py
```

Os resultados dos testes serão exibidos no terminal, incluindo métricas como tempo de resposta e uso de recursos.

## Problemas Conhecidos

- **Erro de Importação**: Certifique-se de que todas as dependências estão instaladas corretamente.
- **Configuração da AWS**: Verifique se as credenciais da AWS estão configuradas corretamente.

## Recursos Úteis

- [Documentação do Flask](https://flask.palletsprojects.com/)
- [Documentação do Dash](https://dash.plotly.com/)
- [Documentação do SQLite](https://www.sqlite.org/docs.html)
- [Documentação do Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Atualizações Recentes

### Integração com Modelos Avançados

- Suporte para OpenAI GPT-4 e Hugging Face Transformers para geração de texto.
- Adicionada integração com Ollama para uso de modelos locais, como Llama-2.

### Painel de Monitoramento

- Gráficos em tempo real e análise de logs adicionados ao painel Dash.

### Automação de Implantação

- Dockerfile atualizado para Python 3.10.
- Suporte para implantação em contêineres.

### Experiência do Usuário

- Frontend moderno adicionado com React.
- Documentação interativa com Swagger.

### Segurança

- Implementação de OAuth2 e JWT para autenticação.

### Funcionalidades Adicionais

- Agendamento de tarefas com Celery.
- Exportação de dados em CSV/JSON.

### Testes Avançados

- Testes de carga adicionados com Locust.

### Integração com Serviços Externos

- Banco de dados migrado para PostgreSQL na nuvem.
- Integração com AWS Lambda para tarefas específicas.

### Personalização

- Configurações dinâmicas e perfis de usuário adicionados.

### Treinamento e Recomendações

- Suporte para treinamento de modelos personalizados.
- Sistema de recomendações baseado em contexto.
