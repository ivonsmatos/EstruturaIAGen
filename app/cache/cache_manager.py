"""
Cache Manager - Gerenciador Central de Cache
Implementa LRU Cache com TTL e suporte a Redis (opcional)
v1.4.0 - P1.3 Cache Implementation
"""

import time
import logging
from typing import Any, Optional, Dict
from collections import OrderedDict
from datetime import datetime
import os
import json

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Gerenciador de cache com suporte a LRU e TTL
    Compatível com Redis para aplicações distribuídas
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Inicializa o gerenciador de cache
        
        Args:
            max_size: Tamanho máximo do cache (itens)
            default_ttl: TTL padrão em segundos (1h)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, Dict[str, Any]] = OrderedDict()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "total_requests": 0
        }
        self.redis_client = None
        
        # Tentar conectar a Redis se disponível
        self._init_redis()
        
        logger.info(f"✓ CacheManager inicializado (max_size={max_size}, ttl={default_ttl}s)")
    
    def _init_redis(self):
        """Tenta inicializar conexão com Redis"""
        try:
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                import redis
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("✓ Conectado a Redis")
        except Exception as e:
            logger.debug(f"Redis não disponível: {str(e)} (usando cache local)")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor em cache ou None se não existir/expirado
        """
        self.stats["total_requests"] += 1
        
        # Tentar Redis primeiro
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self.stats["hits"] += 1
                    logger.debug(f"✓ Cache hit (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.debug(f"Redis read error: {str(e)}")
        
        # Fallback para cache local
        if key in self.cache:
            entry = self.cache[key]
            
            # Verificar TTL
            if entry["expires_at"] > time.time():
                self.stats["hits"] += 1
                logger.debug(f"✓ Cache hit (LRU): {key}")
                
                # Mover para o final (LRU)
                self.cache.move_to_end(key)
                return entry["value"]
            else:
                # Expirado
                del self.cache[key]
                logger.debug(f"✓ Cache expirado: {key}")
        
        self.stats["misses"] += 1
        logger.debug(f"✗ Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            value: Valor a armazenar
            ttl: TTL em segundos (usa default se None)
        """
        ttl = ttl or self.default_ttl
        
        # Armazenar em Redis se disponível
        if self.redis_client:
            try:
                self.redis_client.setex(
                    key,
                    ttl,
                    json.dumps(value, default=str)
                )
                logger.debug(f"✓ Valor armazenado em Redis: {key} (TTL={ttl}s)")
            except Exception as e:
                logger.debug(f"Redis write error: {str(e)}")
        
        # Armazenar em cache local
        expires_at = time.time() + ttl
        
        # Remover se já existe para atualizar
        if key in self.cache:
            del self.cache[key]
        
        # Verificar limite de tamanho
        if len(self.cache) >= self.max_size:
            # Remover item mais antigo (LRU)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
            logger.debug(f"Cache eviction: {oldest_key} (tamanho={self.max_size})")
        
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }
        
        logger.debug(f"✓ Valor armazenado em cache local: {key} (TTL={ttl}s)")
    
    def invalidate(self, key: str):
        """Remove item do cache"""
        if key in self.cache:
            del self.cache[key]
            logger.info(f"✓ Cache invalidado: {key}")
        
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.debug(f"Redis delete error: {str(e)}")
    
    def clear(self):
        """Limpa todo o cache"""
        self.cache.clear()
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception as e:
                logger.debug(f"Redis flush error: {str(e)}")
        logger.info("✓ Cache limpo completamente")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total = self.stats["total_requests"]
        hit_rate = (self.stats["hits"] / total * 100) if total > 0 else 0
        
        return {
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "evictions": self.stats["evictions"],
            "total_requests": total,
            "hit_rate": f"{hit_rate:.2f}%",
            "cache_size": len(self.cache),
            "max_size": self.max_size,
            "redis_connected": self.redis_client is not None,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def cleanup_expired(self):
        """Remove itens expirados do cache"""
        now = time.time()
        expired_keys = [
            key for key, entry in self.cache.items()
            if entry["expires_at"] <= now
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            logger.info(f"✓ Cleanup: {len(expired_keys)} itens expirados removidos")
        
        return len(expired_keys)




# ============================================================================
# INSTÂNCIA GLOBAL
# ============================================================================

cache_manager = CacheManager(
    max_size=int(os.getenv("CACHE_MAX_SIZE", 1000)),
    default_ttl=int(os.getenv("CACHE_TTL", 3600))
)


# ============================================================================
# FUNÇÕES PÚBLICAS
# ============================================================================

def clear_cache():
    """Limpa o cache"""
    cache_manager.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Retorna estatísticas do cache"""
    return cache_manager.get_stats()


# ============================================================================
# DASHBOARD-SPECIFIC CACHE FUNCTIONS (sem decorator para evitar ciclo)
# ============================================================================

def get_dashboard_metrics(periodo: str = "24h", user_id: int = 1):
    """
    Fetch e cache de métricas do dashboard
    
    Args:
        periodo: Período (24h, 7d, 30d, all)
        user_id: ID do usuário
        
    Returns:
        Métricas agregadas (cacheadas por 5 minutos)
    """
    cache_key = f"dashboard_metrics:{periodo}:{user_id}"
    cached_result = cache_manager.get(cache_key)
    
    if cached_result:
        logger.debug(f"✓ Retornando métricas do cache: {periodo}")
        return cached_result
    
    logger.info(f"🔄 Fetchando métricas (não estava em cache): {periodo}")
    try:
        from app.db.metrics import fetch_metrics_from_db
        result = fetch_metrics_from_db(periodo, user_id)
        cache_manager.set(cache_key, result, ttl=300)  # 5 minutos
        return result
    except ImportError:
        logger.warning("app.db.metrics não disponível")
        return {}


def get_dashboard_stats(periodo: str = "24h", user_id: int = 1):
    """
    Estatísticas consolidadas do dashboard
    
    Args:
        periodo: Período para análise
        user_id: ID do usuário
        
    Returns:
        Estatísticas (cacheadas por 10 minutos)
    """
    cache_key = f"dashboard_stats:{periodo}:{user_id}"
    cached_result = cache_manager.get(cache_key)
    
    if cached_result:
        logger.debug(f"✓ Retornando stats do cache: {periodo}")
        return cached_result
    
    logger.info(f"🔄 Calculando estatísticas (não estava em cache): {periodo}")
    try:
        from app.db.metrics import get_metric_stats
        result = get_metric_stats(user_id, periodo)
        cache_manager.set(cache_key, result, ttl=600)  # 10 minutos
        return result
    except ImportError:
        logger.warning("app.db.metrics não disponível")
        return {}


def get_chart_config(chart_type: str = "efficiency"):
    """
    Configuração de gráfico cacheada
    
    Args:
        chart_type: Tipo de gráfico
        
    Returns:
        Configuração do Plotly
    """
    cache_key = f"chart_config:{chart_type}"
    cached_result = cache_manager.get(cache_key)
    
    if cached_result:
        logger.debug(f"✓ Retornando config do cache: {chart_type}")
        return cached_result
    
    configs = {
        "efficiency": {"title": "Eficiência", "type": "bar"},
        "tokens": {"title": "Tokens", "type": "line"},
        "latency": {"title": "Latência", "type": "scatter"}
    }
    result = configs.get(chart_type, configs["efficiency"])
    cache_manager.set(cache_key, result, ttl=60)  # 1 minuto
    return result
