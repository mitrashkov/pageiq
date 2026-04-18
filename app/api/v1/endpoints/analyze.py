import time
import uuid
from typing import List

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
from app.core.cache import get_cached_response, set_cached_response, generate_cache_key

router = APIRouter()

class AnalyzeRequest(BaseModel):
    url: str  # Will be validated separately
    options: dict = {}

    def __init__(self, **data):
        super().__init__(**data)
        # Validate inputs
        self.url = validate_url_input(self.url)
        self.options = validate_options_input(self.options)

class TechDetectionResponse(BaseModel):
    """Response model for tech detection"""
    url: str
    technologies: List[str]
    timestamp: float
    processing_time_ms: int

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

    # 1. Check Cache first
    options = dict(request.options or {})
    cache_key = generate_cache_key("analyze", url=request.url, **options)
    
    # Only use cache if no fresh analysis is explicitly requested (can add an option for this)
    if not options.get("refresh_cache"):
        cached_data = await get_cached_response(cache_key)
        if cached_data:
            return APIResponse.success(
                data=cached_data,
                request_id=f"cached_{request_id}",
                processing_time_ms=0,
                quota_remaining=quota_service.get_quota_info(user, db).get('remaining', 0) if user else 0
            )

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

        # Inject user plan into options for service-level gating
        options["user_plan"] = getattr(user, "plan", "free").lower()

        try:
            data, processing_time = await analyze_url_core(request.url, options)
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Track analyzed domain for analytics.
        analytics_service.track_analyzed_url(request.url)

        # 2. Store in cache
        await set_cached_response(cache_key, data)

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


@router.post("/tech", response_model=TechDetectionResponse)
async def detect_tech_endpoint(
    request: AnalyzeRequest,
    user: User = Depends(get_optional_user),
):
    """
    Detect technology stack, CMS, and tracking pixels for a website.
    """
    start_time = time.time()
    url = str(validate_url_input(str(request.url)))
    options = validate_options_input(request.options)
    use_browser = bool(options.get("use_browser", False))
    
    try:
        # Fetch HTML
        html_content, error, headers = await html_fetcher.fetch_html_async(url, use_browser=use_browser)
        if error or not html_content:
            raise HTTPException(status_code=400, detail=f"Failed to fetch webpage: {error}")
            
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if soup is None:
            raise HTTPException(status_code=400, detail="Failed to parse HTML content")
            
        # Detect Tech
        from app.services.tech_detector import tech_detector
        tech_stack = tech_detector.detect_technologies(soup, html_content, headers)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return TechDetectionResponse(
            url=url,
            technologies=tech_stack,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting tech: {str(e)}")


@router.options("")
async def analyze_preflight():
    # Helps simple OPTIONS requests used by tests.
    return {}