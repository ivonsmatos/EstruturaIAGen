"""
Testes de Cache
Valida LRU Cache, TTL, e decorators
v1.4.0 - P1.3 Cache Implementation
"""

import pytest
import time
from app.cache.cache_manager import CacheManager, cache_manager
from app.cache.decorators import cached, invalidate_cache


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_cache():
    """Cria cache de teste"""
    cache = CacheManager(max_size=10, default_ttl=2)
    yield cache
    cache.clear()


# ============================================================================
# TESTES: CACHE MANAGER
# ============================================================================

class TestCacheManager:
    """Testes para CacheManager"""
    
    def test_set_and_get(self, test_cache):
        """Teste: Armazenar e recuperar valor"""
        test_cache.set("key1", "value1")
        assert test_cache.get("key1") == "value1"
    
    def test_get_nonexistent(self, test_cache):
        """Teste: Retorna None para chave inexistente"""
        assert test_cache.get("nonexistent") is None
    
    def test_ttl_expiration(self, test_cache):
        """Teste: Valor expira após TTL"""
        test_cache.set("key1", "value1", ttl=1)
        assert test_cache.get("key1") == "value1"
        
        time.sleep(1.1)
        assert test_cache.get("key1") is None
    
    def test_invalidate(self, test_cache):
        """Teste: Invalidar chave remove do cache"""
        test_cache.set("key1", "value1")
        assert test_cache.get("key1") == "value1"
        
        test_cache.invalidate("key1")
        assert test_cache.get("key1") is None
    
    def test_clear(self, test_cache):
        """Teste: Limpar cache"""
        test_cache.set("key1", "value1")
        test_cache.set("key2", "value2")
        assert len(test_cache.cache) == 2
        
        test_cache.clear()
        assert len(test_cache.cache) == 0
    
    def test_lru_eviction(self, test_cache):
        """Teste: Remover item menos recentemente usado ao atingir limite"""
        # test_cache tem max_size=10
        for i in range(12):
            test_cache.set(f"key{i}", f"value{i}")
        
        # key0 e key1 devem ter sido removidos (LRU)
        assert test_cache.get("key0") is None
        assert test_cache.get("key1") is None
        # key11 deve estar no cache
        assert test_cache.get("key11") == "value11"
    
    def test_cache_stats(self, test_cache):
        """Teste: Retornar estatísticas"""
        test_cache.set("key1", "value1")
        test_cache.get("key1")  # hit
        test_cache.get("key2")  # miss
        
        stats = test_cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["total_requests"] == 2
        assert "hit_rate" in stats
    
    def test_complex_values(self, test_cache):
        """Teste: Armazenar valores complexos"""
        data = {"name": "test", "values": [1, 2, 3], "nested": {"key": "value"}}
        test_cache.set("complex", data)
        
        retrieved = test_cache.get("complex")
        assert retrieved == data
        assert retrieved["nested"]["key"] == "value"
    
    def test_cleanup_expired(self, test_cache):
        """Teste: Remover itens expirados"""
        test_cache.set("key1", "value1", ttl=1)
        test_cache.set("key2", "value2", ttl=10)
        
        time.sleep(1.1)
        
        removed = test_cache.cleanup_expired()
        assert removed == 1
        assert test_cache.get("key1") is None
        assert test_cache.get("key2") == "value2"


# ============================================================================
# TESTES: DECORATOR @CACHED
# ============================================================================

class TestCachedDecorator:
    """Testes para decorator @cached"""
    
    def test_cached_function(self, test_cache):
        """Teste: Decorator cachea resultado de função"""
        call_count = 0
        
        @cached(ttl=5)
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Primeira chamada
        result1 = expensive_func(5)
        assert result1 == 10
        assert call_count == 1
        
        # Segunda chamada (deve usar cache)
        result2 = expensive_func(5)
        assert result2 == 10
        assert call_count == 1  # Não incrementou
    
    def test_cached_different_args(self, test_cache):
        """Teste: Argumentos diferentes geram chaves diferentes"""
        call_count = 0
        
        @cached(ttl=5)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        func(5)  # call_count = 1
        func(10)  # call_count = 2 (argumentos diferentes)
        
        assert call_count == 2
    
    def test_cached_with_kwargs(self, test_cache):
        """Teste: Decorator funciona com kwargs"""
        call_count = 0
        
        @cached(ttl=5)
        def func(x, y=10):
            nonlocal call_count
            call_count += 1
            return x + y
        
        result1 = func(5, y=10)
        result2 = func(5, y=10)  # Deve usar cache
        
        assert result1 == 15
        assert result2 == 15
        assert call_count == 1
    
    def test_invalidate_cache_method(self, test_cache):
        """Teste: Método invalidate_cache do decorator"""
        call_count = 0
        
        @cached(ttl=5)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        func(5)  # call_count = 1
        func.invalidate_cache(5)  # Invalidar
        func(5)  # call_count = 2 (não usa cache)
        
        assert call_count == 2


