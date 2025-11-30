"""
Session Management e Connection Pooling
Gerencia o ciclo de vida das sessões de BD com context managers
v1.3.0 - P1.2 Database Integration
"""

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.orm import sessionmaker
from app.models.database import Base, db_manager
import os
import logging

logger = logging.getLogger(__name__)


@contextmanager
def get_db_session():
    """
    Context manager para gerenciar sessões de BD
    Garante que a sessão seja fechada mesmo em caso de erro
    
    Uso:
        with get_db_session() as session:
            user = session.query(User).first()
            
    Raises:
        Exception: Qualquer erro ocorrido na operação
    """
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
        logger.debug("✓ Sessão commitada com sucesso")
    except Exception as e:
        session.rollback()
        logger.error(f"✗ Erro na sessão - Rollback executado: {str(e)}")
        raise
    finally:
        session.close()
        logger.debug("✓ Sessão fechada")


def init_database():
    """
    Inicializa o banco de dados com todas as tabelas
    Deve ser chamado uma vez na startup da aplicação
    
    Returns:
        engine: Engine SQLAlchemy configurada
    """
    try:
        logger.info("🔧 Inicializando banco de dados...")
        db_manager.init_db()
        logger.info("✅ Banco de dados inicializado com sucesso")
        return db_manager.engine
    except Exception as e:
        logger.error(f"✗ Erro ao inicializar BD: {str(e)}")
        raise


def create_engine_with_pooling(database_url: str = None, **kwargs) -> object:
    """
    Cria uma engine SQLAlchemy com pooling de conexões
    
    Args:
        database_url: URL de conexão (ex: sqlite:///data.db)
        **kwargs: Argumentos adicionais para create_engine
    
    Returns:
        engine: Engine configurada com pooling
        
    Configuração de Pooling:
        - pool_size: 10 (conexões ativas na pool)
        - max_overflow: 20 (conexões adicionais temporárias)
        - pool_recycle: 3600s (recicla conexões a cada hora)
    """
    url = database_url or os.getenv("DATABASE_URL", "sqlite:///./data.db")
    
    pool_size = int(os.getenv("DB_POOL_SIZE", 10))
    max_overflow = int(os.getenv("DB_MAX_OVERFLOW", 20))
    pool_recycle = int(os.getenv("DB_POOL_RECYCLE", 3600))
    echo = os.getenv("SQL_ECHO", "False").lower() == "true"
    
    engine = create_engine(
        url,
        poolclass=QueuePool,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_recycle=pool_recycle,
        echo=echo,
        connect_args={"check_same_thread": False} if "sqlite" in url else {},
        **kwargs
    )
    
    logger.debug(
        f"Engine criada: pool_size={pool_size}, "
        f"max_overflow={max_overflow}, pool_recycle={pool_recycle}s"
    )
    
    return engine


def get_db():
    """
    Dependency injection para FastAPI (compatível com Dependency Injection)
    
    Uso em FastAPI:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    session = db_manager.get_session()
    try:
        yield session
    finally:
        session.close()
