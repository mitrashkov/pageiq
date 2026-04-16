# PageIQ Technical Specification

## API Endpoints

### Core Endpoint: POST /analyze
Analyze a website and return structured business data.

**Request:**
```json
{
  "url": "https://example.com",
  "options": {
    "screenshot": true,
    "timeout": 30,
    "wait_for_network_idle": true
  }
}
```

**Response:**
```json
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
      "facebook": "https://facebook.com/example",
      "instagram": "https://instagram.com/example",
      "youtube": "https://youtube.com/c/example"
    },
    "tech_stack": [
      "React",
      "Next.js",
      "TypeScript",
      "Node.js",
      "PostgreSQL",
      "AWS",
      "Cloudflare",
      "Stripe"
    ],
    "industry_guess": "Technology",
    "language": "en",
    "country_guess": "US",
    "keywords": ["technology", "software", "saas", "innovation"],
    "schema_org": {
      "@type": "Organization",
      "name": "Example Company",
      "url": "https://example.com",
      "logo": "https://example.com/logo.png",
      "contactPoint": [{
        "@type": "ContactPoint",
        "telephone": "+1-555-123-4567",
        "contactType": "Customer Service"
      }]
    },
    "og_tags": {
      "og:title": "Example Company | Home",
      "og:description": "Leading provider of innovative solutions",
      "og:image": "https://example.com/og-image.jpg",
      "og:url": "https://example.com",
      "og:type": "website"
    },
    "screenshot_url": "https://screenshots.pageiq.io/example-com-12345.png",
    "page_speed_score": 89,
    "ai_summary": "Example Company provides innovative technology solutions for businesses looking to improve their operations and customer experience.",
    "timestamp": "2026-04-16T10:30:00Z",
    "processing_time_ms": 2450
  },
  "request_id": "req_abc123",
  "quota_remaining": 4999
}
```

### Additional Endpoints (Phase 2+)

#### POST /batch-analyze
Analyze multiple URLs in a single request.

#### GET /screenshot/{url_hash}
Get screenshot for a previously analyzed URL.

#### POST /extract-emails
Extract emails from HTML content.

#### POST /extract-schema
Extract Schema.org structured data.

#### GET /seo-audit
Perform SEO audit on a URL.

#### GET /broken-links
Find broken links on a page.

#### GET /detect-cms
Detect Content Management System.

#### GET /competitor-diff
Compare two websites for competitive analysis.