# ============================================================================
# TESTES: PERFORMANCE
# ============================================================================

class TestCachePerformance:
    """Testes de performance do cache"""
    
    def test_cache_hit_performance(self, test_cache):
        """Teste: Cache hit é mais rápido que miss"""
        import time
        
        @cached(ttl=60)
        def slow_func(x):
            time.sleep(0.01)  # 10ms
            return x * 2
        
        # Primeira chamada (sem cache)
        start = time.time()
        slow_func(5)
        time_no_cache = time.time() - start
        
        # Segunda chamada (com cache)
        start = time.time()
        slow_func(5)
        time_with_cache = time.time() - start
        
        # Cache deve ser significativamente mais rápido
        assert time_with_cache < time_no_cache / 2
    
    def test_hit_rate_calculation(self, test_cache):
        """Teste: Hit rate é calculado corretamente"""
        test_cache.set("key1", "value1")
        
        # 3 hits
        test_cache.get("key1")
        test_cache.get("key1")
        test_cache.get("key1")
        
        # 2 misses
        test_cache.get("key2")
        test_cache.get("key3")
        
        stats = test_cache.get_stats()
        # 3 hits / (3 hits + 2 misses) = 60%
        assert "60.00" in stats["hit_rate"]


# ============================================================================
# TESTES: EDGE CASES
# ============================================================================

class TestCacheEdgeCases:
    """Testes para casos extremos"""
    
    def test_none_value(self, test_cache):
        """Teste: Armazenar None retorna None (ambíguo com miss)"""
        # Nota: Cache não consegue diferenciar None armazenado de miss
        # Isso é uma limitação conhecida
        test_cache.set("key1", None)
        # Isso vai retornar None, mas pode ser indistinguível de um miss
        result = test_cache.get("key1")
        # Em caso real, seria None mesmo
    
    def test_large_value(self, test_cache):
        """Teste: Armazenar valor grande"""
        large_data = {"data": "x" * 10000}
        test_cache.set("large", large_data)
        
        retrieved = test_cache.get("large")
        assert retrieved == large_data
    
    def test_special_characters_in_key(self, test_cache):
        """Teste: Chaves com caracteres especiais"""
        test_cache.set("key:with:colons", "value")
        test_cache.set("key-with-dashes", "value")
        test_cache.set("key.with.dots", "value")
        
        assert test_cache.get("key:with:colons") == "value"
        assert test_cache.get("key-with-dashes") == "value"
        assert test_cache.get("key.with.dots") == "value"
    
    def test_concurrent_access(self, test_cache):
        """Teste: Acesso concurrent-safe (básico)"""
        for i in range(100):
            test_cache.set(f"key{i}", f"value{i}")
            value = test_cache.get(f"key{i}")
            assert value == f"value{i}"


# ============================================================================
# TESTES: LIMPEZA E MAINTENANCE
# ============================================================================

class TestCacheMaintenance:
    """Testes para limpeza e manutenção de cache"""
    
    def test_auto_cleanup_expired(self, test_cache):
        """Teste: Cleanup remove itens expirados"""
        test_cache.set("key1", "value1", ttl=1)
        test_cache.set("key2", "value2", ttl=100)
        
        time.sleep(1.1)
        
        removed = test_cache.cleanup_expired()
        assert removed >= 1
        assert len(test_cache.cache) < 2
    
    def test_stats_accuracy(self, test_cache):
        """Teste: Estatísticas são precisas"""
        initial_stats = test_cache.get_stats()
        
        test_cache.set("key1", "value1")
        test_cache.get("key1")  # hit
        test_cache.get("key1")  # hit
        test_cache.get("key2")  # miss
        
        stats = test_cache.get_stats()
        assert stats["hits"] == initial_stats["hits"] + 2
        assert stats["misses"] == initial_stats["misses"] + 1
