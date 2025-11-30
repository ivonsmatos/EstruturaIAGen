"""
Chat Module - Sistema de conversa interativa com suporte a contexto e histórico
v1.0.0 - P4.2 Chat Interface Implementation

Componentes:
- ChatManager: Gerenciamento de sessões de conversa
- ChatSession: Representação de uma conversa
- ChatMessage: Representação de mensagens
- ChatUI: Interface Dash para o chat
"""

from app.chat.chat_manager import (
    ChatManager,
    ChatSession,
    ChatMessage,
    MessageRole,
    chat_manager
)

from app.chat.chat_ui import (
    create_chat_ui,
    create_message_bubble,
    register_chat_callbacks
)

__all__ = [
    "ChatManager",
    "ChatSession",
    "ChatMessage",
    "MessageRole",
    "chat_manager",
    "create_chat_ui",
    "create_message_bubble",
    "register_chat_callbacks"
]
