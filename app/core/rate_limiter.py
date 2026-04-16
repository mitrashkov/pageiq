import time
from typing import Optional

from fastapi import HTTPException, Request, status
from redis import Redis

from app.core.redis import get_redis
from app.core.config import settings


class RateLimiter:
    """Redis-based sliding window rate limiter"""

    def __init__(self, redis_client: Optional[Redis] = None):
        self.redis = redis_client or get_redis()

    async def check_rate_limit(
        self,
        key: str,
        limit: int = None,
        window_seconds: int = 60
    ) -> tuple[bool, int, float]:
        """
        Check if request is within rate limit.

        Args:
            key: Rate limit key (e.g., "user:123" or "ip:192.168.1.1")
            limit: Maximum requests allowed in window
            window_seconds: Time window in seconds

        Returns:
            Tuple of (allowed: bool, remaining: int, reset_time: float)
        """
        if limit is None:
            limit = settings.RATE_LIMIT_REQUESTS_PER_MINUTE

        current_time = time.time()
        window_start = current_time - window_seconds

        # Use Redis sorted set to track requests
        # Score is timestamp, member is unique request ID
        request_id = f"{key}:{current_time}:{id(self)}"

        # Remove old entries outside the window
        self.redis.zremrangebyscore(key, 0, window_start)

        # Count current requests in window
        current_count = self.redis.zcard(key)

        # Calculate reset time (when oldest request expires)
        oldest_timestamp = self.redis.zrange(key, 0, 0, withscores=True)
        if oldest_timestamp:
            reset_time = float(oldest_timestamp[0][1]) + window_seconds
        else:
            reset_time = current_time + window_seconds

        if current_count >= limit:
            # Rate limit exceeded
            remaining = 0
            allowed = False
        else:
            # Add current request
            self.redis.zadd(key, {request_id: current_time})
            # Set expiration on the key to clean up automatically
            self.redis.expire(key, window_seconds * 2)

            remaining = limit - (current_count + 1)
            allowed = True

        return allowed, remaining, reset_time


class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    def __init__(self, app, redis_client: Optional[Redis] = None):
        self.app = app
        self.rate_limiter = RateLimiter(redis_client)

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Skip rate limiting for health checks
        if request.url.path == "/health":
            await self.app(scope, receive, send)
            return

        # Determine rate limit key
        # For authenticated users, use user ID
        # For anonymous users, use IP address
        rate_limit_key = self._get_rate_limit_key(request)

        # Check rate limit
        allowed, remaining, reset_time = await self.rate_limiter.check_rate_limit(
            rate_limit_key,
            limit=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            window_seconds=60
        )

        if not allowed:
            # Rate limit exceeded
            response = self._create_rate_limit_response(remaining, reset_time)
            await response(scope, receive, send)
            return

        # Add rate limit headers to request state for response middleware
        request.state.rate_limit_remaining = remaining
        request.state.rate_limit_reset = reset_time

        await self.app(scope, receive, send)

    def _get_rate_limit_key(self, request: Request) -> str:
        """Get rate limit key for request"""
        # Check if user is authenticated
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            return f"user:{user_id}"

        # Use IP address for anonymous users
        client_ip = self._get_client_ip(request)
        return f"ip:{client_ip}"

    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check X-Forwarded-For header (for proxies/load balancers)
        x_forwarded_for = request.headers.get("x-forwarded-for")
        if x_forwarded_for:
            # Take the first IP in the chain
            return x_forwarded_for.split(",")[0].strip()

        # Check X-Real-IP header
        x_real_ip = request.headers.get("x-real-ip")
        if x_real_ip:
            return x_real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"

    def _create_rate_limit_response(self, remaining: int, reset_time: float):
        """Create rate limit exceeded response"""
        from starlette.responses import JSONResponse

        response = JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "retry_after": int(reset_time - time.time())
            }
        )

        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        response.headers["Retry-After"] = str(int(reset_time - time.time()))

        return response


# Global rate limiter instance
rate_limiter = RateLimiter()