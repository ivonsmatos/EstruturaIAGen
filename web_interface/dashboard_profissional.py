import dash
from dash import dcc, html, callback, Input, Output
import plotly.graph_objects as go
import numpy as np

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

# App Dash
app = dash.Dash(__name__)

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
    """Gera dados diferentes baseado no período selecionado"""
    np.random.seed(42)  # Para consistência
    
    if periodo == '24h':
        multiplier = 1.0
        requisicoes = 1500
        erro_pct = 1.25
    elif periodo == '7d':
        multiplier = 2.5
        requisicoes = 8000
        erro_pct = 1.15
    elif periodo == '30d':
        multiplier = 4.0
        requisicoes = 32000
        erro_pct = 1.10
    else:  # 'all'
        multiplier = 6.0
        requisicoes = 95000
        erro_pct = 1.05
    
    tokens_in = [int(350 * multiplier), int(200 * multiplier), int(450 * multiplier)]
    tokens_out = [int(500 * multiplier), int(600 * multiplier), int(400 * multiplier)]
    latencias = [1.2 / multiplier * 0.5, 0.8 / multiplier * 0.5, 0.4 / multiplier * 0.5]
    custo = f"${120.50 * multiplier:.2f}"
    
    # Gráfico em tempo real
    x_time = list(range(30))
    y_reqs = [10 * multiplier + np.random.normal(0, 2) for _ in range(30)]
    y_reqs = [max(5, r) for r in y_reqs]
    y_reqs = [y_reqs[i] + (i * 2 * multiplier / 2) for i in range(len(y_reqs))]
    
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
        # Header com Filtro e Botão
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
            
            # Botão Exportar em Outline
            html.Button(
                "↓ Exportar Relatório",
                className='export-button'
            )
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
    Input('periodo-filter', 'value')
)
def update_dashboard(selected_periodo):
    """Atualiza todos os gráficos e KPIs quando o período é alterado"""
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

if __name__ == '__main__':
    app.run(debug=True)
