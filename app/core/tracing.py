"""
OpenTelemetry distributed tracing configuration
"""

import os
from typing import Any, Optional

try:  # pragma: no cover - optional dependency
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
    from opentelemetry.instrumentation.redis import RedisInstrumentor
    from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
except Exception:  # pragma: no cover
    trace = None  # type: ignore[assignment]
    TracerProvider = BatchSpanProcessor = Resource = object  # type: ignore[misc,assignment]
    JaegerExporter = OTLPSpanExporter = object  # type: ignore[misc,assignment]
    FastAPIInstrumentor = SQLAlchemyInstrumentor = RedisInstrumentor = HTTPXClientInstrumentor = object  # type: ignore[misc,assignment]

from app.core.config import settings


def setup_tracing():
    """Initialize OpenTelemetry distributed tracing"""
    if trace is None:
        # Tracing is optional; app must run without opentelemetry installed.
        return

    # Create resource with service information
    resource = Resource.create({
        "service.name": "pageiq-api",
        "service.version": "1.0.0",
        "service.instance.id": os.getenv("HOSTNAME", "localhost"),
        "environment": os.getenv("ENVIRONMENT", "development"),
    })

    # Set up tracer provider
    trace.set_tracer_provider(TracerProvider(resource=resource))

    # Configure span processors based on environment
    if settings.is_production or os.getenv("TRACING_ENABLED", "false").lower() == "true":
        _setup_production_tracing()
    else:
        _setup_development_tracing()

    # Instrument libraries
    _setup_instrumentation()


def _setup_production_tracing():
    """Set up tracing for production environment"""
    if trace is None:
        return

    # Use OTLP exporter for production (works with Jaeger, Zipkin, etc.)
    otlp_exporter = OTLPSpanExporter(
        endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
        insecure=True,  # Set to False in production with proper TLS
    )

    span_processor = BatchSpanProcessor(otlp_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)


def _setup_development_tracing():
    """Set up tracing for development environment"""
    if trace is None:
        return

    # Use Jaeger exporter for development
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv("JAEGER_AGENT_HOST", "localhost"),
        agent_port=int(os.getenv("JAEGER_AGENT_PORT", "6831")),
    )

    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)


def _setup_instrumentation():
    """Set up automatic instrumentation for libraries"""
    if trace is None:
        return

    # Instrument FastAPI
    FastAPIInstrumentor().instrument()

    # Instrument SQLAlchemy (will be done after engine creation)
    # This is handled in the database session setup

    # Instrument Redis
    RedisInstrumentor().instrument()

    # Instrument HTTPX (for outgoing requests)
    HTTPXClientInstrumentor().instrument()


def instrument_sqlalchemy(engine):
    """Instrument SQLAlchemy engine for tracing"""
    if trace is None:
        return
    SQLAlchemyInstrumentor().instrument(engine=engine)


def get_tracer(name: str = "pageiq-api"):
    """Get a tracer instance for manual instrumentation"""
    if trace is None:
        return None
    return trace.get_tracer(name)


# Tracing utilities for manual instrumentation
class TracingUtils:
    """Utilities for manual tracing instrumentation"""

    @staticmethod
    def create_span(name: str, kind: Optional[Any] = None):
        """Create a new span"""
        tracer = get_tracer()
        if tracer is None:
            return _NullSpan()
        return tracer.start_as_current_span(name, kind=kind)

    @staticmethod
    def add_span_attributes(span, **attributes):
        """Add attributes to a span"""
        for key, value in attributes.items():
            span.set_attribute(key, value)

    @staticmethod
    def record_exception(span, exception):
        """Record an exception in a span"""
        if trace is None:
            return
        span.record_exception(exception)
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))

    @staticmethod
    def set_span_status(span, status_code: trace.StatusCode, description: str = ""):
        """Set span status"""
        if trace is None:
            return
        span.set_status(trace.Status(status_code, description))


class _NullSpan:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


# Global tracing utilities instance
tracing_utils = TracingUtils()