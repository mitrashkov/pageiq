"""
PageIQ API Documentation - Week 8 Complete Implementation

This document provides comprehensive documentation for all PageIQ API endpoints,
authentication, rate limiting, error handling, and usage examples.
"""

# ==============================================================================
# AUTHENTICATION
# ==============================================================================

"""
API Key Authentication

All endpoints (except /health) require an API key passed via header:

    Authorization: Bearer YOUR_API_KEY

Or via query parameter:

    ?api_key=YOUR_API_KEY

Rate limits are applied per API key and subscription tier.
"""

# ==============================================================================
# ENDPOINTS - CORE ANALYSIS
# ==============================================================================

"""
POST /api/v1/analyze
Core website analysis endpoint

Request:
{
    "url": "https://example.com",
    "options": {
        "screenshot": true,
        "use_browser": false,
        "wait_for_network_idle": true,
        "timeout": 30
    }
}

Response:
{
    "success": true,
    "data": {
        "url": "https://example.com",
        "title": "Example Company | Home",
        "description": "Leading provider of innovative solutions",
        "logo": "https://example.com/logo.png",
        "favicon": "https://example.com/favicon.ico",
        "emails": ["info@example.com", "support@example.com"],
        "phones": ["+1-555-123-4567"],
        "socials": {
            "linkedin": "https://linkedin.com/company/example",
            "twitter": "https://twitter.com/example",
            "facebook": "https://facebook.com/example"
        },
        "tech_stack": ["React", "Next.js", "Node.js", "PostgreSQL", "AWS"],
        "industry_guess": {"label": "Technology", "confidence": 0.85},
        "language": "en",
        "country_guess": "US",
        "keywords": ["technology", "innovation", "software"],
        "schema_org": {
            "@type": "Organization",
            "name": "Example Company",
            "url": "https://example.com"
        },
        "og_tags": {
            "title": "Example Company",
            "description": "Leading provider...",
            "image": "https://example.com/og-image.jpg"
        },
        "screenshot_url": "/screenshots/example-com-12345.png",
        "page_speed_score": 85,
        "ai_summary": "Example Company provides innovative technology solutions...",
        "timestamp": 1681900800000,
        "processing_time_ms": 2450
    },
    "request_id": "req_abc123xyz",
    "quota_remaining": 4999
}

Query Parameters:
- url (required): Website URL to analyze
- options.screenshot (bool): Capture screenshot (default: false)
- options.use_browser (bool): Use Playwright for JS rendering (default: false)
- options.timeout (int): Request timeout in seconds (default: 30, max: 120)

Rate Limits:
- Free tier: 100/month, 1 request/minute
- Basic tier: 5,000/month, 10 requests/minute
- Pro tier: 50,000/month, 100 requests/minute
- Business tier: 500,000/month, 1000 requests/minute

HTTP Status Codes:
- 200: Success
- 400: Invalid URL or parameters
- 403: Robots.txt blocking or region restriction
- 429: Rate limit exceeded
- 500: Server error
"""

# ==============================================================================
# ENDPOINTS - EXTRACTION
# ==============================================================================

"""
POST /api/v1/extract/emails
Extract email addresses from a webpage

Request:
{
    "url": "https://example.com",
    "options": {}
}

Response:
{
    "url": "https://example.com",
    "emails": ["info@example.com", "support@example.com", "contact@example.com"],
    "count": 3,
    "timestamp": 1681900800.123,
    "processing_time_ms": 850
}
"""

"""
POST /api/v1/extract/schema
Extract Schema.org structured data and Open Graph tags

Request:
{
    "url": "https://example.com",
    "options": {}
}

Response:
{
    "url": "https://example.com",
    "schema_org": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Example Company",
        "url": "https://example.com",
        "logo": "https://example.com/logo.png",
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "Customer Service",
            "telephone": "+1-555-123-4567"
        }
    },
    "og_tags": {
        "title": "Example Company",
        "description": "Leading provider of innovative solutions",
        "image": "https://example.com/og-image.jpg",
        "url": "https://example.com",
        "type": "website"
    },
    "timestamp": 1681900800.123,
    "processing_time_ms": 650
}
"""

"""
POST /api/v1/extract/metadata
Extract all metadata (title, description, schema, OG tags)

Request:
{
    "url": "https://example.com",
    "options": {}
}

Response:
{
    "url": "https://example.com",
    "title": "Example Company | Home",
    "description": "Leading provider of innovative solutions",
    "schema_org": {...},
    "og_tags": {...},
    "timestamp": 1681900800.123,
    "processing_time_ms": 750
}
"""

# ==============================================================================
# ENDPOINTS - SEO ANALYSIS
# ==============================================================================

