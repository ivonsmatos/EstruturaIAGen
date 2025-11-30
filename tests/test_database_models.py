"""
Testes de Modelos de Banco de Dados
Valida os modelos SQLAlchemy e operações CRUD
v1.3.0 - P1.2 Database Integration
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, User, Dashboard, Metric, DatabaseManager


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_db():
    """Cria BD em memória para testes"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    return TestingSessionLocal


@pytest.fixture
def session(test_db):
    """Retorna uma sessão de teste"""
    db = test_db()
    yield db
    db.close()


# ============================================================================
# TESTES: USER MODEL
# ============================================================================

class TestUserModel:
    """Testes para o modelo User"""
    
    def test_create_user(self, session):
        """Teste: Criar usuário simples"""
        user = User(username="test_user", email="test@example.com")
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert user.username == "test_user"
        assert user.email == "test@example.com"
        assert isinstance(user.created_at, datetime)
    
    def test_user_unique_username(self, session):
        """Teste: Username deve ser único"""
        user1 = User(username="duplicate", email="user1@example.com")
        user2 = User(username="duplicate", email="user2@example.com")
        
        session.add(user1)
        session.commit()
        session.add(user2)
        
        with pytest.raises(Exception):  # IntegrityError
            session.commit()
    
    def test_user_relationships(self, session):
        """Teste: Usuário pode ter múltiplos dashboards"""
        user = User(username="test", email="test@test.com")
        dashboard = Dashboard(name="Dashboard 1", owner=user)
        
        session.add(user)
        session.add(dashboard)
        session.commit()
        
        assert len(user.dashboards) == 1
        assert user.dashboards[0].name == "Dashboard 1"
        assert dashboard.owner.username == "test"


# ============================================================================
# TESTES: DASHBOARD MODEL
# ============================================================================

class TestDashboardModel:
    """Testes para o modelo Dashboard"""
    
    def test_create_dashboard(self, session):
        """Teste: Criar dashboard"""
        user = User(username="test", email="test@test.com")
        dashboard = Dashboard(name="Test Dashboard", owner=user)
        
        session.add(user)
        session.add(dashboard)
        session.commit()
        
        assert dashboard.id is not None
        assert dashboard.name == "Test Dashboard"
        assert dashboard.user_id == user.id
    
    def test_dashboard_timestamps(self, session):
        """Teste: Timestamps de criação e atualização"""
        user = User(username="test", email="test@test.com")
        dashboard = Dashboard(name="Test", owner=user)
        
        session.add(user)
        session.add(dashboard)
        session.commit()
        
        created = dashboard.created_at
        updated = dashboard.updated_at
        
        assert created is not None
        assert updated is not None
        assert created <= updated


# ============================================================================
# TESTES: METRIC MODEL
# ============================================================================

class TestMetricModel:
    """Testes para o modelo Metric"""
    
    def test_create_metric(self, session):
        """Teste: Criar métrica"""
        user = User(username="test", email="test@test.com")
        metric = Metric(
            user=user,
            ia_efficiency=0.95,
            model_accuracy=0.92,
            processing_time_ms=45.2,
            memory_usage_mb=256.5,
            error_rate=0.02
        )
        
        session.add(user)
        session.add(metric)
        session.commit()
        
        assert metric.id is not None
        assert metric.ia_efficiency == 0.95
        assert metric.model_accuracy == 0.92
        assert metric.processing_time_ms == 45.2
        assert metric.memory_usage_mb == 256.5
        assert metric.error_rate == 0.02
    
    def test_metric_with_dashboard(self, session):
        """Teste: Métrica associada a um dashboard"""
        user = User(username="test", email="test@test.com")
        dashboard = Dashboard(name="Test", owner=user)
        metric = Metric(
            user=user,
            dashboard=dashboard,
            ia_efficiency=0.95,
            model_accuracy=0.92,
            processing_time_ms=45.2,
            memory_usage_mb=256.5,
            error_rate=0.02
        )
        
        session.add(user)
        session.add(dashboard)
        session.add(metric)
        session.commit()
        
        assert metric.dashboard_id == dashboard.id
        assert dashboard.metrics[0].id == metric.id
    
    def test_metric_periodo_filter(self, session):
        """Teste: Filtrar métricas por período"""
        user = User(username="test", email="test@test.com")
        now = datetime.utcnow()
        
        # Métrica de 30 dias atrás
        metric_30d = Metric(
            user=user,
            ia_efficiency=0.95,
            model_accuracy=0.92,
            processing_time_ms=45.2,
            memory_usage_mb=256.5,
            error_rate=0.02,
            timestamp=now - timedelta(days=30),
            periodo="30d"
        )
        
        # Métrica de hoje
        metric_today = Metric(
            user=user,
            ia_efficiency=0.93,
            model_accuracy=0.91,
            processing_time_ms=50.0,
            memory_usage_mb=300.0,
            error_rate=0.03,
            timestamp=now,
            periodo="24h"
        )
        
        session.add(user)
        session.add(metric_30d)
        session.add(metric_today)
        session.commit()
        
        # Verificar períodos
        metrics_24h = session.query(Metric).filter_by(periodo="24h").all()
        metrics_30d = session.query(Metric).filter_by(periodo="30d").all()
        
        assert len(metrics_24h) == 1
        assert len(metrics_30d) == 1


