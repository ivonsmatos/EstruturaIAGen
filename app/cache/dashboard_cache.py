"""
Cache para Dashboard
Funções específicas para cachear gráficos e dados do dashboard
v1.4.0 - P1.3 Cache Implementation
"""

from app.cache.decorators import cached
from app.db.metrics import fetch_metrics_from_db, get_metric_stats
import logging

logger = logging.getLogger(__name__)


@cached(ttl=300)  # 5 minutos
def get_dashboard_metrics(periodo: str = "24h", user_id: int = 1):
    """
    Fetch e cache de métricas do dashboard
    
    Args:
        periodo: Período (24h, 7d, 30d, all)
        user_id: ID do usuário
        
    Returns:
        Métricas agregadas (cacheadas por 5 minutos)
    """
    logger.info(f"🔄 Fetchando métricas (não estava em cache): {periodo}")
    return fetch_metrics_from_db(periodo, user_id)


@cached(ttl=600)  # 10 minutos
def get_dashboard_stats(periodo: str = "24h", user_id: int = 1):
    """
    Estatísticas consolidadas do dashboard
    
    Args:
        periodo: Período para análise
        user_id: ID do usuário
        
    Returns:
        Estatísticas (cacheadas por 10 minutos)
    """
    logger.info(f"🔄 Calculando estatísticas (não estava em cache): {periodo}")
    return get_metric_stats(user_id, periodo)


@cached(ttl=60)  # 1 minuto
def get_chart_config(chart_type: str = "efficiency"):
    """
    Configuração de gráfico cacheada
    
    Args:
        chart_type: Tipo de gráfico
        
    Returns:
        Configuração do gráfico
    """
    configs = {
        "efficiency": {
            "title": "AI Efficiency",
            "color": "#BBF244",
            "unit": "%"
        },
        "accuracy": {
            "title": "Model Accuracy",
            "color": "#F27244",
            "unit": "%"
        },
        "performance": {
            "title": "Processing Time",
            "color": "#00D9FF",
            "unit": "ms"
        },
        "memory": {
            "title": "Memory Usage",
            "color": "#FF00FF",
            "unit": "MB"
        }
    }
    
    return configs.get(chart_type, configs["efficiency"])


def invalidate_dashboard_cache():
    """Invalida todo o cache do dashboard"""
    logger.info("🔄 Invalidando cache do dashboard...")
    get_dashboard_metrics.invalidate_cache()
    get_dashboard_stats.invalidate_cache()
    get_chart_config.clear_all()
    logger.info("✓ Cache do dashboard invalidado")
