"""
Funções de Integração com Banco de Dados para Dashboard
Conecta o dashboard aos dados persistidos em BD
v1.3.0 - P1.2 Database Integration
"""

from app.db.session import get_db_session
from app.models.database import Metric
from datetime import datetime, timedelta
import logging
import numpy as np

logger = logging.getLogger(__name__)


def fetch_metrics_from_db(periodo: str = "24h", user_id: int = 1):
    """
    Busca métricas do banco de dados em vez de gerar dados aleatórios
    
    Args:
        periodo: '24h', '7d', '30d', 'all'
        user_id: ID do usuário (padrão: 1)
    
    Returns:
        dict: Dicionário com métricas agregadas para o período
        
    Raises:
        Exception: Se erro ao buscar do BD
    """
    
    try:
        with get_db_session() as session:
            # Calcular intervalo de tempo
            now = datetime.utcnow()
            
            if periodo == "24h":
                start_date = now - timedelta(hours=24)
            elif periodo == "7d":
                start_date = now - timedelta(days=7)
            elif periodo == "30d":
                start_date = now - timedelta(days=30)
            else:  # "all"
                start_date = datetime(2024, 1, 1)
            
            # Consultar métricas do BD
            metrics = session.query(Metric).filter(
                Metric.user_id == user_id,
                Metric.timestamp >= start_date
            ).order_by(Metric.timestamp).all()
            
            if not metrics:
                logger.warning(f"Nenhuma métrica encontrada para user_id={user_id}, periodo={periodo}")
                return _generate_fallback_data(periodo)
            
            logger.info(f"✓ {len(metrics)} métricas carregadas do BD para período: {periodo}")
            
            # Agregar dados
            return {
                "ia_efficiency": [m.ia_efficiency for m in metrics],
                "model_accuracy": [m.model_accuracy for m in metrics],
                "processing_time": [m.processing_time_ms for m in metrics],
                "memory_usage": [m.memory_usage_mb for m in metrics],
                "error_rate": [m.error_rate * 100 for m in metrics],  # Converter para percentual
                "timestamps": [m.timestamp for m in metrics],
                "periodo": periodo,
                "total_metrics": len(metrics),
                "avg_efficiency": np.mean([m.ia_efficiency for m in metrics]),
                "avg_accuracy": np.mean([m.model_accuracy for m in metrics]),
                "avg_processing_time": np.mean([m.processing_time_ms for m in metrics]),
                "avg_memory": np.mean([m.memory_usage_mb for m in metrics]),
                "avg_error_rate": np.mean([m.error_rate for m in metrics]) * 100
            }
            
    except Exception as e:
        logger.error(f"Erro ao buscar métricas do BD: {str(e)}", exc_info=True)
        return _generate_fallback_data(periodo)


def _generate_fallback_data(periodo: str = "24h") -> dict:
    """
    Dados de fallback quando BD não disponível
    Usado para testes e desenvolvimento
    
    Args:
        periodo: Período para escalar dados
    
    Returns:
        dict: Dicionário com dados de teste
    """
    logger.warning(f"⚠ Usando dados de fallback para período: {periodo}")
    
    # Multiplicadores por período
    multipliers = {
        "24h": 1.0,
        "7d": 2.5,
        "30d": 4.0,
        "all": 6.0
    }
    
    multiplier = multipliers.get(periodo, 1.0)
    
    # Gerar dados aleatórios
    np.random.seed(42)
    num_points = int(24 * multiplier)  # 1 ponto por hora
    
    timestamps = [
        datetime.utcnow() - timedelta(hours=i)
        for i in range(num_points, 0, -1)
    ]
    
    efficiency = [np.random.uniform(0.85, 0.99) for _ in range(num_points)]
    accuracy = [np.random.uniform(0.88, 0.98) for _ in range(num_points)]
    processing_time = [np.random.uniform(20, 100) for _ in range(num_points)]
    memory_usage = [np.random.uniform(200, 512) for _ in range(num_points)]
    error_rate = [np.random.uniform(0.01, 0.05) * 100 for _ in range(num_points)]
    
    return {
        "ia_efficiency": efficiency,
        "model_accuracy": accuracy,
        "processing_time": processing_time,
        "memory_usage": memory_usage,
        "error_rate": error_rate,
        "timestamps": timestamps,
        "periodo": periodo,
        "total_metrics": num_points,
        "avg_efficiency": np.mean(efficiency),
        "avg_accuracy": np.mean(accuracy),
        "avg_processing_time": np.mean(processing_time),
        "avg_memory": np.mean(memory_usage),
        "avg_error_rate": np.mean(error_rate),
        "is_fallback": True
    }


def get_metric_stats(user_id: int = 1, periodo: str = "24h") -> dict:
    """
    Retorna estatísticas consolidadas de métricas
    
    Args:
        user_id: ID do usuário
        periodo: Período para análise
    
    Returns:
        dict: Estatísticas consolidadas
    """
    try:
        data = fetch_metrics_from_db(periodo, user_id)
        
        return {
            "total_records": data.get("total_metrics", 0),
            "avg_efficiency": round(data.get("avg_efficiency", 0), 3),
            "avg_accuracy": round(data.get("avg_accuracy", 0), 3),
            "avg_processing_time": round(data.get("avg_processing_time", 0), 2),
            "avg_memory_usage": round(data.get("avg_memory", 0), 2),
            "avg_error_rate": round(data.get("avg_error_rate", 0), 2),
            "periodo": periodo,
            "last_updated": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Erro ao calcular estatísticas: {str(e)}")
        return {}


if __name__ == "__main__":
    # Teste local
    logging.basicConfig(level=logging.INFO)
    
    print("Testando fetch_metrics_from_db()...")
    data = fetch_metrics_from_db("24h", user_id=1)
    print(f"✓ Carregadas {data.get('total_metrics', 0)} métricas")
    print(f"✓ Eficiência média: {data.get('avg_efficiency', 0):.2%}")
