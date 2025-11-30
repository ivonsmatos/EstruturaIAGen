# 📊 Sprint P1: Altos (High Priority) - Planejamento

**Versão**: 1.2.0 → 1.3.0 → 1.4.0  
**Período**: Sprint 2 (Semana de 01-07 de Dezembro)  
**Status**: 🔄 EM PROGRESSO

---

## 🎯 Resumo Executivo

Sprint P1 visa implementar 3 funcionalidades de **alta prioridade**:

| Item     | Título                        | Status          | Dependências | Prazo     |
| -------- | ----------------------------- | --------------- | ------------ | --------- |
| **P1.1** | Testes Automatizados (pytest) | ✅ **COMPLETO** | -            | 30/Nov ✅ |
| **P1.2** | Integração com Banco de Dados | 🔄 EM PROGRESSO | P1.1         | 04/Dez    |
| **P1.3** | Cache de Gráficos (Redis/LRU) | ⏳ PENDENTE     | P1.2         | 07/Dez    |

---

## ✅ P1.1: Testes Automatizados - COMPLETO

**Commit**: `882a09c`  
**Arquivos**:

- `tests/test_dashboard.py` (27 testes)
- `tests/README.md` (documentação)

**Métricas**:

- ✅ 27 testes passando (100%)
- ✅ 94% cobertura de código
- ✅ Tempo: 2.45s por execução
- ✅ Documentação completa

**Teste**:

```bash
pytest tests/test_dashboard.py -v
# RESULTADO: 27 passed in 2.45s ✅
```

---

## 🔄 P1.2: Integração com Banco de Dados - EM PROGRESSO

### 📋 Descrição

Migrar o dashboard de dados gerados dinamicamente (random) para dados persistidos em banco de dados relacional.

### 🎯 Objetivos

1. **Modelos SQLAlchemy** - Criar estrutura de dados

   - `User` - Usuários do sistema
   - `Dashboard` - Painéis
   - `Metric` - Métricas de IA

2. **Session Management** - Gerenciar conexões

   - Context managers
   - Connection pooling
   - Tratamento de erros

3. **Migração de Dados** - Atualizar `generate_data()`

   - Buscar do BD em vez de gerar aleatoriamente
   - Fallback para dados de teste
   - Suporte a múltiplos períodos

4. **Testes de Integração** - Validar BD

   - Mocks SQLAlchemy
   - Testes de sessão
   - Testes de agregação

5. **Scripts de Migração** - Inicializar dados
   - Criar tabelas
   - Popular com dados de exemplo
   - Verificação

### 📦 Arquivos a Criar

```
app/
├── models/
│   └── database.py          [NEW] Modelos SQLAlchemy + DatabaseManager
└── db/
    └── session.py           [NEW] Session management + pooling

tests/
├── test_database_models.py  [NEW] Testes de modelos
├── test_database_fetch.py   [NEW] Testes de fetch_metrics_from_db()
└── test_session_mgmt.py     [NEW] Testes de sessão/pooling

migrations/
└── init_db.py              [NEW] Script de inicialização
```

### 📝 Arquivos a Modificar

```
web_interface/
└── dashboard_profissional.py [MODIFY] Usar fetch_metrics_from_db()

requirements.txt             [UPDATE] +sqlalchemy, +alembic, +psycopg2
.env.example                 [UPDATE] +DATABASE_URL, +DB_POOL_*
CHANGELOG.md                 [UPDATE] v1.3.0 section
```

### 🔧 Tarefas Detalhadas

**Tarefa 1: Modelos de Dados** (1h)

- [ ] Criar `app/models/database.py`
- [ ] Implementar 3 modelos + relationships
- [ ] Implementar `DatabaseManager`
- [ ] Teste: `pytest tests/test_database_models.py`

**Tarefa 2: Session Management** (30min)

- [ ] Criar `app/db/session.py`
- [ ] Implementar context manager
- [ ] Configurar connection pooling
- [ ] Teste: Concorrência com 10+ sessões

**Tarefa 3: Migrar `generate_data()`** (45min)

- [ ] Criar `fetch_metrics_from_db()`
- [ ] Refatorar `generate_data()` para usar BD
- [ ] Implementar fallback
- [ ] Teste: Dashboard ainda funciona

**Tarefa 4: Testes com Mocks** (1h)

- [ ] Criar `tests/test_database_models.py`
- [ ] Criar `tests/test_database_fetch.py`
- [ ] Criar `tests/test_session_mgmt.py`
- [ ] 12+ testes, >85% coverage

**Tarefa 5: Scripts de Migração** (30min)

- [ ] Criar `migrations/init_db.py`
- [ ] Testar: `python migrations/init_db.py`
- [ ] Verificar dados com sqlite3

### 📊 Testes (12+)

```
test_database_models.py:
  ✓ test_create_user
  ✓ test_user_relationships
  ✓ test_create_dashboard
  ✓ test_create_metric
  ✓ test_metric_aggregation

test_database_fetch.py:
  ✓ test_fetch_24h
  ✓ test_fetch_7d
  ✓ test_fetch_30d
  ✓ test_fetch_fallback
  ✓ test_fetch_error_handling

test_session_mgmt.py:
  ✓ test_context_manager_commit
  ✓ test_context_manager_rollback
  ✓ test_connection_pool_limits
```

### ⏱️ Cronograma

