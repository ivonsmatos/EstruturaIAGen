"""
Testes para o sistema de drill-down analysis
v2.0.0 - P2.2
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import numpy as np
from app.analysis.drilldown import DrilldownAnalyzer


class TestDrilldownAnalyzerInit:
    """Testes de inicialização"""
    
    def test_analyzer_init(self):
        """Testa inicialização do analisador"""
        analyzer = DrilldownAnalyzer()
        assert analyzer is not None
        assert len(analyzer.metrics_names) == 5
        assert 'ia_efficiency' in analyzer.metrics_names


class TestCalculateStatistics:
    """Testes para cálculo de estatísticas"""
    
    def test_statistics_calculation(self):
        """Testa cálculo de estatísticas básicas"""
        analyzer = DrilldownAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        stats = analyzer._calculate_statistics(values)
        
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert stats['mean'] == 3.0
        assert stats['median'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
    
    def test_statistics_with_single_value(self):
        """Testa estatísticas com um único valor"""
        analyzer = DrilldownAnalyzer()
        values = [5.0]
        
        stats = analyzer._calculate_statistics(values)
        
        assert stats['mean'] == 5.0
        assert stats['median'] == 5.0
        assert stats['min'] == 5.0
        assert stats['max'] == 5.0
    
    def test_quartiles_calculation(self):
        """Testa cálculo de quartis"""
        analyzer = DrilldownAnalyzer()
        values = list(range(1, 101))  # 1-100
        
        stats = analyzer._calculate_statistics(values)
        
        assert 'q25' in stats
        assert 'q75' in stats
        assert 'iqr' in stats
        assert stats['q25'] < stats['q75']


class TestTrendDetection:
    """Testes para detecção de tendências"""
    
    def test_uptrend_detection(self):
        """Testa detecção de tendência crescente"""
        analyzer = DrilldownAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        trends = analyzer._calculate_trends(values)
        
        assert trends['direction'] == 'crescente'
        assert trends['slope'] > 0
        assert trends['percent_change'] > 0
    
    def test_downtrend_detection(self):
        """Testa detecção de tendência decrescente"""
        analyzer = DrilldownAnalyzer()
        values = [5.0, 4.0, 3.0, 2.0, 1.0]
        
        trends = analyzer._calculate_trends(values)
        
        assert trends['direction'] == 'decrescente'
        assert trends['slope'] < 0
        assert trends['percent_change'] < 0
    
    def test_stable_trend_detection(self):
        """Testa detecção de tendência estável"""
        analyzer = DrilldownAnalyzer()
        values = [3.0, 3.0, 3.0, 3.0, 3.0]
        
        trends = analyzer._calculate_trends(values)
        
        assert trends['direction'] == 'estável' or trends['percent_change'] == 0


class TestOutlierDetection:
    """Testes para detecção de outliers"""
    
    def test_no_outliers(self):
        """Testa dados sem outliers"""
        analyzer = DrilldownAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        
        outliers = analyzer._detect_outliers(values)
        
        assert outliers['count'] == 0
        assert len(outliers['outliers']) == 0
    
    def test_high_outlier_detection(self):
        """Testa detecção de outlier alto"""
        analyzer = DrilldownAnalyzer()
        values = [1.0, 2.0, 3.0, 4.0, 5.0, 100.0]
        
        outliers = analyzer._detect_outliers(values)
        
        assert outliers['count'] > 0
        assert any(o['type'] == 'high' for o in outliers['outliers'])
    
    def test_low_outlier_detection(self):
        """Testa detecção de outlier baixo"""
        analyzer = DrilldownAnalyzer()
        values = [1.0, 50.0, 51.0, 52.0, 53.0, 54.0]
        
        outliers = analyzer._detect_outliers(values)
        
        assert outliers['count'] > 0
        assert any(o['type'] == 'low' for o in outliers['outliers'])


class TestDistributionAnalysis:
    """Testes para análise de distribuição"""
    
    def test_distribution_analysis(self):
        """Testa análise de distribuição"""
        analyzer = DrilldownAnalyzer()
        values = np.random.normal(50, 10, 1000).tolist()
        
        distribution = analyzer._analyze_distribution(values)
        
        assert 'histogram' in distribution
        assert 'skewness' in distribution
        assert 'kurtosis' in distribution
        assert 'is_normal' in distribution
        assert len(distribution['histogram']['bins']) == 11  # 10 bins + 1
    
    def test_skewed_distribution(self):
        """Testa análise de distribuição enviesada"""
        analyzer = DrilldownAnalyzer()
        values = list(range(1, 50)) + [100, 200, 300]  # Enviesada para cima
        
        distribution = analyzer._analyze_distribution(values)
        
        assert distribution['skewness'] > 0  # Enviesada positivamente


class TestGetDetailedMetrics:
    """Testes para obtenção de métricas detalhadas"""
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_get_detailed_metrics_success(self, mock_fetch):
        """Testa obtenção de métricas detalhadas com sucesso"""
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.92, 0.91, 0.93],
            'model_accuracy': [0.88, 0.89, 0.87, 0.90],
            'processing_time': [45.0, 43.0, 44.0, 42.0],
            'memory_usage': [500.0, 510.0, 505.0, 520.0],
            'error_rate': [0.05, 0.04, 0.05, 0.03]
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.get_detailed_metrics('24h', 1)
        
        assert len(result) == 5
        assert 'ia_efficiency' in result
        assert 'statistics' in result['ia_efficiency']
        assert 'trends' in result['ia_efficiency']
        assert 'outliers' in result['ia_efficiency']
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_get_detailed_metrics_single_metric(self, mock_fetch):
        """Testa obtenção de métrica única"""
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.92, 0.91, 0.93],
            'model_accuracy': [0.88, 0.89, 0.87, 0.90]
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.get_detailed_metrics('24h', 1, 'ia_efficiency')
        
        assert len(result) == 1
        assert 'ia_efficiency' in result
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_invalid_metric_name(self, mock_fetch):
        """Testa nome de métrica inválido"""
        mock_fetch.return_value = {}
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.get_detailed_metrics('24h', 1, 'invalid_metric')
        
        assert result == {}


class TestCompareMetrics:
    """Testes para comparação de métricas"""
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_compare_metrics_success(self, mock_fetch):
        """Testa comparação de métricas com sucesso"""
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.92, 0.91, 0.93],
            'model_accuracy': [0.88, 0.89, 0.87, 0.90]
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.compare_metrics('24h', 1, 'ia_efficiency', 'model_accuracy')
        
        assert 'correlation' in result
        assert 'metric1_stats' in result
        assert 'metric2_stats' in result
        assert 'normalized' in result
        assert -1 <= result['correlation'] <= 1
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_compare_metrics_high_correlation(self, mock_fetch):
        """Testa métricas altamente correlacionadas"""
        # Mesma sequência = correlação 1.0
        values = [0.9, 0.92, 0.91, 0.93]
        mock_fetch.return_value = {
            'ia_efficiency': values,
            'model_accuracy': values
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.compare_metrics('24h', 1, 'ia_efficiency', 'model_accuracy')
        
        assert abs(result['correlation'] - 1.0) < 0.01  # Quase 1.0


class TestTimeSeries:
    """Testes para análise de série temporal"""
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_get_time_series_data(self, mock_fetch):
        """Testa obtenção de dados de série temporal"""
        now = datetime.utcnow()
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.92, 0.91, 0.93],
            'timestamps': [
                now,
                now + timedelta(hours=1),
                now + timedelta(hours=2),
                now + timedelta(hours=3)
            ]
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.get_time_series_data('24h', 1, 'ia_efficiency', 'hour')
        
        assert 'metric' in result
        assert 'data' in result
        assert result['metric'] == 'ia_efficiency'
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_aggregate_by_day(self, mock_fetch):
        """Testa agregação diária"""
        base_date = datetime(2024, 1, 1, 0, 0, 0)
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.91, 0.92],
            'timestamps': [
                base_date,
                base_date + timedelta(hours=12),
                base_date + timedelta(days=1)
            ]
        }
        
        analyzer = DrilldownAnalyzer()
        result = analyzer.get_time_series_data('7d', 1, 'ia_efficiency', 'day')
        
        assert 'data' in result
        assert len(result['data']) >= 1


class TestPerformanceReport:
    """Testes para geração de relatório"""
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_get_performance_report(self, mock_fetch):
        """Testa geração de relatório de performance"""
        mock_fetch.return_value = {
            'ia_efficiency': [0.9, 0.92, 0.91, 0.93],
            'model_accuracy': [0.88, 0.89, 0.87, 0.90],
            'processing_time': [45.0, 43.0, 44.0, 42.0],
            'memory_usage': [500.0, 510.0, 505.0, 520.0],
            'error_rate': [0.05, 0.04, 0.05, 0.03]
        }
        
        analyzer = DrilldownAnalyzer()
        report = analyzer.get_performance_report('24h', 1)
        
        assert 'periodo' in report
        assert 'generated_at' in report
        assert 'metrics' in report
        assert 'summary' in report
        assert report['periodo'] == '24h'


class TestAggregationLogic:
    """Testes para lógica de agregação"""
    
    def test_aggregate_by_hour(self):
        """Testa agregação por hora"""
        analyzer = DrilldownAnalyzer()
        base_ts = datetime(2024, 1, 1, 10, 30, 45)
        
        data = [
            (base_ts, 0.9),
            (base_ts + timedelta(minutes=15), 0.92),
            (base_ts + timedelta(hours=1, minutes=15), 0.91)
        ]
        
        result = analyzer._aggregate_data(data, 'hour')
        
        assert len(result) == 2  # Duas horas diferentes
        assert all('period' in item for item in result)
        assert all('mean' in item for item in result)
    
    def test_aggregate_empty_data(self):
        """Testa agregação com dados vazios"""
        analyzer = DrilldownAnalyzer()
        
        result = analyzer._aggregate_data([], 'hour')
        
        assert result == []


class TestIntegration:
    """Testes de integração"""
    
    @patch('app.analysis.drilldown.fetch_metrics_from_db')
    def test_complete_analysis_flow(self, mock_fetch):
        """Testa fluxo completo de análise"""
        now = datetime.utcnow()
        mock_fetch.return_value = {
            'ia_efficiency': [0.85, 0.90, 0.92, 0.88, 0.95],
            'model_accuracy': [0.82, 0.88, 0.90, 0.86, 0.92],
            'processing_time': [50.0, 45.0, 42.0, 48.0, 40.0],
            'memory_usage': [520.0, 510.0, 500.0, 515.0, 495.0],
            'error_rate': [0.08, 0.05, 0.03, 0.07, 0.02],
            'timestamps': [
                now + timedelta(hours=i) for i in range(5)
            ]
        }
        
        analyzer = DrilldownAnalyzer()
        
        # Executar análises múltiplas
        detailed = analyzer.get_detailed_metrics('24h', 1)
        comparison = analyzer.compare_metrics('24h', 1)
        report = analyzer.get_performance_report('24h', 1)
        
        assert len(detailed) == 5
        assert 'correlation' in comparison
        assert 'summary' in report
