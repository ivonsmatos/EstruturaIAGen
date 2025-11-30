# 🚀 CI/CD e DevOps - EstruturaIAGen

## Visão Geral

Este documento descreve a estratégia de CI/CD (Continuous Integration / Continuous Deployment) e DevOps para o projeto EstruturaIAGen, implementando um pipeline automatizado de alta qualidade.

---

## 1. GitHub Actions Pipeline (main.yml)

### 🎯 Objetivos

- ✅ Automatizar testes em cada push/PR
- ✅ Bloquear merge se cobertura < 90%
- ✅ Verificar qualidade de código com linters
- ✅ Realizar scans de segurança
- ✅ Fazer build e deploy automático do Docker

### 📋 Jobs Implementados

#### 1.1 **Test Job** (Matriz Python 3.10, 3.11, 3.12)

```yaml
- Checkout do código
- Setup Python com cache pip
- Instalação de dependências
- Pylint para análise de qualidade
- Pytest com cobertura de código (mín. 90%)
- Upload para Codecov
- Relatório de cobertura em HTML
```

**Resultado esperado**: 212 testes passando com cobertura ≥ 90%

#### 1.2 **Build Job** (somente em push para main)

```yaml
- Build da imagem Docker
- Push para Docker Hub (se credenciais fornecidas)
- Verificação de sucesso
```

**Trigger**: Apenas em push para `main` e após sucesso do `test` job

#### 1.3 **Lint Job** (verificação de qualidade)

```yaml
- Black: Verificação de formatação
- Flake8: Linting
- Pylint: Análise estática
- Mypy: Type checking
```

#### 1.4 **Security Job** (scans de segurança)

```yaml
- Bandit: Scan de vulnerabilidades de segurança
- Safety: Verificação de dependências vulneráveis
```

#### 1.5 **Notify Job** (notificações finais)

```yaml
- Sucesso/Falha do pipeline
- Relatório consolidado
```

---

## 2. Docker Setup

### 2.1 Dockerfile

```dockerfile
FROM python:3.11-slim
- Python 3.11 (moderno, estável)
- Usuário não-root (appuser, UID 1000)
- Health check configurado
- Otimizado para produção
```

**Build e Deploy**:
```bash
# Build local
docker build -t estruturaiagen:latest .

# Push para Docker Hub (com credenciais)
docker tag estruturaiagen:latest username/estruturaiagen:latest
docker push username/estruturaiagen:latest
```

### 2.2 Docker Compose

Arquivo `docker-compose.yml` com 3 serviços:

#### Serviço 1: Dashboard (Dash)
- Porta: 8050
- Healthcheck: Verifica endpoint /
- Restart: unless-stopped

#### Serviço 2: Redis
- Porta: 6379
- Volume persistente: redis-data
- Persistence: AOF habilitado
- Healthcheck: redis-cli ping

#### Serviço 3: PostgreSQL
- Porta: 5432
- Database: estruturaiagen_db
- User: estrutura_user
- Volume persistente: postgres-data
- Healthcheck: pg_isready

**Uso**:

```bash
# Iniciar em desenvolvimento
docker-compose up -d

# Ver logs
docker-compose logs -f dashboard

# Parar e limpar
docker-compose down -v

# Rebuild
docker-compose build --no-cache
```

---

## 3. Configuração do GitHub Actions

### 3.1 Variáveis de Ambiente

Adicione os seguintes secrets no repositório GitHub (Settings → Secrets):

```
DOCKER_USERNAME      # Seu usuário Docker Hub
DOCKER_PASSWORD      # Token de acesso Docker Hub
CODECOV_TOKEN        # Token Codecov (opcional)
```

### 3.2 Configuração Inicial

1. **Criar workflow**: `.github/workflows/main.yml` (já criado)

2. **Proteger branch main**:
   - Settings → Branches → Add rule
   - Branch name: `main`
   - ✅ Require status checks to pass before merging
   - ✅ Require code reviews before merging
   - ✅ Require passing builds

3. **Configurar secrets**:
   ```bash
   # Gerar Docker Hub token em hub.docker.com/settings/security
   gh secret set DOCKER_USERNAME -b "seu_usuario"
   gh secret set DOCKER_PASSWORD -b "seu_token"
   ```

---

## 4. Fluxo de Desenvolvimento

### 4.1 Local Development

```bash
# 1. Criar feature branch
git checkout -b feature/sua-feature

# 2. Fazer alterações
# ... editar arquivos ...

# 3. Rodar testes localmente
pytest tests/ --cov=app --cov-report=term-missing

# 4. Commit
git add .
git commit -m "feat: descrição da feature"

# 5. Push
git push origin feature/sua-feature
```

### 4.2 Pull Request Workflow

1. **Criar PR** no GitHub
2. **GitHub Actions roda automaticamente**:
   - ✅ Testes em 3 versões Python
   - ✅ Linting (Black, Flake8, Pylint, Mypy)
   - ✅ Security scan (Bandit, Safety)
   - ✅ Cobertura mínima 90%
3. **Revisão de código** (obrigatória)
4. **Merge** quando todas as checks passarem
5. **Push para main** dispara build Docker

---

## 5. Monitoramento e Observabilidade

### 5.1 Logs do CI/CD

Acesse em: `https://github.com/ivonsmatos/EstruturaIAGen/actions`

Verificar:
- ✅ Status dos testes
- ✅ Cobertura de código
- ✅ Resultados de linting
- ✅ Scans de segurança

### 5.2 Coverage Reports

- **HTML Report**: Gerado automaticamente em `htmlcov/`
- **Codecov**: Upload automático para codecov.io
- **Badge**: ![Coverage Badge](https://img.shields.io/codecov/c/github/ivonsmatos/EstruturaIAGen)

---

## 6. Troubleshooting

### 6.1 Pipeline falha nos testes

```bash
# Rodar localmente para debug
pytest tests/ --ignore=tests/test_api.py -v

# Verificar cobertura
coverage report --fail-under=90
```

### 6.2 Docker build falha

```bash
# Build local para debug
docker build -t estruturaiagen:test .

# Ver logs detalhados
docker build --progress=plain -t estruturaiagen:test .
```

### 6.3 Linting falha

```bash
# Verificar e corrigir com Black
black app/ src/ tests/

# Executar Pylint
pylint app/ src/ --exit-zero
```

---

## 7. Roadmap - Próximos Passos

### 7.1 Immediate (P4.1)
- ✅ CI/CD com GitHub Actions
- ✅ Docker containerization
- ⏳ Configurar branch protection

### 7.2 Short-term (P4.2)
- ⏳ Automated deployment para staging
- ⏳ Performance testing pipeline
- ⏳ SAST (Static Application Security Testing)

### 7.3 Medium-term (P4.3)
- ⏳ Kubernetes deployment configs
- ⏳ ArgoCD para GitOps
- ⏳ Infrastructure as Code (Terraform)

### 7.4 Long-term (P4.4)
- ⏳ Multi-region deployment
- ⏳ Observabilidade avançada (Prometheus, Grafana)
- ⏳ Disaster recovery procedures

---

## 8. Referências

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

---

**Versão**: 1.0  
**Última atualização**: 30 de Novembro de 2025  
**Status**: Production Ready
