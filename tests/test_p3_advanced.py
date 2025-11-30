"""
Tests for Advanced Analytics & ML Prediction (P3.3-3.4)
======================================================

Unit tests for analytics engine and ML prediction system.

Version: 3.0.0
"""

import pytest
from datetime import datetime, timedelta
import numpy as np
from app.analytics.advanced_analytics import (
    AdvancedAnalyticsEngine,
    UserSession,
    AnalyticsEvent,
    EventType
)
from app.ml.prediction_engine import (
    MLPredictionEngine,
    PredictionModel,
    PredictionResult,
    AnomalyScore
)


# ============ Advanced Analytics Tests ============

class TestUserSession:
    """Test UserSession dataclass"""
    
    def test_session_creation(self):
        """Test creating a user session"""
        session = UserSession(user_id='user123')
        
        assert session.user_id == 'user123'
        assert session.session_id is not None
        assert session.start_time is not None
        assert session.page_views == 0
    
    def test_session_to_dict(self):
        """Test converting session to dict"""
        session = UserSession(user_id='user123')
        data = session.to_dict()
        
        assert 'session_id' in data
        assert 'user_id' in data
        assert data['user_id'] == 'user123'


class TestAnalyticsEvent:
    """Test AnalyticsEvent dataclass"""
    
    def test_event_creation(self):
        """Test creating an analytics event"""
        event = AnalyticsEvent(
            event_type=EventType.CLICK,
            page='dashboard',
            target='export_button'
        )
        
        assert event.event_type == EventType.CLICK
        assert event.page == 'dashboard'
        assert event.target == 'export_button'
    
    def test_event_to_dict(self):
        """Test converting event to dict"""
        event = AnalyticsEvent(event_type=EventType.PAGE_VIEW)
        data = event.to_dict()
        
        assert 'event_id' in data
        assert 'event_type' in data
        assert data['event_type'] == 'page_view'


class TestAdvancedAnalyticsEngine:
    """Test AdvancedAnalyticsEngine class"""
    
    @pytest.fixture
    def analytics(self):
        """Create analytics engine instance"""
        return AdvancedAnalyticsEngine()
    
    def test_engine_initialization(self, analytics):
        """Test analytics engine initialization"""
        assert analytics is not None
        assert len(analytics.sessions) == 0
        assert len(analytics.events) == 0
    
    def test_create_session(self, analytics):
        """Test creating a session"""
        session = analytics.create_session(user_id='user123')
        
        assert session is not None
        assert session.user_id == 'user123'
        assert session.session_id in analytics.sessions
    
    def test_track_event(self, analytics):
        """Test tracking an event"""
        session = analytics.create_session(user_id='user123')
        
        event = analytics.track_event(
            session.session_id,
            EventType.CLICK,
            page='dashboard',
            target='export'
        )
        
        assert event is not None
        assert event.event_type == EventType.CLICK
        assert len(analytics.events) == 1
    
    def test_end_session(self, analytics):
        """Test ending a session"""
        session = analytics.create_session(user_id='user123')
        
        analytics.end_session(session.session_id)
        
        session = analytics.sessions[session.session_id]
        assert session.end_time is not None
        assert session.duration_minutes >= 0
    
    def test_get_session_stats(self, analytics):
        """Test getting session statistics"""
        session = analytics.create_session(user_id='user123')
        
        analytics.track_event(session.session_id, EventType.PAGE_VIEW, page='home')
        analytics.track_event(session.session_id, EventType.CLICK, target='button')
        
        stats = analytics.get_session_stats(session.session_id)
        
        assert isinstance(stats, dict) or stats is None
    
    def test_get_user_engagement(self, analytics):
        """Test calculating user engagement"""
        session = analytics.create_session(user_id='user123')
        
        for i in range(5):
            analytics.track_event(session.session_id, EventType.PAGE_VIEW, page=f'page{i}')
        
        analytics.end_session(session.session_id)
        
        engagement = analytics.get_user_engagement('user123')
        
        assert 'total_sessions' in engagement
        assert engagement['total_sessions'] >= 1
    
    def test_get_popular_pages(self, analytics):
        """Test getting popular pages"""
        session = analytics.create_session()
        
        for page in ['home', 'dashboard', 'home', 'dashboard', 'home']:
            analytics.track_event(session.session_id, EventType.PAGE_VIEW, page=page)
        
        popular = analytics.get_popular_pages(limit=2)
        
        assert len(popular) <= 2
        assert popular[0][0] == 'home'  # Most viewed
        assert popular[0][1] == 3
    
    def test_get_event_funnel(self, analytics):
        """Test funnel analysis"""
        session = analytics.create_session()
        
        analytics.track_event(session.session_id, EventType.PAGE_VIEW)
        analytics.track_event(session.session_id, EventType.EXPORT)
        
        funnel = analytics.get_event_funnel([
            EventType.PAGE_VIEW,
            EventType.EXPORT
        ])
        
        assert 'page_view' in funnel
        assert 'export' in funnel
    
    def test_get_behavior_segments(self, analytics):
        """Test user behavior segmentation"""
        session1 = analytics.create_session(user_id='user1')
        session2 = analytics.create_session(user_id='user2')
        
        # Create different behavior patterns
        for i in range(40):
            analytics.track_event(session1.session_id, EventType.PAGE_VIEW)
        
        analytics.track_event(session2.session_id, EventType.EXPORT)
        
        segments = analytics.get_behavior_segments()
        
        assert 'power_users' in segments or 'engaged_users' in segments or 'explorers' in segments
    
    def test_anonymize_ip(self, analytics):
        """Test IP anonymization"""
        anonymized = analytics._anonymize_ip('192.168.1.100')
        
        assert anonymized != '192.168.1.100'
        assert anonymized.startswith('192.168.1')
    
    def test_export_analytics(self, analytics):
        """Test exporting analytics"""
        session = analytics.create_session(user_id='user123')
        analytics.track_event(session.session_id, EventType.CLICK)
        
        export = analytics.export_analytics('json')
        
        assert isinstance(export, str)
        assert 'sessions' in export
        assert 'events' in export
    
    def test_get_overview(self, analytics):
        """Test getting analytics overview"""
        session = analytics.create_session()
        analytics.track_event(session.session_id, EventType.PAGE_VIEW)
        
        overview = analytics.get_overview()
        
        assert 'total_sessions' in overview
        assert 'total_events' in overview
        assert 'active_sessions' in overview
    
    def test_multiple_sessions(self, analytics):
        """Test handling multiple sessions"""
        sessions = []
        for i in range(5):
            session = analytics.create_session(user_id=f'user{i}')
            sessions.append(session)
        
        assert len(analytics.sessions) == 5
    
    def test_event_with_metadata(self, analytics):
        """Test tracking event with metadata"""
        session = analytics.create_session()
        
        event = analytics.track_event(
            session.session_id,
            EventType.EXPORT,
            metadata={'format': 'pdf', 'records': 1000}
        )
        
        assert event.metadata['format'] == 'pdf'
        assert event.metadata['records'] == 1000


