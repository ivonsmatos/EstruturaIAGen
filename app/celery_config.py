"""
Celery Configuration for EstruturaIAGen
Async task queue with Redis backend
"""

from celery import Celery
from celery.schedules import crontab
import os
from datetime import timedelta

# Broker and backend configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

# Create Celery app
celery_app = Celery('estrutura_iagen')

# Celery configuration
celery_app.conf.update(
    # Broker settings
    broker_url=CELERY_BROKER_URL,
    result_backend=CELERY_RESULT_BACKEND,
    
    # Task settings
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_extended=True,
    
    # Worker settings
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    
    # Task timeout
    task_soft_time_limit=600,  # 10 minutes soft limit
    task_time_limit=900,  # 15 minutes hard limit
    
    # Retry settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Rate limiting
    task_default_rate_limit='1000/m',  # Max 1000 tasks per minute
    
    # Periodic tasks (beat schedule)
    beat_schedule={
        'check-alerts-every-5-minutes': {
            'task': 'app.async_tasks.check_system_alerts',
            'schedule': timedelta(minutes=5),
        },
        'update-dashboard-cache-every-10-minutes': {
            'task': 'app.async_tasks.update_dashboard_cache',
            'schedule': timedelta(minutes=10),
        },
        'cleanup-old-sessions-daily': {
            'task': 'app.async_tasks.cleanup_old_sessions',
            'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        },
        'generate-reports-daily': {
            'task': 'app.async_tasks.generate_daily_reports',
            'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
        },
        'health-check-every-minute': {
            'task': 'app.async_tasks.health_check',
            'schedule': timedelta(minutes=1),
        }
    }
)


# Task routing
celery_app.conf.task_routes = {
    'app.async_tasks.llm_inference': {'queue': 'llm', 'routing_key': 'llm.task'},
    'app.async_tasks.heavy_computation': {'queue': 'compute', 'routing_key': 'compute.task'},
    'app.async_tasks.database_operations': {'queue': 'db', 'routing_key': 'db.task'},
    'app.async_tasks.notifications': {'queue': 'notifications', 'routing_key': 'notify.task'},
}


def make_celery(app=None):
    """Create Celery instance for Flask app"""
    if app is not None:
        class ContextTask(celery_app.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery_app.Task = ContextTask
    return celery_app
