# PageIQ - Website Intelligence API# PageIQ - Website Intelligence API



## 🚀 Quick Start## Overview

PageIQ is a Website Intelligence API that turns any URL into structured business data in one request. It solves the real developer pain of building crawling + parsing infrastructure by providing a simple endpoint that returns comprehensive website intelligence including metadata, tech stack, contact information, social profiles, screenshots, and more.

**API Endpoint:** `https://pageiq.pompora.dev/api/v1`

## Vision

**Documentation:** `https://pageiq.pompora.dev/docs`To become the go-to infrastructure utility API for lead generation, sales automation, CRM enrichment, SEO software, and automation builders who need instant website intelligence without the complexity of building and maintaining their own scraping infrastructure.



## Overview## Target Audience

- Lead generation tools

PageIQ is a Website Intelligence API that turns any URL into structured business data in one request. Get comprehensive website analysis including metadata, tech stack detection, contact information, social profiles, screenshots, and AI-powered insights.- Sales automation platforms

- CRM enrichment services

### What You Get- SEO software companies

- 📊 Comprehensive metadata extraction- AI agent developers

- 🔍 Tech stack detection- Browser extension creators

- 📧 Contact information (emails, phones)- Competitor monitoring tools

- 🌐 Social media profiles- Website auditing platforms

- 📸 Website screenshots- Startup scouting services

- 📝 AI-powered summaries- Due diligence tools

- 📄 Schema.org & Open Graph data- Prospecting workflow builders

- 🗣️ Language & keyword detection

## Core Value Proposition

## Pricing PlansDevelopers pay for time saved + infrastructure complexity removed. Instead of building and maintaining:

- Headless browsers

| Plan | Price | Requests/Month | Features |- Anti-bot logic

|------|-------|-----------------|----------|- HTML parsing

| Free | $0 | 100 | Basic metadata |- Metadata extraction

| Basic | $9/mo | 5,000 | +Socials, Tech stack |- Logo finding

| Pro | $29/mo | 50,000 | +Screenshots, AI summary |- Email scraping

| Business | $99/mo | 500,000 | +Batch, Webhooks, SLA |- Tech stack detection

| Enterprise | Custom | Custom | Custom features, Priority support |- Schema parsing

- Social profile extraction

## Installation & Deployment- Page screenshotting

- Caching

### Option 1: Deploy to Render (Recommended)- Retry logic

- Proxies

See [RENDER_DEPLOYMENT.md](./RENDER_DEPLOYMENT.md) for complete step-by-step instructions.

They can simply call our API and get structured data instantly.

### Option 2: Local Development

## Business Model

#### PrerequisitesFreemium with metered usage tiers:

- Python 3.11+- Free: 100 requests/month (slow queue, watermark screenshot)

- Node.js 18+ (for Playwright)- Basic: $9/mo (5,000 requests, metadata + socials)

- Redis 7+ (optional, for caching)- Pro: $29/mo (50,000 requests, screenshots, tech stack, AI summary)

- Business: $99/mo (500,000 requests, batch endpoint, webhook completion, SLA)

#### Setup- Enterprise: Custom pricing

```bash

# Clone and enter directory## Success Metrics

git clone <your-repo>- RapidAPI marketplace presence with consistent monthly recurring revenue

cd PageIQ- Low churn due to workflow integration

- Volume-based scaling (100 sites/day = hobby, 10K/day = agency, 1M/day = SaaS)

# Create virtual environment- High customer lifetime value through sticky integration

python -m venv venv

source venv/bin/activate  # or `venv\Scripts\activate` on Windows## Technical Approach

Built with modern, scalable technologies:

# Install dependencies- Backend: FastAPI (Python)

pip install -r requirements.txt- Browser Automation: Playwright

- HTML Parsing: BeautifulSoup

# Set up environment- Tech Stack Detection: Wappalyzer/builtwith integration

cp .env.example .env- Caching: Redis

- Database: PostgreSQL

# Run development server- Background Jobs: Celery

python -m uvicorn app.main:app --reload --port 8000- Infrastructure: Docker → Railway/Render → AWS ECS

```- CDN: Cloudflare

- Rate Limiting: Redis-based

Access API at `http://localhost:8000`- Payments: Stripe

- API Management: RapidAPI publishing

## API Usage- Documentation: Strong docs with code snippets



### Analyze Endpoint## Phase 1: MVP (Weeks 1-4)

- Core /analyze endpoint

```bash- Basic metadata extraction (title, description, logos, favicons)

curl -X POST https://pageiq.pompora.dev/api/v1/analyze \- Contact information (emails, phones)

  -H "X-API-Key: YOUR_API_KEY" \- Social media profiles

  -H "Content-Type: application/json" \- Basic tech stack detection

  -d '{- Open Graph and Schema.org parsing

    "url": "https://example.com",- Language and country detection

    "options": {- Keyword extraction

      "screenshot": true,- Basic screenshot functionality

      "tech_stack": true,

      "summary": true## Phase 2: Production Ready (Weeks 5-8)

    }- User authentication and API key management

  }'- Rate limiting and quota enforcement

```- Redis caching layer

- PostgreSQL for persistent storage

### Health Check- Docker containerization

- Basic monitoring and logging

```bash- Stripe payment integration

curl https://pageiq.pompora.dev/api/v1/ping- RapidAPI publication

```- Comprehensive documentation



## Environment Variables## Phase 3: Scaling & Optimization (Weeks 9-12)

- Advanced anti-bot measures

See `.env.example` for all configuration options. Key variables:- Proxy rotation system

- Enhanced caching strategies

- `SERVER_HOST`: API domain (e.g., `https://pageiq.pompora.dev`)- Batch processing capabilities

