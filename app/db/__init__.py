"""
Gerenciamento de banco de dados
Contém session management e connection pooling
"""

from app.db.session import (
    get_db_session,
    init_database,
    create_engine_with_pooling
)

__all__ = [
    "get_db_session",
    "init_database",
    "create_engine_with_pooling"
]
