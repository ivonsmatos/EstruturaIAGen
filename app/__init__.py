"""
Estrutura da Aplicação IA Gen
Módulo principal para organização de código modular
"""

__version__ = "2.0.0"
__author__ = "Estrutura IA Gen Team"

from app.models.database import db_manager
from app.export import export_manager

__all__ = ["db_manager", "export_manager"]
