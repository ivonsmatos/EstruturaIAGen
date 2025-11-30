"""
Sistema de Exportação - CSV e PDF
Exporta dados do dashboard em múltiplos formatos
v2.0.0 - P2.1 Advanced Exports
"""

from app.cache import get_cache_stats
from app.db.metrics import fetch_metrics_from_db, get_metric_stats
from datetime import datetime, timedelta
import csv
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import io

logger = logging.getLogger(__name__)

# Tentar importar reportlab para PDF
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
    from reportlab.lib.units import inch
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False
    logger.warning("⚠ ReportLab não instalado - PDF export desabilitado")


class ExportManager:
    """Gerenciador de exportação de dados"""
    
    def __init__(self, output_dir: str = "./exports"):
        """
        Inicializa ExportManager
        
        Args:
            output_dir: Diretório para salvar arquivos exportados
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ ExportManager inicializado: {self.output_dir}")
    
    def export_to_csv(
        self, 
        periodo: str = "24h", 
        user_id: int = 1,
        include_stats: bool = True,
        filename: Optional[str] = None
    ) -> str:
        """
        Exporta métricas para CSV
        
        Args:
            periodo: Período (24h, 7d, 30d, all)
            user_id: ID do usuário
            include_stats: Incluir estatísticas no CSV
            filename: Nome do arquivo (auto-gerado se None)
            
        Returns:
            Caminho do arquivo exportado
        """
        try:
            logger.info(f"📥 Exportando para CSV: periodo={periodo}")
            
            # Buscar dados
            data = fetch_metrics_from_db(periodo, user_id)
            stats = get_metric_stats(user_id, periodo) if include_stats else {}
            
            # Gerar nome do arquivo
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics_{periodo}_{timestamp}.csv"
            
            filepath = self.output_dir / filename
            
            # Escrever CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([
                    "Timestamp",
                    "IA Efficiency",
                    "Model Accuracy",
                    "Processing Time (ms)",
                    "Memory Usage (MB)",
                    "Error Rate (%)"
                ])
                
                # Dados
                for i, ts in enumerate(data.get("timestamps", [])):
                    writer.writerow([
                        ts.isoformat() if hasattr(ts, 'isoformat') else str(ts),
                        f"{data['ia_efficiency'][i]:.4f}",
                        f"{data['model_accuracy'][i]:.4f}",
                        f"{data['processing_time'][i]:.2f}",
                        f"{data['memory_usage'][i]:.2f}",
                        f"{data['error_rate'][i]:.2f}"
                    ])
                
                # Estatísticas (se solicitado)
                if stats:
                    writer.writerow([])
                    writer.writerow(["ESTATÍSTICAS"])
                    writer.writerow(["Total Records", stats.get("total_records", 0)])
                    writer.writerow(["Avg Efficiency", f"{stats.get('avg_efficiency', 0):.4f}"])
                    writer.writerow(["Avg Accuracy", f"{stats.get('avg_accuracy', 0):.4f}"])
                    writer.writerow(["Avg Processing Time", f"{stats.get('avg_processing_time', 0):.2f}"])
                    writer.writerow(["Avg Memory Usage", f"{stats.get('avg_memory_usage', 0):.2f}"])
                    writer.writerow(["Avg Error Rate", f"{stats.get('avg_error_rate', 0):.2f}"])
            
            logger.info(f"✓ CSV exportado: {filepath} ({filepath.stat().st_size} bytes)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"✗ Erro ao exportar CSV: {str(e)}")
            raise
    
    def export_to_pdf(
        self,
        periodo: str = "24h",
        user_id: int = 1,
        filename: Optional[str] = None
    ) -> str:
        """
        Exporta métricas para PDF
        
        Args:
            periodo: Período (24h, 7d, 30d, all)
            user_id: ID do usuário
            filename: Nome do arquivo (auto-gerado se None)
            
        Returns:
            Caminho do arquivo exportado
        """
        if not HAS_REPORTLAB:
            logger.error("✗ ReportLab não instalado - PDF export indisponível")
            raise ImportError("ReportLab é necessário para exportar PDF")
        
        try:
            logger.info(f"📥 Exportando para PDF: periodo={periodo}")
            
            # Buscar dados
            data = fetch_metrics_from_db(periodo, user_id)
            stats = get_metric_stats(user_id, periodo)
            
            # Gerar nome do arquivo
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics_{periodo}_{timestamp}.pdf"
            
            filepath = self.output_dir / filename
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                str(filepath),
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            elements = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#BBF244'),
                spaceAfter=30
            )
            elements.append(Paragraph("Dashboard de Métricas de IA", title_style))
            
            # Informações gerais
            info_data = [
                ["Período", periodo],
                ["Data de Exportação", datetime.utcnow().strftime("%d/%m/%Y %H:%M:%S")],
                ["Total de Registros", str(stats.get("total_records", 0))],
                ["Usuário ID", str(user_id)]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 4*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1A1F3A')),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#E0E0E0')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.HexColor('#151B35'), colors.HexColor('#1A1F3A')]),
            ]))
            
            elements.append(info_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Estatísticas
            elements.append(Paragraph("Estatísticas", styles['Heading2']))
            
            stats_data = [
                ["Métrica", "Valor"],
                ["Eficiência Média", f"{stats.get('avg_efficiency', 0):.2%}"],
                ["Acurácia Média", f"{stats.get('avg_accuracy', 0):.2%}"],
                ["Tempo de Processamento Médio", f"{stats.get('avg_processing_time', 0):.2f}ms"],
                ["Uso de Memória Médio", f"{stats.get('avg_memory_usage', 0):.2f}MB"],
                ["Taxa de Erro Média", f"{stats.get('avg_error_rate', 0):.2f}%"]
            ]
            
            stats_table = Table(stats_data, colWidths=[3.5*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#BBF244')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#0D0D0D')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#151B35'), colors.HexColor('#1A1F3A')]),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#E0E0E0')),
            ]))
            
            elements.append(stats_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Dados detalhados (primeiros 20)
            elements.append(Paragraph("Dados Detalhados (Últimos 20)", styles['Heading2']))
            
            detail_data = [["Timestamp", "Eficiência", "Acurácia", "Tempo (ms)", "Memória (MB)", "Erro %"]]
            
            timestamps = data.get("timestamps", [])[-20:]
            for i in range(len(timestamps)):
                detail_data.append([
                    timestamps[i].strftime("%H:%M") if hasattr(timestamps[i], 'strftime') else str(timestamps[i])[:5],
                    f"{data['ia_efficiency'][-(len(timestamps)-i)]:.2%}",
                    f"{data['model_accuracy'][-(len(timestamps)-i)]:.2%}",
                    f"{data['processing_time'][-(len(timestamps)-i)]:.1f}",
                    f"{data['memory_usage'][-(len(timestamps)-i)]:.0f}",
                    f"{data['error_rate'][-(len(timestamps)-i)]:.1f}"
                ])
            
            detail_table = Table(detail_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
            detail_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F27244')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#151B35'), colors.HexColor('#1A1F3A')]),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#E0E0E0')),
            ]))
            
            elements.append(detail_table)
            
            # Build PDF
            doc.build(elements)
            
            logger.info(f"✓ PDF exportado: {filepath} ({filepath.stat().st_size} bytes)")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"✗ Erro ao exportar PDF: {str(e)}")
            raise
    
    def export_to_json(
        self,
        periodo: str = "24h",
        user_id: int = 1,
        filename: Optional[str] = None
    ) -> str:
        """
        Exporta métricas para JSON
        
        Args:
            periodo: Período
            user_id: ID do usuário
            filename: Nome do arquivo
            
        Returns:
            Caminho do arquivo
        """
        try:
            logger.info(f"📥 Exportando para JSON: periodo={periodo}")
            
            data = fetch_metrics_from_db(periodo, user_id)
            stats = get_metric_stats(user_id, periodo)
            
            if not filename:
                timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
                filename = f"metrics_{periodo}_{timestamp}.json"
            
            filepath = self.output_dir / filename
            
            # Converter timestamps para string
            export_data = {
                "metadata": {
                    "periodo": periodo,
                    "user_id": user_id,
                    "exported_at": datetime.utcnow().isoformat(),
                    "total_records": data.get("total_metrics", 0)
                },
                "statistics": stats,
                "data": {
                    "timestamps": [str(ts) for ts in data.get("timestamps", [])],
                    "ia_efficiency": data.get("ia_efficiency", []),
                    "model_accuracy": data.get("model_accuracy", []),
                    "processing_time": data.get("processing_time", []),
                    "memory_usage": data.get("memory_usage", []),
                    "error_rate": data.get("error_rate", [])
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"✓ JSON exportado: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"✗ Erro ao exportar JSON: {str(e)}")
            raise


# Instância global
export_manager = ExportManager()
