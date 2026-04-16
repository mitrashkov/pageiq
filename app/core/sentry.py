"""
Sentry error tracking and alerting configuration
"""

import os
import logging
from typing import Any, Optional

try:  # pragma: no cover - optional dependency/version differences
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration as FastAPIIntegration  # type: ignore
except Exception:  # pragma: no cover
    sentry_sdk = None  # type: ignore[assignment]
    FastAPIIntegration = None  # type: ignore[assignment]

try:  # pragma: no cover
    from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
except Exception:  # pragma: no cover
    SqlalchemyIntegration = None  # type: ignore[assignment]

try:  # pragma: no cover
    from sentry_sdk.integrations.redis import RedisIntegration
except Exception:  # pragma: no cover
    RedisIntegration = None  # type: ignore[assignment]

try:  # pragma: no cover
    from sentry_sdk.integrations.logging import LoggingIntegration
except Exception:  # pragma: no cover
    LoggingIntegration = None  # type: ignore[assignment]

from app.core.config import settings


def setup_sentry():
    """Initialize Sentry error tracking"""
    if sentry_sdk is None:
        return

    sentry_dsn = os.getenv("SENTRY_DSN")
    environment = os.getenv("ENVIRONMENT", "development")

    if not sentry_dsn:
        # Skip Sentry setup if no DSN provided
        return

    integrations = []
    if FastAPIIntegration is not None:
        integrations.append(
            FastAPIIntegration(
                transaction_style="endpoint",
                http_methods_to_capture=["GET", "POST", "PUT", "DELETE"],
            )
        )
    if SqlalchemyIntegration is not None:
        integrations.append(SqlalchemyIntegration())
    if RedisIntegration is not None:
        integrations.append(RedisIntegration())
    if LoggingIntegration is not None:
        integrations.append(
            LoggingIntegration(
                level=logging.INFO,  # Capture info and above as breadcrumbs
                event_level=logging.ERROR,  # Send errors as events
            )
        )

    sentry_sdk.init(
        dsn=sentry_dsn,
        environment=environment,
        release=os.getenv("RELEASE_VERSION", "1.0.0"),

        # Integrations
        integrations=integrations,

        # Performance monitoring
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
        profiles_sample_rate=float(os.getenv("SENTRY_PROFILES_SAMPLE_RATE", "0.1")),

        # Error tracking
        send_default_pii=False,  # Don't send personally identifiable information
        before_send=before_send_filter,
        before_breadcrumb=before_breadcrumb_filter,

        # Release health
        enable_tracing=True,
        attach_stacktrace=True,
    )


def before_send_filter(event, hint):
    """Filter events before sending to Sentry"""
    # Don't send events in development unless explicitly enabled
    if settings.DEBUG and not os.getenv("SENTRY_DEBUG", "false").lower() == "true":
        return None

    # Filter out certain types of errors
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']

        # Filter out common non-critical errors
        if exc_type in [
            ConnectionError,
            TimeoutError,
            KeyboardInterrupt,
        ]:
            return None

        # Filter out client disconnects
        if hasattr(exc_value, 'args') and exc_value.args:
            error_msg = str(exc_value.args[0]).lower()
            if any(term in error_msg for term in [
                'connection closed',
                'client disconnected',
                'broken pipe',
            ]):
                return None

    return event


def before_breadcrumb_filter(crumb, hint):
    """Filter breadcrumbs before sending to Sentry"""
    # Don't include sensitive data in breadcrumbs
    if crumb.get('category') == 'httpx':
        # Remove sensitive headers
        if 'data' in crumb and 'headers' in crumb['data']:
            headers = crumb['data']['headers']
            sensitive_headers = ['authorization', 'x-api-key', 'cookie']
            for header in sensitive_headers:
                if header in headers:
                    headers[header] = '[FILTERED]'

    return crumb


def capture_exception(exc, **kwargs):
    """Capture an exception with additional context"""
    if sentry_sdk is None:
        return
    with sentry_sdk.configure_scope() as scope:
        for key, value in kwargs.items():
            scope.set_tag(key, str(value))
        sentry_sdk.capture_exception(exc)


def capture_message(message, level='info', **kwargs):
    """Capture a message with additional context"""
    if sentry_sdk is None:
        return
    with sentry_sdk.configure_scope() as scope:
        for key, value in kwargs.items():
            scope.set_tag(key, str(value))
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id=None, email=None, **kwargs):
    """Set user context for error tracking"""
    if sentry_sdk is None:
        return
    with sentry_sdk.configure_scope() as scope:
        if user_id:
            scope.set_user({
                "id": str(user_id),
                "email": email,
                **kwargs
            })


def set_request_context(request_id=None, endpoint=None, **kwargs):
    """Set request context for error tracking"""
    if sentry_sdk is None:
        return
    with sentry_sdk.configure_scope() as scope:
        if request_id:
            scope.set_tag("request_id", request_id)
        if endpoint:
            scope.set_tag("endpoint", endpoint)

        for key, value in kwargs.items():
            scope.set_tag(key, str(value))


# Alerting utilities
class AlertManager:
    """Utilities for sending alerts based on error patterns"""

    @staticmethod
    def alert_high_error_rate(service="pageiq-api", error_rate=None, time_window="5m"):
        """Send alert for high error rate"""
        message = f"High error rate detected in {service}: {error_rate}% in last {time_window}"
        capture_message(message, level='error',
                       service=service,
                       error_rate=error_rate,
                       time_window=time_window)

    @staticmethod
    def alert_performance_degradation(service="pageiq-api", metric=None, threshold=None):
        """Send alert for performance degradation"""
        message = f"Performance degradation in {service}: {metric} exceeded threshold {threshold}"
        capture_message(message, level='warning',
                       service=service,
                       metric=metric,
                       threshold=threshold)

    @staticmethod
    def alert_security_incident(service="pageiq-api", incident_type=None, details=None):
        """Send alert for security incidents"""
        message = f"Security incident detected in {service}: {incident_type}"
        capture_message(message, level='fatal',
                       service=service,
                       incident_type=incident_type,
                       details=details)


# Global alert manager instance
alert_manager = AlertManager()