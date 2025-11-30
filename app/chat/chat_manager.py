"""
Chat Manager - Sistema de conversa interativo com memória de contexto
Suporta múltiplas conversas por usuário com persistência em banco de dados
v1.0.0 - P4.2 Chat Interface Implementation
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict, field
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class MessageRole(Enum):
    """Roles de mensagem no chat"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass
class ChatMessage:
    """Representa uma mensagem individual no chat"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole = MessageRole.USER
    content: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "id": self.id,
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatMessage":
        """Cria a partir de dicionário"""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            role=MessageRole(data.get("role", "user")),
            content=data.get("content", ""),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {})
        )


@dataclass
class ChatSession:
    """Representa uma sessão de conversa"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int = 1
    title: str = "Nova Conversa"
    messages: List[ChatMessage] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_archived: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "title": self.title,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
            "is_archived": self.is_archived,
            "message_count": len(self.messages)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        """Cria a partir de dicionário"""
        messages = [ChatMessage.from_dict(msg) for msg in data.get("messages", [])]
        return cls(
            session_id=data.get("session_id", str(uuid.uuid4())),
            user_id=data.get("user_id", 1),
            title=data.get("title", "Nova Conversa"),
            messages=messages,
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat()),
            metadata=data.get("metadata", {}),
            is_archived=data.get("is_archived", False)
        )
    
    def add_message(self, role: MessageRole, content: str, metadata: Optional[Dict] = None) -> ChatMessage:
        """Adiciona uma mensagem à sessão"""
        msg = ChatMessage(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.updated_at = datetime.utcnow().isoformat()
        
        # Atualizar título se vazio (baseado na primeira mensagem do usuário)
        if self.title == "Nova Conversa" and role == MessageRole.USER:
            self.title = content[:50].replace("\n", " ") + ("..." if len(content) > 50 else "")
        
        logger.info(f"✓ Mensagem adicionada à sessão {self.session_id}: {role.value}")
        return msg
    
    def get_context(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Retorna o contexto das últimas mensagens para LLM"""
        recent_messages = self.messages[-max_messages:]
        return [{"role": msg.role.value, "content": msg.content} for msg in recent_messages]
    
    def get_summary(self) -> str:
        """Gera um resumo da conversa"""
        if not self.messages:
            return "Conversa vazia"
        
        user_messages = [msg for msg in self.messages if msg.role == MessageRole.USER]
        assistant_messages = [msg for msg in self.messages if msg.role == MessageRole.ASSISTANT]
        
        return (
            f"Conversa com {len(user_messages)} mensagens do usuário, "
            f"{len(assistant_messages)} respostas do assistente. "
            f"Duração: {self._calculate_duration()}"
        )
    
    def _calculate_duration(self) -> str:
        """Calcula duração da conversa"""
        if len(self.messages) < 2:
            return "< 1 minuto"
        
        first_time = datetime.fromisoformat(self.messages[0].timestamp)
        last_time = datetime.fromisoformat(self.messages[-1].timestamp)
        duration = last_time - first_time
        
        if duration.total_seconds() < 60:
            return "< 1 minuto"
        elif duration.total_seconds() < 3600:
            return f"{int(duration.total_seconds() / 60)} minutos"
        else:
            return f"{int(duration.total_seconds() / 3600)} horas"


class ChatManager:
    """Gerenciador central de conversas de chat"""
    
    def __init__(self, cache_manager=None, db_connection=None):
        """
        Inicializa o gerenciador de chat
        
        Args:
            cache_manager: Gerenciador de cache para sessões ativas
            db_connection: Conexão com banco de dados para persistência
        """
        self.cache_manager = cache_manager
        self.db_connection = db_connection
        self.active_sessions: Dict[str, ChatSession] = {}
        logger.info("✓ ChatManager inicializado")
    
    def create_session(self, user_id: int, title: str = "Nova Conversa") -> ChatSession:
        """
        Cria uma nova sessão de conversa
        
        Args:
            user_id: ID do usuário
            title: Título da conversa
            
        Returns:
            ChatSession: Sessão criada
        """
        session = ChatSession(user_id=user_id, title=title)
        self.active_sessions[session.session_id] = session
        
        # Cache da sessão
        if self.cache_manager:
            cache_key = f"chat_session:{session.session_id}"
            self.cache_manager.set(cache_key, session.to_dict(), ttl=3600)
        
        logger.info(f"✓ Sessão de chat criada: {session.session_id} (usuário: {user_id})")
        return session
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Obtém uma sessão pelo ID"""
        # Verificar cache primeiro
        if self.cache_manager:
            cache_key = f"chat_session:{session_id}"
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                return ChatSession.from_dict(cached_data)
        
        # Verificar sessões ativas
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        logger.warning(f"✗ Sessão não encontrada: {session_id}")
        return None
    
    def add_message(self, session_id: str, role: MessageRole, content: str, 
                   metadata: Optional[Dict] = None) -> Optional[ChatMessage]:
        """
        Adiciona uma mensagem a uma sessão
        
        Args:
            session_id: ID da sessão
            role: Role da mensagem (user/assistant)
            content: Conteúdo da mensagem
            metadata: Metadados opcionais
            
        Returns:
            ChatMessage: Mensagem adicionada ou None se sessão não existe
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        message = session.add_message(role, content, metadata)
        
        # Atualizar cache
        if self.cache_manager:
            cache_key = f"chat_session:{session_id}"
            self.cache_manager.set(cache_key, session.to_dict(), ttl=3600)
        
        return message
    
    def get_user_sessions(self, user_id: int, limit: int = 20) -> List[ChatSession]:
        """Obtém todas as sessões de um usuário"""
        sessions = [
            session for session in self.active_sessions.values()
            if session.user_id == user_id and not session.is_archived
        ]
        return sorted(sessions, key=lambda s: s.updated_at, reverse=True)[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """Deleta uma sessão"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
            # Limpar cache
            if self.cache_manager:
                cache_key = f"chat_session:{session_id}"
                self.cache_manager.invalidate(cache_key)
            
            logger.info(f"✓ Sessão deletada: {session_id}")
            return True
        
        return False
    
    def archive_session(self, session_id: str) -> bool:
        """Arquiva uma sessão"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.is_archived = True
        session.updated_at = datetime.utcnow().isoformat()
        
        # Atualizar cache
        if self.cache_manager:
            cache_key = f"chat_session:{session_id}"
            self.cache_manager.set(cache_key, session.to_dict(), ttl=3600)
        
        logger.info(f"✓ Sessão arquivada: {session_id}")
        return True
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de uma sessão"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        user_messages = len([m for m in session.messages if m.role == MessageRole.USER])
        assistant_messages = len([m for m in session.messages if m.role == MessageRole.ASSISTANT])
        total_chars = sum(len(m.content) for m in session.messages)
        
        return {
            "session_id": session_id,
            "total_messages": len(session.messages),
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_characters": total_chars,
            "average_message_length": total_chars / len(session.messages) if session.messages else 0,
            "duration": session._calculate_duration(),
            "created_at": session.created_at,
            "updated_at": session.updated_at
        }
    
    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """
        Exporta uma sessão em diferentes formatos
        
        Args:
            session_id: ID da sessão
            format: Formato (json, markdown, text)
            
        Returns:
            String com o conteúdo exportado
        """
        session = self.get_session(session_id)
        if not session:
            return None
        
        if format == "json":
            return json.dumps(session.to_dict(), indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            md = f"# {session.title}\n\n"
            md += f"**Criado em**: {session.created_at}\n"
            md += f"**Atualizado em**: {session.updated_at}\n\n"
            
            for msg in session.messages:
                role_label = "👤 Você" if msg.role == MessageRole.USER else "🤖 Assistente"
                md += f"## {role_label}\n\n{msg.content}\n\n"
            
            return md
        
        elif format == "text":
            text = f"Conversa: {session.title}\n"
            text += f"Criado em: {session.created_at}\n\n"
            
            for msg in session.messages:
                role_label = "VOCÊ" if msg.role == MessageRole.USER else "ASSISTENTE"
                text += f"[{role_label}] {msg.timestamp}\n{msg.content}\n\n"
            
            return text
        
        return None


# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

chat_manager = ChatManager()

__all__ = [
    "ChatManager",
    "ChatSession",
    "ChatMessage",
    "MessageRole",
    "chat_manager"
]
