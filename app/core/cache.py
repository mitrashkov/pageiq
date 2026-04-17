import json
import hashlib
from functools import wraps
from typing import Any, Callable, Optional, Union
import logging

from app.core.redis import get_redis
from app.core.config import settings

logger = logging.getLogger(__name__)

def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate a deterministic cache key from arguments"""
    # Create a stable representation of args and kwargs
    key_parts = [prefix]
    for arg in args:
        key_parts.append(str(arg))
    
    # Sort kwargs to ensure stability
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    raw_key = ":".join(key_parts)
    # Use MD5 hash for long keys to keep them manageable in Redis
    key_hash = hashlib.md5(raw_key.encode()).hexdigest()
    return f"cache:{prefix}:{key_hash}"

async def get_cached_response(key: str) -> Optional[Any]:
    """Retrieve a response from cache"""
    redis = get_redis()
    try:
        data = redis.get(key)
        if data:
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Cache retrieval failed for {key}: {e}")
    return None

async def set_cached_response(key: str, data: Any, ttl: int = None) -> bool:
    """Store a response in cache"""
    if ttl is None:
        ttl = settings.CACHE_TTL_SECONDS
    
    redis = get_redis()
    try:
        redis.set(key, json.dumps(data), ex=ttl)
        return True
    except Exception as e:
        logger.warning(f"Cache storage failed for {key}: {e}")
        return False

def cache_response(prefix: str, ttl: int = None):
    """
    Decorator for caching API responses.
    Note: This is a simplified version. In a real production app, 
    you'd want to handle FastAPI-specific things like Depends and BackgroundTasks.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip cache if disabled in settings or for specific requests
            if not settings.DEBUG: # Just an example, maybe use a CACHE_ENABLED setting
                cache_key = generate_cache_key(prefix, *args, **kwargs)
                cached_data = await get_cached_response(cache_key)
                if cached_data:
                    return cached_data
            
            result = await func(*args, **kwargs)
            
            if not settings.DEBUG:
                await set_cached_response(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
