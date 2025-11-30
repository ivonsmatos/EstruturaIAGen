"""
Advanced Analytics Engine
========================

Provides comprehensive user behavior and platform analytics.
Tracks events, user sessions, page metrics, and engagement patterns.

Version: 3.0.0
Author: AI Dashboard Team
License: MIT
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import logging
import json
from enum import Enum
from collections import defaultdict, Counter
import hashlib
import uuid

# Configure logging
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event types tracked by analytics"""
    PAGE_VIEW = "page_view"
    CLICK = "click"
    EXPORT = "export"
    THEME_CHANGE = "theme_change"
    LANGUAGE_CHANGE = "language_change"
    FILTER_APPLY = "filter_apply"
    DATA_DOWNLOAD = "data_download"
    REPORT_GENERATE = "report_generate"
    ERROR = "error"
    CUSTOM = "custom"


@dataclass
class UserSession:
    """Represents a user session"""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_minutes: float = 0.0
    page_views: int = 0
    events: List['AnalyticsEvent'] = field(default_factory=list)
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'page_views': self.page_views,
            'event_count': len(self.events),
            'user_agent': self.user_agent,
            'ip_address': self.ip_address
        }


@dataclass
class AnalyticsEvent:
    """Represents an analytics event"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType = EventType.CUSTOM
    timestamp: datetime = field(default_factory=datetime.now)
    session_id: str = ""
    user_id: Optional[str] = None
    page: str = ""
    source: str = ""
    target: str = ""
    value: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'timestamp': self.timestamp.isoformat(),
            'session_id': self.session_id,
            'user_id': self.user_id,
            'page': self.page,
            'source': self.source,
            'target': self.target,
            'value': self.value,
            'metadata': self.metadata
        }


class AdvancedAnalyticsEngine:
    """
    Tracks and analyzes user behavior and platform usage.
    
    Features:
    - User session tracking
    - Event collection and analysis
    - Behavior patterns recognition
    - Engagement metrics
    - Funnel analysis
    - Heatmap data generation
    - Real-time dashboards
    
    Example:
        >>> analytics = AdvancedAnalyticsEngine()
        >>> session = analytics.create_session('user123')
        >>> analytics.track_event(
        ...     session.session_id,
        ...     EventType.CLICK,
        ...     page='dashboard',
        ...     target='export_button'
        ... )
    """
    
    def __init__(self, max_sessions: int = 10000, retention_days: int = 30):
        """
        Initialize analytics engine.
        
        Args:
            max_sessions: Maximum sessions to store in memory
            retention_days: Days to retain analytics data
        """
        self.max_sessions = max_sessions
        self.retention_days = retention_days
        self.sessions: Dict[str, UserSession] = {}
        self.events: List[AnalyticsEvent] = []
        self.current_session: Optional[UserSession] = None
        self.logger = logging.getLogger(__name__)
    
    def create_session(
        self,
        user_id: Optional[str] = None,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> UserSession:
        """
        Create a new user session.
        
        Args:
            user_id: Optional user identifier
            user_agent: Browser user agent string
            ip_address: User IP address
            
        Returns:
            New UserSession instance
        """
        try:
            session = UserSession(
                user_id=user_id,
                user_agent=user_agent,
                ip_address=self._anonymize_ip(ip_address) if ip_address else None
            )
            
            # Store session
            if len(self.sessions) >= self.max_sessions:
                self._cleanup_old_sessions()
            
            self.sessions[session.session_id] = session
            self.current_session = session
            
            self.logger.info(f"Session created: {session.session_id}")
            return session
        
        except Exception as e:
            self.logger.error(f"Error creating session: {str(e)}")
            raise
    
    def track_event(
        self,
        session_id: str,
        event_type: EventType,
        page: str = "",
        source: str = "",
        target: str = "",
        value: Optional[str] = None,
        metadata: Dict[str, Any] = None
    ) -> AnalyticsEvent:
        """
        Track an event.
        
        Args:
            session_id: Session identifier
            event_type: Type of event
            page: Current page
            source: Event source
            target: Event target
            value: Optional event value
            metadata: Additional metadata
            
        Returns:
            Created AnalyticsEvent
            
        Example:
            >>> analytics.track_event(
            ...     session_id='sess_123',
            ...     event_type=EventType.EXPORT,
            ...     page='dashboard',
            ...     target='csv_export',
            ...     metadata={'format': 'csv', 'records': 1000}
            ... )
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                self.logger.warning(f"Session not found: {session_id}")
                return None
            
            event = AnalyticsEvent(
                event_type=event_type,
                session_id=session_id,
                user_id=session.user_id,
                page=page,
                source=source,
                target=target,
                value=value,
                metadata=metadata or {}
            )
            
            # Add to session and global events
            session.events.append(event)
            self.events.append(event)
            
            # Update session metrics
            if event_type == EventType.PAGE_VIEW:
                session.page_views += 1
            
            self.logger.debug(f"Event tracked: {event_type.value}")
            return event
        
        except Exception as e:
            self.logger.error(f"Error tracking event: {str(e)}")
            return None
    
    def end_session(self, session_id: str) -> None:
        """
        End a user session.
        
        Args:
            session_id: Session identifier
        """
        try:
            session = self.sessions.get(session_id)
            if session and not session.end_time:
                session.end_time = datetime.now()
                session.duration_minutes = (
                    session.end_time - session.start_time
                ).total_seconds() / 60
                self.logger.info(f"Session ended: {session_id}")
        
        except Exception as e:
            self.logger.error(f"Error ending session: {str(e)}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with session statistics
        """
        try:
            session = self.sessions.get(session_id)
            if not session:
                return {}
            
            return {
                **session.to_dict(),
                'event_types': Counter(
                    e.event_type.value for e in session.events
                ).to_dict(),
                'pages_visited': set(e.page for e in session.events)
            }
        
        except Exception as e:
            self.logger.error(f"Error getting session stats: {str(e)}")
            return {}
    
    def get_user_engagement(self, user_id: str = None) -> Dict[str, Any]:
        """
        Calculate user engagement metrics.
        
        Args:
            user_id: Optional user identifier (all users if None)
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            sessions = [
                s for s in self.sessions.values()
                if user_id is None or s.user_id == user_id
            ]
            
            if not sessions:
                return {}
            
            total_duration = sum(s.duration_minutes for s in sessions if s.duration_minutes)
            total_events = sum(len(s.events) for s in sessions)
            total_page_views = sum(s.page_views for s in sessions)
            
            return {
                'total_sessions': len(sessions),
                'total_duration_minutes': round(total_duration, 2),
                'total_events': total_events,
                'total_page_views': total_page_views,
                'avg_session_duration': round(
                    total_duration / len(sessions) if sessions else 0, 2
                ),
                'avg_events_per_session': round(
                    total_events / len(sessions) if sessions else 0, 2
                ),
                'avg_pages_per_session': round(
                    total_page_views / len(sessions) if sessions else 0, 2
                )
            }
        
        except Exception as e:
            self.logger.error(f"Error calculating engagement: {str(e)}")
            return {}
    
    def get_popular_pages(self, limit: int = 10) -> List[Tuple[str, int]]:
        """
        Get most viewed pages.
        
        Args:
            limit: Maximum number of pages to return
            
        Returns:
            List of (page, view_count) tuples sorted by views
        """
        try:
            page_views = Counter(e.page for e in self.events if e.page)
            return page_views.most_common(limit)
        
        except Exception as e:
            self.logger.error(f"Error getting popular pages: {str(e)}")
            return []
    
    def get_event_funnel(self, events: List[EventType]) -> Dict[str, Any]:
        """
        Analyze event funnel/conversion path.
        
        Args:
            events: Sequence of events to track
            
        Returns:
            Dictionary with funnel analysis
        """
        try:
            funnel_data = {e.value: 0 for e in events}
            
            for session in self.sessions.values():
                event_types = [e.event_type for e in session.events]
                
                for i, event_type in enumerate(events):
                    if event_type in event_types:
                        idx = event_types.index(event_type)
                        if i == 0 or event_types[:idx][-1:] == [events[i-1]]:
                            funnel_data[event_type.value] += 1
            
            # Calculate conversion rates
            conversions = {}
            total = funnel_data[events[0].value] if funnel_data else 0
            
            for event in events:
                count = funnel_data[event.value]
                conversions[event.value] = {
                    'count': count,
                    'conversion_rate': round(
                        (count / total * 100) if total > 0 else 0, 2
                    )
                }
            
            return conversions
        
        except Exception as e:
            self.logger.error(f"Error analyzing funnel: {str(e)}")
            return {}
    
    def get_behavior_segments(self) -> Dict[str, List[str]]:
        """
        Segment users by behavior patterns.
        
        Returns:
            Dictionary with behavior segments
        """
        try:
            segments = defaultdict(list)
            
            for session_id, session in self.sessions.items():
                # Define segments based on behavior
                if session.duration_minutes > 30:
                    segments['power_users'].append(session_id)
                elif session.duration_minutes > 10:
                    segments['engaged_users'].append(session_id)
                elif session.page_views > 5:
                    segments['explorers'].append(session_id)
                else:
                    segments['casual_visitors'].append(session_id)
                
                # Event-based segments
                event_types = set(e.event_type for e in session.events)
                if EventType.EXPORT in event_types:
                    segments['exporters'].append(session_id)
                if EventType.THEME_CHANGE in event_types:
                    segments['customizers'].append(session_id)
            
            return {k: v for k, v in segments.items()}
        
        except Exception as e:
            self.logger.error(f"Error segmenting behavior: {str(e)}")
            return {}
    
    def _anonymize_ip(self, ip: str) -> str:
        """
        Anonymize IP address (keep first 3 octets for IPv4).
        
        Args:
            ip: IP address string
            
        Returns:
            Anonymized IP
        """
        try:
            parts = ip.split('.')
            if len(parts) == 4:
                return '.'.join(parts[:3]) + '.0'
            return hashlib.sha256(ip.encode()).hexdigest()[:16]
        except:
            return "anonymized"
    
    def _cleanup_old_sessions(self) -> None:
        """Remove old sessions to prevent memory overflow"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            sessions_to_delete = [
                sid for sid, session in self.sessions.items()
                if session.start_time < cutoff_date
            ]
            
            for sid in sessions_to_delete:
                del self.sessions[sid]
            
            self.logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
        
        except Exception as e:
            self.logger.error(f"Error cleaning up sessions: {str(e)}")
    
    def export_analytics(self, format: str = "json") -> str:
        """
        Export analytics data.
        
        Args:
            format: Export format ('json')
            
        Returns:
            Exported analytics as string
        """
        try:
            data = {
                'sessions': [s.to_dict() for s in self.sessions.values()],
                'events': [e.to_dict() for e in self.events],
                'export_date': datetime.now().isoformat()
            }
            
            return json.dumps(data, indent=2, ensure_ascii=False)
        
        except Exception as e:
            self.logger.error(f"Error exporting analytics: {str(e)}")
            return "{}"
    
    def get_overview(self) -> Dict[str, Any]:
        """
        Get overview of all analytics.
        
        Returns:
            Dictionary with comprehensive analytics overview
        """
        try:
            return {
                'total_sessions': len(self.sessions),
                'total_events': len(self.events),
                'active_sessions': sum(
                    1 for s in self.sessions.values() if s.end_time is None
                ),
                'total_users': len(set(s.user_id for s in self.sessions.values())),
                'engagement': self.get_user_engagement(),
                'popular_pages': self.get_popular_pages(5),
                'behavior_segments': self.get_behavior_segments(),
                'retention_days': self.retention_days
            }
        
        except Exception as e:
            self.logger.error(f"Error getting overview: {str(e)}")
            return {}


# Export public API
__all__ = [
    'AdvancedAnalyticsEngine',
    'UserSession',
    'AnalyticsEvent',
    'EventType'
]
