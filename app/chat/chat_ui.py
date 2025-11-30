"""
Chat UI Component - Interface interativa de chat para Dash
Suporta conversas em tempo real com histórico persistente
v1.0.0 - P4.2 Chat Interface UI
"""

import logging
from typing import List, Dict, Any, Tuple
import dash
from dash import dcc, html, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from datetime import datetime

from app.chat.chat_manager import (
    ChatManager,
    MessageRole,
    chat_manager
)

logger = logging.getLogger(__name__)


def create_chat_ui() -> html.Div:
    """
    Cria a interface de usuário para o chat
    
    Returns:
        html.Div: Layout do chat
    """
    return html.Div(
        id="chat-container",
        style={
            "display": "flex",
            "flexDirection": "column",
            "height": "80vh",
            "backgroundColor": "#0a0e27",
            "borderRadius": "8px",
            "overflow": "hidden"
        },
        children=[
            # Header do chat
            html.Div(
                style={
                    "padding": "15px",
                    "backgroundColor": "#1a1f3a",
                    "borderBottom": "1px solid #bff244",
                    "color": "#bff244"
                },
                children=[
                    html.Div(
                        style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"},
                        children=[
                            html.H4("💬 Chat Interativo", style={"margin": 0}),
                            html.Div(
                                style={"display": "flex", "gap": "10px"},
                                children=[
                                    dbc.Button(
                                        "Nova Conversa",
                                        id="btn-new-chat",
                                        size="sm",
                                        color="warning",
                                        outline=True
                                    ),
                                    dbc.Button(
                                        "Exportar",
                                        id="btn-export-chat",
                                        size="sm",
                                        color="info",
                                        outline=True
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            ),
            
            # Área de mensagens (scrollável)
            html.Div(
                id="chat-messages-container",
                style={
                    "flex": "1",
                    "overflowY": "auto",
                    "padding": "20px",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "15px"
                },
                children=[]
            ),
            
            # Input de mensagem
            html.Div(
                style={
                    "padding": "15px",
                    "backgroundColor": "#1a1f3a",
                    "borderTop": "1px solid #bff244"
                },
                children=[
                    html.Div(
                        style={"display": "flex", "gap": "10px"},
                        children=[
                            dcc.Input(
                                id="chat-input",
                                type="text",
                                placeholder="Digite sua mensagem aqui...",
                                style={
                                    "flex": "1",
                                    "padding": "10px 15px",
                                    "backgroundColor": "#0a0e27",
                                    "color": "#fff",
                                    "border": "1px solid #bff244",
                                    "borderRadius": "4px",
                                    "fontSize": "14px"
                                },
                                n_submit=0
                            ),
                            dbc.Button(
                                "Enviar",
                                id="btn-send",
                                color="warning",
                                style={"width": "100px"}
                            )
                        ]
                    )
                ]
            ),
            
            # Store para armazenar sessão atual
            dcc.Store(id="current-session-store", data={"session_id": None}),
        ]
    )


def create_message_bubble(content: str, role: str, timestamp: str) -> html.Div:
    """
    Cria uma bolha de mensagem no chat
    
    Args:
        content: Conteúdo da mensagem
        role: Role (user/assistant)
        timestamp: Timestamp da mensagem
        
    Returns:
        html.Div: Elemento da mensagem
    """
    is_user = role == "user"
    
    return html.Div(
        style={
            "display": "flex",
            "justifyContent": "flex-end" if is_user else "flex-start",
            "marginBottom": "10px"
        },
        children=[
            html.Div(
                style={
                    "maxWidth": "70%",
                    "padding": "12px 15px",
                    "backgroundColor": "#bff244" if is_user else "#2a3055",
                    "color": "#000" if is_user else "#fff",
                    "borderRadius": "8px",
                    "wordWrap": "break-word"
                },
                children=[
                    html.Div(
                        content,
                        style={"marginBottom": "5px"}
                    ),
                    html.Small(
                        timestamp,
                        style={
                            "opacity": 0.7,
                            "fontSize": "11px",
                            "display": "block",
                            "textAlign": "right"
                        }
                    )
                ]
            )
        ]
    )


def register_chat_callbacks(app):
    """
    Registra os callbacks do chat
    
    Args:
        app: Aplicação Dash
    """
    
    @callback(
        Output("chat-messages-container", "children"),
        Output("current-session-store", "data"),
        Output("chat-input", "value"),
        Input("btn-send", "n_clicks"),
        Input("btn-new-chat", "n_clicks"),
        Input("chat-input", "n_submit"),
        State("chat-input", "value"),
        State("current-session-store", "data"),
        prevent_initial_call=True
    )
    def handle_chat_interaction(
        send_clicks, new_chat_clicks, input_submit,
        input_value, session_data
    ):
        """Manipula interações do chat"""
        
        # Determinar qual botão foi clicado
        triggered_id = ctx.triggered_id if ctx.triggered else None
        
        # Nova conversa
        if triggered_id == "btn-new-chat":
            session = chat_manager.create_session(user_id=1, title="Nova Conversa")
            return [], {"session_id": session.session_id}, ""
        
        # Enviar mensagem
        if triggered_id in ["btn-send", "chat-input"] and input_value:
            session_id = session_data.get("session_id")
            
            # Se não há sessão, criar uma
            if not session_id:
                session = chat_manager.create_session(user_id=1)
                session_id = session.session_id
            
            # Adicionar mensagem do usuário
            chat_manager.add_message(
                session_id,
                MessageRole.USER,
                input_value
            )
            
            # Simular resposta do assistente (substituir com LLM real)
            assistant_response = f"Você disse: '{input_value}'. Essa é uma resposta simulada."
            chat_manager.add_message(
                session_id,
                MessageRole.ASSISTANT,
                assistant_response
            )
            
            # Renderizar mensagens
            session = chat_manager.get_session(session_id)
            messages = []
            
            if session:
                for msg in session.messages:
                    bubble = create_message_bubble(
                        msg.content,
                        msg.role.value,
                        msg.timestamp[-8:]  # HH:MM:SS
                    )
                    messages.append(bubble)
            
            return messages, {"session_id": session_id}, ""
        
        # Carregar mensagens existentes
        session_id = session_data.get("session_id")
        if session_id:
            session = chat_manager.get_session(session_id)
            messages = []
            
            if session:
                for msg in session.messages:
                    bubble = create_message_bubble(
                        msg.content,
                        msg.role.value,
                        msg.timestamp[-8:]
                    )
                    messages.append(bubble)
            
            return messages, session_data, ""
        
        return [], session_data, ""
    
    @callback(
        Output("chat-input", "placeholder"),
        Input("btn-export-chat", "n_clicks"),
        State("current-session-store", "data"),
        prevent_initial_call=True
    )
    def export_chat(export_clicks, session_data):
        """Exporta a conversa"""
        session_id = session_data.get("session_id")
        
        if session_id:
            markdown_content = chat_manager.export_session(session_id, format="markdown")
            if markdown_content:
                logger.info(f"✓ Conversa exportada: {session_id}")
                return "Conversa exportada! 📥"
        
        return "Digite sua mensagem aqui..."


__all__ = [
    "create_chat_ui",
    "create_message_bubble",
    "register_chat_callbacks"
]
