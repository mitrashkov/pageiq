"""
Enhanced data extraction endpoints for Week 8 features.
"""
import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

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

router = APIRouter()


class ExtractEmailsRequest(BaseModel):
    """Request model for email extraction"""
    url: HttpUrl
    options: dict = {}


class ExtractEmailsResponse(BaseModel):
    """Response model for email extraction"""
    url: str
    emails: List[str]
    count: int
    timestamp: float
    processing_time_ms: int


@router.post("/emails", response_model=ExtractEmailsResponse)
async def extract_emails_endpoint(
    request: ExtractEmailsRequest,
    user: User = Depends(get_optional_user),
):
    """
    Extract email addresses from a webpage.
    
    This endpoint specializes in finding and validating email addresses
    present on a webpage in contact forms, footer, or any text content.
    
    Returns validated, unique email addresses.
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
        
        # Fetch HTML
        html_content, error, _ = html_fetcher.fetch_html(url)
        if error or not html_content:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch webpage: {error}"
            )
        
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if not soup:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse HTML content"
            )
        
        # Extract emails
        emails = extract_emails_service(soup)
        
        # Remove duplicates and sort
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
        
        # Fetch HTML
        html_content, error, _ = html_fetcher.fetch_html(url)
        if error or not html_content:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch webpage: {error}"
            )
        
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if not soup:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse HTML content"
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
        
        # Fetch HTML
        html_content, error, _ = html_fetcher.fetch_html(url)
        if error or not html_content:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch webpage: {error}"
            )
        
        # Parse HTML
        soup = html_fetcher.parse_html(html_content)
        if not soup:
            raise HTTPException(
                status_code=400,
                detail="Failed to parse HTML content"
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
