"""
Testes para o Chat Manager e Chat Interface
v1.0.0 - P4.2 Tests
"""

import pytest
from datetime import datetime
from app.chat.chat_manager import (
    ChatManager,
    ChatSession,
    ChatMessage,
    MessageRole
)


class TestChatMessage:
    """Testes para ChatMessage"""
    
    def test_create_message(self):
        """Teste: Criar mensagem"""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Olá, como você está?"
        )
        
        assert msg.role == MessageRole.USER
        assert msg.content == "Olá, como você está?"
        assert msg.id is not None
        assert msg.timestamp is not None
    
    def test_message_to_dict(self):
        """Teste: Converter mensagem para dicionário"""
        msg = ChatMessage(
            role=MessageRole.ASSISTANT,
            content="Estou bem, obrigado!"
        )
        
        msg_dict = msg.to_dict()
        
        assert msg_dict["role"] == "assistant"
        assert msg_dict["content"] == "Estou bem, obrigado!"
        assert "id" in msg_dict
        assert "timestamp" in msg_dict
    
    def test_message_from_dict(self):
        """Teste: Criar mensagem a partir de dicionário"""
        data = {
            "id": "test-id",
            "role": "user",
            "content": "Olá",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        msg = ChatMessage.from_dict(data)
        
        assert msg.id == "test-id"
        assert msg.role == MessageRole.USER
        assert msg.content == "Olá"


class TestChatSession:
    """Testes para ChatSession"""
    
    def test_create_session(self):
        """Teste: Criar sessão de chat"""
        session = ChatSession(user_id=1, title="Primeira Conversa")
        
        assert session.user_id == 1
        assert session.title == "Primeira Conversa"
        assert session.session_id is not None
        assert len(session.messages) == 0
    
    def test_add_message_to_session(self):
        """Teste: Adicionar mensagem à sessão"""
        session = ChatSession(user_id=1)
        
        msg = session.add_message(MessageRole.USER, "Olá!")
        
        assert len(session.messages) == 1
        assert session.messages[0].content == "Olá!"
        assert session.messages[0].role == MessageRole.USER
    
    def test_auto_title_from_first_message(self):
        """Teste: Título automático baseado na primeira mensagem"""
        session = ChatSession(user_id=1, title="Nova Conversa")
        
        long_text = "Este é um texto muito longo que deve ser truncado para criar um título útil"
        session.add_message(MessageRole.USER, long_text)
        
        assert session.title != "Nova Conversa"
        assert len(session.title) <= 53  # 50 + "..."
    
    def test_get_context(self):
        """Teste: Obter contexto da conversa"""
        session = ChatSession(user_id=1)
        session.add_message(MessageRole.USER, "Primeira pergunta")
        session.add_message(MessageRole.ASSISTANT, "Primeira resposta")
        session.add_message(MessageRole.USER, "Segunda pergunta")
        
        context = session.get_context(max_messages=2)
        
        assert len(context) == 2
        assert context[0]["role"] == "assistant"
        assert context[1]["role"] == "user"
    
    def test_session_summary(self):
        """Teste: Gerar resumo da sessão"""
        session = ChatSession(user_id=1)
        session.add_message(MessageRole.USER, "Pergunta 1")
        session.add_message(MessageRole.ASSISTANT, "Resposta 1")
        
        summary = session.get_summary()
        
        assert "1 mensagens do usuário" in summary
        assert "1 respostas do assistente" in summary
    
    def test_session_to_dict(self):
        """Teste: Converter sessão para dicionário"""
        session = ChatSession(user_id=2, title="Teste")
        session.add_message(MessageRole.USER, "Teste")
        
        session_dict = session.to_dict()
        
        assert session_dict["user_id"] == 2
        assert session_dict["title"] == "Teste"
        assert session_dict["message_count"] == 1
        assert "session_id" in session_dict


class TestChatManager:
    """Testes para ChatManager"""
    
    def test_create_session(self):
        """Teste: ChatManager criar sessão"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1, title="Test Session")
        
        assert session is not None
        assert session.user_id == 1
        assert session.title == "Test Session"
    
    def test_get_session(self):
        """Teste: ChatManager obter sessão"""
        manager = ChatManager()
        
        session1 = manager.create_session(user_id=1)
        session2 = manager.get_session(session1.session_id)
        
        assert session2 is not None
        assert session2.session_id == session1.session_id
    
    def test_add_message_to_manager(self):
        """Teste: ChatManager adicionar mensagem"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1)
        msg = manager.add_message(
            session.session_id,
            MessageRole.USER,
            "Olá, mundo!"
        )
        
        assert msg is not None
        assert msg.content == "Olá, mundo!"
    
    def test_get_user_sessions(self):
        """Teste: Obter todas as sessões de um usuário"""
        manager = ChatManager()
        
        session1 = manager.create_session(user_id=1, title="Chat 1")
        session2 = manager.create_session(user_id=1, title="Chat 2")
        session3 = manager.create_session(user_id=2, title="Chat 3")
        
        user1_sessions = manager.get_user_sessions(user_id=1)
        
        assert len(user1_sessions) == 2
        assert all(s.user_id == 1 for s in user1_sessions)
    
    def test_delete_session(self):
        """Teste: Deletar sessão"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1)
        session_id = session.session_id
        
        success = manager.delete_session(session_id)
        retrieved = manager.get_session(session_id)
        
        assert success is True
        assert retrieved is None
    
    def test_archive_session(self):
        """Teste: Arquivar sessão"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1)
        
        success = manager.archive_session(session.session_id)
        archived_session = manager.get_session(session.session_id)
        
        assert success is True
        assert archived_session.is_archived is True
    
    def test_session_stats(self):
        """Teste: Obter estatísticas da sessão"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1)
        manager.add_message(session.session_id, MessageRole.USER, "Pergunta 1")
        manager.add_message(session.session_id, MessageRole.ASSISTANT, "Resposta 1")
        manager.add_message(session.session_id, MessageRole.USER, "Pergunta 2")
        
        stats = manager.get_session_stats(session.session_id)
        
        assert stats["total_messages"] == 3
        assert stats["user_messages"] == 2
        assert stats["assistant_messages"] == 1
    
    def test_export_session_json(self):
        """Teste: Exportar sessão em JSON"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1, title="Export Test")
        manager.add_message(session.session_id, MessageRole.USER, "Teste")
        
        exported = manager.export_session(session.session_id, format="json")
        
        assert exported is not None
        assert "Export Test" in exported
        assert "Teste" in exported
    
    def test_export_session_markdown(self):
        """Teste: Exportar sessão em Markdown"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1, title="MD Test")
        manager.add_message(session.session_id, MessageRole.USER, "Pergunta")
        manager.add_message(session.session_id, MessageRole.ASSISTANT, "Resposta")
        
        exported = manager.export_session(session.session_id, format="markdown")
        
        assert exported is not None
        assert "# MD Test" in exported
        assert "👤 Você" in exported
        assert "🤖 Assistente" in exported
    
    def test_export_session_text(self):
        """Teste: Exportar sessão em Texto"""
        manager = ChatManager()
        
        session = manager.create_session(user_id=1, title="Text Test")
        manager.add_message(session.session_id, MessageRole.USER, "Teste de texto")
        
        exported = manager.export_session(session.session_id, format="text")
        
        assert exported is not None
        assert "Text Test" in exported
        assert "VOCÊ" in exported
        assert "Teste de texto" in exported


class TestChatIntegration:
    """Testes de integração"""
    
    def test_full_conversation_flow(self):
        """Teste: Fluxo completo de conversa"""
        manager = ChatManager()
        
        # Criar sessão
        session = manager.create_session(user_id=1, title="Integration Test")
        
        # Adicionar múltiplas mensagens
        user_msgs = ["Olá!", "Como você funciona?", "Muito bom!"]
        assistant_msgs = ["Oi! Tudo bem?", "Sou um assistente de IA.", "Fico feliz em ajudar!"]
        
        for user_msg, asst_msg in zip(user_msgs, assistant_msgs):
            manager.add_message(session.session_id, MessageRole.USER, user_msg)
            manager.add_message(session.session_id, MessageRole.ASSISTANT, asst_msg)
        
        # Verificar
        stats = manager.get_session_stats(session.session_id)
        
        assert stats["total_messages"] == 6
        assert stats["user_messages"] == 3
        assert stats["assistant_messages"] == 3
    
    def test_multiple_users(self):
        """Teste: Múltiplos usuários com sessões independentes"""
        manager = ChatManager()
        
        # Usuário 1
        user1_session = manager.create_session(user_id=1, title="User 1 Chat")
        manager.add_message(user1_session.session_id, MessageRole.USER, "Olá da user 1")
        
        # Usuário 2
        user2_session = manager.create_session(user_id=2, title="User 2 Chat")
        manager.add_message(user2_session.session_id, MessageRole.USER, "Olá da user 2")
        
        # Verificar isolamento
        user1_sessions = manager.get_user_sessions(user_id=1)
        user2_sessions = manager.get_user_sessions(user_id=2)
        
        assert len(user1_sessions) == 1
        assert len(user2_sessions) == 1
        assert user1_sessions[0].session_id != user2_sessions[0].session_id
