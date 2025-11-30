"""
Testes para o sistema de temas
v2.0.0 - P2.3
"""

import pytest
import tempfile
import json
from pathlib import Path
from app.themes.theme_manager import ThemeManager, ThemeColors, Theme


class TestThemeManagerInit:
    """Testes de inicialização do ThemeManager"""
    
    def test_manager_init(self):
        """Testa inicialização do gerenciador"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            assert manager is not None
            assert len(manager.themes) >= 5
    
    def test_default_themes_loaded(self):
        """Testa se temas padrão são carregados"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            assert 'dark' in manager.themes
            assert 'light' in manager.themes
            assert 'cyberpunk' in manager.themes
            assert 'ocean' in manager.themes
            assert 'forest' in manager.themes


class TestGetTheme:
    """Testes para obtenção de temas"""
    
    def test_get_default_theme(self):
        """Testa obtenção de tema padrão"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            theme = manager.get_theme('dark')
            assert theme is not None
            assert theme.name == 'dark'
            assert theme.is_default is True
    
    def test_get_nonexistent_theme(self):
        """Testa obtenção de tema inexistente"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            theme = manager.get_theme('nonexistent')
            assert theme is None
    
    def test_list_themes(self):
        """Testa listagem de temas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            themes = manager.list_themes()
            assert len(themes) >= 5
            assert any(t['name'] == 'dark' for t in themes)
            assert any(t['is_default'] for t in themes)


class TestThemeCreation:
    """Testes para criação de temas customizados"""
    
    def test_create_custom_theme(self):
        """Testa criação de tema customizado"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            theme = manager.create_custom_theme('my_theme', 'My custom theme', colors)
            
            assert theme is not None
            assert theme.name == 'my_theme'
            assert theme.is_custom is True
            assert theme.description == 'My custom theme'
    
    def test_create_duplicate_theme_fails(self):
        """Testa que criar tema duplicado falha"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            manager.create_custom_theme('my_theme', 'Theme 1', colors)
            
            with pytest.raises(ValueError):
                manager.create_custom_theme('my_theme', 'Theme 2', colors)
    
    def test_invalid_color_format(self):
        """Testa validação de formato de cor"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': 'INVALID_COLOR',  # Inválido
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            with pytest.raises(ValueError):
                manager.create_custom_theme('bad_theme', 'Bad theme', colors)
    
    def test_missing_required_color(self):
        """Testa validação de cores obrigatórias"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                # Faltam cores obrigatórias
            }
            
            with pytest.raises(ValueError):
                manager.create_custom_theme('incomplete_theme', 'Incomplete', colors)


class TestThemeUpdate:
    """Testes para atualização de temas"""
    
    def test_update_custom_theme(self):
        """Testa atualização de tema customizado"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            manager.create_custom_theme('my_theme', 'Original', colors)
            
            new_colors = {'neon_main': '#00FF00'}
            updated = manager.update_theme('my_theme', colors=new_colors, description='Updated')
            
            assert updated.description == 'Updated'
            assert updated.colors.neon_main == '#00FF00'
    
    def test_cannot_update_default_theme(self):
        """Testa que não pode atualizar tema padrão"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            with pytest.raises(ValueError):
                manager.update_theme('dark', description='New description')


class TestThemeDeletion:
    """Testes para deleção de temas"""
    
    def test_delete_custom_theme(self):
        """Testa deleção de tema customizado"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            manager.create_custom_theme('temp_theme', 'Temporary', colors)
            assert 'temp_theme' in manager.themes
            
            result = manager.delete_theme('temp_theme')
            assert result is True
            assert 'temp_theme' not in manager.themes
    
    def test_cannot_delete_default_theme(self):
        """Testa que não pode deletar tema padrão"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            with pytest.raises(ValueError):
                manager.delete_theme('dark')
    
    def test_delete_nonexistent_theme(self):
        """Testa deleção de tema inexistente"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            with pytest.raises(ValueError):
                manager.delete_theme('nonexistent')


