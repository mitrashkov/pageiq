from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.core.auth import get_optional_user
from app.core.responses import APIResponse
from app.models import User
from app.services.analytics import analytics_service

router = APIRouter()

@router.get("/")
async def get_usage_analytics(
    days: int = Query(7, description="Number of days to look back", ge=1, le=90),
    user: Optional[User] = Depends(get_optional_user)
):
    """
    Get usage analytics for the API.

    This endpoint provides insights into API usage patterns,
    popular endpoints, performance metrics, etc.
    """
    # Get general usage stats
    usage_stats = analytics_service.get_usage_stats(days=days)

    # Get popular domains (if we were tracking them)
    popular_domains = analytics_service.get_popular_domains(days=days)

    # Get performance metrics
    performance_metrics = analytics_service.get_performance_metrics(days=days)

    # Combine all analytics
    analytics = {
        "usage_stats": usage_stats,
        "popular_domains": popular_domains,
        "performance_metrics": performance_metrics,
        "generated_at": "2026-04-16T19:20:00Z"
    }

    return APIResponse.success(
        data=analytics,
        message=f"Analytics for the last {days} days"
    )

@router.get("/performance")
async def get_performance_metrics(
    days: int = Query(7, description="Number of days to look back", ge=1, le=90)
):
    """
    Get detailed performance metrics.

    Includes response times, error rates, uptime, etc.
    """
    metrics = analytics_service.get_performance_metrics(days=days)

    return APIResponse.success(
        data=metrics,
        message=f"Performance metrics for the last {days} days"
    )

@router.get("/endpoints")
async def get_endpoint_usage(
    days: int = Query(7, description="Number of days to look back", ge=1, le=90)
):
    """
    Get usage statistics by endpoint.

    Shows which endpoints are most popular and their performance.
    """
    usage_stats = analytics_service.get_usage_stats(days=days)

    endpoint_data = {
        "total_endpoints": len(usage_stats.get("requests_by_endpoint", {})),
        "endpoint_usage": usage_stats.get("requests_by_endpoint", {}),
        "top_endpoints": usage_stats.get("top_endpoints", [])
    }

    return APIResponse.success(
        data=endpoint_data,
        message=f"Endpoint usage for the last {days} days"
    )