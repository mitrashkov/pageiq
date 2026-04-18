import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.redis import get_redis, test_redis_connection
from app.db.session import engine

router = APIRouter()

@router.get("/")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for production monitoring"""
    start_time = time.time()
    
    # Check Database
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check Redis
    redis_status = "healthy" if test_redis_connection() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "service": "PageIQ API",
        "timestamp": time.time(),
        "latency_ms": int((time.time() - start_time) * 1000),
        "dependencies": {
            "database": db_status,
            "redis": redis_status
        }
    }

@router.get("/ping")
async def ping():
    """Simple ping endpoint for monitoring"""
    return {"status": "ok", "message": "pong"}