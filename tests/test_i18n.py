"""
Tests for I18n Manager (P3.2)
============================

Unit tests for internationalization system with PT/EN/ES support.

Version: 3.0.0
"""

import pytest
from app.i18n.i18n_manager import (
    I18nManager,
    LanguageCode,
    LanguageSettings
)


class TestLanguageSettings:
    """Test LanguageSettings dataclass"""
    
    def test_default_settings(self):
        """Test default language settings"""
        settings = LanguageSettings()
        assert settings.current_language == LanguageCode.PT
        assert settings.fallback_language == LanguageCode.EN
        assert settings.auto_detect is True
        assert settings.cache_translations is True
    
    def test_custom_settings(self):
        """Test custom language settings"""
        settings = LanguageSettings(
            current_language=LanguageCode.EN,
            fallback_language=LanguageCode.PT,
            auto_detect=False
        )
        assert settings.current_language == LanguageCode.EN
        assert settings.fallback_language == LanguageCode.PT
        assert settings.auto_detect is False


class TestI18nManager:
    """Test I18nManager class"""
    
    @pytest.fixture
    def manager(self):
        """Create i18n manager instance"""
        return I18nManager()
    
    def test_initialization(self, manager):
        """Test manager initialization"""
        assert manager is not None
        assert manager.settings.current_language == LanguageCode.PT
        assert len(manager.translations) == 3  # PT, EN, ES
    
    def test_set_language_enum(self, manager):
        """Test setting language with enum"""
        manager.set_language(LanguageCode.EN)
        assert manager.settings.current_language == LanguageCode.EN
        
        manager.set_language(LanguageCode.ES)
        assert manager.settings.current_language == LanguageCode.ES
    
    def test_set_language_string(self, manager):
        """Test setting language with string"""
        manager.set_language('en')
        assert manager.settings.current_language == LanguageCode.EN
        
        manager.set_language('es')
        assert manager.settings.current_language == LanguageCode.ES
    
    def test_set_invalid_language(self, manager):
        """Test setting invalid language"""
        manager.set_language('invalid')
        # Should fallback to current language
        assert manager.settings.current_language == LanguageCode.PT or \
               manager.settings.current_language == LanguageCode.EN
    
    def test_get_translation_portuguese(self, manager):
        """Test getting Portuguese translations"""
        manager.set_language(LanguageCode.PT)
        
        title = manager.get_translation('dashboard.title')
        assert title == 'Dashboard Profissional de IA'
        
        kpi = manager.get_translation('kpi.total_requests')
        assert kpi == 'Total de Requisições'
    
    def test_get_translation_english(self, manager):
        """Test getting English translations"""
        manager.set_language(LanguageCode.EN)
        
        title = manager.get_translation('dashboard.title')
        assert title == 'AI Professional Dashboard'
        
        kpi = manager.get_translation('kpi.total_requests')
        assert kpi == 'Total Requests'
    
    def test_get_translation_spanish(self, manager):
        """Test getting Spanish translations"""
        manager.set_language(LanguageCode.ES)
        
        title = manager.get_translation('dashboard.title')
        assert title == 'Panel Profesional de IA'
        
        kpi = manager.get_translation('kpi.total_requests')
        assert kpi == 'Total de Solicitudes'
    
    def test_get_missing_translation(self, manager):
        """Test getting missing translation returns key"""
        manager.set_language(LanguageCode.EN)
        
        result = manager.get_translation('non.existent.key')
        assert result == 'non.existent.key'
    
    def test_get_all_translations(self, manager):
        """Test getting all translations for a language"""
        translations_pt = manager.get_all_translations(LanguageCode.PT)
        assert isinstance(translations_pt, dict)
        assert 'dashboard' in translations_pt
        assert 'kpi' in translations_pt
        
        translations_en = manager.get_all_translations(LanguageCode.EN)
        assert isinstance(translations_en, dict)
        assert len(translations_en) == len(translations_pt)
    
    def test_add_translation(self, manager):
        """Test adding new translation"""
        manager.add_translation(
            LanguageCode.EN,
            'custom.greeting',
            'Hello!'
        )
        
        manager.set_language(LanguageCode.EN)
        result = manager.get_translation('custom.greeting')
        assert result == 'Hello!'
    
    def test_add_translation_nested(self, manager):
        """Test adding nested translation"""
        manager.add_translation(
            LanguageCode.PT,
            'custom.nested.key',
            'Valor Customizado'
        )
        
        manager.set_language(LanguageCode.PT)
        result = manager.get_translation('custom.nested.key')
        assert result == 'Valor Customizado'
    
    def test_variable_interpolation(self, manager):
        """Test variable interpolation in translations"""
        manager.add_translation(
            LanguageCode.EN,
            'greeting',
            'Hello {{name}}, welcome to {{app}}'
        )
        
        manager.set_language(LanguageCode.EN)
        result = manager.get_translation(
            'greeting',
            {'name': 'John', 'app': 'Dashboard'}
        )
        assert result == 'Hello John, welcome to Dashboard'
    
    def test_get_supported_languages(self, manager):
        """Test getting supported languages list"""
        languages = manager.get_supported_languages()
        
        assert len(languages) == 3
        lang_codes = [l['code'] for l in languages]
        assert 'pt' in lang_codes
        assert 'en' in lang_codes
        assert 'es' in lang_codes
    
    def test_get_current_language_info(self, manager):
        """Test getting current language info"""
        manager.set_language(LanguageCode.PT)
        info = manager.get_current_language()
        
        assert info['code'] == 'pt'
        assert 'name' in info
        assert 'native' in info
    
    def test_translation_completeness(self, manager):
        """Test that all translations are complete"""
        sections = ['dashboard', 'kpi', 'period', 'chart', 'export', 'theme', 'analysis', 'ml', 'analytics', 'button', 'message']
        
        for lang in [LanguageCode.PT, LanguageCode.EN, LanguageCode.ES]:
            translations = manager.get_all_translations(lang)
            for section in sections:
                assert section in translations, f"Missing section {section} for {lang.value}"
    
    def test_dashboard_keys(self, manager):
        """Test dashboard section translations"""
        manager.set_language(LanguageCode.PT)
        
        assert manager.get_translation('dashboard.title') != 'dashboard.title'
        assert manager.get_translation('dashboard.subtitle') != 'dashboard.subtitle'
        assert manager.get_translation('dashboard.welcome') != 'dashboard.welcome'
    
    def test_export_keys(self, manager):
        """Test export section translations"""
        manager.set_language(LanguageCode.EN)
        
        assert manager.get_translation('export.title') == 'Export Data'
        assert manager.get_translation('export.csv') == 'Export as CSV'
        assert manager.get_translation('export.pdf') == 'Export as PDF'
    
    def test_theme_keys(self, manager):
        """Test theme section translations"""
        manager.set_language(LanguageCode.ES)
        
        assert manager.get_translation('theme.dark') == 'Modo Oscuro'
        assert manager.get_translation('theme.light') == 'Modo Claro'
    
    def test_language_switching(self, manager):
        """Test switching between languages"""
        text_pt = manager.get_translation('dashboard.title')
        
        manager.set_language(LanguageCode.EN)
        text_en = manager.get_translation('dashboard.title')
        
        manager.set_language(LanguageCode.ES)
        text_es = manager.get_translation('dashboard.title')
        
        assert text_pt != text_en
        assert text_en != text_es
        assert text_pt != text_es
    
    def test_export_translations_json(self, manager):
        """Test exporting translations as JSON"""
        json_str = manager.export_translations(LanguageCode.EN, 'json')
        
        assert isinstance(json_str, str)
        assert 'dashboard' in json_str
        assert 'dashboard' in json_str
    
    def test_export_translations_yaml(self, manager):
        """Test exporting translations as YAML"""
        yaml_str = manager.export_translations(LanguageCode.PT, 'yaml')
        
        assert isinstance(yaml_str, str)
        assert len(yaml_str) > 0
    
    def test_button_translations(self, manager):
        """Test button translations consistency"""
        manager.set_language(LanguageCode.PT)
        
        buttons = ['export', 'download', 'save', 'cancel', 'apply', 'reset', 'refresh']
        for btn in buttons:
            key = f'button.{btn}'
            translation = manager.get_translation(key)
            assert translation != key  # Should be translated
    
    def test_message_translations(self, manager):
        """Test message translations consistency"""
        manager.set_language(LanguageCode.EN)
        
        messages = ['success', 'error', 'warning', 'info', 'confirm', 'loading']
        for msg in messages:
            key = f'message.{msg}'
            translation = manager.get_translation(key)
            assert translation != key  # Should be translated
    
    def test_period_translations_all_languages(self, manager):
        """Test period translations in all languages"""
        periods = ['24h', '7d', '30d', 'all']
        
        for lang in [LanguageCode.PT, LanguageCode.EN, LanguageCode.ES]:
            manager.set_language(lang)
            for period in periods:
                key = f'period.{period}'
                translation = manager.get_translation(key)
                assert translation != key
    
    def test_ml_analytics_terminology(self, manager):
        """Test ML and analytics terminology translations"""
        manager.set_language(LanguageCode.EN)
        
        assert 'Predictions' in manager.get_translation('ml.predictions')
        assert 'Analytics' in manager.get_translation('analytics.title')
