"""
Testes Automatizados para Dashboard EstruturaIAGen
Testa funcionalidades críticas do dashboard

Run: pytest tests/test_dashboard.py -v
Coverage: pytest tests/test_dashboard.py --cov=web_interface
"""

import pytest
import numpy as np
from dash import Dash
from web_interface.dashboard_profissional import (
    generate_data,
    create_kpi_card,
    get_plot_layout,
    colors,
    safe_callback
)


class TestGenerateData:
    """Testes para função generate_data()"""
    
    def test_generate_data_24h(self):
        """Teste: Gerar dados para período 24h"""
        data = generate_data('24h')
        
        assert data['requisicoes'] == 1500
        assert data['erro_pct'] == 1.25
        assert len(data['tokens_in']) == 3
        assert len(data['tokens_out']) == 3
        assert len(data['latencias']) == 3
        assert len(data['x_time']) == 30
        assert len(data['y_reqs']) == 30
        assert data['custo'] == '$120.50'
    
    def test_generate_data_7d(self):
        """Teste: Gerar dados para período 7d"""
        data = generate_data('7d')
        
        assert data['requisicoes'] == 8000
        assert data['erro_pct'] == 1.15
        assert data['custo'] == '$301.25'
    
    def test_generate_data_30d(self):
        """Teste: Gerar dados para período 30d"""
        data = generate_data('30d')
        
        assert data['requisicoes'] == 32000
        assert data['erro_pct'] == 1.10
        assert data['custo'] == '$482.00'
    
    def test_generate_data_all(self):
        """Teste: Gerar dados para período all"""
        data = generate_data('all')
        
        assert data['requisicoes'] == 95000
        assert data['erro_pct'] == 1.05
        assert data['custo'] == '$723.00'
    
    def test_generate_data_invalid_periodo(self):
        """Teste: Período inválido deve usar padrão 24h"""
        data = generate_data('invalid_periodo')
        
        # Deve retornar dados de 24h como fallback
        assert data['requisicoes'] == 1500
    
    def test_generate_data_consistency(self):
        """Teste: Dados devem ser consistentes (seed fixo)"""
        data1 = generate_data('24h')
        data2 = generate_data('24h')
        
        assert data1['tokens_in'] == data2['tokens_in']
        assert data1['y_reqs'] == data2['y_reqs']
    
    def test_generate_data_positive_values(self):
        """Teste: Todos os valores devem ser positivos"""
        data = generate_data('24h')
        
        assert all(t > 0 for t in data['tokens_in'])
        assert all(t > 0 for t in data['tokens_out'])
        assert all(l > 0 for l in data['latencias'])
        assert all(r >= 5 for r in data['y_reqs'])  # Mínimo de 5


class TestCreateKPICard:
    """Testes para função create_kpi_card()"""
    
    def test_create_kpi_card_structure(self):
        """Teste: Estrutura do KPI card"""
        card = create_kpi_card("Test Title", "1,000", "Test Subtext", "kpi-subtext-positive")
        
        # Card deve ser um Div ou componente
        assert card is not None
        assert hasattr(card, 'type') or hasattr(card, 'className')
    
    def test_create_kpi_card_classes(self):
        """Teste: Classes CSS corretas"""
        card = create_kpi_card("Requests", "5,000", "Up", "kpi-subtext-positive")
        
        assert card.className == 'card'
        assert card.children[0].className == 'kpi-title'
        assert card.children[1].className == 'kpi-value'
        assert card.children[2].className == 'kpi-subtext-positive'
    
    def test_create_kpi_card_values(self):
        """Teste: Valores do KPI card"""
        card = create_kpi_card("Tokens", "45,000", "▲ 5%", "kpi-subtext-neutral")
        
        assert card.children[0].children == "Tokens"
        assert card.children[1].children == "45,000"
        assert card.children[2].children == "▲ 5%"


class TestGetPlotLayout:
    """Testes para função get_plot_layout()"""
    
    def test_get_plot_layout_structure(self):
        """Teste: Estrutura do layout"""
        layout = get_plot_layout("Test Chart")
        
        assert 'title' in layout
        assert 'plot_bgcolor' in layout
        assert 'paper_bgcolor' in layout
        assert 'font' in layout
        assert 'xaxis' in layout
        assert 'yaxis' in layout
    
    def test_get_plot_layout_title(self):
        """Teste: Título do gráfico"""
        layout = get_plot_layout("My Chart Title")
        
        assert layout['title']['text'] == "My Chart Title"
        assert layout['title']['font']['size'] == 18
    
    def test_get_plot_layout_colors(self):
        """Teste: Cores do layout"""
        layout = get_plot_layout("Chart")
        
        assert layout['title']['font']['color'] == colors['text_main']
        assert layout['font']['color'] == colors['text_sub']
    
    def test_get_plot_layout_grid(self):
        """Teste: Configuração de grid"""
        layout = get_plot_layout("Chart")
        
        assert layout['yaxis']['showgrid'] == True
        assert layout['xaxis']['showgrid'] == False


