import time
import uuid
import os
from typing import Optional


class DistributedLock:
    """Redis-based distributed lock for concurrent operations"""
    
    def __init__(self):
        self._redis = None
    
    def _get_redis(self):
        """Lazy load Redis connection"""
        if self._redis is None:
            try:
                import redis
                from app.core.config import settings
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None
        return self._redis
    
    def acquire(self, key: str, timeout: int = 10) -> Optional[str]:
        """
        Acquire a distributed lock
        Returns lock_id if successful, None otherwise
        """
        r = self._get_redis()
        
        if not r:
            # Fallback: no lock in non-distributed mode
            return str(uuid.uuid4())
        
        lock_id = str(uuid.uuid4())
        
        # Try to acquire lock with NX (only set if not exists) and EX (expire)
        acquired = r.set(f"lock:{key}", lock_id, nx=True, ex=timeout)
        
        if acquired:
            return lock_id
        return None
    
    def release(self, key: str, lock_id: str) -> bool:
        """
        Release a distributed lock
        Only releases if lock_id matches (prevents releasing someone else's lock)
        """
        r = self._get_redis()
        
        if not r:
            return True
        
        # Lua script for atomic check-and-delete
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        try:
            result = r.eval(lua_script, 1, f"lock:{key}", lock_id)
            return result == 1
        except Exception:
            return False
    
    def extend(self, key: str, lock_id: str, timeout: int = 10) -> bool:
        """Extend lock timeout"""
        r = self._get_redis()
        
        if not r:
            return True
        
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        
        try:
            result = r.eval(lua_script, 1, f"lock:{key}", lock_id, timeout)
            return result == 1
        except Exception:
            return False


# Singleton instance
lock_manager = DistributedLock()


class OrderLock:
    """Context manager for order locking (抢单)"""
    
    def __init__(self, order_id: int, timeout: int = 10):
        self.order_id = order_id
        self.timeout = timeout
        self.lock_id = None
    
    def __enter__(self):
        self.lock_id = lock_manager.acquire(f"order:{self.order_id}", self.timeout)
        if not self.lock_id:
            raise Exception("Failed to acquire lock - order may be being processed")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock_id:
            lock_manager.release(f"order:{self.order_id}", self.lock_id)
    
    @property
    def is_locked(self) -> bool:
        return self.lock_id is not None
