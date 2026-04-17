from fastapi import APIRouter

from app.api.v1.endpoints import analyze, analytics, batch, health, extract, seo, billing

api_router = APIRouter()

# Include endpoints
api_router.include_router(health.router, tags=["health"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analysis"])
api_router.include_router(batch.router, prefix="/batch-analyze", tags=["batch"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(extract.router, prefix="/extract", tags=["extraction"])
api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
api_router.include_router(billing.router, prefix="/account", tags=["billing"])