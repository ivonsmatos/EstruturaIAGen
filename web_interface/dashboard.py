# Dashboard de Monitoramento usando Dash
import dash
from dash import dcc, html
import plotly.express as px
from web_interface.database import Database

app = dash.Dash(__name__)

# Obter dados do banco de dados
db = Database()
logs = db.fetch_logs()

# Preparar dados para visualização
data = {
    "Prompt": [log[1] for log in logs],
    "Response": [log[2] for log in logs],
    "Timestamp": [log[3] for log in logs]
}

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Monitoramento"),
    dcc.Graph(
        id="response-length",
        figure=px.bar(
            x=data["Prompt"],
            y=[len(response) for response in data["Response"]],
            labels={"x": "Prompt", "y": "Tamanho da Resposta"},
            title="Tamanho das Respostas"
        )
    ),
    dcc.Graph(
        id="response-timestamp",
        figure=px.scatter(
            x=data["Timestamp"],
            y=[len(response) for response in data["Response"]],
            labels={"x": "Timestamp", "y": "Tamanho da Resposta"},
            title="Respostas ao Longo do Tempo"
        )
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)