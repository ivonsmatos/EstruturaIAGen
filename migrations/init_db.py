#!/usr/bin/env python3
"""
Script para Inicializar Banco de Dados com Dados de Exemplo
Execute: python migrations/init_db.py
v1.3.0 - P1.2 Database Integration
"""

import os
import sys

# Adicionar diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import db_manager
from app.db.session import init_database
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Função principal para inicializar BD com dados de exemplo"""
    
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   INICIALIZAÇÃO DE BANCO DE DADOS - Dashboard IA          ║
    ║   v1.3.0 - P1.2 Database Integration                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 1. Inicializar banco de dados (criar tabelas)
        logger.info("📦 Inicializando banco de dados...")
        init_database()
        
        # 2. Criar dados de exemplo
        logger.info("📊 Criando dados de exemplo...")
        db_manager.create_sample_data(num_users=3, metrics_per_user=720)
        
        # 3. Relatório final
        logger.info("""
        ╔═══════════════════════════════════════════════════════════╗
        ║   ✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!            ║
        ╠═══════════════════════════════════════════════════════════╣
        ║                                                           ║
        ║   Arquivo:        data.db (SQLite)                       ║
        ║   Usuários:       3                                      ║
        ║   Métricas/Usuário: 720 (30 dias)                        ║
        ║   Total Métricas: 2,160                                  ║
        ║                                                           ║
        ║   Para conectar via dashboard:                           ║
        ║   DATABASE_URL=sqlite:///./data.db                       ║
        ║                                                           ║
        ║   Para verificar dados:                                  ║
        ║   sqlite3 data.db                                        ║
        ║   sqlite> SELECT COUNT(*) FROM metrics;                  ║
        ║                                                           ║
        ╚═══════════════════════════════════════════════════════════╝
        """)
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Erro durante inicialização: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
