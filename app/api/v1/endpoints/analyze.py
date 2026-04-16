import time
import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from bs4 import BeautifulSoup
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.auth import get_optional_user
from app.core.database import get_db
from app.core.errors import QuotaExceededException, validate_url_input, validate_options_input
from app.core.responses import APIResponse
from app.models import User
import app.services as services
from app.services.browser import browser_service
from app.services.browser import playwright_available
from app.services import extractors as extractors_service
from app.services.fetcher import html_fetcher
from app.services.quota import quota_service
from app.services.robots_checker import robots_checker
from app.services.screenshot import screenshot_service
from app.services.analyzer import analyze_url as analyze_url_core
from app.services.analytics import analytics_service

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str  # Will be validated separately
    options: dict = {}

    def __init__(self, **data):
        super().__init__(**data)
        # Validate inputs
        self.url = validate_url_input(self.url)
        self.options = validate_options_input(self.options)

@router.post("")
async def analyze_website(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Analyze a website and return structured business data.
    """
    start_time = time.time()
    request_id = str(uuid.uuid4())

    try:
        # Check quota
        quota_allowed, quota_remaining, quota_limit = quota_service.check_quota(user, db)
        if not quota_allowed:
            reset_info = quota_service.get_quota_info(user, db)
            raise QuotaExceededException(
                remaining=quota_remaining,
                reset_time=reset_info.get('reset_date', '')
            )

        # Run analysis using shared core pipeline.
        options = dict(request.options or {})
        if options.get("screenshot"):
            options["screenshot_filename"] = f"{request_id}.png"

        try:
            data, processing_time = await analyze_url_core(request.url, options)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Track analyzed domain for analytics.
        analytics_service.track_analyzed_url(request.url)

        # Consume quota
        if user:
            quota_service.consume_quota(user, 1, db)

        return APIResponse.success(
            data=data,
            request_id=request_id,
            processing_time_ms=processing_time,
            quota_remaining=quota_remaining - 1 if user else quota_remaining
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.options("")
async def analyze_preflight():
    # Helps simple OPTIONS requests used by tests.
    return {}