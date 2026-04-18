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
    score: int  # 0-100
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
            score=0,
            message="No title tag found. Title is the most important on-page SEO element.",
            severity="error"
        )
    
    length = len(title)
    # Optimal length: 50-60 characters
    if 50 <= length <= 60:
        score = 100
        message = f"Optimal title length ({length} chars). Your title is perfect for search results."
        passed = True
        severity = "info"
    elif 30 <= length < 50:
        score = 85
        message = f"Good title length ({length} chars). A bit longer (up to 60) might allow more keywords."
        passed = True
        severity = "info"
    elif 10 <= length < 30:
        score = 60
        message = f"Title is short ({length} chars). Try adding more relevant keywords."
        passed = True
        severity = "warning"
    elif 60 < length <= 80:
        score = 75
        message = f"Title is a bit long ({length} chars). It may be truncated in search results (max ~60)."
        passed = True
        severity = "warning"
    else:
        score = 40
        message = f"Suboptimal title length ({length} chars). Aim for 50-60 characters."
        passed = False
        severity = "error"

    return SEOAuditItem(
        check="Title",
        passed=passed,
        score=score,
        message=message,
        severity=severity
    )


def check_description(soup, base_url: str) -> SEOAuditItem:
    """Check if meta description is present and valid"""
    description = extract_description(soup)
    
    if not description:
        return SEOAuditItem(
            check="Meta Description",
            passed=False,
            score=0,
            message="No meta description found. Descriptions improve CTR from search results.",
            severity="error"
        )
    
    length = len(description)
    # Optimal length: 120-160 characters
    if 120 <= length <= 160:
        score = 100
        message = f"Perfect meta description length ({length} chars)."
        passed = True
        severity = "info"
    elif 80 <= length < 120:
        score = 85
        message = f"Good length ({length} chars). Adding a bit more detail (up to 160) might help."
        passed = True
        severity = "info"
    elif 50 <= length < 80:
        score = 65
        message = f"Description is short ({length} chars). Use the space to explain your value proposition."
        passed = True
        severity = "warning"
    elif 160 < length <= 230:
        score = 70
        message = f"Description is a bit long ({length} chars). It will be truncated in search results."
        passed = True
        severity = "warning"
    else:
        score = 40
        message = f"Suboptimal description length ({length} chars). Aim for 120-160 characters."
        passed = False
        severity = "error"

    return SEOAuditItem(
        check="Meta Description",
        passed=passed,
        score=score,
        message=message,
        severity=severity
    )


def check_headings(soup, base_url: str) -> SEOAuditItem:
    """Check if proper heading hierarchy exists"""
    h1_tags = soup.find_all('h1')
    h2_tags = soup.find_all('h2')
    h3_tags = soup.find_all('h3')
    
    score = 100
    messages = []
    severity = "info"
    
    if not h1_tags:
        score -= 50
        messages.append("Missing H1 tag. Your page should have exactly one H1 tag.")
        severity = "error"
    elif len(h1_tags) > 1:
        score -= 20
        messages.append(f"Multiple H1 tags found ({len(h1_tags)}). Use only one for the main title.")
        severity = "warning"
    else:
        messages.append("One H1 tag found.")

    if not h2_tags:
        score -= 15
        messages.append("No H2 tags found. Use them to break up content sections.")
        if severity == "info": severity = "warning"
    else:
        # Check if H2s are too many or too few (simple heuristic)
        if len(h2_tags) < 2:
            score -= 5
            messages.append("Consider using more H2 tags for better content structure.")
        else:
            messages.append(f"Good heading structure with {len(h2_tags)} H2 tags.")

    if not h3_tags and len(h2_tags) > 3:
        score -= 5
        messages.append("Consider using H3 tags to further organize your sub-sections.")

    score = max(0, score)
    return SEOAuditItem(
        check="Headings Hierarchy",
        passed=score >= 70,
        score=score,
        message=" ".join(messages),
        severity=severity
    )


def check_images(soup, base_url: str) -> SEOAuditItem:
    """Check if images have alt attributes"""
    images = soup.find_all('img')
    
    if not images:
        return SEOAuditItem(
            check="Image SEO",
            passed=True,
            score=100,
            message="No images found. No action needed.",
            severity="info"
        )
    
    total = len(images)
    # Ignore small icons or spacers (simple heuristic: if they have a src with 'icon' or 'spacer')
    meaningful_images = [img for img in images if 'spacer' not in img.get('src', '').lower()]
    total_meaningful = len(meaningful_images)
    
    if total_meaningful == 0:
        return SEOAuditItem(
            check="Image SEO",
            passed=True,
            score=100,
            message="Only decorative images found. No action needed.",
            severity="info"
        )

    images_with_alt = sum(1 for img in meaningful_images if img.get('alt'))
    
    score = int((images_with_alt / total_meaningful) * 100)
    
    if score == 100:
        message = f"Excellent! All {total_meaningful} images have descriptive alt attributes."
        severity = "info"
    elif score >= 90:
        message = f"Good. {images_with_alt}/{total_meaningful} images have alt attributes."
        severity = "info"
    elif score >= 70:
        message = f"Fair. {images_with_alt}/{total_meaningful} images have alt attributes. Some are missing."
        severity = "warning"
    else:
        message = f"Poor. Only {images_with_alt}/{total_meaningful} images have alt attributes. Alt text is vital for accessibility and image search ranking."
        severity = "error"

    return SEOAuditItem(
        check="Image SEO",
        passed=score >= 80,
        score=score,
        message=message,
        severity=severity
    )


