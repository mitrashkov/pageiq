from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import asyncio

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import engine
from app.models.base import Base

# Setup logging
setup_logging()

# Setup distributed tracing
from app.core.tracing import setup_tracing, instrument_sqlalchemy
setup_tracing()
instrument_sqlalchemy(engine)

# Setup error tracking
from app.core.sentry import setup_sentry
setup_sentry()

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Website Intelligence API that turns any URL into structured business data",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Disable automatic docs (we provide custom at /docs)
    redoc_url=None,  # Disable automatic redoc
)

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    # Pre-initialize browser service to avoid latency on first request
    from app.services.browser import browser_service
    try:
        # Don't block startup, but start initialization
        asyncio.create_task(browser_service.initialize())
    except Exception as e:
        print(f"Error pre-initializing browser: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    from app.services.browser import browser_service
    await browser_service.cleanup()

# Add exception handlers (requires app instance)
from app.core.errors import (
    PageIQException,
    general_exception_handler,
    http_exception_handler,
    pageiq_exception_handler,
    validation_exception_handler,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PageIQException, pageiq_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Add security middlewares
from app.core.security_headers import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware
)

app.add_middleware(RequestValidationMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Add rate limiting middleware
from app.core.rate_limiter import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware)

# Add request logging and monitoring
from app.core.monitoring import RequestLoggingMiddleware, MetricsMiddleware
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(MetricsMiddleware)

# Include API router with versioning
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include docs and tests endpoints at root level
from app.api.v1.endpoints import docs
app.include_router(docs.router)

# Serve saved screenshots (local dev / default storage)
Path(settings.SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
app.mount(
    settings.SCREENSHOTS_URL_PREFIX.rstrip("/") or "/screenshots",
    StaticFiles(directory=settings.SCREENSHOTS_DIR),
    name="screenshots",
)

# Add API version header to all responses
@app.middleware("http")
async def add_api_version_header(request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = "v1"
    return response

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {"status": "healthy", "service": "PageIQ API", "version": "1.0.0"}


@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with dependency checks"""
    from app.core.redis import get_redis
    from app.db.session import SessionLocal

    health_status = {
        "status": "healthy",
        "service": "PageIQ API",
        "version": "1.0.0",
        "timestamp": "2026-04-16T18:30:00Z",
        "checks": {}
    }

    # Database check
    try:
        db = SessionLocal()
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        health_status["checks"]["database"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["checks"]["database"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"

    # Redis check
    try:
        redis_client = get_redis()
        redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy", "message": "Connected"}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "message": str(e)}
        health_status["status"] = "unhealthy"

    # Application check
    health_status["checks"]["application"] = {
        "status": "healthy",
        "message": "Application running",
        "uptime": "N/A"  # Could be enhanced with actual uptime tracking
    }

    return health_status


@app.get("/metrics")
async def metrics_endpoint():
    """Metrics endpoint for monitoring (Prometheus-compatible)"""
    from app.core.monitoring import metrics_collector

    metrics = metrics_collector.get_metrics()

    # Format as Prometheus metrics
    prometheus_output = "# PageIQ API Metrics\n"

    for key, value in metrics.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                metric_name = f"pageiq_{key}_{sub_key}".replace(" ", "_").lower()
                prometheus_output += f"{metric_name} {sub_value}\n"
        else:
            metric_name = f"pageiq_{key}".replace(" ", "_").lower()
            prometheus_output += f"{metric_name} {value}\n"

    return prometheus_output


@app.get("/status")
async def status_endpoint():
    """System status endpoint"""
    from app.core.monitoring import metrics_collector

    metrics = metrics_collector.get_metrics()

    return {
        "service": "PageIQ API",
        "status": "operational",
        "metrics": metrics,
        "last_updated": "2026-04-16T18:30:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)