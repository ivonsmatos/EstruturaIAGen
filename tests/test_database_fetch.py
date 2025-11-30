"""
Testes de Integração: Fetch de Métricas do BD
Valida a função fetch_metrics_from_db() e agregação de dados
v1.3.0 - P1.2 Database Integration
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, User, Dashboard, Metric
from app.db.metrics import fetch_metrics_from_db, _generate_fallback_data, get_metric_stats


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_db_with_data():
    """Cria BD com dados de exemplo para testes"""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    
    # Adicionar dados de teste
    session = TestingSessionLocal()
    
    user = User(username="test_user", email="test@example.com")
    dashboard = Dashboard(name="Test Dashboard", owner=user)
    session.add(user)
    session.add(dashboard)
    session.flush()
    
    # Inserir métricas dos últimos 30 dias
    now = datetime.utcnow()
    for i in range(720):  # 30 dias * 24 horas
        metric = Metric(
            user=user,
            dashboard=dashboard,
            ia_efficiency=0.85 + (i % 10) * 0.01,  # Varia 0.85-0.94
            model_accuracy=0.88 + (i % 10) * 0.01,  # Varia 0.88-0.97
            processing_time_ms=30.0 + (i % 50),     # Varia 30-80ms
            memory_usage_mb=200.0 + (i % 100),      # Varia 200-300MB
            error_rate=0.01 + (i % 5) * 0.01,       # Varia 0.01-0.05
            timestamp=now - timedelta(hours=i),
            periodo="30d"
        )
        session.add(metric)
    
    session.commit()
    session.close()
    
    return TestingSessionLocal, user.id


# ============================================================================
# TESTES: FETCH_METRICS_FROM_DB
# ============================================================================

class TestFetchMetricsFromDB:
    """Testes para fetch_metrics_from_db()"""
    
    def test_fetch_24h_metrics(self, test_db_with_data, monkeypatch):
        """Teste: Buscar métricas de 24h"""
        TestingSessionLocal, user_id = test_db_with_data
        
        # Monkeypatch para usar BD de teste
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            data = fetch_metrics_from_db("24h", user_id)
            
            assert data is not None
            assert "ia_efficiency" in data
            assert "model_accuracy" in data
            assert "processing_time" in data
            assert "memory_usage" in data
            assert "error_rate" in data
            assert len(data["ia_efficiency"]) > 0
            
        finally:
            app.db.metrics.get_db_session = original_get_session
    
    def test_fetch_returns_averages(self, test_db_with_data, monkeypatch):
        """Teste: Retorna médias corretas"""
        TestingSessionLocal, user_id = test_db_with_data
        
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            data = fetch_metrics_from_db("24h", user_id)
            
            assert "avg_efficiency" in data
            assert "avg_accuracy" in data
            assert "avg_processing_time" in data
            assert "avg_memory" in data
            assert "avg_error_rate" in data
            
            # Verificar que médias estão em ranges válidos
            assert 0 < data["avg_efficiency"] < 1
            assert 0 < data["avg_accuracy"] < 1
            assert data["avg_processing_time"] > 0
            assert data["avg_memory"] > 0
            
        finally:
            app.db.metrics.get_db_session = original_get_session
    
    def test_fetch_different_periods(self, test_db_with_data, monkeypatch):
        """Teste: Períodos diferentes retornam dados"""
        TestingSessionLocal, user_id = test_db_with_data
        
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            for periodo in ["24h", "7d", "30d", "all"]:
                data = fetch_metrics_from_db(periodo, user_id)
                assert data is not None
                assert data["periodo"] == periodo
                assert "total_metrics" in data
                
        finally:
            app.db.metrics.get_db_session = original_get_session


# ============================================================================
# TESTES: FALLBACK DATA
# ============================================================================

class TestFallbackData:
    """Testes para _generate_fallback_data()"""
    
    def test_fallback_generates_data(self):
        """Teste: Fallback gera dados válidos"""
        data = _generate_fallback_data("24h")
        
        assert data is not None
        assert "ia_efficiency" in data
        assert "model_accuracy" in data
        assert len(data["ia_efficiency"]) > 0
    
    def test_fallback_scales_with_period(self):
        """Teste: Fallback escala dados conforme período"""
        data_24h = _generate_fallback_data("24h")
        data_30d = _generate_fallback_data("30d")
        
        # 30d deve ter mais pontos que 24h
        assert len(data_30d["ia_efficiency"]) > len(data_24h["ia_efficiency"])
    
    def test_fallback_ranges_valid(self):
        """Teste: Ranges de valores estão válidos"""
        data = _generate_fallback_data("24h")
        
        # Eficiência: 0-1
        assert all(0 <= e <= 1 for e in data["ia_efficiency"])
        # Acurácia: 0-1
        assert all(0 <= a <= 1 for a in data["model_accuracy"])
        # Tempo: >0
        assert all(t > 0 for t in data["processing_time"])
        # Memória: >0
        assert all(m > 0 for m in data["memory_usage"])


# ============================================================================
# TESTES: METRIC STATS
# ============================================================================

class TestMetricStats:
    """Testes para get_metric_stats()"""
    
    def test_stats_calculation(self, test_db_with_data, monkeypatch):
        """Teste: Calcular estatísticas"""
        TestingSessionLocal, user_id = test_db_with_data
        
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            stats = get_metric_stats(user_id, "24h")
            
            assert "total_records" in stats
            assert "avg_efficiency" in stats
            assert "avg_accuracy" in stats
            assert "last_updated" in stats
            
            # Verificar que valores não são zero
            assert stats["avg_efficiency"] > 0
            assert stats["avg_accuracy"] > 0
            
        finally:
            app.db.metrics.get_db_session = original_get_session


# ============================================================================
# TESTES: DATA INTEGRITY
# ============================================================================

class TestDataIntegrity:
    """Testes para integridade de dados"""
    
    def test_no_null_values_in_response(self, test_db_with_data, monkeypatch):
        """Teste: Resposta não tem valores nulos"""
        TestingSessionLocal, user_id = test_db_with_data
        
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            data = fetch_metrics_from_db("24h", user_id)
            
            # Verificar que não há None nos arrays
            assert None not in data["ia_efficiency"]
            assert None not in data["model_accuracy"]
            assert None not in data["processing_time"]
            
        finally:
            app.db.metrics.get_db_session = original_get_session
    
    def test_metrics_are_ordered(self, test_db_with_data, monkeypatch):
        """Teste: Métricas estão ordenadas por timestamp"""
        TestingSessionLocal, user_id = test_db_with_data
        
        def mock_get_session():
            from contextlib import contextmanager
            @contextmanager
            def context_manager():
                session = TestingSessionLocal()
                try:
                    yield session
                finally:
                    session.close()
            return context_manager()
        
        import app.db.metrics
        original_get_session = app.db.metrics.get_db_session
        app.db.metrics.get_db_session = mock_get_session
        
        try:
            data = fetch_metrics_from_db("24h", user_id)
            timestamps = data["timestamps"]
            
            # Verificar que timestamps estão em ordem crescente
            assert timestamps == sorted(timestamps)
            
        finally:
            app.db.metrics.get_db_session = original_get_session