class TestThemePersistence:
    """Testes para persistência de temas"""
    
    def test_theme_persists_to_file(self):
        """Testa se tema é salvo em arquivo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            colors = {
                'bg_body': '#FFFFFF',
                'bg_card': '#F0F0F0',
                'neon_main': '#FF0000',
                'neon_dim': 'rgba(255, 0, 0, 0.1)',
                'accent_orange': '#FFA500',
                'accent_secondary': '#FF8C00',
                'text_main': '#000000',
                'text_sub': '#666666',
                'border': '#CCCCCC',
                'success': '#00FF00',
                'warning': '#FFFF00',
                'error': '#FF0000'
            }
            
            manager.create_custom_theme('persist_theme', 'Persistent', colors)
            
            theme_file = Path(tmpdir) / 'persist_theme.json'
            assert theme_file.exists()
            
            with open(theme_file, 'r') as f:
                data = json.load(f)
            
            assert data['name'] == 'persist_theme'
    
    def test_theme_loads_from_file(self):
        """Testa se tema é carregado do arquivo"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Criar arquivo de tema
            theme_file = Path(tmpdir) / 'custom_theme.json'
            theme_data = {
                'name': 'custom_theme',
                'description': 'Custom loaded theme',
                'colors': {
                    'bg_body': '#FFFFFF',
                    'bg_card': '#F0F0F0',
                    'neon_main': '#FF0000',
                    'neon_dim': 'rgba(255, 0, 0, 0.1)',
                    'accent_orange': '#FFA500',
                    'accent_secondary': '#FF8C00',
                    'text_main': '#000000',
                    'text_sub': '#666666',
                    'border': '#CCCCCC',
                    'success': '#00FF00',
                    'warning': '#FFFF00',
                    'error': '#FF0000'
                },
                'created_at': '2024-01-01T00:00:00',
                'updated_at': '2024-01-01T00:00:00',
                'is_default': False,
                'is_custom': True
            }
            
            with open(theme_file, 'w') as f:
                json.dump(theme_data, f)
            
            # Carregar manager
            manager = ThemeManager(tmpdir)
            
            theme = manager.get_theme('custom_theme')
            assert theme is not None
            assert theme.name == 'custom_theme'
            assert theme.is_custom is True


class TestCSSExport:
    """Testes para exportação de CSS"""
    
    def test_export_theme_as_css(self):
        """Testa exportação de tema como CSS"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            css = manager.export_theme_as_css('dark')
            
            assert css is not None
            assert ':root' in css
            assert '--bg-body' in css
            assert '--neon-main' in css
    
    def test_css_contains_colors(self):
        """Testa se CSS contém todas as cores"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            css = manager.export_theme_as_css('dark')
            
            required_vars = [
                '--bg-body', '--bg-card', '--neon-main',
                '--accent-orange', '--text-main', '--error'
            ]
            
            for var in required_vars:
                assert var in css


class TestThemeDuplication:
    """Testes para duplicação de temas"""
    
    def test_duplicate_theme(self):
        """Testa duplicação de tema"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            new_theme = manager.duplicate_theme('dark', 'dark_copy')
            
            assert new_theme is not None
            assert new_theme.name == 'dark_copy'
            assert new_theme.colors.neon_main == manager.DARK_THEME.colors.neon_main


class TestColorValidation:
    """Testes para validação de cores"""
    
    def test_valid_hex_colors(self):
        """Testa validação de cores hex"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            assert manager._is_valid_color('#FFFFFF') is True
            assert manager._is_valid_color('#FFF') is True
            assert manager._is_valid_color('#000000') is True
    
    def test_valid_rgba_colors(self):
        """Testa validação de cores rgba"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            assert manager._is_valid_color('rgba(255, 0, 0, 1)') is True
            assert manager._is_valid_color('rgba(0, 255, 0, 0.5)') is True
    
    def test_invalid_colors(self):
        """Testa rejeição de cores inválidas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            assert manager._is_valid_color('INVALID') is False
            assert manager._is_valid_color('#GGGGGG') is False
            assert manager._is_valid_color('red') is False


class TestIntegration:
    """Testes de integração"""
    
    def test_complete_theme_workflow(self):
        """Testa fluxo completo de gerenciamento de temas"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ThemeManager(tmpdir)
            
            # Listar temas
            themes = manager.list_themes()
            assert len(themes) >= 5
            
            # Obter tema
            dark = manager.get_theme('dark')
            assert dark is not None
            
            # Criar customizado
            colors = dark.colors.to_dict()
            colors['neon_main'] = '#00FF00'
            custom = manager.create_custom_theme('neon_green', 'Green neon', colors)
            assert custom is not None
            
            # Exportar como CSS
            css = manager.export_theme_as_css('neon_green')
            assert '--neon-main: #00FF00' in css
            
            # Duplicar
            copy = manager.duplicate_theme('neon_green', 'neon_green_copy')
            assert copy is not None
            
            # Atualizar
            manager.update_theme('neon_green', description='Updated description')
            
            # Deletar
            manager.delete_theme('neon_green_copy')
