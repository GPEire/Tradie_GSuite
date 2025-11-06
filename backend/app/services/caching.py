"""
Caching Service
TASK-043: Implement caching strategies for performance optimization
"""

from typing import Optional, Any, Dict
from functools import wraps
import hashlib
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryCache:
    """In-memory cache with TTL support"""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize memory cache
        
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        
        # Check if expired
        if datetime.now() > entry['expires_at']:
            del self.cache[key]
            return None
        
        return entry['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache"""
        ttl = ttl or self.default_ttl
        self.cache[key] = {
            'value': value,
            'expires_at': datetime.now() + timedelta(seconds=ttl),
            'created_at': datetime.now()
        }
    
    def delete(self, key: str) -> None:
        """Delete key from cache"""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        now = datetime.now()
        active = sum(1 for entry in self.cache.values() if entry['expires_at'] > now)
        expired = len(self.cache) - active
        
        return {
            'total_keys': len(self.cache),
            'active_keys': active,
            'expired_keys': expired,
            'memory_size': sum(len(str(v)) for v in self.cache.values())
        }


# Global cache instance
_cache = MemoryCache(default_ttl=300)


def get_cache() -> MemoryCache:
    """Get global cache instance"""
    return _cache


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = {
        'args': args,
        'kwargs': sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Generate cache key
            full_prefix = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            cache_key_str = f"{full_prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache.get(cache_key_str)
            if cached_value is not None:
                logger.debug(f"Cache hit for {cache_key_str}")
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key_str, result, ttl=ttl)
            logger.debug(f"Cache miss for {cache_key_str}, cached result")
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache entries matching pattern
    
    Args:
        pattern: Pattern to match (prefix)
        
    Returns:
        Number of keys invalidated
    """
    cache = get_cache()
    keys_to_delete = [key for key in cache.cache.keys() if key.startswith(pattern)]
    
    for key in keys_to_delete:
        cache.delete(key)
    
    return len(keys_to_delete)


class QueryCache:
    """Cache for database queries"""
    
    def __init__(self):
        self.cache = MemoryCache(default_ttl=60)  # 1 minute default for queries
    
    def get_user_projects_key(self, user_id: int, status: Optional[str] = None) -> str:
        """Generate cache key for user projects"""
        return f"user_projects:{user_id}:{status or 'all'}"
    
    def get_project_key(self, project_id: str) -> str:
        """Generate cache key for project"""
        return f"project:{project_id}"
    
    def get_email_mappings_key(self, project_id: int) -> str:
        """Generate cache key for email mappings"""
        return f"email_mappings:{project_id}"
    
    def invalidate_project_cache(self, project_id: str) -> None:
        """Invalidate all cache entries for a project"""
        patterns = [
            f"project:{project_id}",
            f"email_mappings:{project_id}",
        ]
        for pattern in patterns:
            invalidate_cache(pattern)
    
    def invalidate_user_cache(self, user_id: int) -> None:
        """Invalidate all cache entries for a user"""
        invalidate_cache(f"user_projects:{user_id}")


# Global query cache instance
_query_cache = QueryCache()


def get_query_cache() -> QueryCache:
    """Get global query cache instance"""
    return _query_cache