## Architecture Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   API Gateway   │    │   Rate Limiter   │    │   Auth Service   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Request Queue │    │   Cache Layer    │    │   User DB        │
│   (Redis)       │    │   (Redis)        │    │   (PostgreSQL)   │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   Worker Pool   │    │   Storage Service│    │   Billing Service│
│   (Celery)      │    │   (S3/Cloud)     │    │   (Stripe)       │
└─────────┬───────┘    └─────────┬────────┘    └─────────┬────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ Analysis Engine │    │   Screenshot Svc │    │ Notification Svc │
└─────────────────┘    └──────────────────┘    └──────────────────┘
```

## Component Details

### 1. API Layer (FastAPI)
- RESTful endpoints with OpenAPI/Swagger documentation
- Request validation using Pydantic models
- Authentication via API keys
- Error handling and standardized responses
- Request/response logging
- CORS middleware

### 2. Authentication & Authorization
- API key generation and validation
- JWT tokens for session management
- Role-based access control (free, basic, pro, business, enterprise)
- Key rotation and revocation
- Usage tracking per API key

### 3. Rate Limiting & Quota Enforcement
- Redis-based sliding window rate limiter
- Per-tier request limits (100/month free, 5K/month basic, etc.)
- Burst protection
- Real-time quota tracking
- HTTP 429 responses with retry-after headers

### 4. Analysis Engine
- URL validation and normalization
- Robots.txt checking (respectful crawling)
- Headless browser automation (Playwright)
- Anti-bot evasion techniques:
  - Realistic browser fingerprints
  - Randomized user agents
  - Proxy rotation
  - Human-like interaction patterns
  - CAPTCHA avoidance strategies
- HTML parsing and cleaning (BeautifulSoup)
- Metadata extraction pipeline:
  - Title, description extraction
  - Logo and favicon detection
  - Email and phone number extraction
  - Social media profile discovery
  - Tech stack detection (Wappalyzer integration)
  - Schema.org and Open Graph parsing
  - Language and country detection
  - Keyword extraction (TF-IDF, RAKE)
  - AI summarization (using lightweight models)

### 5. Screenshot Service
- Full-page screenshots with Playwright
- Viewport configuration options
- Image optimization and compression
- Watermarking for free tier
- CDN delivery via Cloudflare
- Expiration and cleanup policies

### 6. Caching Layer
- Redis cache for analysis results
- TTL-based expiration (24h for most data)
- Cache warming for popular domains
- Cache invalidation strategies
- Memory-efficient serialization

### 7. Storage Service
- Persistent storage for screenshots and assets
- Metadata storage in PostgreSQL
- Object storage for binary data (S3-compatible)
- Backup and disaster recovery
- GDPR compliance features

### 8. Background Job Processing (Celery)
- Asynchronous analysis processing
- Priority queues for different tiers
- Retry mechanisms with exponential backoff
- Dead letter queues for failed jobs
- Monitoring and metrics collection
- Horizontal scaling capabilities

### 9. Billing & Subscription Management
- Stripe integration for payments
- Subscription plan management
- Usage-based billing for overages
- Invoice generation and emailing
- Payment failure handling
- Subscription lifecycle management
- Revenue analytics and reporting

### 10. Monitoring & Observability
- Structured logging (JSON format)
- Metrics collection (Prometheus-compatible)
- Health check endpoints
- Distributed tracing (OpenTelemetry)
- Error tracking and alerting
- Performance dashboards
- Usage analytics

## Data Models

### WebsiteAnalysis Result
```python
class WebsiteAnalysis(BaseModel):
    url: HttpUrl
    title: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[HttpUrl] = None
    favicon: Optional[HttpUrl] = None
    emails: List[EmailStr] = []
    phones: List[str] = []
    socials: Dict[str, Optional[HttpUrl]] = {}
    tech_stack: List[str] = []
    industry_guess: Optional[str] = None
    language: Optional[str] = None
    country_guess: Optional[str] = None
    keywords: List[str] = []
    schema_org: Optional[Dict[str, Any]] = None
    og_tags: Optional[Dict[str, str]] = None
    screenshot_url: Optional[HttpUrl] = None
    page_speed_score: Optional[int] = None
    ai_summary: Optional[str] = None
    timestamp: datetime
    processing_time_ms: int
```

### User/Subscription Model
```python
class User(BaseModel):
    id: UUID
    email: EmailStr
    api_key: str
    plan: PlanType  # free, basic, pro, business, enterprise
    status: SubscriptionStatus  # active, past_due, canceled, etc.
    created_at: datetime
    updated_at: datetime
    quota_used: int
    quota_limit: int
```

### Rate Limit Model
```python
class RateLimitInfo(BaseModel):
    limit: int
    remaining: int
    reset_time: datetime
