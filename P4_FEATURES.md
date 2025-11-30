"""
P4.3, P4.4, P4.5 Features Documentation
Advanced Features: Alerts, Async Architecture, RBAC
"""

# P4.3 - ALERTAS ATIVOS

## Visão Geral

Sistema completo de alertas com múltiplos canais de notificação, regras customizáveis e rastreamento de histórico.

## Componentes Principais

### AlertRule

- **Propósito**: Define condições para gatilho de alertas
- **Atributos**:
  - `metric`: Métrica a ser monitorada (error_rate, cpu_usage, cost, etc)
  - `condition`: Tipo de comparação (greater_than, less_than, equals, between)
  - `threshold`: Valor limite
  - `severity`: LOW, MEDIUM, HIGH, CRITICAL
  - `check_interval`: Intervalo de verificação (segundos)
  - `max_consecutive_before_alert`: Número de violações consecutivas antes de alertar
  - `cooldown`: Tempo mínimo entre alertas da mesma regra
  - `channels`: Canais de notificação (EMAIL, SLACK, WEBHOOK)

### Alert

- **Propósito**: Representa um alerta disparado
- **Atributos**:
  - `rule_id`: ID da regra que disparou
  - `severity`: Nível de severidade
  - `current_value`: Valor atual da métrica
  - `threshold`: Valor limite
  - `acknowledged`: Se foi reconhecido
  - `metadata`: Dados adicionais

### Canais de Notificação

1. **EmailChannel**: Envia emails HTML formatados
2. **SlackChannel**: Integração com Slack webhooks
3. **WebhookChannel**: Webhooks customizados

## Uso

```python
from app.alerts import get_alert_manager, AlertSeverity, AlertChannel

# Obter gerenciador
alert_mgr = get_alert_manager()

# Criar regra
rule = alert_mgr.add_rule(
    name="High Error Rate",
    metric="error_rate",
    condition="greater_than",
    threshold=5.0,
    severity=AlertSeverity.HIGH,
    channels=[AlertChannel.EMAIL, AlertChannel.SLACK],
    check_interval=300,
    max_consecutive=2,
    cooldown=3600
)

# Avaliar e disparar alerta
alert = alert_mgr.evaluate_rule(rule.id, current_value=7.5)

# Reconhecer alerta
if alert:
    alert_mgr.acknowledge_alert(alert.id, user_id="admin")

# Obter alertas ativos
active = alert_mgr.get_active_alerts()

# Subscrever a eventos
def on_alert(alert):
    print(f"Alerta disparado: {alert.rule_name}")

alert_mgr.subscribe(on_alert)
```

## Variáveis de Ambiente

```
ALERT_EMAIL_SENDER=your-email@gmail.com
ALERT_EMAIL_PASSWORD=app-specific-password
ALERT_EMAIL_RECIPIENTS=admin@example.com,ops@example.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

## UI

- Dashboard com abas para alertas ativos, gerenciamento de regras, histórico e estatísticas
- Criação visual de regras sem código
- Visualização em tempo real de alertas
- Timeline de alertas com Plotly

---

# P4.4 - CELERY/ASYNC ARCHITECTURE

## Visão Geral

Arquitetura assíncrona com Celery + Redis para processamento de tarefas de longa duração, agendamento periódico e fila de trabalho.

## Componentes Principais

### Task Types

1. **LLM Inference**: Processamento de chat com LLM
2. **Heavy Computation**: Cálculos ML, previsões
3. **Database Operations**: Operações bulk, migrações
4. **Notifications**: Envio de emails, SMS, push
5. **System Health**: Verificação de saúde, alertas
6. **Data Export**: Exportação assíncrona de dados

### Celery Configuration

- **Broker**: Redis (default: localhost:6379/0)
- **Result Backend**: Redis (default: localhost:6379/1)
- **Task Serializer**: JSON
- **Worker Prefetch**: 4 tasks
- **Soft Timeout**: 10 minutos
- **Hard Timeout**: 15 minutos

### Task Routes (Queue Separation)

```python
{
    'llm': {'queue': 'llm', 'routing_key': 'llm.task'},
    'compute': {'queue': 'compute', 'routing_key': 'compute.task'},
    'db': {'queue': 'db', 'routing_key': 'db.task'},
    'notifications': {'queue': 'notifications', 'routing_key': 'notify.task'}
}
```

### Periodic Tasks (Beat Schedule)

```
- check-alerts-every-5-minutes: Verifica alertas do sistema
- update-dashboard-cache-every-10-minutes: Atualiza cache
- cleanup-old-sessions-daily (2 AM): Limpa sessões antigas
- generate-reports-daily (1 AM): Gera relatórios diários
- health-check-every-minute: Verifica saúde do sistema
```

## Uso

```python
from app.async_tasks import llm_inference, heavy_computation
from app.celery_config import celery_app

# Executar tarefa assíncrona
task = llm_inference.delay(
    prompt="Qual é o impacto disso?",
    model="gpt-3.5-turbo",
    max_tokens=500
)

# Aguardar resultado (com timeout)
result = task.get(timeout=30)

# Executar computação pesada
computation = heavy_computation.apply_async(
    args=({'data': 'value'}, 'forecast'),
    queue='compute'
)

# Verificar status
status = computation.status  # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE'
```

## Workers

```bash
# Worker padrão
celery -A app.celery_config worker --loglevel=info

