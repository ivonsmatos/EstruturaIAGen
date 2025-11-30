"""
Testes para o sistema de exportação
v2.0.0 - P2.1
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.export import ExportManager
import tempfile
import csv


class TestExportManagerInit:
    """Testes de inicialização do ExportManager"""
    
    def test_init_default_path(self):
        """Testa inicialização com caminho padrão"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager(tmpdir)
            assert manager.output_dir == Path(tmpdir)
            assert manager.output_dir.exists()
    
    def test_init_creates_directory(self):
        """Testa se cria diretório se não existir"""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = Path(tmpdir) / "exports" / "nested"
            manager = ExportManager(str(new_dir))
            assert new_dir.exists()


class TestExportToCSV:
    """Testes para exportação CSV"""
    
    @pytest.fixture
    def manager(self):
        """Cria ExportManager com diretório temporário"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExportManager(tmpdir)
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_csv_success(self, mock_stats, mock_fetch, manager):
        """Testa exportação bem-sucedida para CSV"""
        # Mock dos dados
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08]
        }
        mock_stats.return_value = {
            "total_records": 1,
            "avg_efficiency": 0.95,
            "avg_accuracy": 0.92,
            "avg_processing_time": 45.5,
            "avg_memory_usage": 512.0,
            "avg_error_rate": 0.08
        }
        
        filepath = manager.export_to_csv("24h", 1)
        
        assert Path(filepath).exists()
        assert Path(filepath).suffix == ".csv"
        assert "24h" in Path(filepath).name
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_csv_content(self, mock_stats, mock_fetch, manager):
        """Testa conteúdo do CSV exportado"""
        mock_fetch.return_value = {
            "timestamps": [
                datetime(2024, 1, 1, 10, 0),
                datetime(2024, 1, 1, 11, 0)
            ],
            "ia_efficiency": [0.95, 0.97],
            "model_accuracy": [0.92, 0.94],
            "processing_time": [45.5, 42.3],
            "memory_usage": [512.0, 520.0],
            "error_rate": [0.08, 0.06]
        }
        mock_stats.return_value = {"total_records": 2}
        
        filepath = manager.export_to_csv("24h", 1, include_stats=False)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) >= 3  # Header + 2 dados
        assert "Timestamp" in rows[0]
        assert "IA Efficiency" in rows[0]
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_csv_with_stats(self, mock_stats, mock_fetch, manager):
        """Testa CSV com estatísticas incluídas"""
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08]
        }
        mock_stats.return_value = {
            "total_records": 100,
            "avg_efficiency": 0.95,
            "avg_accuracy": 0.92
        }
        
        filepath = manager.export_to_csv("24h", 1, include_stats=True)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "ESTATÍSTICAS" in content
        assert "Total Records" in content
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    def test_export_csv_error_handling(self, mock_fetch, manager):
        """Testa tratamento de erro ao exportar CSV"""
        mock_fetch.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            manager.export_to_csv("24h", 1)
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_csv_custom_filename(self, mock_stats, mock_fetch, manager):
        """Testa exportação com nome customizado"""
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08]
        }
        mock_stats.return_value = {"total_records": 1}
        
        custom_name = "custom_export.csv"
        filepath = manager.export_to_csv("24h", 1, filename=custom_name)
        
        assert Path(filepath).name == custom_name


class TestExportToPDF:
    """Testes para exportação PDF"""
    
    @pytest.fixture
    def manager(self):
        """Cria ExportManager com diretório temporário"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExportManager(tmpdir)
    
    @patch('app.export.export_manager.HAS_REPORTLAB', False)
    def test_pdf_export_without_reportlab(self, manager):
        """Testa erro quando ReportLab não está instalado"""
        with pytest.raises(ImportError):
            manager.export_to_pdf("24h", 1)
    
    @patch('app.export.export_manager.HAS_REPORTLAB', True)
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_pdf_success(self, mock_stats, mock_fetch, manager):
        """Testa exportação bem-sucedida para PDF (com ReportLab)"""
        try:
            from reportlab.lib.pagesizes import letter
        except ImportError:
            pytest.skip("ReportLab não instalado")
        
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {
            "total_records": 1,
            "avg_efficiency": 0.95,
            "avg_accuracy": 0.92,
            "avg_processing_time": 45.5,
            "avg_memory_usage": 512.0,
            "avg_error_rate": 0.08
        }
        
        filepath = manager.export_to_pdf("24h", 1)
        
        assert Path(filepath).exists()
        assert Path(filepath).suffix == ".pdf"
        assert Path(filepath).stat().st_size > 0
    
    @patch('app.export.export_manager.HAS_REPORTLAB', True)
    @patch('app.export.export_manager.fetch_metrics_from_db')
    def test_pdf_export_error_handling(self, mock_fetch, manager):
        """Testa tratamento de erro ao exportar PDF"""
        try:
            from reportlab.lib.pagesizes import letter
        except ImportError:
            pytest.skip("ReportLab não instalado")
        
        mock_fetch.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            manager.export_to_pdf("24h", 1)


