"""
Drill-down Analysis - Análise Detalhada de Métricas
Permite exploração profunda de dados com time-series interativo
v2.0.0 - P2.2 Advanced Analysis
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, timedelta
import numpy as np
from app.db.metrics import fetch_metrics_from_db, get_metric_stats
from app.cache.decorators import cached

logger = logging.getLogger(__name__)


class DrilldownAnalyzer:
    """Analisador de drill-down para métricas detalhadas"""
    
    def __init__(self):
        """Inicializa o analisador"""
        self.metrics_names = [
            'ia_efficiency',
            'model_accuracy',
            'processing_time',
            'memory_usage',
            'error_rate'
        ]
        logger.info("✓ DrilldownAnalyzer inicializado")
    
    @cached(ttl=300)  # Cache de 5 minutos
    def get_detailed_metrics(
        self,
        periodo: str = "24h",
        user_id: int = 1,
        metric_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtém métricas detalhadas com análise estatística
        
        Args:
            periodo: Período (24h, 7d, 30d, all)
            user_id: ID do usuário
            metric_name: Nome da métrica específica (None = todas)
            
        Returns:
            Dict com análise completa
        """
        try:
            logger.info(f"📊 Obtendo análise detalhada: {metric_name or 'todas'} ({periodo})")
            
            data = fetch_metrics_from_db(periodo, user_id)
            
            if metric_name and metric_name not in self.metrics_names:
                logger.warning(f"Métrica inválida: {metric_name}")
                return {}
            
            metrics_to_analyze = [metric_name] if metric_name else self.metrics_names
            
            detailed = {}
            for metric in metrics_to_analyze:
                if metric in data:
                    values = data[metric]
                    detailed[metric] = {
                        'values': values,
                        'statistics': self._calculate_statistics(values),
                        'trends': self._calculate_trends(values),
                        'outliers': self._detect_outliers(values),
                        'distribution': self._analyze_distribution(values)
                    }
            
            logger.info(f"✓ Análise concluída para {len(detailed)} métrica(s)")
            return detailed
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter análise detalhada: {str(e)}")
            raise
    
    def _calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """Calcula estatísticas descritivas"""
        arr = np.array(values)
        
        return {
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'q25': float(np.percentile(arr, 25)),
            'q75': float(np.percentile(arr, 75)),
            'iqr': float(np.percentile(arr, 75) - np.percentile(arr, 25))
        }
    
    def _calculate_trends(self, values: List[float]) -> Dict[str, Any]:
        """Calcula tendências nos dados"""
        arr = np.array(values)
        x = np.arange(len(arr))
        
        # Regressão linear
        if len(arr) > 1:
            coeffs = np.polyfit(x, arr, 1)
            slope = float(coeffs[0])
            direction = "crescente" if slope > 0 else "decrescente"
            strength = abs(slope)
        else:
            slope, direction, strength = 0, "estável", 0
        
        # Mudança percentual
        pct_change = ((arr[-1] - arr[0]) / arr[0] * 100) if arr[0] != 0 else 0
        
        return {
            'slope': slope,
            'direction': direction,
            'strength': strength,
            'percent_change': float(pct_change),
            'recent_avg': float(np.mean(arr[-10:] if len(arr) >= 10 else arr)),
            'previous_avg': float(np.mean(arr[:-10] if len(arr) >= 10 else arr[:1]))
        }
    
    def _detect_outliers(self, values: List[float]) -> Dict[str, Any]:
        """Detecta outliers usando IQR"""
        arr = np.array(values)
        q1 = np.percentile(arr, 25)
        q3 = np.percentile(arr, 75)
        iqr = q3 - q1
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [
            {
                'index': int(i),
                'value': float(val),
                'type': 'low' if val < lower_bound else 'high'
            }
            for i, val in enumerate(arr)
            if val < lower_bound or val > upper_bound
        ]
        
        return {
            'count': len(outliers),
            'outliers': outliers,
            'bounds': {
                'lower': float(lower_bound),
                'upper': float(upper_bound)
            }
        }
    
    def _analyze_distribution(self, values: List[float]) -> Dict[str, Any]:
        """Analisa a distribuição dos dados"""
        arr = np.array(values)
        
        # Histograma em 10 bins
        hist, bins = np.histogram(arr, bins=10)
        
        # Simetria (skewness) e curtose
        from scipy.stats import skew, kurtosis
        
        return {
            'histogram': {
                'bins': [float(b) for b in bins],
                'counts': [int(c) for c in hist]
            },
            'skewness': float(skew(arr)),
            'kurtosis': float(kurtosis(arr)),
            'is_normal': abs(skew(arr)) < 2 and abs(kurtosis(arr)) < 3
        }
    
    def compare_metrics(
        self,
        periodo: str = "24h",
        user_id: int = 1,
        metric1: str = 'ia_efficiency',
        metric2: str = 'model_accuracy'
    ) -> Dict[str, Any]:
        """
        Compara duas métricas
        
        Args:
            periodo: Período
            user_id: ID do usuário
            metric1: Primeira métrica
            metric2: Segunda métrica
            
        Returns:
            Dict com análise comparativa
        """
        try:
            logger.info(f"🔍 Comparando {metric1} vs {metric2}")
            
            data = fetch_metrics_from_db(periodo, user_id)
            
            if metric1 not in data or metric2 not in data:
                logger.warning(f"Métrica não encontrada")
                return {}
            
            values1 = np.array(data[metric1])
            values2 = np.array(data[metric2])
            
            # Correlação
            correlation = float(np.corrcoef(values1, values2)[0, 1])
            
            # Normalizando para comparação
            v1_norm = (values1 - values1.min()) / (values1.max() - values1.min() + 1e-10)
            v2_norm = (values2 - values2.min()) / (values2.max() - values2.min() + 1e-10)
            
            return {
                'metric1': metric1,
                'metric2': metric2,
                'correlation': correlation,
                'metric1_stats': self._calculate_statistics(values1.tolist()),
                'metric2_stats': self._calculate_statistics(values2.tolist()),
                'normalized': {
                    'metric1': v1_norm.tolist(),
                    'metric2': v2_norm.tolist()
                }
            }
            
        except Exception as e:
            logger.error(f"✗ Erro ao comparar métricas: {str(e)}")
            raise
    
    def get_time_series_data(
        self,
        periodo: str = "24h",
        user_id: int = 1,
        metric: str = 'ia_efficiency',
        aggregate_by: str = 'hour'  # hour, day, week
    ) -> Dict[str, Any]:
        """
        Obtém dados de série temporal agregados
        
        Args:
            periodo: Período
            user_id: ID do usuário
            metric: Métrica a analisar
            aggregate_by: Agregação (hour, day, week)
            
        Returns:
            Dict com série temporal agregada
        """
        try:
            logger.info(f"📈 Obtendo série temporal: {metric} agregada por {aggregate_by}")
            
            data = fetch_metrics_from_db(periodo, user_id)
            
            if metric not in data:
                logger.warning(f"Métrica não encontrada: {metric}")
                return {}
            
            values = data[metric]
            timestamps = data.get('timestamps', [])
            
            if not timestamps or len(timestamps) != len(values):
                logger.warning("Timestamps inconsistentes")
                return {}
            
            # Agregação
            aggregated = self._aggregate_data(
                list(zip(timestamps, values)),
                aggregate_by
            )
            
            return {
                'metric': metric,
                'aggregate_by': aggregate_by,
                'original_count': len(values),
                'aggregated_count': len(aggregated),
                'data': aggregated
            }
            
        except Exception as e:
            logger.error(f"✗ Erro ao obter série temporal: {str(e)}")
            raise
    
    def _aggregate_data(
        self,
        data: List[Tuple],
        aggregate_by: str
    ) -> List[Dict[str, Any]]:
        """Agrega dados por período"""
        if aggregate_by == 'hour':
            delta = timedelta(hours=1)
        elif aggregate_by == 'day':
            delta = timedelta(days=1)
        elif aggregate_by == 'week':
            delta = timedelta(weeks=1)
        else:
            delta = timedelta(hours=1)
        
        aggregated = {}
        
        for ts, value in data:
            if not hasattr(ts, 'replace'):
                continue
            
            # Arredondar timestamp para o período
            if aggregate_by == 'hour':
                period_ts = ts.replace(minute=0, second=0, microsecond=0)
            elif aggregate_by == 'day':
                period_ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
            else:  # week
                period_ts = ts.replace(hour=0, minute=0, second=0, microsecond=0)
                period_ts = period_ts - timedelta(days=period_ts.weekday())
            
            key = period_ts.isoformat()
            if key not in aggregated:
                aggregated[key] = []
            aggregated[key].append(value)
        
        # Calcular média para cada período
        result = []
        for period_key in sorted(aggregated.keys()):
            values = aggregated[period_key]
            result.append({
                'period': period_key,
                'mean': float(np.mean(values)),
                'min': float(np.min(values)),
                'max': float(np.max(values)),
                'count': len(values)
            })
        
        return result
    
    def get_performance_report(
        self,
        periodo: str = "24h",
        user_id: int = 1
    ) -> Dict[str, Any]:
        """
        Gera relatório de performance completo
        
        Args:
            periodo: Período
            user_id: ID do usuário
            
        Returns:
            Dict com análise completa
        """
        try:
            logger.info(f"📋 Gerando relatório de performance")
            
            detailed = self.get_detailed_metrics(periodo, user_id)
            
            report = {
                'periodo': periodo,
                'generated_at': datetime.utcnow().isoformat(),
                'metrics': detailed,
                'summary': self._generate_summary(detailed)
            }
            
            logger.info("✓ Relatório gerado com sucesso")
            return report
            
        except Exception as e:
            logger.error(f"✗ Erro ao gerar relatório: {str(e)}")
            raise
    
    def _generate_summary(self, detailed: Dict) -> Dict[str, str]:
        """Gera resumo textual da análise"""
        summary = {}
        
        for metric, analysis in detailed.items():
            stats = analysis['statistics']
            trends = analysis['trends']
            outliers = analysis['outliers']
            
            # Determinar saúde da métrica
            if outliers['count'] > len(analysis['values']) * 0.1:
                health = "⚠ Atenção"
            elif trends['direction'] == 'decrescente' and 'efficiency' in metric:
                health = "🔴 Crítico"
            elif trends['direction'] == 'crescente' and 'error' in metric:
                health = "🔴 Crítico"
            else:
                health = "✅ Normal"
            
            summary[metric] = (
                f"{health} | Média: {stats['mean']:.2f} | "
                f"Tendência: {trends['direction']} ({trends['strength']:.2%}) | "
                f"Outliers: {outliers['count']}"
            )
        
        return summary


# Instância global
drilldown_analyzer = DrilldownAnalyzer()