def check_structured_data(soup, base_url: str) -> SEOAuditItem:
    """Check if structured data is present"""
    schema = extract_schema_org(soup)
    json_ld = soup.find_all('script', type='application/ld+json')
    
    if schema or json_ld:
        return SEOAuditItem(
            check="Structured Data",
            passed=True,
            score=100,
            message=f"Structured data (JSON-LD/Schema) found. This helps search engines understand your content.",
            severity="info"
        )
    else:
        return SEOAuditItem(
            check="Structured Data",
            passed=False,
            score=0,
            message="No structured data found. Consider adding JSON-LD for better rich results.",
            severity="warning"
        )


def check_open_graph(soup, base_url: str) -> SEOAuditItem:
    """Check if Open Graph tags are present"""
    og_tags = extract_open_graph(soup)
    
    required = ['title', 'description', 'image', 'url']
    found = [tag for tag in required if tag in og_tags]
    
    score = int((len(found) / len(required)) * 100)
    
    if score == 100:
        message = "All core Open Graph tags are present."
        severity = "info"
    elif score >= 50:
        missing = [tag for tag in required if tag not in og_tags]
        message = f"Partially optimized. Missing OG tags: {', '.join(missing)}."
        severity = "warning"
    else:
        message = "Open Graph tags are missing. These are vital for social media sharing."
        severity = "warning"

    return SEOAuditItem(
        check="Social Sharing (OG)",
        passed=score >= 75,
        score=score,
        message=message,
        severity=severity
    )


def check_mobile_friendly(soup, base_url: str) -> SEOAuditItem:
    """Check if page has mobile viewport meta tag"""
    viewport = soup.find('meta', {'name': 'viewport'})
    
    if viewport:
        content = viewport.get('content', '')
        if 'width=device-width' in content:
            return SEOAuditItem(
                check="Mobile Friendly",
                passed=True,
                score=100,
                message="Viewport meta tag is correctly configured for mobile devices.",
                severity="info"
            )
        else:
            return SEOAuditItem(
                check="Mobile Friendly",
                passed=False,
                score=50,
                message="Viewport tag found but might not be optimized (width=device-width missing).",
                severity="warning"
            )
    else:
        return SEOAuditItem(
            check="Mobile Friendly",
            passed=False,
            score=0,
            message="Missing viewport meta tag. This is critical for mobile optimization.",
            severity="error"
        )


def check_technical_seo(soup, base_url: str) -> List[SEOAuditItem]:
    """Check technical SEO elements like canonicals, SSL, and robots"""
    items = []
    
    # 1. SSL Check
    is_https = base_url.startswith('https://')
    items.append(SEOAuditItem(
        check="Security (SSL)",
        passed=is_https,
        score=100 if is_https else 0,
        message="Site is using HTTPS." if is_https else "Site is NOT using HTTPS. Security is a ranking factor.",
        severity="info" if is_https else "error"
    ))
    
    # 2. Canonical Check
    canonical = soup.find('link', rel='canonical')
    items.append(SEOAuditItem(
        check="Canonical Link",
        passed=bool(canonical),
        score=100 if canonical else 0,
        message="Canonical link found." if canonical else "Missing canonical link. This can lead to duplicate content issues.",
        severity="info" if canonical else "warning"
    ))
    
    # 3. Robots meta
    robots_meta = soup.find('meta', {'name': 'robots'})
    noindex = robots_meta and 'noindex' in robots_meta.get('content', '').lower()
    items.append(SEOAuditItem(
        check="Search Indexing",
        passed=not noindex,
        score=100 if not noindex else 0,
        message="Page is indexable." if not noindex else "Page has 'noindex' tag. It will not appear in search results.",
        severity="info" if not noindex else "error"
    ))
    
    # 4. URL structure
    parsed = urlparse(base_url)
    url_score = 100
    url_msg = "URL structure is clean."
    if len(base_url) > 100:
        url_score -= 30
        url_msg = "URL is very long. Short URLs are better for SEO."
    if '_' in parsed.path:
        url_score -= 20
        url_msg = "URL contains underscores. Use hyphens (-) instead."
    
    items.append(SEOAuditItem(
        check="URL Optimization",
        passed=url_score >= 80,
        score=url_score,
        message=url_msg,
        severity="info" if url_score >= 80 else "warning"
    ))
    
    return items


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
        ]
        
        # Add technical SEO checks
        audit_items.extend(check_technical_seo(soup, url))
        
        # Calculate overall score as weighted average
        # Critical items have more weight
        weights = {
            "Title": 2.0,
            "Meta Description": 1.5,
            "Headings Hierarchy": 1.0,
            "Image SEO": 0.8,
            "Structured Data": 1.0,
            "Social Sharing (OG)": 0.5,
            "Mobile Friendly": 1.5,
            "Security (SSL)": 1.0,
            "Canonical Link": 0.8,
            "Search Indexing": 2.0,
            "URL Optimization": 0.5,
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for item in audit_items:
            weight = weights.get(item.check, 1.0)
            weighted_sum += item.score * weight
            total_weight += weight
            
        score = int(weighted_sum / total_weight)
        
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