class TestExportToJSON:
    """Testes para exportação JSON"""
    
    @pytest.fixture
    def manager(self):
        """Cria ExportManager com diretório temporário"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExportManager(tmpdir)
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_json_success(self, mock_stats, mock_fetch, manager):
        """Testa exportação bem-sucedida para JSON"""
        mock_fetch.return_value = {
            "timestamps": [datetime(2024, 1, 1, 10, 0)],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {
            "total_records": 1,
            "avg_efficiency": 0.95,
            "avg_accuracy": 0.92
        }
        
        filepath = manager.export_to_json("24h", 1)
        
        assert Path(filepath).exists()
        assert Path(filepath).suffix == ".json"
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_json_content(self, mock_stats, mock_fetch, manager):
        """Testa conteúdo do JSON exportado"""
        test_ts = datetime(2024, 1, 1, 10, 0)
        mock_fetch.return_value = {
            "timestamps": [test_ts],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {
            "total_records": 1,
            "avg_efficiency": 0.95
        }
        
        filepath = manager.export_to_json("24h", 1)
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "metadata" in data
        assert "statistics" in data
        assert "data" in data
        assert data["metadata"]["periodo"] == "24h"
        assert data["metadata"]["user_id"] == 1
        assert len(data["data"]["timestamps"]) == 1
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_json_custom_filename(self, mock_stats, mock_fetch, manager):
        """Testa JSON com nome customizado"""
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {"total_records": 1}
        
        custom_name = "export_data.json"
        filepath = manager.export_to_json("24h", 1, filename=custom_name)
        
        assert Path(filepath).name == custom_name


class TestExportIntegration:
    """Testes de integração entre formatos"""
    
    @pytest.fixture
    def manager(self):
        """Cria ExportManager com diretório temporário"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield ExportManager(tmpdir)
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_multiple_exports_same_data(self, mock_stats, mock_fetch, manager):
        """Testa múltiplas exportações com mesmos dados"""
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {"total_records": 1}
        
        csv_file = manager.export_to_csv("24h", 1)
        json_file = manager.export_to_json("24h", 1)
        
        assert Path(csv_file).exists()
        assert Path(json_file).exists()
        assert csv_file != json_file
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_different_periods(self, mock_stats, mock_fetch, manager):
        """Testa exportação de diferentes períodos"""
        mock_fetch.return_value = {
            "timestamps": [datetime.utcnow()],
            "ia_efficiency": [0.95],
            "model_accuracy": [0.92],
            "processing_time": [45.5],
            "memory_usage": [512.0],
            "error_rate": [0.08],
            "total_metrics": 1
        }
        mock_stats.return_value = {"total_records": 1}
        
        for period in ["24h", "7d", "30d"]:
            filepath = manager.export_to_csv(period, 1)
            assert Path(filepath).exists()
            assert period in Path(filepath).name
    
    @patch('app.export.export_manager.fetch_metrics_from_db')
    @patch('app.export.export_manager.get_metric_stats')
    def test_export_creates_files_in_correct_directory(self, mock_stats, mock_fetch):
        """Testa se arquivos são criados no diretório correto"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ExportManager(tmpdir)
            
            mock_fetch.return_value = {
                "timestamps": [datetime.utcnow()],
                "ia_efficiency": [0.95],
                "model_accuracy": [0.92],
                "processing_time": [45.5],
                "memory_usage": [512.0],
                "error_rate": [0.08],
                "total_metrics": 1
            }
            mock_stats.return_value = {"total_records": 1}
            
            filepath = manager.export_to_csv("24h", 1)
            
            assert Path(filepath).parent == Path(tmpdir)
