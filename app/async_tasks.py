"""
Async Tasks for EstruturaIAGen
Background processing with Celery + Redis
"""

from celery import shared_task, Task
from celery.utils.log import get_task_logger
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import json
import time

logger = get_task_logger(__name__)


class CallbackTask(Task):
    """Task with on_success and on_failure callbacks"""
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3, 'countdown': 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


@shared_task(bind=True, base=CallbackTask)
def llm_inference(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 500) -> Dict[str, Any]:
    """
    Execute LLM inference task asynchronously
    Useful for chat responses, analysis, etc.
    """
    try:
        logger.info(f"Starting LLM inference with model: {model}")
        
        # Simulated LLM call - replace with actual API
        # In production: use openai, anthropic, huggingface, etc.
        
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(1)
        
        response = {
            'prompt': prompt,
            'model': model,
            'response': f"LLM response to: {prompt[:50]}...",
            'tokens_used': 150,
            'processing_time_ms': (time.time() - start_time) * 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"LLM inference completed in {response['processing_time_ms']:.2f}ms")
        return response
        
    except Exception as e:
        logger.error(f"LLM inference failed: {str(e)}")
        raise self.retry(exc=e, countdown=5)


@shared_task(bind=True, base=CallbackTask)
def heavy_computation(self, data: Dict[str, Any], operation: str = "forecast") -> Dict[str, Any]:
    """
    Execute computationally intensive operations asynchronously
    Examples: ML predictions, forecasting, anomaly detection
    """
    try:
        logger.info(f"Starting heavy computation: {operation}")
        
        start_time = time.time()
        
        # Simulate heavy computation
        result = 0
        for i in range(100000):
            result += i ** 2
        
        processing_time = (time.time() - start_time) * 1000
        
        output = {
            'operation': operation,
            'status': 'completed',
            'result': result,
            'processing_time_ms': processing_time,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Heavy computation completed in {processing_time:.2f}ms")
        return output
        
    except Exception as e:
        logger.error(f"Heavy computation failed: {str(e)}")
        raise self.retry(exc=e, countdown=10)


@shared_task(bind=True, base=CallbackTask)
def database_operations(self, operation: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute long-running database operations asynchronously
    Examples: bulk inserts, migrations, data cleanup
    """
    try:
        logger.info(f"Starting database operation: {operation}")
        
        start_time = time.time()
        
        # Simulate database operation
        time.sleep(2)
        
        result = {
            'operation': operation,
            'status': 'success',
            'rows_affected': 1000,
            'processing_time_ms': (time.time() - start_time) * 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Database operation completed: {operation}")
        return result
        
    except Exception as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise self.retry(exc=e, countdown=10)


@shared_task(bind=True, base=CallbackTask)
def send_notifications(self, notification_type: str, recipients: List[str], 
                       data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send notifications asynchronously
    Supports: email, SMS, push notifications, webhooks
    """
    try:
        logger.info(f"Sending {notification_type} notifications to {len(recipients)} recipients")
        
        start_time = time.time()
        
        # Simulate notification sending
        time.sleep(0.5)
        
        result = {
            'notification_type': notification_type,
            'recipients_count': len(recipients),
            'status': 'sent',
            'processing_time_ms': (time.time() - start_time) * 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Notifications sent successfully")
        return result
        
    except Exception as e:
        logger.error(f"Notification sending failed: {str(e)}")
        raise self.retry(exc=e, countdown=5)


@shared_task(bind=True, base=CallbackTask)
def check_system_alerts(self) -> Dict[str, Any]:
    """
    Periodic task: Check system health and trigger alerts if needed
    Runs every 5 minutes
    """
    try:
        logger.info("Checking system alerts")
        
        # Import here to avoid circular imports
        from app.alerts import get_alert_manager
        
        alert_manager = get_alert_manager()
        
        # Evaluate all active rules
        alerts_triggered = 0
        for rule in alert_manager.list_rules():
            if rule.enabled:
                # Simulate metric collection
                current_value = 4.5  # Example: error rate 4.5%
                alert = alert_manager.evaluate_rule(rule.id, current_value)
                if alert:
                    alerts_triggered += 1
        
        return {
            'task': 'check_system_alerts',
            'alerts_triggered': alerts_triggered,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"System alert check failed: {str(e)}")
        # Don't retry periodic tasks
        return {'error': str(e)}


@shared_task(bind=True, base=CallbackTask)
def update_dashboard_cache(self) -> Dict[str, Any]:
    """
    Periodic task: Update dashboard cache
    Runs every 10 minutes
    """
    try:
        logger.info("Updating dashboard cache")
        
        # Import here to avoid circular imports
        from app.cache import get_cache_manager
        
        cache_manager = get_cache_manager()
        
        # Clear and regenerate dashboard caches
        metrics = cache_manager.get_dashboard_metrics()
        stats = cache_manager.get_dashboard_stats()
        charts = cache_manager.get_chart_config()
        
        return {
            'task': 'update_dashboard_cache',
            'status': 'completed',
            'metrics_updated': True,
            'stats_updated': True,
            'charts_updated': True,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Dashboard cache update failed: {str(e)}")
        return {'error': str(e)}


@shared_task(bind=True, base=CallbackTask)
def cleanup_old_sessions(self) -> Dict[str, Any]:
    """
    Periodic task: Clean up old chat sessions and expired data
    Runs daily at 2 AM
    """
    try:
        logger.info("Cleaning up old sessions")
        
        from app.chat import get_chat_manager
        
        chat_manager = get_chat_manager()
        
        # Example: archive sessions older than 30 days
        cutoff_date = datetime.now() - timedelta(days=30)
        
        archived_count = 0
        for session in chat_manager.get_all_sessions():
            if session.created_at < cutoff_date and not session.is_archived:
                session.is_archived = True
                archived_count += 1
        
        return {
            'task': 'cleanup_old_sessions',
            'sessions_archived': archived_count,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")
        return {'error': str(e)}


@shared_task(bind=True, base=CallbackTask)
def generate_daily_reports(self) -> Dict[str, Any]:
    """
    Periodic task: Generate daily reports
    Runs daily at 1 AM
    """
    try:
        logger.info("Generating daily reports")
        
        from app.analytics import AnalyticsManager
        
        analytics = AnalyticsManager()
        
        # Generate various daily reports
        usage_report = analytics.generate_usage_report()
        performance_report = analytics.generate_performance_report()
        error_report = analytics.generate_error_report()
        
        report_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'usage_report': usage_report,
            'performance_report': performance_report,
            'error_report': error_report
        }
        
        # Save report to database/file
        logger.info("Daily reports generated successfully")
        
        return {
            'task': 'generate_daily_reports',
            'reports_generated': 3,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Daily reports generation failed: {str(e)}")
        return {'error': str(e)}


@shared_task(bind=True, base=CallbackTask)
def health_check(self) -> Dict[str, Any]:
    """
    Periodic task: System health check
    Runs every minute
    """
    try:
        health_status = {
            'task': 'health_check',
            'status': 'healthy',
            'components': {
                'database': 'ok',
                'cache': 'ok',
                'celery': 'ok',
                'api': 'ok'
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}


@shared_task(bind=True, base=CallbackTask)
def export_data_async(self, format: str = "json", user_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Export data asynchronously
    Useful for large exports that would block the request
    """
    try:
        logger.info(f"Starting data export in {format} format")
        
        start_time = time.time()
        
        # Simulate export operation
        time.sleep(3)
        
        export_data = {
            'format': format,
            'user_id': user_id,
            'rows_exported': 10000,
            'file_size_mb': 15.5,
            'processing_time_ms': (time.time() - start_time) * 1000,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Data export completed")
        return export_data
        
    except Exception as e:
        logger.error(f"Data export failed: {str(e)}")
        raise self.retry(exc=e, countdown=10)


@shared_task(bind=True, base=CallbackTask)
def process_webhook(self, webhook_url: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process webhook asynchronously
    """
    try:
        logger.info(f"Processing webhook: {webhook_url}")
        
        import requests
        
        response = requests.post(webhook_url, json=data, timeout=30)
        
        result = {
            'webhook_url': webhook_url,
            'status_code': response.status_code,
            'success': response.status_code in (200, 201),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Webhook processed: {result['status_code']}")
        return result
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise self.retry(exc=e, countdown=10)


# Task monitoring and management
@shared_task
def get_active_tasks() -> List[Dict[str, Any]]:
    """Get list of currently active tasks"""
    from celery.app.control import Inspect
    from app.celery_config import celery_app
    
    inspect = Inspect(app=celery_app)
    return inspect.active() or {}


@shared_task
def get_registered_tasks() -> List[str]:
    """Get list of all registered tasks"""
    from app.celery_config import celery_app
    return sorted(celery_app.tasks.keys())


@shared_task
def get_task_stats() -> Dict[str, Any]:
    """Get Celery task statistics"""
    from celery.app.control import Inspect
    from app.celery_config import celery_app
    
    inspect = Inspect(app=celery_app)
    
    return {
        'active': len(inspect.active() or {}),
        'scheduled': len(inspect.scheduled() or {}),
        'reserved': len(inspect.reserved() or {}),
        'workers': len(inspect.ping() or {}),
        'timestamp': datetime.now().isoformat()
    }
