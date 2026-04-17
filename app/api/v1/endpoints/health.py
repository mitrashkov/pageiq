from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PageIQ API"}

@router.get("/ping", methods=["GET", "HEAD"])
async def ping():
    """Simple ping endpoint for monitoring"""
    return {"status": "ok", "message": "pong"}