"""
POST /api/v1/seo/seo-audit
Perform comprehensive SEO audit

Request:
{
    "url": "https://example.com",
    "options": {}
}

Response:
{
    "url": "https://example.com",
    "score": 78,
    "audit_items": [
        {
            "check": "Title",
            "passed": true,
            "message": "Title is present and well-formed (42 chars)",
            "severity": "info"
        },
        {
            "check": "Meta Description",
            "passed": false,
            "message": "Description too long (250 chars, should be 50-160)",
            "severity": "warning"
        },
        {
            "check": "Mobile Friendly",
            "passed": true,
            "message": "Viewport meta tag is present",
            "severity": "info"
        }
    ],
    "timestamp": 1681900800.123,
    "processing_time_ms": 1200
}

Score Breakdown:
- 90-100: Excellent
- 80-89: Good
- 70-79: Needs Improvement
- 60-69: Poor
- 0-59: Very Poor

Audit Checks:
- Title tag presence and length (10-60 chars ideal)
- Meta description presence and length (50-160 chars ideal)
- Heading hierarchy (1 H1, multiple H2s)
- Image alt attributes
- Structured data (Schema.org)
- Open Graph tags
- Mobile friendliness (viewport meta tag)
- Robots.txt compliance
"""

"""
POST /api/v1/seo/broken-links
Detect broken links on a webpage

Request:
{
    "url": "https://example.com",
    "check_external": false,
    "options": {}
}

Response:
{
    "url": "https://example.com",
    "total_links": 42,
    "broken_links_count": 2,
    "internal_links": 35,
    "external_links": 7,
    "broken_links": [
        {
            "url": "https://example.com/old-page",
            "text": "Old Page",
            "error": "404 Not Found",
            "status_code": 404
        }
    ],
    "timestamp": 1681900800.123,
    "processing_time_ms": 3500
}

Parameters:
- check_external (bool): Check external links (slower, default: false)

Note: External link checking is limited to avoid performance issues.
Only internal links are checked by default.
"""

# ==============================================================================
# ENDPOINTS - BATCH PROCESSING
# ==============================================================================

"""
POST /api/v1/batch-analyze
Analyze multiple URLs in a single request

Request:
{
    "urls": [
        "https://example1.com",
        "https://example2.com",
        "https://example3.com"
    ],
    "options": {
        "screenshot": true
    },
    "webhook_url": "https://yourdomain.com/webhook"
}

Response (Immediate):
{
    "batch_id": "batch_abc123xyz",
    "urls_count": 3,
    "estimated_completion_time": 45,
    "webhook_url": "https://yourdomain.com/webhook"
}

Webhook Notification (Upon Completion):
POST https://yourdomain.com/webhook
{
    "batch_id": "batch_abc123xyz",
    "status": "completed",
    "urls_count": 3,
    "successful_analyses": 3,
    "failed_analyses": 0,
    "results": [
        {
            "url": "https://example1.com",
            "success": true,
            "data": {...}
        }
    ],
    "completed_at": 1681900800.123
}

Limits:
- Free/Basic: 10 URLs per batch
- Pro: 50 URLs per batch
- Business: 100 URLs per batch

Webhook Parameters:
- Timeout: 5 seconds
- Retries: 3 attempts with exponential backoff
- Signature: Includes X-PageIQ-Signature header for verification
"""

# ==============================================================================
# ENDPOINTS - ANALYTICS & HEALTH
# ==============================================================================

"""
GET /api/v1/analytics
Get usage analytics and performance metrics

Query Parameters:
- days (int): Number of days to look back (1-90, default: 7)

Response:
{
    "usage_stats": {
        "total_requests": 12456,
        "successful_analyses": 12100,
        "failed_analyses": 356,
        "average_response_time_ms": 1850
    },
    "popular_domains": [
        {
            "domain": "techcrunch.com",
            "analysis_count": 234
        }
    ],
    "performance_metrics": {
        "p50_response_time_ms": 1200,
        "p95_response_time_ms": 3100,
        "p99_response_time_ms": 5000
    },
    "generated_at": 1681900800.123
}
"""

"""
GET /api/v1/health
Health check endpoint

Response:
{
    "status": "healthy",
    "service": "PageIQ API",
    "timestamp": 1681900800.123,
    "components": {
        "database": "healthy",
        "redis": "healthy",
        "browser": "available"
    }
}
"""

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

