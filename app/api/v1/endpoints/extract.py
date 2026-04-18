"""
Enhanced data extraction endpoints for Week 8 features.
"""
import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl, Field

from app.core.auth import get_optional_user
from app.core.responses import APIResponse
from app.models import User
from app.services.fetcher import html_fetcher
from app.services.robots_checker import robots_checker
from app.core.errors import validate_url_input, validate_options_input
from app.services.extractors import (
    extract_emails as extract_emails_service,
    extract_schema_org,
    extract_open_graph,
    extract_description,
    extract_title,
)
from app.services.email_crawler import email_crawler

router = APIRouter()


class ExtractEmailsRequest(BaseModel):
    """Request model for email extraction"""
    url: HttpUrl = Field(..., description="The URL of the website to extract emails from")
    options: dict = Field(default_factory=dict, description="Extraction options including deep_search and pages_limit")


class ExtractEmailsResponse(BaseModel):
    """Response model for email extraction"""
    url: str
    emails: List[str]
    count: int
    timestamp: float
    processing_time_ms: int


class ExtractSchemaResponse(BaseModel):
    """Response model for schema extraction"""
    url: str
    schema_org: Optional[Dict[str, Any]]
    timestamp: float
    processing_time_ms: int


@router.post("/emails", response_model=ExtractEmailsResponse)
async def extract_emails_endpoint(
    request: ExtractEmailsRequest,
    user: User = Depends(get_optional_user),
):
    """
    Extract email addresses from a website.
    
    This endpoint specializes in finding and validating email addresses.
    By default, it searches the provided URL. Set 'deep_search': true 
    in options to crawl the entire website (up to 10 pages by default).
    
    Options:
    - deep_search: bool (default: false)
    - pages_limit: int (default: 10, max: 20)
    """
    start_time = time.time()
    url = str(validate_url_input(str(request.url)))
    options = validate_options_input(request.options)
    
    deep_search = bool(options.get("deep_search", False))
    use_browser = bool(options.get("use_browser", False))
    pages_limit = min(int(options.get("pages_limit", 10)), 20)  # Cap at 20 pages for performance
    
    # Plan check: Deep search is only for PRO, ULTRA, and MEGA plans
    if deep_search:
        user_plan = getattr(user, "plan", "free").lower()
        # Deep search restricted to Pro, Ultra, and Mega
        premium_plans = ["pro", "ultra", "mega"]
        
        if user_plan not in premium_plans:
            raise HTTPException(
                status_code=403,
                detail=f"Deep Search is a Premium Feature. Upgrade to PRO, ULTRA, or MEGA to crawl entire websites. Current plan: {user_plan.upper()}"
            )
        
        # MASSIVE LIMITS for High Tiers (Matched to pricing table)
        if user_plan == "mega":
            # MEGA: 500/Month quota, but we allow deep crawl up to 500 pages per request for extreme lead gen
            pages_limit = min(int(options.get("pages_limit", 100)), 500)
        elif user_plan == "ultra":
            # ULTRA: 150/Month quota, deep crawl up to 150 pages
            pages_limit = min(int(options.get("pages_limit", 50)), 150)
        elif user_plan == "pro":
            # PRO: 50/Month quota, deep crawl up to 50 pages
            pages_limit = min(int(options.get("pages_limit", 20)), 50)

    # JS Rendering check: Only for PRO, ULTRA, and MEGA
    if use_browser:
        user_plan = getattr(user, "plan", "free").lower()
        if user_plan not in ["pro", "ultra", "mega"]:
            raise HTTPException(
                status_code=403,
                detail=f"JavaScript Rendering (use_browser) is a PRO/ULTRA/MEGA feature. Current plan: {user_plan.upper()}"
            )

    try:
        if deep_search:
            # Deep search across multiple pages
            emails = await email_crawler.crawl_website(url, max_pages=pages_limit, use_browser=use_browser)
        else:
            # Standard single-page extraction
            # Check robots.txt
            if not robots_checker.can_fetch(url):
                raise HTTPException(
                    status_code=403,
                    detail="Crawling not allowed by robots.txt"
                )
            
            # Fetch HTML asynchronously (supports browser)
            html_content, error, _ = await html_fetcher.fetch_html_async(url, use_browser=use_browser)
            if error or not html_content:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch webpage: {error}"
                )
            
            # Parse HTML
            soup = html_fetcher.parse_html(html_content)
            if soup is None:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to parse HTML content. The website might be using a non-standard format."
                )
            
            # Extract emails
            emails = extract_emails_service(soup)
        
        # Remove duplicates and sort (already handled by crawler but good for single-page)
        emails = sorted(list(set(emails)))
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ExtractEmailsResponse(
            url=url,
            emails=emails,
            count=len(emails),
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting emails: {str(e)}"
        )


