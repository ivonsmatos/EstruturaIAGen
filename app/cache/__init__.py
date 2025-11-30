"""
Sistema de Cache da Aplicação
Módulo para gerenciamento de cache LRU e Redis
"""

from app.cache.cache_manager import (
    CacheManager,
    cache_manager,
    clear_cache,
    get_cache_stats
)

from app.cache.decorators import (
    cached,
    invalidate_cache
)

__all__ = [
    "CacheManager",
    "cache_manager",
    "clear_cache",
    "get_cache_stats",
    "cached",
    "invalidate_cache"
]