```

## Security Considerations

### Input Validation
- URL validation and sanitization
- Prevention of SSRF attacks
- HTML sanitization to prevent XSS
- Size limits on requests and responses

### Data Protection
- Encryption at rest for sensitive data
- TLS encryption in transit
- API key hashing (not storage of plain keys)
- Regular security audits
- Dependency vulnerability scanning

### Privacy & Compliance
- GDPR/CCPA compliance features
- Data retention policies
- Right to be forgotten implementation
- Respect for robots.txt and crawl-delay
- Transparent data usage policies

### Anti-Abuse Measures
- CAPTCHA integration for suspicious activity
- Behavioral analysis for bot detection
- IP reputation checking
- Geographic rate limiting
- Content filtering for prohibited sites

## Performance Requirements

### Response Times
- 95th percentile: < 5 seconds for standard analysis
- 99th percentile: < 10 seconds for complex analysis
- Cached responses: < 200ms

### Throughput
- Minimum: 10 concurrent analyses
- Target: 100 concurrent analyses
- Scalable to: 1000+ concurrent analyses

### Availability
- Target uptime: 99.9%
- Planned maintenance windows
- Graceful degradation strategies
- Circuit breaker patterns

## Infrastructure Requirements

### Development Environment
- Python 3.11+
- Node.js 18+ (for Playwright)
- Redis 7+
- PostgreSQL 15+
- Docker and Docker Compose
- Git

### Production Infrastructure
- Container orchestration (Docker Swarm/Kubernetes)
- Load balancing
- Auto-scaling groups
- Multi-region deployment capability
- Database read replicas
- Redis clustering
- CDN for static assets
- Monitoring and logging stack

## Testing Strategy

### Unit Testing
- Test coverage target: 80%
- Mock external dependencies
- Test individual components in isolation

### Integration Testing
- Test API endpoints with real dependencies
- Test database interactions
- Test caching mechanisms
- Test background job processing

### End-to-End Testing
- Simulate user workflows
- Test complete analysis pipeline
- Test error scenarios and edge cases
- Performance testing under load

### Security Testing
- OWASP Top 10 testing
- Penetration testing
- Dependency vulnerability scanning
- API security testing

## Deployment Strategy

### CI/CD Pipeline
- Automated testing on pull requests
- Staging deployment on merge to main
- Manual approval for production deployment
- Blue-green deployment strategy
- Rollback capabilities
- Database migration management

### Environment Strategy
- Development: Local Docker Compose
- Staging: Mirror of production with sanitized data
- Production: Multi-zone deployment
- Feature flags for gradual rollouts

## Future Enhancements (Version 2+)

### Advanced Features
- Custom analysis workflows
- Webhook notifications for completed analyses
- Batch processing with webhook callbacks
- Custom data extraction rules
- Historical analysis and trending
- Competitive intelligence dashboards
- API usage analytics for customers
- Custom branding and white-labeling

### Integrations
- Native integrations with popular CRMs (Salesforce, HubSpot)
- Zapier and Make.com integration
- Browser extension for one-click analysis
- WordPress plugin
- API SDKs for popular languages (Python, JavaScript, Java, etc.)

### Analytics & Intelligence
- Domain reputation scoring
- Technology adoption trends
- Market sizing estimates
- Lead scoring based on website analysis
- Predictive analytics for tech stack changes

## Appendix

### Error Codes
- 400: Bad Request (invalid URL, missing parameters)
- 401: Unauthorized (invalid/missing API key)
- 402: Payment Required (subscription past due)
- 403: Forbidden (insufficient permissions)
- 404: Not Found (endpoint doesn't exist)
- 429: Too Many Requests (rate limit exceeded)
- 500: Internal Server Error
- 502: Bad Gateway (dependency failure)
- 503: Service Unavailable (temporary overload)
- 504: Gateway Timeout (analysis timeout)

### Headers
- `X-Request-ID`: Unique identifier for tracing
- `X-RateLimit-Limit`: Request limit for current window
- `X-RateLimit-Remaining`: Requests remaining in current window
- `X-RateLimit-Reset`: Time when rate limit resets
- `X-Quota-Limit`: Monthly quota limit
- `X-Quota-Remaining`: Monthly quota remaining
- `X-Processing-Time-MS`: Analysis processing time
- `X-Cached`: Whether response was served from cache

### Supported Browsers for Screenshots
- Chromium (default)
- Firefox (optional)
- WebKit (optional)

### Supported Output Formats
- JSON (primary)
- CSV (for batch operations)
- Excel (for enterprise tier)