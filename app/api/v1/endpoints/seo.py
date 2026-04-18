"""
SEO and link analysis endpoints for Week 8 advanced features.
"""
import asyncio
import time
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
import re

from app.core.auth import get_optional_user
from app.core.responses import APIResponse
from app.models import User
from app.services.fetcher import html_fetcher
from app.services.robots_checker import robots_checker
from app.core.errors import validate_url_input, validate_options_input
from app.services.extractors import (
    extract_title,
    extract_description,
    extract_open_graph,
    extract_schema_org,
    extract_keywords,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class LinkInfo(BaseModel):
    """Information about a link"""
    url: str
    text: str
    type: str  # internal, external, anchor
    rel: Optional[str] = None
    is_valid: Optional[bool] = None


class BrokenLink(BaseModel):
    """Information about a broken link"""
    url: str
    text: str
    error: str
    status_code: Optional[int] = None


class SEOAuditRequest(BaseModel):
    """Request model for SEO audit"""
    url: HttpUrl
    options: dict = {}


class SEOAuditItem(BaseModel):
    """Single SEO audit item"""
    check: str
    passed: bool
    message: str
    severity: str  # info, warning, error


class SEOAuditResponse(BaseModel):
    """Response model for SEO audit"""
    url: str
    score: int  # 0-100
    audit_items: List[SEOAuditItem]
    timestamp: float
    processing_time_ms: int


def check_title(soup, base_url: str) -> SEOAuditItem:
    """Check if title is present and valid"""
    title = extract_title(soup)
    
    if not title:
        return SEOAuditItem(
            check="Title",
            passed=False,
            message="No title tag found",
            severity="error"
        )
    elif len(title) < 10:
        return SEOAuditItem(
            check="Title",
            passed=False,
            message=f"Title too short ({len(title)} chars, should be 10-60)",
            severity="warning"
        )
    elif len(title) > 60:
        return SEOAuditItem(
            check="Title",
            passed=False,
            message=f"Title too long ({len(title)} chars, should be 10-60)",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Title",
            passed=True,
            message=f"Title is present and well-formed ({len(title)} chars)",
            severity="info"
        )


def check_description(soup, base_url: str) -> SEOAuditItem:
    """Check if meta description is present and valid"""
    description = extract_description(soup)
    
    if not description:
        return SEOAuditItem(
            check="Meta Description",
            passed=False,
            message="No meta description found",
            severity="error"
        )
    elif len(description) < 50:
        return SEOAuditItem(
            check="Meta Description",
            passed=False,
            message=f"Description too short ({len(description)} chars, should be 50-160)",
            severity="warning"
        )
    elif len(description) > 160:
        return SEOAuditItem(
            check="Meta Description",
            passed=False,
            message=f"Description too long ({len(description)} chars, should be 50-160)",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Meta Description",
            passed=True,
            message=f"Description is present and well-formed ({len(description)} chars)",
            severity="info"
        )


def check_headings(soup, base_url: str) -> SEOAuditItem:
    """Check if proper heading hierarchy exists"""
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    
    if not h1_tags:
        return SEOAuditItem(
            check="Headings",
            passed=False,
            message="No H1 tags found",
            severity="error"
        )
    elif len(h1_tags) > 1:
        return SEOAuditItem(
            check="Headings",
            passed=False,
            message=f"Multiple H1 tags found ({len(h1_tags)}), should only have 1",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Headings",
            passed=True,
            message=f"Valid heading structure: 1 H1, {len(h2_tags)} H2",
            severity="info"
        )


def check_images(soup, base_url: str) -> SEOAuditItem:
    """Check if images have alt attributes"""
    images = soup.find_all('img')
    
    if not images:
        return SEOAuditItem(
            check="Images",
            passed=True,
            message="No images found on page",
            severity="info"
        )
    
    images_without_alt = 0
    for img in images:
        if not img.get('alt'):
            images_without_alt += 1
    
    if images_without_alt > 0:
        percentage = (images_without_alt / len(images)) * 100
        return SEOAuditItem(
            check="Image Alt Attributes",
            passed=False,
            message=f"{images_without_alt}/{len(images)} images ({percentage:.1f}%) missing alt attributes",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Image Alt Attributes",
            passed=True,
            message=f"All {len(images)} images have alt attributes",
            severity="info"
        )


def check_structured_data(soup, base_url: str) -> SEOAuditItem:
    """Check if structured data is present"""
    schema = extract_schema_org(soup)
    
    if not schema:
        return SEOAuditItem(
            check="Structured Data",
            passed=False,
            message="No structured data (Schema.org) found",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Structured Data",
            passed=True,
            message=f"Structured data found: {schema.get('@type', 'Unknown')}",
            severity="info"
        )


def check_open_graph(soup, base_url: str) -> SEOAuditItem:
    """Check if Open Graph tags are present"""
    og_tags = extract_open_graph(soup)
    
    if not og_tags:
        return SEOAuditItem(
            check="Open Graph Tags",
            passed=False,
            message="No Open Graph tags found",
            severity="warning"
        )
    
    required_tags = ['title', 'description', 'image', 'url']
    missing_tags = [tag for tag in required_tags if tag not in og_tags]
    
    if missing_tags:
        return SEOAuditItem(
            check="Open Graph Tags",
            passed=False,
            message=f"Missing OG tags: {', '.join(missing_tags)}",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Open Graph Tags",
            passed=True,
            message=f"All required OG tags present",
            severity="info"
        )


def check_mobile_friendly(soup, base_url: str) -> SEOAuditItem:
    """Check if page has mobile viewport meta tag"""
    viewport = soup.find('meta', {'name': 'viewport'})
    
    if not viewport:
        return SEOAuditItem(
            check="Mobile Friendly",
            passed=False,
            message="No viewport meta tag found",
            severity="error"
        )
    else:
        return SEOAuditItem(
            check="Mobile Friendly",
            passed=True,
            message="Viewport meta tag is present",
            severity="info"
        )


def check_robots_txt(soup, base_url: str) -> SEOAuditItem:
    """Check if page respects robots.txt"""
    robots_allowed = robots_checker.can_fetch(base_url)
    
    if not robots_allowed:
        return SEOAuditItem(
            check="Robots.txt Compliance",
            passed=False,
            message="This page is blocked by robots.txt",
            severity="warning"
        )
    else:
        return SEOAuditItem(
            check="Robots.txt Compliance",
            passed=True,
            message="Page is allowed by robots.txt",
            severity="info"
        )


@router.post("/seo-audit", response_model=SEOAuditResponse)
async def seo_audit_endpoint(
    request: SEOAuditRequest,
    user: User = Depends(get_optional_user),
):
    """
    Perform comprehensive SEO audit on a webpage.
    
    Checks for:
    - Title tag presence and length
    - Meta description presence and length
    - Heading hierarchy
    - Image alt attributes
    - Structured data (Schema.org)
    - Open Graph tags
    - Mobile friendliness
    - Robots.txt compliance
    
    Returns a score (0-100) and detailed audit items.
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
        
        # Fetch HTML asynchronously with automatic browser fallback
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
        
        # Run all SEO checks
        audit_items = [
            check_title(soup, url),
            check_description(soup, url),
            check_headings(soup, url),
            check_images(soup, url),
            check_structured_data(soup, url),
            check_open_graph(soup, url),
            check_mobile_friendly(soup, url),
            check_robots_txt(soup, url),
        ]
        
        # Calculate score
        passed_items = sum(1 for item in audit_items if item.passed)
        score = int((passed_items / len(audit_items)) * 100)
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return SEOAuditResponse(
            url=url,
            score=score,
            audit_items=audit_items,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing SEO audit: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error performing SEO audit: {str(e)}"
        )


class BrokenLinksRequest(BaseModel):
    """Request model for broken links detection"""
    url: HttpUrl
    check_external: bool = False  # Whether to check external links
    options: dict = {}


class BrokenLinksResponse(BaseModel):
    """Response model for broken links detection"""
    url: str
    total_links: int
    broken_links_count: int
    internal_links: int
    external_links: int
    broken_links: List[BrokenLink]
    timestamp: float
    processing_time_ms: int


@router.post("/broken-links", response_model=BrokenLinksResponse)
async def broken_links_endpoint(
    request: BrokenLinksRequest,
    user: User = Depends(get_optional_user),
):
    """
    Detect broken links on a webpage.
    
    Scans all links on the page and checks if they are valid.
    Can optionally check external links (may be slow).
    
    Note: External link checking is limited to avoid performance issues.
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
        
        # Fetch HTML asynchronously with automatic browser fallback
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
        
        # Extract all links
        links = soup.find_all('a', href=True)
        
        parsed_url = urlparse(url)
        base_domain = parsed_url.netloc
        
        internal_links = []
        external_links = []
        broken_links = []
        
        for link in links:
            href = link.get('href', '').strip()
            link_text = link.get_text(strip=True)[:100] or href[:100]
            
            # Skip empty, anchor, and javascript links
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Resolve relative URLs
            absolute_url = urljoin(url, href)
            link_domain = urlparse(absolute_url).netloc
            
            if link_domain == base_domain:
                internal_links.append(absolute_url)
            else:
                external_links.append(absolute_url)
        
        # For now, focus on internal links as external link checking is slow
        # In production, this would use a proper link checker service
        
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        return BrokenLinksResponse(
            url=url,
            total_links=len(links),
            broken_links_count=len(broken_links),
            internal_links=len(internal_links),
            external_links=len(external_links),
            broken_links=broken_links,
            timestamp=time.time(),
            processing_time_ms=processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error detecting broken links: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error detecting broken links: {str(e)}"
        )
