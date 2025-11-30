# 🚀 Executando o EstruturaIAGen Dashboard

## Configuração Rápida

### 1. Ativar Virtual Environment

```bash
# Windows
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Executar o Dashboard

**Opção 1: Usando o script de inicialização (Recomendado)**

```bash
python run_dashboard.py
```

**Opção 2: Direto do diretório raiz**

```bash
python -c "import sys; from pathlib import Path; sys.path.insert(0, str(Path('.'))); from web_interface.dashboard_profissional import app; app.run(debug=False, host='127.0.0.1', port=8050)"
```

**Opção 3: Do diretório web_interface (após adicionar ao PYTHONPATH)**

```bash
cd web_interface
set PYTHONPATH=..;%PYTHONPATH%
python dashboard_profissional.py
```

### 4. Acessar o Dashboard

Abra seu navegador em: **http://127.0.0.1:8050**

## 📊 Features Disponíveis

### P2.1 - Exportação de Dados

- CSV com formatação e estatísticas
- PDF com tabelas profissionais (ReportLab)
- JSON com estrutura hierárquica
- Botões de download integrados

### P2.2 - Análise de Drill-down

- Estatísticas descritivas (média, mediana, quartis)
- Detecção de tendências e anomalias
- Comparação de métricas com correlação
- Série temporal agregada

### P2.3 - Temas Customizáveis

- 5 temas predefinidos (Dark, Light, Cyberpunk, Ocean, Forest)
- Criação de temas customizados
- Persistência em JSON
- Exportação para CSS

## 🔧 Troubleshooting

### Erro: ModuleNotFoundError: No module named 'app'

**Solução**: Rodar sempre do diretório raiz do projeto, ou usar `python run_dashboard.py`

### Erro: Port 8050 já em uso

**Solução**: Matar processo Python:

```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
killall python
```

Depois alterar porta no código:

```python
app.run(debug=False, host='127.0.0.1', port=8051)  # outra porta
```

### Warning: ReportLab não instalado

**Solução**:

```bash
pip install reportlab==4.0.4
```

### Erro: dcc.Download não funciona

**Solução**: Certifique-se de que está usando Dash >= 2.0:

```bash
pip install --upgrade dash
```

## 📝 Endpoints Disponíveis

- **GET** `http://127.0.0.1:8050/` - Dashboard principal
- **POST** `http://127.0.0.1:8050/export/csv` - Exportar CSV
- **POST** `http://127.0.0.1:8050/export/pdf` - Exportar PDF
- **POST** `http://127.0.0.1:8050/export/json` - Exportar JSON

## 🧪 Executar Testes

```bash
# Todos os testes
python -m pytest tests/ -v

# Apenas P2
python -m pytest tests/test_export.py tests/test_drilldown.py tests/test_themes.py -v

# Com cobertura
python -m pytest tests/ --cov=app --cov-report=html
```

## 📦 Estrutura do Projeto

```
EstruturaIAGen/
├── app/
│   ├── export/           # Sistema de exportação
│   ├── analysis/         # Análise drill-down
│   ├── themes/           # Sistema de temas
│   ├── cache/            # Cache layer
│   ├── db/               # Database
│   └── models/           # ORM models
├── web_interface/
│   ├── dashboard_profissional.py  # Dashboard Dash
│   └── assets/           # CSS e recursos
├── tests/                # Testes automatizados
├── run_dashboard.py      # Script de inicialização
├── requirements.txt      # Dependências
└── README.md            # Este arquivo
```

## 🎯 Próximos Passos

- [ ] Integrar theme selector no dashboard
- [ ] Adicionar drill-down UI interativa
- [ ] Persistência de preferências de usuário
- [ ] Animações e transições
- [ ] Suporte mobile responsivo

## 📞 Suporte

Para problemas ou dúvidas, verifique:

1. Logs em `dashboard.log`
2. Console do navegador (F12)
3. Terminal onde o servidor está rodando

---

**Versão**: 2.0.0  
**Última atualização**: 30 de Novembro de 2024
