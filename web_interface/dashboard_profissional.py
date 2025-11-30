import dash
from dash import dcc, html, callback, Input, Output, no_update
import plotly.graph_objects as go
import numpy as np
import logging
import os
from functools import wraps
from app.export import export_manager

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dashboard.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============================================================================
# ENVIRONMENT & DEBUG MODE
# ============================================================================
DEBUG_MODE = os.getenv('DASH_DEBUG', 'False').lower() == 'true'
if not DEBUG_MODE:
    logger.info("✓ Debug mode desativado (Production mode)")
else:
    logger.warning("⚠ Debug mode ativado (Development mode)")

# Paleta de Cores
colors = {
    'bg_body': '#0D0D0D',
    'bg_card': 'rgba(26, 26, 26, 0.8)',
    'neon_main': '#BBF244',
    'neon_dim': 'rgba(187, 242, 68, 0.1)',
    'accent_orange': '#F27244',
    'text_main': '#E0E0E0',
    'text_sub': '#888888',
    'border': '#333333'
}

# ============================================================================
# ERROR HANDLING DECORATOR
# ============================================================================
def safe_callback(func):
    """Decorator para tratamento de erros em callbacks"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            logger.info(f"Executando callback: {func.__name__}")
            result = func(*args, **kwargs)
            logger.info(f"Callback {func.__name__} completado com sucesso")
            return result
        except Exception as e:
            logger.error(f"Erro no callback {func.__name__}: {str(e)}", exc_info=True)
            # Retorna dados padrão em caso de erro
            return None
    return wrapper

# App Dash
app = dash.Dash(__name__)
logger.info("Aplicação Dash inicializada")

# Dados Fictícios base
models = ['GPT-4', 'Claude 3', 'Llama 3']

# Função para layout dos gráficos
def get_plot_layout(title):
    return dict(
        title=dict(text=title, font=dict(size=18, color=colors['text_main'])),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=colors['text_sub']),
        xaxis=dict(showgrid=False, zeroline=False, color=colors['text_sub']),
        yaxis=dict(showgrid=True, gridcolor=colors['border'], gridwidth=0.5, zeroline=False),
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

def create_kpi_card(title, value, subtext, subtext_color_class):
    return html.Div(className='card', children=[
        html.H6(title, className='kpi-title'),
        html.H2(value, className='kpi-value'),
        html.Div(subtext, className=subtext_color_class)
    ])

# Função para gerar dados baseado no período
def generate_data(periodo):
    """Gera dados diferentes baseado no período selecionado
    
    Args:
        periodo (str): Período selecionado (24h, 7d, 30d, all)
    
    Returns:
        dict: Dicionário com dados gerados
    """
    try:
        logger.debug(f"Gerando dados para período: {periodo}")
        np.random.seed(42)  # Para consistência
        
        # Mapeamento de períodos
        periodo_config = {
            '24h': {'multiplier': 1.0, 'requisicoes': 1500, 'erro_pct': 1.25},
            '7d': {'multiplier': 2.5, 'requisicoes': 8000, 'erro_pct': 1.15},
            '30d': {'multiplier': 4.0, 'requisicoes': 32000, 'erro_pct': 1.10},
            'all': {'multiplier': 6.0, 'requisicoes': 95000, 'erro_pct': 1.05}
        }
        
        if periodo not in periodo_config:
            logger.warning(f"Período inválido: {periodo}. Usando padrão '24h'")
            periodo = '24h'
        
        config = periodo_config[periodo]
        multiplier = config['multiplier']
        requisicoes = config['requisicoes']
        erro_pct = config['erro_pct']
        
        tokens_in = [int(350 * multiplier), int(200 * multiplier), int(450 * multiplier)]
        tokens_out = [int(500 * multiplier), int(600 * multiplier), int(400 * multiplier)]
        latencias = [1.2 / multiplier * 0.5, 0.8 / multiplier * 0.5, 0.4 / multiplier * 0.5]
        custo = f"${120.50 * multiplier:.2f}"
        
        # Gráfico em tempo real
        x_time = list(range(30))
        y_reqs = [10 * multiplier + np.random.normal(0, 2) for _ in range(30)]
        y_reqs = [max(5, r) for r in y_reqs]
        y_reqs = [y_reqs[i] + (i * 2 * multiplier / 2) for i in range(len(y_reqs))]
        
        logger.debug(f"Dados gerados com sucesso para período: {periodo}")
        
        return {
            'tokens_in': tokens_in,
            'tokens_out': tokens_out,
            'latencias': latencias,
            'custo': custo,
            'requisicoes': requisicoes,
            'erro_pct': erro_pct,
            'x_time': x_time,
            'y_reqs': y_reqs
        }
    except Exception as e:
        logger.error(f"Erro ao gerar dados para período {periodo}: {str(e)}", exc_info=True)
        raise

# Gráficos iniciais (24h)
initial_data = generate_data('24h')

fig_tokens = go.Figure(data=[
    go.Bar(name='Input Tokens', x=models, y=initial_data['tokens_in'], marker_color=colors['accent_orange'], marker_line_width=0),
    go.Bar(name='Output Tokens', x=models, y=initial_data['tokens_out'], marker_color=colors['neon_main'], marker_line_width=0)
])
fig_tokens.update_layout(get_plot_layout('Consumo de Tokens por Modelo'), barmode='stack')

fig_latency = go.Figure(data=[
    go.Scatter(x=models, y=initial_data['latencias'], mode='lines+markers',
               line=dict(color=colors['neon_main'], width=3, shape='spline'),
               marker=dict(size=12, color=colors['bg_body'], line=dict(width=2, color=colors['neon_main'])))
])
fig_latency.update_layout(get_plot_layout('Latência Média (segundos)'))

fig_realtime = go.Figure(data=[
    go.Scatter(x=initial_data['x_time'], y=initial_data['y_reqs'], fill='tozeroy', mode='lines',
               line=dict(color=colors['neon_main'], width=2),
               fillcolor=colors['neon_dim'])
])
fig_realtime.update_layout(get_plot_layout('Taxa de Requisições por Segundo'))

# Layout
app.layout = html.Div(children=[
    # Hero Section
    html.Div(className='hero', children=[
        html.H1("EstruturaIAGen"),
        html.P("Painel de Monitoramento de Performance em Tempo Real")
    ]),
    
    # Container Principal
    html.Div(className='container', children=[
        # Header com Filtro e Botões
        html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '40px'}, children=[
            # Dropdown de Filtro
            html.Div(children=[
                html.Label("Período:", style={'color': '#E0E0E0', 'marginRight': '10px', 'fontWeight': '500'}),
                dcc.Dropdown(
                    id='periodo-filter',
                    options=[
                        {'label': 'Últimas 24h', 'value': '24h'},
                        {'label': 'Últimos 7 dias', 'value': '7d'},
                        {'label': 'Últimos 30 dias', 'value': '30d'},
                        {'label': 'Todos os dados', 'value': 'all'}
                    ],
                    value='24h',
                    style={
                        'backgroundColor': '#151B35',
                        'color': '#BBF244',
                        'border': '1px solid #BBF244',
                        'borderRadius': '6px',
                        'width': '180px'
                    }
                )
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            # Grupo de Botões de Exportação
            html.Div(style={'display': 'flex', 'gap': '10px'}, children=[
                html.Button(
                    "📊 CSV",
                    id='btn-export-csv',
                    className='export-button',
                    style={'padding': '10px 15px', 'fontSize': '13px'}
                ),
                html.Button(
                    "📄 PDF",
                    id='btn-export-pdf',
                    className='export-button',
                    style={'padding': '10px 15px', 'fontSize': '13px'}
                ),
                html.Button(
                    "📋 JSON",
                    id='btn-export-json',
                    className='export-button',
                    style={'padding': '10px 15px', 'fontSize': '13px'}
                ),
                dcc.Download(id='download-dataframe-csv'),
                dcc.Download(id='download-dataframe-pdf'),
                dcc.Download(id='download-dataframe-json'),
                html.Div(id='export-status', style={'marginLeft': '15px', 'color': '#BBF244', 'fontSize': '12px'})
            ])
        ]),
        
        # KPIs
        html.Div(id='kpis-container', style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '25px', 'marginBottom': '50px', 'justifyContent': 'center'}, children=[]),
        
        # Título da seção de gráficos
        html.H2("Análise de Performance", style={'color': '#FFFFFF', 'fontSize': '24px', 'fontWeight': '700', 'marginBottom': '30px', 'marginTop': '20px', 'letterSpacing': '-0.3px'}),
        
        # Gráficos lado a lado
        html.Div(style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '30px', 'marginBottom': '30px'}, children=[
            html.Div(className='graph-container', children=[dcc.Graph(id='graph-tokens', config={'displayModeBar': False})]),
            html.Div(className='graph-container', children=[dcc.Graph(id='graph-latency', config={'displayModeBar': False})]),
        ]),
        
        # Gráfico em tempo real - full width
        html.Div(className='graph-container', children=[
            dcc.Graph(id='graph-realtime', config={'displayModeBar': False})
        ])
    ])
])

# Callback para atualizar todos os dados quando o período muda
@callback(
    [Output('kpis-container', 'children'),
     Output('graph-tokens', 'figure'),
     Output('graph-latency', 'figure'),
     Output('graph-realtime', 'figure')],
    Input('periodo-filter', 'value'),
    prevent_initial_call=False
)
@safe_callback
def update_dashboard(selected_periodo):
    """Atualiza todos os gráficos e KPIs quando o período é alterado
    
    Args:
        selected_periodo (str): Período selecionado
    
    Returns:
        tuple: (KPIs, fig_tokens, fig_latency, fig_realtime)
    """
    try:
        data = generate_data(selected_periodo)
        
        # KPIs
        kpi_cards = [
            create_kpi_card("Requisições", f"{data['requisicoes']:,}", "▲ 12% vs período anterior", 'kpi-subtext-positive'),
            create_kpi_card("Tokens Totais", f"{(sum(data['tokens_in']) + sum(data['tokens_out'])):,}", "▲ 5% vs média", 'kpi-subtext-positive'),
            create_kpi_card("Custo Estimado", data['custo'], "● Dentro do budget", 'kpi-subtext-neutral'),
            create_kpi_card("Taxa de Erro", f"{data['erro_pct']:.2f}%", "▼ 2% melhoria", 'kpi-subtext-positive'),
        ]
        
        # Gráfico de Tokens
        fig_tokens_new = go.Figure(data=[
            go.Bar(name='Input Tokens', x=models, y=data['tokens_in'], marker_color=colors['accent_orange'], marker_line_width=0),
            go.Bar(name='Output Tokens', x=models, y=data['tokens_out'], marker_color=colors['neon_main'], marker_line_width=0)
        ])
        fig_tokens_new.update_layout(get_plot_layout('Consumo de Tokens por Modelo'), barmode='stack')
        
        # Gráfico de Latência
        fig_latency_new = go.Figure(data=[
            go.Scatter(x=models, y=data['latencias'], mode='lines+markers',
                       line=dict(color=colors['neon_main'], width=3, shape='spline'),
                       marker=dict(size=12, color=colors['bg_body'], line=dict(width=2, color=colors['neon_main'])))
        ])
        fig_latency_new.update_layout(get_plot_layout('Latência Média (segundos)'))
        
        # Gráfico em Tempo Real
        fig_realtime_new = go.Figure(data=[
            go.Scatter(x=data['x_time'], y=data['y_reqs'], fill='tozeroy', mode='lines',
                       line=dict(color=colors['neon_main'], width=2),
                       fillcolor=colors['neon_dim'])
        ])
        fig_realtime_new.update_layout(get_plot_layout('Taxa de Requisições por Segundo'))
        
        return kpi_cards, fig_tokens_new, fig_latency_new, fig_realtime_new
    except Exception as e:
        logger.error(f"Erro ao atualizar dashboard: {str(e)}", exc_info=True)
        # Retorna valores padrão em caso de erro
        return [], go.Figure(), go.Figure(), go.Figure()

if __name__ == '__main__':
    logger.info(f"Iniciando dashboard em modo: {'DEBUG' if DEBUG_MODE else 'PRODUCTION'}")
    app.run(debug=DEBUG_MODE, host='127.0.0.1', port=8050)

# ============================================================================
# CALLBACKS DE EXPORTAÇÃO
# ============================================================================

@callback(
    Output('download-dataframe-csv', 'data'),
    Output('export-status', 'children'),
    Input('btn-export-csv', 'n_clicks'),
    Input('periodo-filter', 'value'),
    prevent_initial_call=True
)
@safe_callback
def export_csv(n_clicks, periodo):
    """Exporta dados para CSV"""
    try:
        if not n_clicks:
            return no_update, ""
        
        logger.info(f"Exportando CSV para período: {periodo}")
        filepath = export_manager.export_to_csv(periodo, user_id=1)
        
        # Ler arquivo para envio
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return dict(content=content, filename=f"metrics_{periodo}.csv"), "✓ CSV exportado!"
    except Exception as e:
        logger.error(f"Erro ao exportar CSV: {str(e)}")
        return no_update, "✗ Erro na exportação"


@callback(
    Output('download-dataframe-pdf', 'data'),
    Input('btn-export-pdf', 'n_clicks'),
    Input('periodo-filter', 'value'),
    prevent_initial_call=True
)
@safe_callback
def export_pdf(n_clicks, periodo):
    """Exporta dados para PDF"""
    try:
        if not n_clicks:
            return no_update
        
        logger.info(f"Exportando PDF para período: {periodo}")
        filepath = export_manager.export_to_pdf(periodo, user_id=1)
        
        # Retornar path do arquivo
        return dcc.send_file(filepath, filename=f"metrics_{periodo}.pdf")
    except ImportError:
        logger.warning("ReportLab não está instalado")
        return no_update
    except Exception as e:
        logger.error(f"Erro ao exportar PDF: {str(e)}")
        return no_update


@callback(
    Output('download-dataframe-json', 'data'),
    Input('btn-export-json', 'n_clicks'),
    Input('periodo-filter', 'value'),
    prevent_initial_call=True
)
@safe_callback
def export_json(n_clicks, periodo):
    """Exporta dados para JSON"""
    try:
        if not n_clicks:
            return no_update
        
        logger.info(f"Exportando JSON para período: {periodo}")
        filepath = export_manager.export_to_json(periodo, user_id=1)
        
        # Ler arquivo para envio
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return dict(content=content, filename=f"metrics_{periodo}.json")
    except Exception as e:
        logger.error(f"Erro ao exportar JSON: {str(e)}")
        return no_update
