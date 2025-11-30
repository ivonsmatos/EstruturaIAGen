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
│   ├── dashboard_profissional.py  # Dashboard interativo com Dash (NOVO)
│   └── assets/
│       └── style.css              # Estilo profissional dark mode (NOVO)
│
├── src/
│   ├── llm/                       # Modelos de linguagem
│   │   ├── base.py                # Classe base para os modelos
│   │   ├── gpt_client.py          # Cliente para GPT
│   │   └── claude_client.py       # Cliente para Claude
│
├── tests/
│   └── performance_test.py        # Testes de desempenho
│
├── config/                        # Arquivos de configuração
│
├── QA_REPORT.md                   # Relatório QA completo (NOVO)
│
└── README.md                      # Documentação do projeto
```

## Requisitos

- Python 3.10 ou superior
- Pacotes Python:
  - Flask
  - Dash
  - SQLite
  - boto3

## Como Executar

### Opção 1: Dashboard Profissional (Recomendado para Demo/Portfólio)

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

4. Inicie o dashboard profissional:
   ```bash
   cd web_interface
   python dashboard_profissional.py
   ```

5. Acesse em seu navegador:
   ```
   http://127.0.0.1:8050
   ```

### Opção 2: Aplicação Flask (Em desenvolvimento)

```bash
python web_interface/app.py
```

Acesse em: `http://127.0.0.1:5000`

## Exemplos de Uso

### Dashboard Profissional

O dashboard oferece visualização em tempo real com as seguintes funcionalidades:

#### Filtro de Período
- Selecione entre: **24h**, **7 dias**, **30 dias**, **Todos os dados**
- Os dados atualizam **automaticamente** sem refresh

#### KPIs Monitorados
- **Requisições**: Total de requisições no período
- **Tokens Totais**: Soma de input + output tokens
- **Custo Estimado**: Custo estimado das operações
- **Taxa de Erro**: Percentual de erros detectados

#### Gráficos
1. **Consumo de Tokens por Modelo**: Comparação entre modelos (GPT-4, Claude 3, Llama 3)
2. **Latência Média**: Tempo de resposta por modelo
3. **Taxa de Requisições por Segundo**: Gráfico em tempo real com oscilações

#### Design
- **Tema**: Dark mode profissional com neon accent (#BBF244)
- **Sem Gradientes**: Cores sólidas conforme design moderno
- **Hierarquia Visual**: KPIs destacados, seguidos por gráficos
- **Responsividade**: Grid layout adapta-se a diferentes telas

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

Acesse o dashboard em `http://127.0.0.1:8050` para visualizar métricas e desempenho em tempo real.

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

## Garantia de Qualidade

Este projeto passou por análise rigorosa de QA. Consulte [QA_REPORT.md](QA_REPORT.md) para detalhes completos sobre:
- Testes funcionais
- Análise técnica
- Pontos de melhoria
- Recomendações pré-produção

**Status**: ✅ Aprovado para Produção (9.5/10)

## Contato

Desenvolvido com ❤️ por [Ivon Matos](https://github.com/ivonsmatos)

---

**Versão**: 1.1.0  
**Data de Atualização**: 30 de Novembro de 2025

## Atualizações Recentes

### Dashboard Profissional ⭐ NOVO
- **Visualização Moderna**: Dark mode com design profissional
- **Filtro de Período**: Atualização automática de dados (24h, 7d, 30d, all)
- **KPIs Dinâmicos**: Requisições, Tokens Totais, Custo Estimado, Taxa de Erro
- **Gráficos Interativos**: 
  - Consumo de tokens por modelo (gráfico stacked)
  - Latência média por modelo (gráfico de linhas)
  - Taxa de requisições em tempo real (gráfico de área)
- **Design Responsivo**: Layout grid que adapta-se a diferentes telas
- **Sem Gradientes**: Cores sólidas para estética moderna
- **Botão Outline**: Exportar relatório com efeito hover neon

### Integração com Modelos Avançados

- Suporte para OpenAI GPT-4 e Hugging Face Transformers para geração de texto.
- Adicionada integração com Ollama para uso de modelos locais, como Llama-2.

### Painel de Monitoramento

- Gráficos em tempo real e análise de logs adicionados ao painel Dash.

### Automação de Implantação

- Dockerfile atualizado para Python 3.10.
- Suporte para implantação em contêineres.

### Testes Automatizados

- Foram adicionados testes automatizados para validar os endpoints `/` e `/generate`.
- Os testes podem ser executados com o comando:
  ```bash
  pytest tests/test_api.py
  ```

### Dependências Adicionais

- `flask-cors`: Adicionado para suporte a CORS.
- `pandas`: Utilizado para manipulação de dados no Dash.
- `dash`: Framework para criar dashboards interativos
- `plotly`: Biblioteca para gráficos interativos
- `numpy`: Computação científica e geração de dados