- `DATABASE_URL`: Database connection string- Webhook completion notifications

- `REDIS_URL`: Redis connection for caching- SLA monitoring and alerting

- `STRIPE_SECRET_KEY`: Stripe API key- Performance optimization

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`: S3 credentials- Security hardening



## Project Structure## Phase 4: Suite Expansion (Post-Launch)

- /batch-analyze endpoint

```- Dedicated /screenshot endpoint

PageIQ/- /extract-emails endpoint

├── app/- /extract-schema endpoint

│   ├── api/              # API routes- /seo-audit endpoint

│   ├── core/             # Core utilities (config, auth, etc.)- /broken-links endpoint

│   ├── db/               # Database session- /detect-cms endpoint

│   ├── models/           # SQLAlchemy models- /competitor-diff endpoint

│   ├── schemas/          # Request/response schemas

│   ├── services/         # Business logic## Competitive Advantages

│   ├── tasks/            # Celery tasks1. **Infrastructure Utility**: Solves real, painful infrastructure problems

│   ├── utils/            # Helper functions2. **Marketplace Fit**: Perfect for RapidAPI's utility API audience

│   └── main.py           # FastAPI app entry point3. **Sticky Integration**: Becomes part of customer workflows

├── tests/                # Test suite4. **Clear Value Proposition**: Easy to explain, demo, and understand

├── requirements.txt      # Python dependencies5. **Scalable Economics**: Volume-based pricing aligns with customer growth

├── .env.example          # Environment template6. **Low Support Burden**: Well-defined inputs/outputs reduce complexity

├── render.yaml           # Render deployment config

└── Procfile              # Render/Heroku deployment## Risks and Mitigations

```- **Anti-bot measures**: Mitigate with rotating proxies, realistic browser fingerprints, rate limiting

- **Legal compliance**: Focus on publicly available data, respect robots.txt, implement proper rate limiting

## Testing- **Performance**: Use caching, async processing, and efficient parsing libraries

- **Maintenance**: Modular design allows updating individual components without system overhaul

```bash

# Run all tests## Next Steps

pytest1. Complete detailed technical specification

2. Set up development environment

# Run with coverage3. Implement core extraction modules

pytest --cov=app --cov-report=html4. Build API layer with FastAPI

5. Implement authentication and billing

# Run specific test file6. Deploy to staging environment

pytest tests/test_analyze.py -v7. Begin beta testing with target customers

```8. Publish to RapidAPI

9. Launch marketing and sales efforts

## Documentation

## Installation

- **API Docs:** `https://pageiq.pompora.dev/docs` (Swagger UI)

- **ReDoc:** `https://pageiq.pompora.dev/redoc` (Alternative API docs)### Prerequisites

- **OpenAPI Schema:** `https://pageiq.pompora.dev/api/v1/openapi.json`- Python 3.11+

- Node.js 18+ (for Playwright)

## Rate Limiting- Docker and Docker Compose

- PostgreSQL 15+

Requests are rate-limited based on your plan:- Redis 7+



- Free tier: 10 req/min### Local Development Setup

- Basic tier: 60 req/min1. Clone the repository

- Pro tier: 600 req/min2. Create virtual environment: `python -m venv venv`

- Business tier: 6000 req/min3. Activate venv: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Unix)

4. Install dependencies: `pip install -r requirements.txt`

Response headers include:5. Set up environment variables (see .env.example)

- `X-RateLimit-Limit`: Total requests allowed6. Run database migrations: `alembic upgrade head`

- `X-RateLimit-Remaining`: Requests remaining7. Start development server: `uvicorn app.main:app --reload`

- `X-RateLimit-Reset`: Time until reset (Unix timestamp)

### Docker Development

## Monitoring & Logs1. `docker-compose up -d`

2. Access API at http://localhost:8000

### Health Check3. View docs at http://localhost:8000/docs



```bash## Usage

curl https://pageiq.pompora.dev/api/v1/ping```python

# Returns: {"status": "ok", "timestamp": "2024-04-16T..."}import requests

```

response = requests.post('http://localhost:8000/analyze', json={

### View Logs (Render Dashboard)    'url': 'https://example.com',

    'options': {'screenshot': True}

1. Go to https://render.com/dashboard}, headers={'X-API-Key': 'your-api-key'})

2. Select "pageiq-api" service

3. Click "Logs" tabprint(response.json())

4. Real-time logs appear here```



### Metrics Monitored## Contributing

See CONTRIBUTING.md for guidelines.

- CPU Usage

- Memory Usage## License

- Request latency (p50, p95, p99)MIT License
- Error rate
- Uptime %

## Security Features

- ✅ API Key authentication (X-API-Key header)
- ✅ Rate limiting & quota enforcement
- ✅ CORS configured for production domain
- ✅ SSL/TLS via Cloudflare
- ✅ SSRF protection
- ✅ Input validation
- ✅ Secure response headers
- ✅ HTTPS-only in production

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 502 Bad Gateway | Check Render logs for errors; restart service if needed |
| 429 Too Many Requests | Rate limit exceeded. Wait for X-RateLimit-Reset time. |
| 401 Unauthorized | Invalid/missing X-API-Key header in request |
| 503 Service Unavailable | API redeploying. Try again in 30 seconds. |
| CORS error | Domain not in BACKEND_CORS_ORIGINS config |

## Support & Community

- 📧 Email: support@pageiq.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/pageiq-api/issues)
- 💬 Discord: [Join Community](https://discord.gg/pageiq)
- 📚 Docs: See `/docs` endpoint for full API documentation

## License

MIT License - See LICENSE file for details

## Version

Current Version: 1.0.0
Latest Update: April 2026