@router.post("/schema", response_model=ExtractSchemaResponse)
async def extract_schema_endpoint(
    request: ExtractEmailsRequest, # Reuse model for URL/options
    user: User = Depends(get_optional_user),
):
    """
    Extract Schema.org structured data from a website.
    
    This endpoint finds and parses JSON-LD or Microdata structured content.
    """
    start_time = time.time()
    url = str(validate_url_input(str(request.url)))
    options = validate_options_input(request.options)
    use_browser = bool(options.get("use_browser", False))
    
    try:
        # Fetch HTML asynchronously
        html_content, error, _ = await html_fetcher.fetch_html_async(url, use_browser=use_browser)
        if error or not html_content:
            raise HTTPException(status_code=400, detail=f"Failed to fetch webpage: {error}")
            
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if soup is None:
            raise HTTPException(status_code=400, detail="Failed to parse HTML content")
            
        # Extract Schema
        schema_data = extract_schema_org(soup)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ExtractSchemaResponse(
            url=url,
            schema_org=schema_data,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting schema: {str(e)}")


class ExtractSchemaRequest(BaseModel):
    """Request model for Schema.org extraction"""
    url: HttpUrl
    options: dict = {}


class ExtractSchemaResponse(BaseModel):
    """Response model for Schema.org extraction"""
    url: str
    schema_org: Optional[dict]
    og_tags: Optional[dict]
    timestamp: float
    processing_time_ms: int


@router.post("/schema", response_model=ExtractSchemaResponse)
async def extract_schema_endpoint(
    request: ExtractSchemaRequest,
    user: User = Depends(get_optional_user),
):
    """
    Extract Schema.org structured data and Open Graph tags.
    
    This endpoint extracts machine-readable structured data
    including JSON-LD and microdata formats.
    """
    start_time = time.time()
    url = str(validate_url_input(str(request.url)))
    options = validate_options_input(request.options)
    
    try:
        # Check robots.txt
        if not robots_checker.can_fetch(url):
            raise HTTPException(
                status_code=403,
                detail="Crawling not allowed by robots.txt"
            )
        
        # Fetch HTML asynchronously (supports browser)
        use_browser = bool(options.get("use_browser", False))
        html_content, error, _ = await html_fetcher.fetch_html_async(url, use_browser=use_browser)
        if error or not html_content:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch webpage: {error}"
            )
        
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if soup is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse HTML content. The website might be using a non-standard format."
            )
        
        # Extract schema.org data
        schema_org = extract_schema_org(soup)
        
        # Extract Open Graph tags
        og_tags = extract_open_graph(soup)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return ExtractSchemaResponse(
            url=url,
            schema_org=schema_org,
            og_tags=og_tags,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting schema data: {str(e)}"
        )


class MetadataExtractRequest(BaseModel):
    """Request model for metadata extraction"""
    url: HttpUrl
    options: dict = {}


class MetadataExtractResponse(BaseModel):
    """Response model for metadata extraction"""
    url: str
    title: Optional[str]
    description: Optional[str]
    schema_org: Optional[dict]
    og_tags: Optional[dict]
    timestamp: float
    processing_time_ms: int


@router.post("/metadata", response_model=MetadataExtractResponse)
async def extract_metadata_endpoint(
    request: MetadataExtractRequest,
    user: User = Depends(get_optional_user),
):
    """
    Extract all metadata from a webpage.
    
    Combines title, description, schema.org data, and Open Graph tags
    for comprehensive metadata retrieval.
    """
    start_time = time.time()
    url = str(validate_url_input(str(request.url)))
    options = validate_options_input(request.options)
    
    try:
        # Check robots.txt
        if not robots_checker.can_fetch(url):
            raise HTTPException(
                status_code=403,
                detail="Crawling not allowed by robots.txt"
            )
        
        # Fetch HTML asynchronously (supports browser)
        use_browser = bool(options.get("use_browser", False))
        html_content, error, _ = await html_fetcher.fetch_html_async(url, use_browser=use_browser)
        if error or not html_content:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch webpage: {error}"
            )
        
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if soup is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse HTML content. The website might be using a non-standard format."
            )
        
        # Extract all metadata
        title = extract_title(soup)
        description = extract_description(soup)
        schema_org = extract_schema_org(soup)
        og_tags = extract_open_graph(soup)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return MetadataExtractResponse(
            url=url,
            title=title,
            description=description,
            schema_org=schema_org,
            og_tags=og_tags,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting metadata: {str(e)}"
        )
