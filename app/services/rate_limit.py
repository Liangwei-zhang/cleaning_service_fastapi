import time
import os
from typing import Dict
from fastapi import HTTPException, Request


class RateLimiter:
    """Redis-based rate limiter"""
    
    def __init__(self):
        self.enabled = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
        self.requests: Dict[str, list] = {}
        self._redis = None
    
    def _get_redis(self):
        """Lazy load Redis connection"""
        if self._redis is None and self.enabled:
            try:
                import redis
                from app.core.config import settings
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
            except Exception:
                self._redis = None
        return self._redis
    
    def is_allowed(self, key: str, max_requests: int = 60, window_seconds: int = 60) -> bool:
        """Check if request is allowed"""
        if not self.enabled:
            return True
        
        r = self._get_redis()
        
        if r:
            # Use Redis
            try:
                current = r.get(f"rate:{key}")
                current = int(current) if current else 0
                
                if current >= max_requests:
                    return False
                
                pipe = r.pipeline()
                pipe.incr(f"rate:{key}")
                pipe.expire(f"rate:{key}", window_seconds)
                pipe.execute()
                return True
            except Exception:
                pass
        
        # Fallback to in-memory
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        self.requests[key] = [t for t in self.requests[key] if now - t < window_seconds]
        
        if len(self.requests[key]) >= max_requests:
            return False
        
        self.requests[key].append(now)
        return True
    
    def get_remaining(self, key: str, max_requests: int = 60, window_seconds: int = 60) -> int:
        """Get remaining requests"""
        r = self._get_redis()
        
        if r:
            try:
                current = r.get(f"rate:{key}")
                current = int(current) if current else 0
                return max(0, max_requests - current)
            except Exception:
                pass
        
        # In-memory fallback
        now = time.time()
        if key not in self.requests:
            return max_requests
        
        self.requests[key] = [t for t in self.requests[key] if now - t < window_seconds]
        return max(0, max_requests - len(self.requests[key]))


# Global rate limiter
rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 60, window_seconds: int = 60):
    """Rate limiting decorator"""
    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            # Get client IP
            client_ip = request.client.host if request.client else "unknown"
            
            # Check rate limit
            if not rate_limiter.is_allowed(f"{client_ip}:{request.url.path}", max_requests, window_seconds):
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Please try again later."
                )
            
            return await func(request, *args, **kwargs)
        return wrapper
    return decorator
