"""
Internationalization (i18n) Manager
===================================

Provides multi-language support for the dashboard.
Supports Portuguese (PT), English (EN), and Spanish (ES).

Version: 3.0.0
Author: AI Dashboard Team
License: MIT
"""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import logging
import json
from enum import Enum
from pathlib import Path
import yaml

# Configure logging
logger = logging.getLogger(__name__)


class LanguageCode(Enum):
    """Supported language codes"""
    PT = "pt"
    EN = "en"
    ES = "es"


@dataclass
class LanguageSettings:
    """Language configuration settings"""
    current_language: LanguageCode = LanguageCode.PT
    fallback_language: LanguageCode = LanguageCode.EN
    auto_detect: bool = True
    cache_translations: bool = True


class I18nManager:
    """
    Manages internationalization for the dashboard.
    
    Features:
    - Multi-language support (PT, EN, ES)
    - Dynamic language switching
    - Translation caching
    - Variable interpolation
    - Language-aware formatting
    
    Example:
        >>> i18n = I18nManager()
        >>> i18n.set_language(LanguageCode.EN)
        >>> text = i18n.get_translation('dashboard.title')
    """
    
    # Default translations embedded in code
    DEFAULT_TRANSLATIONS = {
        "pt": {
            # Dashboard
            "dashboard": {
                "title": "Dashboard Profissional de IA",
                "subtitle": "Monitore modelos de IA em tempo real",
                "welcome": "Bem-vindo ao Dashboard",
                "loading": "Carregando...",
                "error": "Erro ao carregar dados",
                "no_data": "Sem dados disponíveis"
            },
            # KPIs
            "kpi": {
                "total_requests": "Total de Requisições",
                "total_tokens": "Total de Tokens",
                "total_cost": "Custo Total",
                "avg_latency": "Latência Média",
                "daily": "Diário",
                "growth": "Crescimento"
            },
            # Period
            "period": {
                "24h": "Últimas 24 horas",
                "7d": "Últimos 7 dias",
                "30d": "Últimos 30 dias",
                "all": "Período Completo",
                "select_period": "Selecione o período"
            },
            # Charts
            "chart": {
                "tokens": "Tokens Utilizados",
                "latency": "Latência de Resposta",
                "requests": "Taxa de Requisições",
                "models": "Modelos de IA",
                "usage_by_model": "Uso por Modelo",
                "hourly_trend": "Tendência por Hora",
                "performance": "Performance"
            },
            # Export
            "export": {
                "title": "Exportar Dados",
                "csv": "Exportar como CSV",
                "pdf": "Exportar como PDF",
                "json": "Exportar como JSON",
                "success": "Dados exportados com sucesso",
                "error": "Erro ao exportar dados",
                "select_format": "Selecione o formato"
            },
            # Themes
            "theme": {
                "title": "Temas",
                "dark": "Modo Escuro",
                "light": "Modo Claro",
                "cyberpunk": "Cyberpunk",
                "ocean": "Oceano",
                "forest": "Floresta",
                "custom": "Personalizado",
                "select_theme": "Selecione um tema"
            },
            # Analysis
            "analysis": {
                "title": "Análise Avançada",
                "statistics": "Estatísticas",
                "trends": "Tendências",
                "outliers": "Anomalias",
                "correlation": "Correlação",
                "distribution": "Distribuição",
                "forecast": "Previsão"
            },
            # ML
            "ml": {
                "predictions": "Previsões",
                "forecast_title": "Previsão de Uso",
                "confidence": "Confiança",
                "accuracy": "Precisão",
                "model": "Modelo"
            },
            # Analytics
            "analytics": {
                "title": "Analytics",
                "user_activity": "Atividade do Usuário",
                "page_views": "Visualizações de Página",
                "session_duration": "Duração da Sessão",
                "bounce_rate": "Taxa de Rejeição",
                "conversion": "Conversão"
            },
            # Buttons
            "button": {
                "export": "Exportar",
                "download": "Baixar",
                "save": "Salvar",
                "cancel": "Cancelar",
                "apply": "Aplicar",
                "reset": "Redefinir",
                "refresh": "Atualizar"
            },
            # Messages
            "message": {
                "success": "Operação realizada com sucesso",
                "error": "Erro na operação",
                "warning": "Atenção",
                "info": "Informação",
                "confirm": "Tem certeza?",
                "loading": "Processando..."
            }
        },
        "en": {
            # Dashboard
            "dashboard": {
                "title": "AI Professional Dashboard",
                "subtitle": "Monitor AI models in real time",
                "welcome": "Welcome to Dashboard",
                "loading": "Loading...",
                "error": "Error loading data",
                "no_data": "No data available"
            },
            # KPIs
            "kpi": {
                "total_requests": "Total Requests",
                "total_tokens": "Total Tokens",
                "total_cost": "Total Cost",
                "avg_latency": "Average Latency",
                "daily": "Daily",
                "growth": "Growth"
            },
            # Period
            "period": {
                "24h": "Last 24 hours",
                "7d": "Last 7 days",
                "30d": "Last 30 days",
                "all": "All Time",
                "select_period": "Select period"
            },
            # Charts
            "chart": {
                "tokens": "Tokens Used",
                "latency": "Response Latency",
                "requests": "Request Rate",
                "models": "AI Models",
                "usage_by_model": "Usage by Model",
                "hourly_trend": "Hourly Trend",
                "performance": "Performance"
            },
            # Export
            "export": {
                "title": "Export Data",
                "csv": "Export as CSV",
                "pdf": "Export as PDF",
                "json": "Export as JSON",
                "success": "Data exported successfully",
                "error": "Error exporting data",
                "select_format": "Select format"
            },
            # Themes
            "theme": {
                "title": "Themes",
                "dark": "Dark Mode",
                "light": "Light Mode",
                "cyberpunk": "Cyberpunk",
                "ocean": "Ocean",
                "forest": "Forest",
                "custom": "Custom",
                "select_theme": "Select a theme"
            },
            # Analysis
            "analysis": {
                "title": "Advanced Analysis",
                "statistics": "Statistics",
                "trends": "Trends",
                "outliers": "Anomalies",
                "correlation": "Correlation",
                "distribution": "Distribution",
                "forecast": "Forecast"
            },
            # ML
            "ml": {
                "predictions": "Predictions",
                "forecast_title": "Usage Forecast",
                "confidence": "Confidence",
                "accuracy": "Accuracy",
                "model": "Model"
            },
            # Analytics
            "analytics": {
                "title": "Analytics",
                "user_activity": "User Activity",
                "page_views": "Page Views",
                "session_duration": "Session Duration",
                "bounce_rate": "Bounce Rate",
                "conversion": "Conversion"
            },
            # Buttons
            "button": {
                "export": "Export",
                "download": "Download",
                "save": "Save",
                "cancel": "Cancel",
                "apply": "Apply",
                "reset": "Reset",
                "refresh": "Refresh"
            },
            # Messages
            "message": {
                "success": "Operation completed successfully",
                "error": "Operation error",
                "warning": "Warning",
                "info": "Information",
                "confirm": "Are you sure?",
                "loading": "Processing..."
            }
        },
        "es": {
            # Dashboard
            "dashboard": {
                "title": "Panel Profesional de IA",
                "subtitle": "Monitorea modelos de IA en tiempo real",
                "welcome": "Bienvenido al Panel",
                "loading": "Cargando...",
                "error": "Error al cargar datos",
                "no_data": "No hay datos disponibles"
            },
            # KPIs
            "kpi": {
                "total_requests": "Total de Solicitudes",
                "total_tokens": "Total de Tokens",
                "total_cost": "Costo Total",
                "avg_latency": "Latencia Promedio",
                "daily": "Diario",
                "growth": "Crecimiento"
            },
            # Period
            "period": {
                "24h": "Últimas 24 horas",
                "7d": "Últimos 7 días",
                "30d": "Últimos 30 días",
                "all": "Período Completo",
                "select_period": "Seleccionar período"
            },
            # Charts
            "chart": {
                "tokens": "Tokens Utilizados",
                "latency": "Latencia de Respuesta",
                "requests": "Tasa de Solicitudes",
                "models": "Modelos de IA",
                "usage_by_model": "Uso por Modelo",
                "hourly_trend": "Tendencia por Hora",
                "performance": "Rendimiento"
            },
            # Export
            "export": {
                "title": "Exportar Datos",
                "csv": "Exportar como CSV",
                "pdf": "Exportar como PDF",
                "json": "Exportar como JSON",
                "success": "Datos exportados exitosamente",
                "error": "Error al exportar datos",
                "select_format": "Seleccionar formato"
            },
            # Themes
            "theme": {
                "title": "Temas",
                "dark": "Modo Oscuro",
                "light": "Modo Claro",
                "cyberpunk": "Cyberpunk",
                "ocean": "Océano",
                "forest": "Bosque",
                "custom": "Personalizado",
                "select_theme": "Seleccionar tema"
            },
            # Analysis
            "analysis": {
                "title": "Análisis Avanzado",
                "statistics": "Estadísticas",
                "trends": "Tendencias",
                "outliers": "Anomalías",
                "correlation": "Correlación",
                "distribution": "Distribución",
                "forecast": "Pronóstico"
            },
            # ML
            "ml": {
                "predictions": "Predicciones",
                "forecast_title": "Pronóstico de Uso",
                "confidence": "Confianza",
                "accuracy": "Precisión",
                "model": "Modelo"
            },
            # Analytics
            "analytics": {
                "title": "Análitica",
                "user_activity": "Actividad del Usuario",
                "page_views": "Vistas de Página",
                "session_duration": "Duración de la Sesión",
                "bounce_rate": "Tasa de Rebote",
                "conversion": "Conversión"
            },
            # Buttons
            "button": {
                "export": "Exportar",
                "download": "Descargar",
                "save": "Guardar",
                "cancel": "Cancelar",
                "apply": "Aplicar",
                "reset": "Restablecer",
                "refresh": "Actualizar"
            },
            # Messages
            "message": {
                "success": "Operación completada exitosamente",
                "error": "Error en la operación",
                "warning": "Advertencia",
                "info": "Información",
                "confirm": "¿Estás seguro?",
                "loading": "Procesando..."
            }
        }
    }
    
    def __init__(self, settings: LanguageSettings = None):
        """Initialize i18n manager"""
        self.settings = settings or LanguageSettings()
        self.translations = self.DEFAULT_TRANSLATIONS.copy()
        self.logger = logging.getLogger(__name__)
    
    def set_language(self, language: Union[LanguageCode, str]) -> None:
        """
        Set the current language.
        
        Args:
            language: LanguageCode or language code string (e.g., 'en', 'pt', 'es')
        """
        try:
            if isinstance(language, str):
                language = LanguageCode(language)
            
            self.settings.current_language = language
            self.logger.info(f"Language set to {language.value}")
        
        except ValueError:
            self.logger.error(f"Unsupported language: {language}")
            self.settings.current_language = self.settings.fallback_language
    
    def get_translation(
        self,
        key: str,
        variables: Dict[str, Any] = None
    ) -> str:
        """
        Get translated text.
        
        Args:
            key: Translation key in dot notation (e.g., 'dashboard.title')
            variables: Optional variables for interpolation
            
        Returns:
            Translated text or key if translation not found
            
        Example:
            >>> i18n.get_translation('kpi.total_requests')
            'Total de Requisições'
        """
        try:
            lang_code = self.settings.current_language.value
            keys = key.split('.')
            
            # Navigate through nested dictionary
            value = self.translations.get(lang_code, {})
            for k in keys:
                value = value.get(k, {})
            
            # Return translated string or fallback
            if isinstance(value, str):
                text = value
            else:
                # Try fallback language
                value = self.translations.get(self.settings.fallback_language.value, {})
                for k in keys:
                    value = value.get(k, {})
                text = str(value) if value else key
            
            # Interpolate variables if provided
            if variables:
                text = self._interpolate(text, variables)
            
            return text
        
        except Exception as e:
            self.logger.error(f"Error getting translation for {key}: {str(e)}")
            return key
    
    def get_all_translations(self, language: LanguageCode = None) -> Dict:
        """
        Get all translations for a language.
        
        Args:
            language: Language code (defaults to current language)
            
        Returns:
            Dictionary of all translations
        """
        if language is None:
            language = self.settings.current_language
        
        return self.translations.get(language.value, {})
    
    def add_translation(
        self,
        language: LanguageCode,
        key: str,
        value: str
    ) -> None:
        """
        Add or update a translation.
        
        Args:
            language: Language code
            key: Translation key in dot notation
            value: Translated text
            
        Example:
            >>> i18n.add_translation(LanguageCode.EN, 'custom.greeting', 'Hello!')
        """
        try:
            lang_code = language.value
            keys = key.split('.')
            
            # Ensure language exists
            if lang_code not in self.translations:
                self.translations[lang_code] = {}
            
            # Navigate to parent dictionary
            current = self.translations[lang_code]
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]
            
            # Set value
            current[keys[-1]] = value
            self.logger.info(f"Translation added: {language.value}.{key}")
        
        except Exception as e:
            self.logger.error(f"Error adding translation: {str(e)}")
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        Get list of supported languages.
        
        Returns:
            List of language information dictionaries
        """
        return [
            {"code": "pt", "name": "Português", "native": "Português"},
            {"code": "en", "name": "English", "native": "English"},
            {"code": "es", "name": "Español", "native": "Español"}
        ]
    
    def get_current_language(self) -> Dict[str, str]:
        """
        Get current language information.
        
        Returns:
            Dictionary with current language details
        """
        lang_code = self.settings.current_language.value
        languages = self.get_supported_languages()
        return next((l for l in languages if l['code'] == lang_code), {})
    
    def _interpolate(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Interpolate variables in text.
        
        Args:
            text: Text with {{variable}} placeholders
            variables: Dictionary of variables
            
        Returns:
            Interpolated text
        """
        try:
            for var_name, var_value in variables.items():
                placeholder = "{{" + var_name + "}}"
                text = text.replace(placeholder, str(var_value))
            return text
        except Exception as e:
            self.logger.error(f"Error interpolating variables: {str(e)}")
            return text
    
    def export_translations(self, language: LanguageCode, format: str = "json") -> str:
        """
        Export translations in specified format.
        
        Args:
            language: Language to export
            format: Export format ('json' or 'yaml')
            
        Returns:
            Exported translations as string
        """
        try:
            translations = self.get_all_translations(language)
            
            if format == "yaml":
                return yaml.dump(translations, allow_unicode=True, default_flow_style=False)
            else:  # json
                return json.dumps(translations, ensure_ascii=False, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error exporting translations: {str(e)}")
            return ""


# Export public API
__all__ = [
    'I18nManager',
    'LanguageCode',
    'LanguageSettings'
]