| Tarefa          | Tempo   | Início | Fim        | Status |
| --------------- | ------- | ------ | ---------- | ------ |
| 1. Modelos      | 1h      | 01/Dez | 01/Dez     | ⏳     |
| 2. Session Mgmt | 30min   | 01/Dez | 02/Dez     | ⏳     |
| 3. Migrar dados | 45min   | 02/Dez | 02/Dez     | ⏳     |
| 4. Testes       | 1h      | 02/Dez | 03/Dez     | ⏳     |
| 5. Migrations   | 30min   | 03/Dez | 04/Dez     | ⏳     |
| QA & Commit     | 15min   | 04/Dez | 04/Dez     | ⏳     |
| **TOTAL**       | **~4h** |        | **04/Dez** | 🔄     |

### 📍 Localização de Informações

Documentação detalhada: [`P1_DATABASE_INTEGRATION.md`](./P1_DATABASE_INTEGRATION.md)

---

## ⏳ P1.3: Cache de Gráficos - PENDENTE

### 📋 Descrição

Implementar cache em memória (LRU) para gráficos Plotly, reduzindo latência em 70%.

### 🎯 Objetivos

1. **Cache LRU**

   - Implementar com `functools.lru_cache`
   - TTL configurável (5min, 15min, 1h)
   - Invalidação manual

2. **Redis Integration** (opcional)

   - Cache distribuído
   - Compartilhamento entre workers
   - Persistência

3. **Monitoramento**
   - Métricas de hit/miss
   - Taxa de acerto
   - Tamanho do cache

### 📦 Arquivos

```
app/cache/
├── __init__.py
├── cache_manager.py    [NEW]
├── redis_cache.py      [NEW] (opcional)
└── decorators.py       [NEW]

tests/
└── test_cache.py       [NEW]
```

### ⏱️ Cronograma

| Fase             | Tempo | Prazo  |
| ---------------- | ----- | ------ |
| LRU Cache        | 45min | 05/Dez |
| Monitoramento    | 30min | 06/Dez |
| Redis (opcional) | 1h    | 07/Dez |
| Testes           | 45min | 07/Dez |

### 📍 Localização

Documentação detalhada: [`P1_CACHE_IMPLEMENTATION.md`](./P1_CACHE_IMPLEMENTATION.md) (a ser criado)

---

## 📈 Roadmap Visual

```
Sprint P1 (Altos) - Semana de 1-7 de Dezembro
═══════════════════════════════════════════════

01/Dez (Seg)  |████████████████████████████████ P1.2 Start (Modelos)
02/Dez (Ter)  |████████████████████████████████ P1.2 (Session Mgmt + Migração)
03/Dez (Qua)  |████████████████████████████████ P1.2 (Testes + Migrations)
04/Dez (Qui)  |████████████████████ ▓▓▓▓▓▓▓▓▓▓▓ P1.2 Complete + P1.3 Start
05/Dez (Sex)  |████████████████████████████████ P1.3 (LRU Cache)
06/Dez (Sab)  |████████████████████████████████ P1.3 (Monitoramento)
07/Dez (Dom)  |████████████████████ ▓▓▓▓▓▓▓▓▓▓▓ P1.3 Complete (QA)

Legend:
  ████ = Development work
  ▓▓▓▓ = Testing & QA

Milestone: P1 Sprint Complete by 07/Dez ✓
```

---

## 🔗 Dependências entre Tarefas

```
P1.1 (Testes)
    ↓ [COMPLETO ✅]
    ├─→ P1.2 (BD) [Pronto para iniciar]
    │       ├─→ P1.3 (Cache) [Bloqueado por P1.2]
    │
    └─→ Dashboard QA [Iniciado]
```

---

## 📊 Métricas de Sucesso

### P1.1 ✅ (Testes Automatizados)

- [x] 27 testes criados
- [x] 94% cobertura de código
- [x] Tempo: <3s por execução
- [x] Documentação completa

### P1.2 🔄 (Banco de Dados)

- [ ] 3 modelos SQLAlchemy
- [ ] 12+ testes de BD
- [ ] Dashboard busca dados reais
- [ ] Scripts de migração funcionais
- [ ] Pool de conexões: 10/20
- [ ] 100% commits documentados

### P1.3 ⏳ (Cache)

- [ ] LRU Cache implementado
- [ ] Hit rate: >70%
- [ ] Redis opcional integrado
- [ ] Métricas de monitoramento
- [ ] TTL configurável

---

## 🚀 Checklist de Sprint

- [x] P1.1 Completo (Testes)
- [ ] P1.2 em Progresso (BD)
  - [ ] Modelos criados
  - [ ] Session manager pronto
  - [ ] generate_data() refatorada
  - [ ] Testes verdes
  - [ ] Migrations testadas
  - [ ] Commit no GitHub
- [ ] P1.3 Pendente (Cache)
  - [ ] LRU Cache
  - [ ] Monitoramento
  - [ ] Testes completos
  - [ ] Documentação
  - [ ] Commit no GitHub

---

## 📚 Referências de Documentação

| Recurso        | Link                                      |
| -------------- | ----------------------------------------- |
| P1.1 Completo  | `tests/README.md`                         |
| P1.2 Detalhado | `P1_DATABASE_INTEGRATION.md`              |
| P1.3 Detalhado | `P1_CACHE_IMPLEMENTATION.md` (TBD)        |
| Testes         | `tests/test_dashboard.py`                 |
| Dashboard      | `web_interface/dashboard_profissional.py` |

---

## 📞 Contato & Suporte

- **Tech Lead**: Estrutura IA Gen
- **Repository**: `EstruturaIAGen`
- **Branch**: `main` (manter verde ✅)
- **Slack**: #sprint-updates

---

**Última Atualização**: 30/Nov/2025  
**Próxima Revisão**: Diariamente (Status Updates)  
**Sprint End Review**: 07/Dez/2025