# ============================================================================
# TESTES: DATABASE MANAGER
# ============================================================================

class TestDatabaseManager:
    """Testes para DatabaseManager"""
    
    def test_database_manager_init(self):
        """Teste: Inicializar DatabaseManager"""
        manager = DatabaseManager("sqlite:///:memory:")
        
        assert manager.database_url == "sqlite:///:memory:"
        assert manager.engine is not None
        assert manager.SessionLocal is not None
    
    def test_get_session(self):
        """Teste: Obter sessão do gerenciador"""
        manager = DatabaseManager("sqlite:///:memory:")
        session = manager.get_session()
        
        assert session is not None
        session.close()
    
    def test_init_db_creates_tables(self):
        """Teste: init_db() cria tabelas"""
        manager = DatabaseManager("sqlite:///:memory:")
        manager.init_db()
        
        # Verificar que as tabelas foram criadas
        inspector = __import__('sqlalchemy').inspect(manager.engine)
        tables = inspector.get_table_names()
        
        assert "users" in tables
        assert "dashboards" in tables
        assert "metrics" in tables


# ============================================================================
# TESTES: DATA AGGREGATION
# ============================================================================

class TestDataAggregation:
    """Testes para agregação de dados"""
    
    def test_user_can_have_many_metrics(self, session):
        """Teste: Um usuário pode ter múltiplas métricas"""
        user = User(username="test", email="test@test.com")
        session.add(user)
        session.flush()
        
        # Adicionar 100 métricas
        for i in range(100):
            metric = Metric(
                user=user,
                ia_efficiency=0.95,
                model_accuracy=0.92,
                processing_time_ms=45.2,
                memory_usage_mb=256.5,
                error_rate=0.02,
                timestamp=datetime.utcnow() - timedelta(hours=i)
            )
            session.add(metric)
        
        session.commit()
        
        user_metrics = session.query(Metric).filter_by(user_id=user.id).all()
        assert len(user_metrics) == 100
    
    def test_metric_average_query(self, session):
        """Teste: Calcular média de métricas"""
        from sqlalchemy import func
        
        user = User(username="test", email="test@test.com")
        session.add(user)
        session.flush()
        
        # Adicionar métricas variadas
        efficiencies = [0.85, 0.90, 0.95, 0.99, 0.88]
        for eff in efficiencies:
            metric = Metric(
                user=user,
                ia_efficiency=eff,
                model_accuracy=0.92,
                processing_time_ms=45.2,
                memory_usage_mb=256.5,
                error_rate=0.02
            )
            session.add(metric)
        
        session.commit()
        
        # Calcular média
        avg_efficiency = session.query(
            func.avg(Metric.ia_efficiency)
        ).filter_by(user_id=user.id).scalar()
        
        expected_avg = sum(efficiencies) / len(efficiencies)
        assert abs(avg_efficiency - expected_avg) < 0.01


# ============================================================================
# TESTES: INTEGRAÇÃO
# ============================================================================

class TestIntegration:
    """Testes de integração entre modelos"""
    
    def test_cascade_delete_user(self, session):
        """Teste: Deletar user também deleta dashboards e métricas"""
        user = User(username="test", email="test@test.com")
        dashboard = Dashboard(name="Dashboard", owner=user)
        metric = Metric(
            user=user,
            dashboard=dashboard,
            ia_efficiency=0.95,
            model_accuracy=0.92,
            processing_time_ms=45.2,
            memory_usage_mb=256.5,
            error_rate=0.02
        )
        
        session.add(user)
        session.add(dashboard)
        session.add(metric)
        session.commit()
        
        user_id = user.id
        
        # Deletar usuário
        session.delete(user)
        session.commit()
        
        # Verificar que tudo foi deletado
        assert session.query(User).filter_by(id=user_id).first() is None
        assert session.query(Dashboard).filter_by(user_id=user_id).first() is None
        assert session.query(Metric).filter_by(user_id=user_id).first() is None
    
    def test_full_workflow(self, session):
        """Teste: Workflow completo de criação e consulta"""
        # 1. Criar usuário
        user = User(username="john", email="john@example.com")
        session.add(user)
        session.commit()
        
        # 2. Criar dashboard
        dashboard = Dashboard(name="John's Dashboard", owner=user)
        session.add(dashboard)
        session.commit()
        
        # 3. Adicionar métricas
        for i in range(10):
            metric = Metric(
                user=user,
                dashboard=dashboard,
                ia_efficiency=0.90 + (i * 0.01),
                model_accuracy=0.90,
                processing_time_ms=40.0,
                memory_usage_mb=250.0,
                error_rate=0.02
            )
            session.add(metric)
        session.commit()
        
        # 4. Consultar dados
        found_user = session.query(User).filter_by(username="john").first()
        assert found_user is not None
        assert len(found_user.dashboards) == 1
        assert len(found_user.dashboards[0].metrics) == 10
        
        # 5. Validar dados
        metrics = session.query(Metric).filter_by(user_id=found_user.id).all()
        assert metrics[0].ia_efficiency == 0.90
        assert metrics[-1].ia_efficiency == 0.99
