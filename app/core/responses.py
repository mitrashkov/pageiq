import time
from typing import Any, Dict, Optional

from fastapi.responses import JSONResponse

from app.core.config import settings


class APIResponse:
    """Standardized API response formatter"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = None,
        request_id: str = None,
        processing_time_ms: Optional[int] = None,
        quota_remaining: Optional[int] = None
    ) -> JSONResponse:
        """Create successful response"""
        response_data = {
            "success": True,
        }

        if data is not None:
            response_data["data"] = data

        if message:
            response_data["message"] = message

        if request_id:
            response_data["request_id"] = request_id

        if processing_time_ms is not None:
            response_data["processing_time_ms"] = processing_time_ms

        if quota_remaining is not None:
            response_data["quota_remaining"] = quota_remaining

        response = JSONResponse(
            status_code=200,
            content=response_data
        )

        # Add standard headers
        response.headers["X-API-Version"] = settings.API_V1_STR
        if request_id:
            response.headers["X-Request-ID"] = request_id
        if processing_time_ms is not None:
            response.headers["X-Processing-Time-MS"] = str(processing_time_ms)

        return response

    @staticmethod
    def error(
        message: str,
        error_code: str = None,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create error response"""
        response_data = {
            "success": False,
            "error": {
                "message": message,
            }
        }

        if error_code:
            response_data["error"]["code"] = error_code

        if details:
            response_data["error"]["details"] = details

        if request_id:
            response_data["request_id"] = request_id

        response = JSONResponse(
            status_code=status_code,
            content=response_data
        )

        # Add standard headers
        response.headers["X-API-Version"] = settings.API_V1_STR
        if request_id:
            response.headers["X-Request-ID"] = request_id

        return response

    @staticmethod
    def paginated(
        items: list,
        total: int,
        page: int,
        page_size: int,
        request_id: Optional[str] = None
    ) -> JSONResponse:
        """Create paginated response"""
        response_data = {
            "success": True,
            "data": items,
            "pagination": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }
        }

        if request_id:
            response_data["request_id"] = request_id

        response = JSONResponse(
            status_code=200,
            content=response_data
        )

        response.headers["X-API-Version"] = settings.API_V1_STR
        if request_id:
            response.headers["X-Request-ID"] = request_id

        return response


class ResponseHeaders:
    """Utilities for adding response headers"""

    @staticmethod
    def add_rate_limit_headers(response: JSONResponse, remaining: int, reset_time: float):
        """Add rate limit headers to response"""
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)

    @staticmethod
    def add_quota_headers(response: JSONResponse, remaining: int, limit: int, reset_date: str):
        """Add quota headers to response"""
        response.headers["X-Quota-Remaining"] = str(remaining)
        response.headers["X-Quota-Limit"] = str(limit)
        response.headers["X-Quota-Reset"] = reset_date

    @staticmethod
    def add_cors_headers(response: JSONResponse):
        """Add CORS headers to response"""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, X-Requested-With"

    @staticmethod
    def add_security_headers(response: JSONResponse):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

    @staticmethod
    def add_cache_headers(response: JSONResponse, cache_control: str = "no-cache"):
        """Add cache control headers"""
        response.headers["Cache-Control"] = cache_control