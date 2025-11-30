# Dashboard de Monitoramento usando Dash
import sys
import os

# Adiciona o diretório raiz do projeto ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../..')

from dash import Dash, dcc, html
import plotly.express as px
from web_interface.database import Database
from flask_cors import CORS
import pandas as pd
from web_interface.app import app as flask_app

# Inicializar o Dash
app = Dash(__name__, url_base_pathname='/dashboard/')
CORS(app.server)

# Obter dados do banco de dados
db = Database()
logs = db.fetch_logs()

# Preparar dados para visualização
data = {
    "Prompt": [log[1] for log in logs],
    "Response": [log[2] for log in logs],
    "Timestamp": [log[3] for log in logs]
}

# Converte os dados em um DataFrame para evitar problemas
logs_df = pd.DataFrame(data)

# Layout do dashboard
app.layout = html.Div([
    html.H1("Dashboard de Monitoramento"),
    dcc.Graph(
        id="response-length",
        figure=px.bar(
            logs_df,
            x="Prompt",
            y=logs_df["Response"].apply(len),
            labels={"x": "Prompt", "y": "Tamanho da Resposta"},
            title="Tamanho das Respostas"
        )
    ),
    dcc.Graph(
        id="response-timestamp",
        figure=px.scatter(
            logs_df,
            x="Timestamp",
            y=logs_df["Response"].apply(len),
            labels={"x": "Timestamp", "y": "Tamanho da Resposta"},
            title="Respostas ao Longo do Tempo"
        )
    )
])

if __name__ == "__main__":
    app.run_server(debug=True)