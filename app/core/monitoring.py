import time
import uuid
from typing import Callable

from fastapi import Request, Response
import structlog

from app.core.config import settings
from app.core.context import set_request_context

logger = structlog.get_logger(__name__)


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses"""

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Set request context for logging
        set_request_context(
            request_id=request_id,
            trace_id=request.headers.get("x-trace-id") or request.headers.get("x-request-id")
        )

        # Start timing
        start_time = time.time()

        # Extract request info
        method = request.method
        url = str(request.url)
        user_agent = request.headers.get("user-agent", "")
        content_length = request.headers.get("content-length", 0)

        # Log request start
        logger.info(
            "Request started",
            request_id=request_id,
            method=method,
            url=url,
            user_agent=user_agent[:100],  # Truncate long user agents
            content_length=content_length,
            user_id=getattr(request.state, 'user_id', None),
            api_key_id=getattr(request.state, 'api_key_id', None),
        )

        # Process request
        response = None
        try:
            # Custom send function to capture response
            response_info = {}

            async def capture_response(message):
                if message["type"] == "http.response.start":
                    response_info.update({
                        "status_code": message["status"],
                        "headers": dict(message.get("headers", []))
                    })
                elif message["type"] == "http.response.body":
                    response_info["body_length"] = len(message.get("body", b""))

                await send(message)

            await self.app(scope, receive, capture_response)

            # Calculate processing time
            processing_time = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                request_id=request_id,
                status_code=response_info.get("status_code"),
                processing_time_ms=int(processing_time * 1000),
                response_size=response_info.get("body_length", 0),
                user_id=getattr(request.state, 'user_id', None),
            )

        except Exception as e:
            # Log error
            processing_time = time.time() - start_time
            logger.error(
                "Request failed",
                request_id=request_id,
                error=str(e),
                processing_time_ms=int(processing_time * 1000),
                user_id=getattr(request.state, 'user_id', None),
                exc_info=True
            )
            raise


class MetricsCollector:
    """Prometheus-compatible metrics collector"""

    def __init__(self):
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "response_time_sum": 0.0,
            "response_time_count": 0,
            "errors_total": 0,
            "active_connections": 0,
        }

    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float
    ):
        """Record request metrics"""
        self.metrics["requests_total"] += 1

        # Status code counts
        status_key = str(status_code)
        if status_key not in self.metrics["requests_by_status"]:
            self.metrics["requests_by_status"][status_key] = 0
        self.metrics["requests_by_status"][status_key] += 1

        # Endpoint counts
        endpoint_key = f"{method} {endpoint}"
        if endpoint_key not in self.metrics["requests_by_endpoint"]:
            self.metrics["requests_by_endpoint"][endpoint_key] = 0
        self.metrics["requests_by_endpoint"][endpoint_key] += 1

        # Response time histogram data
        self.metrics["response_time_sum"] += response_time
        self.metrics["response_time_count"] += 1

        # Count errors (4xx and 5xx)
        if status_code >= 400:
            self.metrics["errors_total"] += 1

    def increment_active_connections(self):
        """Increment active connections counter"""
        self.metrics["active_connections"] += 1

    def decrement_active_connections(self):
        """Decrement active connections counter"""
        self.metrics["active_connections"] = max(0, self.metrics["active_connections"] - 1)

    def get_metrics(self) -> dict:
        """Get current metrics"""
        metrics = self.metrics.copy()

        # Calculate derived metrics
        if metrics["response_time_count"] > 0:
            metrics["response_time_average"] = (
                metrics["response_time_sum"] / metrics["response_time_count"]
            )
        else:
            metrics["response_time_average"] = 0.0

        return metrics

    def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        metrics = self.get_metrics()
        output = "# PageIQ API Metrics\n"

        # Counter metrics
        output += f'# HELP pageiq_requests_total Total number of HTTP requests\n'
        output += f'# TYPE pageiq_requests_total counter\n'
        output += f'pageiq_requests_total {metrics["requests_total"]}\n'

        output += f'# HELP pageiq_errors_total Total number of HTTP errors\n'
        output += f'# TYPE pageiq_errors_total counter\n'
        output += f'pageiq_errors_total {metrics["errors_total"]}\n'

        # Gauge metrics
        output += f'# HELP pageiq_active_connections Number of active connections\n'
        output += f'# TYPE pageiq_active_connections gauge\n'
        output += f'pageiq_active_connections {metrics["active_connections"]}\n'

        # Histogram metrics
        output += f'# HELP pageiq_response_time_seconds Response time histogram\n'
        output += f'# TYPE pageiq_response_time_seconds histogram\n'
        output += f'pageiq_response_time_sum {metrics["response_time_sum"] / 1000:.6f}\n'
        output += f'pageiq_response_time_count {metrics["response_time_count"]}\n'

        # Status code metrics
        for status_code, count in metrics["requests_by_status"].items():
            output += f'pageiq_requests_by_status{{status="{status_code}"}} {count}\n'

        # Endpoint metrics
        for endpoint, count in metrics["requests_by_endpoint"].items():
            method, path = endpoint.split(' ', 1)
            output += f'pageiq_requests_by_endpoint{{method="{method}",endpoint="{path}"}} {count}\n'

        return output

    def reset(self):
        """Reset metrics"""
        self.metrics = {
            "requests_total": 0,
            "requests_by_status": {},
            "requests_by_endpoint": {},
            "response_time_sum": 0.0,
            "response_time_count": 0,
            "errors_total": 0,
            "active_connections": 0,
        }


# Global metrics collector
metrics_collector = MetricsCollector()


class MetricsMiddleware:
    """Middleware for collecting request metrics"""

    def __init__(self, app: Callable):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()

        # Process request
        response_info = {}

        async def capture_response(message):
            if message["type"] == "http.response.start":
                response_info["status_code"] = message["status"]
            await send(message)

        await self.app(scope, receive, capture_response)

        # Record metrics
        processing_time = time.time() - start_time
        endpoint = request.url.path
        method = request.method
        status_code = response_info.get("status_code", 500)

        metrics_collector.record_request(method, endpoint, status_code, processing_time)

        # Record analytics
        try:
            from app.services.analytics import analytics_service
            user_agent = request.headers.get("user-agent")
            client_ip = self._get_client_ip(request)

            analytics_service.track_request(
                user_id=getattr(request.state, 'user_id', None),
                endpoint=endpoint,
                method=method,
                response_time=processing_time * 1000,  # Convert to milliseconds
                status_code=status_code,
                user_agent=user_agent,
                ip_address=client_ip
            )
        except Exception as e:
            logger.error(f"Analytics tracking error: {str(e)}")

    def _get_client_ip(self, request: Request) -> Optional[str]:
        """Get client IP address"""
        # Check forwarded headers
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return getattr(request.client, 'host', None) if request.client else None