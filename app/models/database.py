"""
Modelos de Banco de Dados - SQLAlchemy ORM
Define as estruturas de dados para User, Dashboard e Metric
v1.3.0 - P1.2 Database Integration
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, 
    ForeignKey, create_engine, event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()

# ============================================================================
# MODELOS DE DADOS
# ============================================================================

class User(Base):
    """Modelo de usuário do sistema"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    dashboards = relationship("Dashboard", back_populates="owner", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Dashboard(Base):
    """Modelo de dashboard"""
    __tablename__ = "dashboards"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relacionamentos
    owner = relationship("User", back_populates="dashboards")
    metrics = relationship("Metric", back_populates="dashboard", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dashboard(id={self.id}, name='{self.name}', user_id={self.user_id})>"


class Metric(Base):
    """Modelo de métrica de IA - Dados de monitoramento"""
    __tablename__ = "metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    dashboard_id = Column(Integer, ForeignKey("dashboards.id"), nullable=True, index=True)
    
    # Métricas de IA (valores entre 0-1 ou 0-100)
    ia_efficiency = Column(Float, nullable=False)           # Eficiência (0-1)
    model_accuracy = Column(Float, nullable=False)          # Acurácia (0-1)
    processing_time_ms = Column(Float, nullable=False)      # Tempo em ms
    memory_usage_mb = Column(Float, nullable=False)         # Memória em MB
    error_rate = Column(Float, nullable=False)              # Taxa de erro (0-1)
    
    # Metadados
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    periodo = Column(String(10), default="24h", nullable=False)  # 24h, 7d, 30d, all
    
    # Relacionamentos
    user = relationship("User", back_populates="metrics")
    dashboard = relationship("Dashboard", back_populates="metrics")
    
    def __repr__(self):
        return f"<Metric(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"


# ============================================================================
# GERENCIADOR DE BANCO DE DADOS
# ============================================================================

class DatabaseManager:
    """
    Gerenciador de conexão com banco de dados
    Responsável por inicializar e gerenciar a conexão SQLAlchemy
    """
    
    def __init__(self, database_url: str = None, echo: bool = False):
        """
        Inicializa o gerenciador de BD
        
        Args:
            database_url: URL da conexão (ex: sqlite:///dashboard.db)
            echo: Se True, loga todas as queries SQL
        """
        self.database_url = database_url or os.getenv(
            "DATABASE_URL",
            "sqlite:///./data.db"  # Padrão: SQLite local
        )
        self.echo = echo or os.getenv("SQL_ECHO", "False").lower() == "true"
        self.engine = None
        self.SessionLocal = None
        self._init_engine()
        logger.info(f"✓ DatabaseManager inicializado com: {self.database_url}")
    
    def _init_engine(self):
        """Cria a engine com connection pooling"""
        try:
            # Configurar pooling
            pool_size = int(os.getenv("DB_POOL_SIZE", 10))
            max_overflow = int(os.getenv("DB_MAX_OVERFLOW", 20))
            pool_recycle = int(os.getenv("DB_POOL_RECYCLE", 3600))
            
            self.engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=pool_size,
                max_overflow=max_overflow,
                pool_recycle=pool_recycle,
                echo=self.echo,
                connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
            )
            
            self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
            
            logger.debug(f"Engine criada com pool_size={pool_size}, max_overflow={max_overflow}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao criar engine: {str(e)}")
            raise
    
    def init_db(self):
        """
        Inicializa o banco de dados criando todas as tabelas
        Operação segura - não sobrescreve tabelas existentes
        """
        try:
            Base.metadata.create_all(self.engine)
            logger.info("✓ Banco de dados inicializado (tabelas criadas/verificadas)")
        except Exception as e:
            logger.error(f"✗ Erro ao inicializar BD: {str(e)}")
            raise
    
    def get_session(self):
        """
        Obtém uma nova sessão de BD
        
        Returns:
            Sessão SQLAlchemy
        """
        if self.SessionLocal is None:
            raise RuntimeError("DatabaseManager não foi inicializado corretamente")
        return self.SessionLocal()
    
    def close(self):
        """Fecha todas as conexões"""
        try:
            if self.engine:
                self.engine.dispose()
                logger.info("✓ Conexões de BD fechadas")
        except Exception as e:
            logger.error(f"✗ Erro ao fechar conexões: {str(e)}")
    
    def create_sample_data(self, num_users: int = 1, metrics_per_user: int = 720):
        """
        Cria dados de exemplo para desenvolvimento/teste
        
        Args:
            num_users: Número de usuários a criar
            metrics_per_user: Número de métricas por usuário (padrão: 30 dias * 24h)
        """
        import random
        
        session = self.get_session()
        try:
            # Verificar se dados já existem
            existing_users = session.query(User).count()
            if existing_users > 0:
                logger.info(f"✓ Dados de exemplo já existem ({existing_users} usuários)")
                return
            
            logger.info(f"📊 Criando {num_users} usuário(s) com {metrics_per_user} métricas cada...")
            
            for u in range(num_users):
                user = User(
                    username=f"user_{u+1}",
                    email=f"user{u+1}@example.com"
                )
                session.add(user)
                session.flush()
                
                # Dashboard
                dashboard = Dashboard(
                    name=f"Dashboard IA {u+1}",
                    owner=user
                )
                session.add(dashboard)
                session.flush()
                
                # Métricas (últimas 30 dias)
                now = datetime.utcnow()
                logger.info(f"  Inserindo {metrics_per_user} métricas para {user.username}...")
                
                for i in range(metrics_per_user):
                    metric = Metric(
                        user=user,
                        dashboard=dashboard,
                        ia_efficiency=random.uniform(0.85, 0.99),
                        model_accuracy=random.uniform(0.88, 0.98),
                        processing_time_ms=random.uniform(20, 100),
                        memory_usage_mb=random.uniform(200, 512),
                        error_rate=random.uniform(0.01, 0.05),
                        timestamp=now - timedelta(hours=i),
                        periodo="30d"
                    )
                    session.add(metric)
                    
                    # Commit a cada 100 métricas para evitar overflow
                    if (i + 1) % 100 == 0:
                        session.commit()
                        logger.debug(f"  → {i+1}/{metrics_per_user} métricas inseridas")
                
                session.commit()
            
            logger.info(f"✅ {num_users} usuário(s) e {num_users * metrics_per_user} métricas criados com sucesso!")
            
        except Exception as e:
            session.rollback()
            logger.error(f"✗ Erro ao criar dados de exemplo: {str(e)}")
            raise
        finally:
            session.close()


# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

db_manager = DatabaseManager()

# Event para suportar SQLite com foreign keys
if "sqlite" in (os.getenv("DATABASE_URL", "sqlite:///./data.db")):
    @event.listens_for(db_manager.engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
