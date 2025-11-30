"""
Decorators de Cache
Simplificam o uso de cache em funções
v1.4.0 - P1.3 Cache Implementation
"""

from functools import wraps
from typing import Callable, Optional
import hashlib
import json
import logging
from app.cache.cache_manager import cache_manager

logger = logging.getLogger(__name__)


def _generate_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """
    Gera chave de cache única baseada em função e argumentos
    
    Args:
        func_name: Nome da função
        args: Argumentos posicionais
        kwargs: Argumentos nomeados
        
    Returns:
        Chave de cache em formato hash
    """
    # Converter argumentos para string
    try:
        key_data = f"{func_name}:{str(args)}:{str(sorted(kwargs.items()))}"
        # Usar hash para reduzir tamanho
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"cache:{func_name}:{key_hash}"
    except Exception:
        # Fallback simples se houver erro
        return f"cache:{func_name}"


def cached(ttl: Optional[int] = None):
    """
    Decorator para cachear resultado de função
    
    Args:
        ttl: Time-to-live em segundos (usa default se None)
        
    Uso:
        @cached(ttl=300)  # 5 minutos
        def expensive_operation(x, y):
            return x + y
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            
            # Tentar obter do cache
            cached_value = cache_manager.get(cache_key)
            if cached_value is not None:
                logger.debug(f"✓ Usando valor em cache: {func.__name__}")
                return cached_value
            
            # Executar função
            logger.debug(f"Executando (não estava em cache): {func.__name__}")
            result = func(*args, **kwargs)
            
            # Armazenar em cache
            cache_manager.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Adicionar método para invalidar cache
        def invalidate(*args, **kwargs):
            cache_key = _generate_cache_key(func.__name__, args, kwargs)
            cache_manager.invalidate(cache_key)
            logger.info(f"✓ Cache invalidado para: {func.__name__}")
        
        wrapper.invalidate_cache = invalidate
        wrapper.clear_all = lambda: cache_manager.clear()
        
        return wrapper
    
    return decorator


def invalidate_cache(func_name: str, *args, **kwargs):
    """
    Invalida cache de uma função específica
    
    Args:
        func_name: Nome da função
        *args: Argumentos da função
        **kwargs: Argumentos nomeados da função
        
    Uso:
        invalidate_cache("expensive_operation", 10, 20)
    """
    cache_key = _generate_cache_key(func_name, args, kwargs)
    cache_manager.invalidate(cache_key)
    logger.info(f"✓ Cache invalidado: {func_name}")