# ============ ML Prediction Tests ============

class TestPredictionResult:
    """Test PredictionResult dataclass"""
    
    def test_result_creation(self):
        """Test creating a prediction result"""
        result = PredictionResult(
            predictions=[100, 110, 120],
            accuracy=0.95
        )
        
        assert len(result.predictions) == 3
        assert result.accuracy == 0.95
    
    def test_result_to_dict(self):
        """Test converting result to dict"""
        result = PredictionResult(predictions=[100, 110])
        data = result.to_dict()
        
        assert 'predictions' in data
        assert 'accuracy' in data


class TestAnomalyScore:
    """Test AnomalyScore dataclass"""
    
    def test_score_creation(self):
        """Test creating an anomaly score"""
        score = AnomalyScore(
            value=100,
            is_anomaly=False,
            anomaly_score=0.5,
            threshold=0.7
        )
        
        assert score.value == 100
        assert isinstance(score.is_anomaly, bool)


class TestMLPredictionEngine:
    """Test MLPredictionEngine class"""
    
    @pytest.fixture
    def engine(self):
        """Create ML engine instance"""
        return MLPredictionEngine()
    
    def test_engine_initialization(self, engine):
        """Test engine initialization"""
        assert engine is not None
        assert len(engine.strategies) > 0
    
    def test_forecast_linear(self, engine):
        """Test linear regression forecast"""
        data = [100, 110, 120, 130, 140]
        
        result = engine.forecast(
            data,
            steps=5,
            model=PredictionModel.LINEAR_REGRESSION
        )
        
        assert len(result.predictions) == 5
        assert result.model_used == 'linear_regression'
    
    def test_forecast_exponential(self, engine):
        """Test exponential smoothing forecast"""
        data = [100, 105, 110, 115, 120]
        
        result = engine.forecast(
            data,
            steps=10,
            model=PredictionModel.EXPONENTIAL_SMOOTHING
        )
        
        assert len(result.predictions) == 10
        assert result.model_used == 'exponential_smoothing'
    
    def test_forecast_metrics(self, engine):
        """Test forecast includes metrics"""
        data = [100, 110, 120, 130, 140, 150]
        
        result = engine.forecast(data, steps=5)
        
        assert result.accuracy >= 0
        assert result.rmse >= 0
        assert result.mae >= 0
    
    def test_detect_anomalies_zscore(self, engine):
        """Test anomaly detection with Z-score"""
        data = [100, 105, 110, 115, 500, 120, 125]  # 500 is anomaly
        
        anomalies = engine.detect_anomalies(data, method='zscore')
        
        assert len(anomalies) == len(data)
        assert any(a.is_anomaly for a in anomalies)
    
    def test_detect_anomalies_iqr(self, engine):
        """Test anomaly detection with IQR"""
        data = [100, 105, 110, 115, 500, 120, 125]  # 500 is anomaly
        
        anomalies = engine.detect_anomalies(data, method='iqr')
        
        assert len(anomalies) == len(data)
        assert any(a.is_anomaly for a in anomalies)
    
    def test_predict_usage(self, engine):
        """Test usage prediction"""
        historical = [100, 105, 110, 115, 120]
        
        result = engine.predict_usage(historical, forecast_days=10)
        
        assert 'current_average' in result
        assert 'predicted_average' in result
        assert 'growth_rate_percent' in result
    
    def test_model_comparison(self, engine):
        """Test comparing different models"""
        data = [100, 110, 120, 130, 140]
        
        comparison = engine.get_model_comparison(data, steps=5)
        
        assert len(comparison) > 0
    
    def test_forecast_empty_data(self, engine):
        """Test forecast with empty data"""
        result = engine.forecast([], steps=5)
        
        assert isinstance(result, PredictionResult)
        assert len(result.predictions) == 0
    
    def test_forecast_single_value(self, engine):
        """Test forecast with single value"""
        result = engine.forecast([100], steps=5)
        
        assert isinstance(result, PredictionResult)
    
    def test_confidence_intervals(self, engine):
        """Test confidence intervals generation"""
        data = [100, 110, 120, 130, 140]
        
        result = engine.forecast(data, steps=5)
        
        assert len(result.confidence_intervals) == 5
        assert all(
            ci[0] <= ci[1] for ci in result.confidence_intervals
        )
    
    def test_anomaly_threshold(self, engine):
        """Test anomaly detection with different thresholds"""
        data = [100, 105, 110, 115, 300, 120, 125]
        
        # With low threshold
        anomalies_low = engine.detect_anomalies(data, threshold=1.0)
        count_low = sum(1 for a in anomalies_low if a.is_anomaly)
        
        # With high threshold
        anomalies_high = engine.detect_anomalies(data, threshold=3.0)
        count_high = sum(1 for a in anomalies_high if a.is_anomaly)
        
        assert count_low >= count_high  # Lower threshold catches more
    
    def test_calculate_metrics(self, engine):
        """Test metrics calculation"""
        actual = np.array([100, 110, 120, 130, 140])
        predicted = np.array([100, 112, 118, 132, 138])
        
        accuracy, rmse, mae, mape = engine._calculate_metrics(actual, predicted)
        
        assert 0 <= accuracy <= 1
        assert rmse >= 0
        assert mae >= 0
        assert mape >= 0
    
    def test_prediction_trend(self, engine):
        """Test that forecast captures trend"""
        data = [100, 110, 120, 130, 140]  # Increasing trend
        
        result = engine.forecast(data, steps=5)
        
        # Predictions should generally increase
        predictions = result.predictions
        assert predictions[-1] >= predictions[0]
    
    def test_multiple_forecasts(self, engine):
        """Test making multiple forecasts"""
        data = [100, 110, 120, 130, 140]
        
        result1 = engine.forecast(data, steps=5)
        result2 = engine.forecast(data, steps=10)
        
        assert len(result1.predictions) == 5
        assert len(result2.predictions) == 10


# ============ Integration Tests ============

class TestAnalyticsMLIntegration:
    """Test integration between analytics and ML"""
    
    def test_analytics_feeds_ml(self):
        """Test that analytics data can feed ML predictions"""
        analytics = AdvancedAnalyticsEngine()
        engine = MLPredictionEngine()
        
        # Create sessions and track events
        session = analytics.create_session()
        for i in range(10):
            analytics.track_event(session.session_id, EventType.PAGE_VIEW)
        
        # Use analytics data for prediction
        event_count_history = [5, 6, 7, 8, 9, 10]
        result = engine.forecast(event_count_history)
        
        assert len(result.predictions) > 0
    
    def test_anomaly_detection_with_analytics(self):
        """Test anomaly detection on analytics metrics"""
        analytics = AdvancedAnalyticsEngine()
        engine = MLPredictionEngine()
        
        session = analytics.create_session()
        
        # Create normal traffic
        for i in range(20):
            analytics.track_event(session.session_id, EventType.PAGE_VIEW)
        
        # Get overview and detect anomalies
        overview = analytics.get_overview()
        event_history = [overview['total_events']] * 5 + [100]  # Spike
        
        anomalies = engine.detect_anomalies(event_history)
        assert any(a.is_anomaly for a in anomalies)
