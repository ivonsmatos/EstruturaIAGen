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

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