# Worker especializado em LLM
celery -A app.celery_config worker -Q llm --concurrency=2

# Scheduler (Beat)
celery -A app.celery_config beat --loglevel=info

# Monitoramento (Flower)
celery -A app.celery_config flower --port=5555
```

## Variáveis de Ambiente

```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

---

# P4.5 - RBAC (ROLE-BASED ACCESS CONTROL)

## Visão Geral

Sistema completo de controle de acesso baseado em funções com suporte a 2FA, auditoria e permissões granulares.

## Conceitos Principais

### ResourceTypes

- DASHBOARD, REPORTS, SETTINGS, USERS, ALERTS, AUDIT_LOG, CHAT, ANALYTICS, EXPORT, ADMIN

### Actions

- CREATE, READ, UPDATE, DELETE, EXECUTE, EXPORT, SHARE, ADMIN

### Built-in Roles

1. **SUPER_ADMIN**: Acesso total a todos os recursos
2. **ADMIN**: Acesso administrativo (sem gerenciamento de usuários)
3. **POWER_USER**: Acesso avançado (criar/editar próprios recursos)
4. **USER**: Acesso básico (leitura e criação)
5. **VIEWER**: Somente leitura

### Permission Model

```
User --[has many]--> Role --[has many]--> Permission
                                             |
                                        Resource + Action
```

## Componentes Principais

### User

- ID, username, email
- Múltiplos roles
- 2FA support
- Password hash seguro
- Audit trail

### Role

- Nome, tipo, descrição
- Set de permissões
- Ativo/inativo
- Timestamp de criação/atualização

### Permission

- Resource (recurso)
- Action (ação)
- Descrição

### AuditLog

- User ID, ação, recurso
- Status (success, denied, error)
- IP address, user agent
- Timestamp

## Uso

```python
from app.security import get_rbac_manager, ResourceType, Action, RoleType

rbac = get_rbac_manager()

# Criar usuário
user = rbac.create_user(
    user_id=1,
    username="john_doe",
    email="john@example.com",
    password="SecurePassword123"
)

# Adicionar role
admin_role = rbac.get_role_by_type(RoleType.ADMIN)
rbac.add_role_to_user(1, admin_role.id)

# Verificar permissão
has_permission = rbac.check_permission(
    user_id=1,
    resource=ResourceType.DASHBOARD,
    action=Action.READ,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0..."
)

# Criar role customizado
custom_role = rbac.create_role(
    name="Data Analyst",
    description="Can view and export analytics"
)

# Adicionar permissões
rbac.add_permission_to_role(
    custom_role.id,
    ResourceType.ANALYTICS,
    Action.READ
)
rbac.add_permission_to_role(
    custom_role.id,
    ResourceType.EXPORT,
    Action.EXECUTE
)

# Habilitar 2FA
secret = rbac.enable_2fa(1)  # Retorna secret para app autenticador

# Obter estatísticas
stats = rbac.get_user_statistics()
# {'total_users': 5, 'active_users': 4, 'users_with_2fa': 2, ...}

# Obter audit log
logs = rbac.get_audit_log(user_id=1, limit=50)
```

## Decorators

```python
from app.security import require_permission, require_role, ResourceType, Action, RoleType

# Requer permissão específica
@require_permission(ResourceType.REPORTS, Action.DELETE)
def delete_report(report_id: int, user_id: int):
    # Função protegida
    pass

# Requer role específico
@require_role(RoleType.ADMIN)
def admin_only_function(user_id: int):
    # Apenas admins podem acessar
    pass
```

## Passwords & Security

- Hashing com SHA256 + salt
- 2FA com suporte a TOTP
- Audit logging completo
- IP tracking
- User agent logging

## UI

- Dashboard com abas para gerenciamento de usuários, roles, audit log
- Criação visual de roles customizados
- Gerenciamento de permissões granulares
- Histórico de auditoria com filtros
- Configuração de políticas de segurança

---

## Integração com Dashboard

### main.py

```python
from app.alerts import create_alerts_panel, register_alert_callbacks
from app.security.rbac_ui import create_rbac_panel, register_rbac_callbacks

# Adicionar às abas principais
dbc.Tabs([
    dbc.Tab(create_alerts_panel(), label="⚠️ Alertas"),
    dbc.Tab(create_rbac_panel(), label="👥 Segurança"),
])

# Registrar callbacks
register_alert_callbacks(app)
register_rbac_callbacks(app)
```

## Telemetria e Monitoramento

### Alertas

- Total de alertas
- Alertas por severidade
- Taxa de reconhecimento
- Tempo médio de resposta

### Async

- Tasks em fila
- Taxa de sucesso/falha
- Tempo médio de execução
- Worker status

### RBAC

- Tentativas de acesso negado
- Usuários mais ativos
- Mudanças de permissão
- Tentativas de escalação de privilégio

## Segurança em Produção

1. Usar environment variables para credenciais
2. HTTPS obrigatório
3. Rate limiting por IP
4. Validação de 2FA
5. Audit log persistido (DB)
6. Alertas de atividade suspeita
7. Rotação de senhas regularmente
8. IP whitelisting

## Roadmap Futuro

- SSO/OAuth2 integration
- SAML support
- API key management
- Session management avançado
- Soft delete com restore
- Permissões granulares por recurso individual
- Delegation de permissões
- Histórico de mudanças com rollback
