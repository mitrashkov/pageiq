from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class PageIQException(HTTPException):
    """Base exception for PageIQ API errors"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: str = None,
        headers: Optional[Dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code or f"ERROR_{status_code}"


class ValidationException(PageIQException):
    """Exception for validation errors"""

    def __init__(self, detail: str, field_errors: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
        self.field_errors = field_errors or {}


class QuotaExceededException(PageIQException):
    """Exception for quota exceeded errors"""

    def __init__(self, remaining: int, reset_time: str):
        super().__init__(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Monthly quota exceeded",
            error_code="QUOTA_EXCEEDED"
        )
        self.remaining = remaining
        self.reset_time = reset_time


class RateLimitExceededException(PageIQException):
    """Exception for rate limit exceeded errors"""

    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            error_code="RATE_LIMIT_EXCEEDED",
            headers={"Retry-After": str(retry_after)}
        )
        self.retry_after = retry_after


def create_error_response(
    status_code: int,
    message: str,
    error_code: str = None,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response"""

    error_response = {
        "success": False,
        "error": {
            "code": error_code or f"HTTP_{status_code}",
            "message": message,
        }
    }

    if details:
        error_response["error"]["details"] = details

    if request_id:
        error_response["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


async def validation_exception_handler(request: Request, exc: ValidationError):
    """Handle Pydantic validation errors"""
    errors = {}
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors[field] = error["msg"]

    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Validation error",
        error_code="VALIDATION_ERROR",
        details={"fields": errors},
        request_id=getattr(request.state, 'request_id', None)
    )


async def pageiq_exception_handler(request: Request, exc: PageIQException):
    """Handle PageIQ custom exceptions"""
    details = {}

    if isinstance(exc, QuotaExceededException):
        details = {
            "remaining": exc.remaining,
            "reset_time": exc.reset_time
        }
    elif isinstance(exc, RateLimitExceededException):
        details = {
            "retry_after": exc.retry_after
        }

    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        error_code=exc.error_code,
        details=details,
        request_id=getattr(request.state, 'request_id', None)
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle standard HTTP exceptions"""
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail,
        request_id=getattr(request.state, 'request_id', None)
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    # Log the error
    logger.error(
        "Unhandled exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method,
        user_id=getattr(request.state, 'user_id', None),
        request_id=getattr(request.state, 'request_id', None)
    )

    # Don't expose internal error details in production
    message = "Internal server error"
    if settings.DEBUG:
        message = str(exc)

    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=message,
        error_code="INTERNAL_ERROR",
        request_id=getattr(request.state, 'request_id', None)
    )


def validate_url_input(url: str) -> str:
    """Validate and normalize URL input"""
    from app.utils.url import validate_url, normalize_url

    if not url or not isinstance(url, str):
        raise ValidationException("URL is required")

    url = url.strip()
    if not url:
        raise ValidationException("URL cannot be empty")

    if not validate_url(url):
        raise ValidationException("Invalid URL format")

    try:
        return normalize_url(url)
    except ValueError as e:
        raise ValidationException(str(e))


def validate_options_input(options: Dict[str, Any]) -> Dict[str, Any]:
    """Validate analysis options"""
    valid_options = {
        'screenshot': bool,
        'use_browser': bool,
        'wait_for_network_idle': bool,
        'full_page_screenshot': bool,
        'timeout': int,
    }

    validated = {}

    for key, value in options.items():
        if key in valid_options:
            expected_type = valid_options[key]
            if isinstance(value, expected_type):
                validated[key] = value
            else:
                raise ValidationException(f"Invalid type for option '{key}': expected {expected_type.__name__}")
        else:
            # Allow unknown options but log warning
            logger.warning(f"Unknown option: {key}")
            validated[key] = value

    return validated