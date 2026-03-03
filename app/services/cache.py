import redis
import json
from typing import Optional, Any
from app.core.config import settings


class RedisCache:
    """Redis caching service"""
    
    def __init__(self):
        self.enabled = settings.REDIS_ENABLED
        self.client: Optional[redis.Redis] = None
        
        if self.enabled:
            self.client = redis.Redis.from_url(
                settings.REDIS_URL,
                decode_responses=True
            )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
        except Exception:
            pass
        return None
    
    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value to cache with TTL"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception:
            return False
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        if not self.enabled or not self.client:
            return 0
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
        except Exception:
            pass
        return 0
    
    def close(self):
        """Close connection"""
        if self.client:
            self.client.close()


# Cache key generators
class CacheKeys:
    CLEANERS = "cleaners:all"
    HOSTS = "hosts:all"
    PROPERTIES = "properties:all"
    ORDERS = "orders:{status}:{page}:{limit}"
    ORDER = "order:{id}"
    STATS = "stats:all"


# Singleton
cache = RedisCache()