"""
Standard Error Response Format:

{
    "success": false,
    "error": {
        "code": "INVALID_URL",
        "message": "The provided URL is not valid",
        "details": "URL must start with http:// or https://"
    },
    "request_id": "req_error123",
    "timestamp": 1681900800.123
}

Common Error Codes:
- INVALID_URL: URL format is invalid
- ROBOTS_BLOCKED: Crawling not allowed by robots.txt
- TIMEOUT: Request timed out
- RATE_LIMITED: API rate limit exceeded
- QUOTA_EXCEEDED: User quota exceeded
- INVALID_API_KEY: API key is invalid or expired
- REGION_BLOCKED: Region is not allowed
- SERVER_ERROR: Internal server error

HTTP Status Codes:
- 200: OK
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error
- 503: Service Unavailable
"""

# ==============================================================================
# RATE LIMITING
# ==============================================================================

"""
Rate Limiting Headers:

X-RateLimit-Limit: 10000
X-RateLimit-Remaining: 9950
X-RateLimit-Reset: 1681904400

All responses include rate limit information.
When limit is exceeded, HTTP 429 is returned with:

{
    "success": false,
    "error": {
        "code": "RATE_LIMITED",
        "message": "Rate limit exceeded",
        "retry_after": 60
    }
}

Retry-After: 60

Tier Limits:
- Free: 100 requests/month, 1 req/min burst
- Basic: 5,000 requests/month, 10 req/min burst
- Pro: 50,000 requests/month, 100 req/min burst
- Business: 500,000 requests/month, 1000 req/min burst
- Enterprise: Custom limits
"""

# ==============================================================================
# USAGE EXAMPLES
# ==============================================================================

"""
Python SDK Example:

from pageiq import PageIQClient

client = PageIQClient(api_key="your_api_key")

# Analyze a website
result = client.analyze("https://example.com", screenshot=True)
print(f"Title: {result['title']}")
print(f"Tech Stack: {result['tech_stack']}")
print(f"Response Time: {result['processing_time_ms']}ms")

# Extract emails
emails = client.extract_emails("https://example.com")
print(f"Emails: {emails['emails']}")

# SEO audit
audit = client.seo_audit("https://example.com")
print(f"SEO Score: {audit['score']}")
for item in audit['audit_items']:
    if not item['passed']:
        print(f"  ⚠ {item['check']}: {item['message']}")

# Batch analysis
batch = client.batch_analyze([
    "https://example1.com",
    "https://example2.com",
    "https://example3.com"
])
print(f"Batch ID: {batch['batch_id']}")
"""

"""
JavaScript SDK Example:

const pageiq = require('@pageiq/client');

const client = new pageiq.Client({
    apiKey: 'your_api_key'
});

// Analyze a website
const result = await client.analyze('https://example.com', {
    screenshot: true
});
console.log(`Title: ${result.title}`);
console.log(`Tech Stack: ${result.tech_stack.join(', ')}`);

// Extract emails
const emails = await client.extractEmails('https://example.com');
console.log(`Emails: ${emails.emails.join(', ')}`);

// SEO audit
const audit = await client.seoAudit('https://example.com');
console.log(`SEO Score: ${audit.score}`);
"""

"""
cURL Example:

# Analyze a website
curl -X POST https://api.pageiq.io/api/v1/analyze \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "options": {
      "screenshot": true
    }
  }'

# Extract emails
curl -X POST https://api.pageiq.io/api/v1/extract/emails \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'

# SEO audit
curl -X POST https://api.pageiq.io/api/v1/seo/seo-audit \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com"
  }'
"""

# ==============================================================================
# WEBHOOK SIGNATURE VERIFICATION
# ==============================================================================

"""
Verify Webhook Signatures:

The X-PageIQ-Signature header contains HMAC-SHA256 signature.

Python Example:
import hmac
import hashlib

def verify_webhook(body, signature, secret):
    computed_signature = hmac.new(
        secret.encode(),
        body.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(computed_signature, signature)

# In your webhook handler
webhook_signature = request.headers.get('X-PageIQ-Signature')
is_valid = verify_webhook(request.body, webhook_signature, your_secret)

JavaScript Example:
const crypto = require('crypto');

function verifyWebhook(body, signature, secret) {
    const computedSignature = crypto
        .createHmac('sha256', secret)
        .update(body)
        .digest('hex');
    return crypto.timingSafeEqual(
        Buffer.from(computedSignature),
        Buffer.from(signature)
    );
}
"""

if __name__ == "__main__":
    print("PageIQ API Documentation - Week 8 Complete")
    print("=" * 80)
    print("\nAll API endpoints are fully documented above.")
    print("For code examples and SDKs, see the examples section.")
    print("\nFor full OpenAPI specification, visit:")
    print("  https://api.pageiq.io/docs")
    print("  https://api.pageiq.io/redoc")
