from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_optional_user
from app.core.database import get_db
from app.core.errors import QuotaExceededException, validate_url_input, validate_options_input
from app.core.responses import APIResponse
from app.models import User
from app.services.quota import quota_service
from app.services.webhook import webhook_service
from app.services.batch_status import batch_status_store
from app.tasks.batch_tasks import batch_analyze_task

router = APIRouter()

class BatchAnalyzeRequest(BaseModel):
    urls: List[str]
    options: dict = {}
    webhook_url: Optional[str] = None

    def __init__(self, **data):
        super().__init__(**data)
        # Validate URLs
        self.urls = [validate_url_input(url) for url in self.urls]
        self.options = validate_options_input(self.options)

class BatchAnalyzeResponse(BaseModel):
    batch_id: str
    urls_count: int
    estimated_completion_time: int  # seconds
    webhook_url: Optional[str] = None

@router.post("/", response_model=BatchAnalyzeResponse)
async def batch_analyze_websites(
    request: BatchAnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Analyze multiple websites in batch.

    This endpoint is available for Business tier and above.
    Processes up to 100 URLs per request.
    """
    # Check batch size limits
    if len(request.urls) > 100:
        raise HTTPException(
            status_code=400,
            detail="Maximum 100 URLs per batch request"
        )

    if len(request.urls) < 1:
        raise HTTPException(
            status_code=400,
            detail="At least 1 URL required"
        )

    # Check quota for batch operation (each URL costs 1 quota)
    urls_count = len(request.urls)
    quota_allowed, remaining, _ = quota_service.check_quota(user, db)
    if not quota_allowed or remaining < urls_count:
        raise QuotaExceededException(
            remaining=remaining,
            reset_time="monthly reset"
        )

    # Generate batch ID
    batch_id = str(uuid4())

    # Estimate completion time (rough estimate: 5 seconds per URL)
    estimated_time = urls_count * 5

    # Initialize status in Redis and enqueue Celery task.
    batch_status_store.init_batch(batch_id=batch_id, total_count=urls_count, webhook_url=request.webhook_url)
    batch_analyze_task.delay(batch_id=batch_id, urls=request.urls, options=request.options, webhook_url=request.webhook_url)

    return APIResponse.success(
        data={
            "batch_id": batch_id,
            "urls_count": urls_count,
            "estimated_completion_time": estimated_time,
            "webhook_url": request.webhook_url
        },
        message=f"Batch analysis started for {urls_count} URLs"
    )

@router.get("/{batch_id}")
async def get_batch_status(
    batch_id: str,
    page: int = 1,
    page_size: int = 50,
    user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get status of batch analysis job with paginated results.
    """
    status = batch_status_store.get_status(batch_id)
    if not status:
        raise HTTPException(status_code=404, detail="Batch not found")

    # Pagination for results
    limit = min(page_size, 100)
    offset = (page - 1) * limit
    
    results = []
    if status.status in {"completed", "failed", "processing"}:
        results = batch_status_store.get_results(batch_id, limit=limit, offset=offset)

    return APIResponse.success(
        data={
            "batch_id": batch_id,
            "status": status.status,
            "progress": status.progress,
            "completed_count": status.completed_count,
            "failed_count": status.failed_count,
            "total_count": status.total_count,
            "updated_at_ms": status.updated_at_ms,
            "page": page,
            "page_size": len(results),
            "results": results,
            "error": status.last_error,
        }
    )

    # Celery handles processing; see `app/tasks/batch_tasks.py`.