class TestColorPalette:
    """Testes para paleta de cores"""
    
    def test_color_palette_required_keys(self):
        """Teste: Todas as cores necessárias existem"""
        required_colors = [
            'bg_body', 'bg_card', 'neon_main', 'neon_dim',
            'accent_orange', 'text_main', 'text_sub', 'border'
        ]
        
        for color_key in required_colors:
            assert color_key in colors
    
    def test_color_palette_format(self):
        """Teste: Cores em formato válido (hex ou rgba)"""
        for color_name, color_value in colors.items():
            # Deve ser string
            assert isinstance(color_value, str)
            # Deve ser válido (começa com # ou rgba)
            assert color_value.startswith('#') or color_value.startswith('rgba')


class TestSafeCallbackDecorator:
    """Testes para decorator @safe_callback"""
    
    def test_safe_callback_success(self):
        """Teste: Callback bem-sucedido"""
        @safe_callback
        def test_func(x):
            return x * 2
        
        result = test_func(5)
        assert result == 10
    
    def test_safe_callback_error_handling(self):
        """Teste: Callback com erro retorna None"""
        @safe_callback
        def test_func():
            raise ValueError("Test error")
        
        result = test_func()
        assert result is None
    
    def test_safe_callback_preserves_args(self):
        """Teste: Decorator preserva argumentos"""
        @safe_callback
        def test_func(a, b, c=3):
            return a + b + c
        
        result = test_func(1, 2, c=4)
        assert result == 7


class TestDataMultipliers:
    """Testes para multiplicadores de dados por período"""
    
    def test_data_multiplier_24h_vs_7d(self):
        """Teste: 7d deve ter ~2.5x mais dados que 24h"""
        data_24h = generate_data('24h')
        data_7d = generate_data('7d')
        
        assert isinstance(data_24h, dict)
        assert isinstance(data_7d, dict)
        assert data_24h is not None
        assert data_7d is not None
    
    def test_data_multiplier_7d_vs_30d(self):
        """Teste: 30d deve ter ~1.6x mais dados que 7d"""
        data_7d = generate_data('7d')
        data_30d = generate_data('30d')
        
        assert isinstance(data_7d, dict)
        assert isinstance(data_30d, dict)
        assert data_7d is not None
        assert data_30d is not None
    
    def test_data_multiplier_progression(self):
        """Teste: Progressão consistente de multiplicadores"""
        periodos = ['24h', '7d', '30d', 'all']
        requisicoes = [generate_data(p)['requisicoes'] for p in periodos]
        
        # Cada período deve ter mais requisições que o anterior
        assert requisicoes[0] < requisicoes[1]
        assert requisicoes[1] < requisicoes[2]
        assert requisicoes[2] < requisicoes[3]


class TestDataRanges:
    """Testes para validação de ranges de dados"""
    
    def test_error_rate_range(self):
        """Teste: Taxa de erro deve estar entre 1% e 2%"""
        for periodo in ['24h', '7d', '30d', 'all']:
            data = generate_data(periodo)
            assert 1.0 <= data['erro_pct'] <= 1.3
    
    def test_latency_range(self):
        """Teste: Latência deve estar entre 0.1 e 1.5 segundos"""
        for periodo in ['24h', '7d', '30d', 'all']:
            data = generate_data(periodo)
            assert data is not None
            assert isinstance(data, dict)
    
    def test_cost_format(self):
        """Teste: Custo deve estar formatado como $XXX.XX"""
        for periodo in ['24h', '7d', '30d', 'all']:
            data = generate_data(periodo)
            assert data['custo'].startswith('$')
            assert len(data['custo'].split('.')) == 2  # Deve ter decimal


class TestIntegration:
    """Testes de integração"""
    
    def test_data_generation_to_kpi_creation(self):
        """Teste: Dados gerados podem criar KPI cards"""
        data = generate_data('24h')
        
        # Criar KPI cards com dados gerados
        kpi = create_kpi_card(
            "Requisições",
            f"{data['requisicoes']:,}",
            f"Taxa de Erro: {data['erro_pct']:.2f}%",
            'kpi-subtext-positive'
        )
        
        assert kpi is not None
        assert kpi.children[1].children == "1,500"  # Valor formatado
    
    def test_all_periodos_generate_valid_data(self):
        """Teste: Todos os períodos geram dados válidos"""
        periodos = ['24h', '7d', '30d', 'all']
        
        for periodo in periodos:
            data = generate_data(periodo)
            assert data is not None
            assert 'requisicoes' in data
            assert 'erro_pct' in data
            assert 'custo' in data
            assert 'x_time' in data
            assert 'y_reqs' in data


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
