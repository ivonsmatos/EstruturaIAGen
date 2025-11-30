"""
Dashboard Cache - Wrapper functions for dashboard-specific caching
v1.0.0 - Dashboard optimization module
"""

from app.cache.cache_manager import (
    get_dashboard_metrics,
    get_dashboard_stats,
    get_chart_config
)

__all__ = [
    "get_dashboard_metrics",
    "get_dashboard_stats",
    "get_chart_config"
]
