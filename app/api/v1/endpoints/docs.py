"""
Web-based documentation and comprehensive interactive test suite for PageIQ API.
Accessible at /docs for documentation and /tests for manual testing all endpoints.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
async def get_landing():
    """Serve public landing page"""
    return HTMLResponse(content=LANDING_PAGE_HTML)


@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Serve the modern, comprehensive documentation page"""
    return HTMLResponse(content=MODERN_DOCS_HTML)

RETRO_BASE_STYLE = """
<style>
    body {
        margin: 0;
        padding: 0;
        font-family: Verdana, Arial, sans-serif;
        background: #0d1b4d;
        background-image: linear-gradient(45deg, rgba(255,255,255,0.05) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0.05) 75%, transparent 75%, transparent);
        background-size: 40px 40px;
        color: #111;
    }
    .page {
        width: 980px;
        margin: 0 auto;
        background: #f5f5ff;
        border: 4px solid #ffcc00;
        box-shadow: 0 0 12px rgba(0,0,0,0.45);
    }
    .topbar {
        background: #001a66;
        color: #fff;
        padding: 8px 14px;
        font-size: 12px;
        border-bottom: 3px solid #ffcc00;
    }
    .hero {
        background: radial-gradient(circle at top left, #66ccff, #003399);
        color: #fff;
        padding: 20px 22px;
        border-bottom: 3px solid #ffcc00;
    }
    .hero h1 {
        margin: 8px 0 10px;
        font-size: 34px;
        line-height: 1.15;
        text-shadow: 2px 2px #001133;
    }
    .hero p {
        margin: 0 0 14px;
        font-size: 15px;
        max-width: 840px;
        line-height: 1.5;
    }
    .button {
        display: inline-block;
        padding: 8px 14px;
        margin-right: 8px;
        margin-bottom: 8px;
        background: #ff6600;
        color: #fff;
        border: 2px outset #ff9933;
        text-decoration: none;
        font-weight: bold;
        font-size: 13px;
    }
    .button.alt {
        background: #3366cc;
        border-color: #6699ff;
    }
    .marquee {
        background: #ffef99;
        color: #990000;
        font-weight: bold;
        border-top: 2px solid #cc9900;
        border-bottom: 2px solid #cc9900;
        padding: 4px 0;
        font-size: 12px;
    }
    .layout {
        display: table;
        width: 100%;
        table-layout: fixed;
    }
    .sidebar {
        display: table-cell;
        width: 240px;
        background: #e5edff;
        border-right: 2px solid #99a8dd;
        vertical-align: top;
        padding: 12px 10px;
        font-size: 12px;
    }
    .main {
        display: table-cell;
        vertical-align: top;
        padding: 14px;
        background: #fdfdff;
    }
    .module {
        border: 2px solid #8aa0dd;
        margin-bottom: 12px;
        background: #fff;
    }
    .module h3 {
        margin: 0;
        background: #2244aa;
        color: #fff;
        padding: 6px 8px;
        font-size: 13px;
        letter-spacing: 0.3px;
    }
    .module .inner {
        padding: 8px;
        line-height: 1.45;
    }
    .module ul {
        margin: 0 0 0 16px;
        padding: 0;
    }
    .module li {
        margin-bottom: 5px;
    }
    .post {
        border: 2px solid #ccccff;
        background: #fff;
        margin-bottom: 14px;
    }
    .post h2 {
        margin: 0;
        padding: 8px 10px;
        background: #dde6ff;
        color: #002266;
        font-size: 18px;
        border-bottom: 1px solid #b6c7ff;
    }
    .post .body {
        padding: 10px 12px;
        line-height: 1.6;
        font-size: 14px;
    }
    .two-col {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
    }
    .counter {
        font-family: "Courier New", monospace;
        font-weight: bold;
        font-size: 15px;
        background: #000;
        color: #00ff66;
        padding: 4px 8px;
        display: inline-block;
        letter-spacing: 2px;
    }
    .footer {
        background: #001a66;
        color: #cfe3ff;
        text-align: center;
        font-size: 12px;
        padding: 14px;
        border-top: 3px solid #ffcc00;
    }
    a { color: #0033cc; }
    a:hover { color: #ff3300; }
    .gif {
        border: 1px solid #999;
        max-width: 100%;
    }
</style>
"""

RETRO_PAGE_SCRIPT = """
<script>
    (function() {
        var key = "pageiq-retro-visit-counter";
        var count = parseInt(localStorage.getItem(key) || "15243", 10);
        count += 1;
        localStorage.setItem(key, String(count));
        var el = document.getElementById("visitCounter");
        if (el) {
            el.textContent = String(count).padStart(6, "0");
        }
    })();
</script>
"""

RETRO_NAV_HTML = """
<div class="module">
  <h3>Site Navigation</h3>
  <div class="inner">
    <ul>
      <li><a href="/">Home Portal</a></li>
      <li><a href="/seo-audit-api">SEO Audit API</a></li>
      <li><a href="/website-scraper-api">Website Scraper API</a></li>
      <li><a href="/email-extractor-api">Email Extractor API</a></li>
      <li><a href="/tech-stack-detector-api">Tech Stack Detector API</a></li>
      <li><a href="/website-metadata-api">Website Metadata API</a></li>
      <li><a href="/competitor-website-analysis-api">Competitor Website Analysis API</a></li>
      <li><a href="/about-pageiq">About PageIQ</a></li>
      <li><a href="/pricing-plans">Pricing and Plans</a></li>
      <li><a href="/faq-page">Frequently Asked Questions</a></li>
      <li><a href="/guestbook">Guestbook</a></li>
      <li><a href="/blog-archive">Blog Archive</a></li>
      <li><a href="/docs">Developer Docs</a></li>
    </ul>
  </div>
</div>
"""

RETRO_SIDEBAR_EXTRAS = """
<div class="module">
  <h3>Visitor Counter</h3>
  <div class="inner">
    <p><strong>Total Visitors:</strong></p>
    <span class="counter" id="visitCounter">015243</span>
    <p style="margin-top:8px;">Thank you for keeping independent web infrastructure alive.</p>
  </div>
</div>
<div class="module">
  <h3>Webmaster Notes</h3>
  <div class="inner">
    <p>Updated every week with new API examples, integration tips, and growth playbooks for SaaS founders and agency builders.</p>
    <p>Current mood: shipping velocity + conversion optimization.</p>
  </div>
</div>
<div class="module">
  <h3>Affiliate Badges</h3>
  <div class="inner">
    <p><a href="https://rapidapi.com" target="_blank" rel="noopener noreferrer">Featured on RapidAPI Marketplace</a></p>
    <p><a href="/api/v1/health">Live Uptime Status</a></p>
    <img class="gif" alt="animated under construction" src="https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif">
  </div>
</div>
"""

def build_retro_page(
    title: str,
    meta_description: str,
    meta_keywords: str,
    hero_title: str,
    hero_subtext: str,
    main_html: str,
) -> str:
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{meta_description}">
  <meta name="keywords" content="{meta_keywords}">
  <meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">
  <meta name="author" content="PageIQ">
  {RETRO_BASE_STYLE}
</head>
<body>
  <div class="page">
    <div class="topbar">
      <strong>PageIQ Retro Portal</strong> | Website Intelligence API | Built for founders, agencies, SEOs, and automation engineers
    </div>
    <div class="hero">
      <marquee behavior="scroll" direction="left" scrollamount="6">NEW: Extended metadata extraction, improved schema parsing, full technology language detection, and production-grade endpoint documentation.</marquee>
      <h1>{hero_title}</h1>
      <p>{hero_subtext}</p>
      <a class="button" href="https://rapidapi.com" target="_blank" rel="noopener noreferrer">Try on RapidAPI</a>
      <a class="button alt" href="/docs">View Developer Docs</a>
      <a class="button alt" href="/api/v1/health">System Health</a>
    </div>
    <div class="marquee">
      <marquee behavior="alternate" direction="left" scrollamount="4">Long-tail landing pages are live: SEO Audit API | Website Scraper API | Email Extractor API | Tech Stack Detector API | Website Metadata API | Competitor Analysis API</marquee>
    </div>
    <div class="layout">
      <div class="sidebar">
        {RETRO_NAV_HTML}
        {RETRO_SIDEBAR_EXTRAS}
      </div>
      <div class="main">
        {main_html}
      </div>
    </div>
    <div class="footer">
      PageIQ Website Intelligence Engine | pageiq.pompora.dev | Designed with retro web spirit, modern API performance.
    </div>
  </div>
  {RETRO_PAGE_SCRIPT}
</body>
</html>
"""

LANDING_PAGE_HTML = build_retro_page(
    title="PageIQ - Turn Any Website Into Actionable Business Data",
    meta_description="Extract SEO score, tech stack, metadata, verified emails, socials, and hidden business intelligence from any URL using the PageIQ API.",
    meta_keywords="website intelligence api, seo audit api, website scraper api, email extractor api, tech stack detector api, metadata scraper api",
    hero_title="Turn Any Website Into Actionable Business Data",
    hero_subtext="Extract SEO score, tech stack, metadata, verified emails, socials, and hidden business intelligence from any URL. PageIQ gives growth teams and developers a practical data engine for prospecting, competitor research, and workflow automation.",
    main_html="""
      <div class="post">
        <h2>Welcome to the PageIQ Growth Hub</h2>
        <div class="body">
          <p>PageIQ is a website intelligence API built for teams that need accurate data extraction at production speed. Instead of building and maintaining a brittle pipeline with crawlers, parsers, browser automation, schema normalization, and contact extraction logic, you can call one endpoint and get immediately useful data in clean JSON. This includes technology fingerprints, metadata, schema entities, SEO signals, and contact touchpoints that can be fed directly into your CRM, analytics stack, and outbound workflows.</p>
          <p>Our platform was designed around practical use cases from agencies, SaaS companies, and operations teams who need to evaluate websites at scale. We focus on signal quality, stable response structure, and predictable endpoint behavior so that your integrations remain maintainable over time. Teams use PageIQ to pre-qualify leads, enrich account records, profile competitors, trigger sales alerts, and generate repeatable market intelligence reports.</p>
          <p>Because major API creators grow through intent-based content strategy, this portal includes dedicated landing pages for core business outcomes. Every page speaks to a specific search intent and maps to a specific workflow. You can explore SEO audit automation, website scraping at scale, verified email extraction, technology stack detection, metadata scraping, and competitor website analysis through purpose-built pages below.</p>
          <div class="two-col">
            <div class="module">
              <h3>Primary Use-Case Portals</h3>
              <div class="inner">
                <ul>
                  <li><a href="/seo-audit-api">SEO Audit API Landing Page</a></li>
                  <li><a href="/website-scraper-api">Website Scraper API Landing Page</a></li>
                  <li><a href="/email-extractor-api">Email Extractor API Landing Page</a></li>
                  <li><a href="/tech-stack-detector-api">Technology Detection API Landing Page</a></li>
                  <li><a href="/website-metadata-api">Metadata Scraper API Landing Page</a></li>
                  <li><a href="/competitor-website-analysis-api">Competitor Analysis API Landing Page</a></li>
                </ul>
              </div>
            </div>
            <div class="module">
              <h3>Why Growth Teams Choose PageIQ</h3>
              <div class="inner">
                <ul>
                  <li>Structured output that drops directly into automation pipelines.</li>
                  <li>Coverage across SEO, metadata, schema, contact, and technology data.</li>
                  <li>Fast implementation path for agencies and product teams.</li>
                  <li>Modern API reliability with old-school directness: no fluff, just data.</li>
                </ul>
                <img class="gif" alt="retro internet gif" src="https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif">
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="post">
        <h2>Customer Voices and Proof</h2>
        <div class="body">
          <p><strong>Agency Owner:</strong> "We reduced website research time from 35 minutes per account to under 2 minutes. The SEO and metadata output became the backbone of our monthly audit deliverables."</p>
          <p><strong>SaaS Founder:</strong> "Before PageIQ we were juggling three providers and custom scrapers. Now our onboarding workflow runs through one endpoint and a clean transformation layer."</p>
          <p><strong>Revenue Operations Manager:</strong> "Technology and contact data are now synced to CRM nightly. It changed how fast we can route opportunities and detect expansion accounts."</p>
          <p>These are the practical wins we optimize for: less manual research, faster GTM execution, and stronger data consistency between systems. The platform is intentionally built to support long-term integration in real business workflows rather than demo-only usage.</p>
        </div>
      </div>
      <div class="post">
        <h2>Frequently Asked Questions</h2>
        <div class="body">
          <p><strong>Can I use this for lead generation workflows?</strong><br>Yes. Teams commonly run target domains through PageIQ, extract contacts and technology context, and use that intelligence to personalize outreach and qualification logic.</p>
          <p><strong>Does it work on JavaScript-heavy websites?</strong><br>Yes. Browser-enabled options are available on supported plans to improve extraction quality for dynamic front-end rendering.</p>
          <p><strong>Is this useful beyond sales teams?</strong><br>Absolutely. Product marketing, SEO operations, competitive intelligence, and customer success teams all use website intelligence for different strategic decisions.</p>
        </div>
      </div>
    """,
)

SEO_ENTRY_PAGES = {
    "/seo-audit-api": {
        "title": "Website SEO Audit API - Automated Technical and On-Page Scoring",
        "description": "Automate website SEO audits with API-based scoring for titles, metadata, headings, schema, and technical factors.",
        "keywords": "seo audit api, technical seo api, on page seo audit api, website seo score api",
        "hero_title": "Website SEO Audit API",
        "hero_subtext": "Programmatically audit any website for ranking-critical SEO factors with machine-readable output and actionable recommendations.",
        "content": """
          <div class="post">
            <h2>Automate SEO Audits Without Manual Checklists</h2>
            <div class="body">
              <p>The Website SEO Audit API is designed for teams that need reliable and repeatable SEO diagnostics at scale. Instead of manually reviewing page titles, descriptions, heading hierarchy, image accessibility, schema signals, mobile readiness, and canonical/indexing controls, you can run structured audit checks from a single endpoint call. This enables consistent QA across client portfolios, landing-page fleets, and enterprise content programs.</p>
              <p>Each audit result includes scored items and severity context so your team can prioritize fixes by impact. Because the output is structured, it can feed dashboards, ticketing systems, and automated workflows. Agencies use this endpoint to generate audit deliverables. In-house SEO teams use it for daily monitoring. Product-led companies use it to enforce launch guardrails before publishing new pages.</p>
              <p>By converting SEO review into a data product, your organization can move from occasional manual auditing to continuous optimization. The endpoint supports integrations where every URL change triggers a re-audit, giving teams confidence that technical regressions are caught quickly and prioritized correctly.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/seo/seo-audit</code></p>
            </div>
          </div>
          <div class="post">
            <h2>What You Can Build</h2>
            <div class="body">
              <ul>
                <li>Automated SEO health dashboards for client account managers.</li>
                <li>Daily page quality alerts routed into Slack or issue trackers.</li>
                <li>Pre-publish QA checks for content operations pipelines.</li>
                <li>Competitor benchmark reports with recurring snapshots.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/website-scraper-api": {
        "title": "Website Scraper API - Structured Business Intelligence from Any URL",
        "description": "Extract actionable website business data with a robust website scraper API built for automation and enrichment workflows.",
        "keywords": "website scraper api, website data extraction api, web scraping api for business intelligence",
        "hero_title": "Website Scraper API",
        "hero_subtext": "Transform websites into structured records that your sales, operations, and analytics systems can use immediately.",
        "content": """
          <div class="post">
            <h2>From Raw HTML to Decision-Ready Data</h2>
            <div class="body">
              <p>PageIQ's Website Scraper API is built around one core idea: scraped data is only useful when it arrives as a coherent business object. While many scraping solutions return fragmented text, this API focuses on practical outputs such as title quality, contact indicators, social profile footprints, schema entities, and technology context. That means less cleanup, fewer brittle parsing rules, and faster deployment into production workflows.</p>
              <p>Teams use this endpoint for lead qualification, account enrichment, market mapping, and competitor monitoring. Whether you are processing a few domains during outreach research or large batches for portfolio-wide intelligence, the response model is consistent and integration-friendly. Developers can plug it into queue workers, cron jobs, enrichment microservices, or user-facing analysis products.</p>
              <p>If your organization wants to cut manual website research and standardize intelligence gathering, this endpoint is the foundation. It delivers broad extraction coverage while preserving the response structure needed for reliable automation and downstream analytics.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/analyze</code></p>
            </div>
          </div>
          <div class="post">
            <h2>Workflow Outcomes</h2>
            <div class="body">
              <ul>
                <li>Populate CRM account records with fresh website intelligence.</li>
                <li>Power prospecting tools with instant domain-level context.</li>
                <li>Generate weekly market intelligence reports automatically.</li>
                <li>Improve segmentation by combining technology and metadata signals.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/email-extractor-api": {
        "title": "Find Business Emails from Website API - Contact Discovery at Scale",
        "description": "Find and extract verified business emails from websites using a scalable API designed for outbound and enrichment workflows.",
        "keywords": "email extractor api, website email finder api, business email scraping api",
        "hero_title": "Find Business Emails from Website API",
        "hero_subtext": "Discover high-value contact emails from websites with deduplicated output and optional deep crawl support.",
        "content": """
          <div class="post">
            <h2>Contact Discovery Built for Real GTM Operations</h2>
            <div class="body">
              <p>The Email Extractor API helps growth teams identify relevant business contacts directly from public web properties. Instead of manually clicking through contact pages, footers, and policy links, your team can automate extraction and feed results into outbound systems. This is especially useful for agencies, B2B SaaS teams, and data operations groups that need repeatable contact sourcing.</p>
              <p>The endpoint returns deduplicated email results and supports deeper crawl behavior on eligible plans for broader domain coverage. In production environments, this enables scheduled enrichment where newly discovered contacts are scored, routed, and synced across CRM and engagement tooling. Combined with website metadata and technology context, extracted emails become part of a richer account intelligence profile.</p>
              <p>PageIQ emphasizes output quality and operational usability, giving teams a pragmatic foundation for contact workflows. Instead of brittle one-off scripts, you get a stable API contract that can be versioned, monitored, and scaled with your data pipeline.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/extract/emails</code></p>
            </div>
          </div>
          <div class="post">
            <h2>Practical Use Cases</h2>
            <div class="body">
              <ul>
                <li>Website-to-CRM contact enrichment jobs.</li>
                <li>Outbound lead list expansion workflows.</li>
                <li>Sales territory refresh with newly detected contacts.</li>
                <li>Market research projects requiring domain-level contact mapping.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/tech-stack-detector-api": {
        "title": "Website Technology Detection API - Framework and Language Intelligence",
        "description": "Detect website technologies, frameworks, analytics tools, and language signals with a dedicated technology detection API.",
        "keywords": "tech stack detector api, website technology api, framework detection api, javascript detection api",
        "hero_title": "Website Technology Detection API",
        "hero_subtext": "Identify frameworks, platforms, analytics tools, and web language signals from any domain with one API call.",
        "content": """
          <div class="post">
            <h2>Understand the Stack Behind Every Website</h2>
            <div class="body">
              <p>Technology context is critical for qualification, personalization, and market segmentation. The Technology Detection API identifies framework and platform fingerprints from HTML structure, script references, stylesheets, and selected response headers. It also reports web language signals such as HTML, CSS, and JavaScript so your team can quickly classify site complexity and front-end profile.</p>
              <p>Revenue teams use technology intelligence to prioritize accounts based on compatibility with their product. Partnerships teams use it for strategic targeting. Product marketers use stack breakdowns to craft better messaging by ecosystem. Because the output is machine-readable, detected signals can be mapped to account scoring models, routing logic, and campaign automation.</p>
              <p>This endpoint is optimized to produce practical stack visibility that supports immediate decision-making. When paired with metadata and SEO diagnostics, it becomes part of a complete website intelligence workflow.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/analyze/tech</code></p>
            </div>
          </div>
          <div class="post">
            <h2>Business Value of Stack Detection</h2>
            <div class="body">
              <ul>
                <li>Segment outbound campaigns by framework or CMS footprint.</li>
                <li>Flag migration opportunities and competitor overlap patterns.</li>
                <li>Build territory ownership rules from detected technology stacks.</li>
                <li>Prioritize implementation-fit accounts faster.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/website-metadata-api": {
        "title": "Website Metadata Scraper API - SEO and Semantic Enrichment",
        "description": "Scrape title, description, schema.org, and Open Graph metadata with a reliable website metadata API.",
        "keywords": "website metadata api, metadata scraper api, schema extraction api, open graph api",
        "hero_title": "Website Metadata Scraper API",
        "hero_subtext": "Extract title, description, schema.org objects, and Open Graph tags to enrich records and improve analysis quality.",
        "content": """
          <div class="post">
            <h2>Metadata Extraction that Feeds Real Systems</h2>
            <div class="body">
              <p>Metadata provides a concise snapshot of how a business presents itself online. The Website Metadata API captures high-value fields such as page title, meta description, schema entities, and Open Graph tags in a single response. This is useful for enrichment pipelines, SEO tooling, catalog curation, and competitive positioning workflows.</p>
              <p>Because metadata often drives search snippets, social previews, and semantic interpretation, it can reveal both branding quality and technical maturity. Teams can use this endpoint to score website messaging, identify optimization gaps, and maintain consistent records across internal platforms. The structured output reduces mapping complexity and shortens implementation cycles.</p>
              <p>If you need a dependable metadata source for large domain sets, this endpoint offers a practical extraction contract that balances breadth and usability. It is especially effective when combined with SEO scoring and contact discovery endpoints.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/extract/metadata</code></p>
            </div>
          </div>
          <div class="post">
            <h2>Key Output Areas</h2>
            <div class="body">
              <ul>
                <li>Title and description quality for SERP-focused analysis.</li>
                <li>Schema.org entity extraction for semantic context.</li>
                <li>Open Graph coverage for social distribution readiness.</li>
                <li>Consistent metadata records for enrichment workflows.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/competitor-website-analysis-api": {
        "title": "Competitor Website Analysis API - Multi-Signal Competitive Intelligence",
        "description": "Analyze competitor websites using SEO, metadata, technology, and contact signals through one integrated website intelligence API.",
        "keywords": "competitor website analysis api, competitor intelligence api, website research api",
        "hero_title": "Competitor Website Analysis API",
        "hero_subtext": "Profile competitor websites with operationally useful intelligence across SEO, technology, metadata, and contact dimensions.",
        "content": """
          <div class="post">
            <h2>Competitive Intelligence with Repeatable Data Pipelines</h2>
            <div class="body">
              <p>Competitor analysis is often inconsistent because teams gather data manually and summarize findings in static decks. This endpoint-driven approach changes that model by making competitor intelligence measurable, repeatable, and automatable. You can capture technical footprints, SEO quality indicators, metadata strategy, and contact hints across a competitor set, then track changes over time.</p>
              <p>With a structured API workflow, every analysis cycle produces comparable outputs that can be plotted, scored, and reviewed in dashboards. Product marketing can monitor positioning shifts. Sales teams can identify messaging trends by segment. Leadership can evaluate market movement with fresh snapshots rather than stale research documents.</p>
              <p>PageIQ provides the extraction layer so your team can focus on strategic interpretation. This is the fastest path from web signals to competitive decision support.</p>
              <p><strong>Main endpoint:</strong> <code>POST /api/v1/analyze</code></p>
            </div>
          </div>
          <div class="post">
            <h2>Competitor Insights You Can Operationalize</h2>
            <div class="body">
              <ul>
                <li>Track SEO and metadata deltas by competitor over time.</li>
                <li>Identify technology adoption patterns in your market.</li>
                <li>Benchmark landing-page quality against your own properties.</li>
                <li>Create automated research briefs for GTM and strategy teams.</li>
              </ul>
            </div>
          </div>
        """,
    },
    "/about-pageiq": {
        "title": "About PageIQ - Website Intelligence Platform Story",
        "description": "Learn about PageIQ, the mission, platform approach, and why website intelligence is essential for modern growth teams.",
        "keywords": "about pageiq, website intelligence company, api platform mission",
        "hero_title": "About PageIQ",
        "hero_subtext": "A practical website intelligence engine built for execution-focused teams that need faster research and cleaner data.",
        "content": """
          <div class="post">
            <h2>Our Story and Mission</h2>
            <div class="body">
              <p>PageIQ was built from a recurring pain point: teams spending too much time manually researching websites and too little time executing on insights. We saw operations leaders, agency strategists, and growth engineers repeatedly rebuilding partial scraping systems that were expensive to maintain and inconsistent in output. The mission became clear: provide a stable API layer that transforms websites into useful business intelligence records.</p>
              <p>Our philosophy is simple: data extraction should be practical, maintainable, and designed for action. That means endpoint reliability, predictable response structures, meaningful fields, and transparent behavior. We prioritize workflows that drive measurable outcomes: faster qualification, better segmentation, stronger competitor awareness, and improved campaign precision.</p>
              <p>As the platform evolves, we continue to expand both extraction depth and integration readiness. The goal is not to produce noisy data, but to produce operationally useful context that teams can trust and put into production quickly.</p>
            </div>
          </div>
        """,
    },
    "/pricing-plans": {
        "title": "PageIQ Pricing and Plans - Website Intelligence API Packages",
        "description": "Explore PageIQ pricing plans for website intelligence API usage across startups, agencies, and enterprise teams.",
        "keywords": "pageiq pricing, website intelligence api pricing, seo api pricing",
        "hero_title": "Pricing and Plans",
        "hero_subtext": "Choose a plan aligned with your usage volume, feature depth, and operational needs.",
        "content": """
          <div class="post">
            <h2>Plan Overview</h2>
            <div class="body">
              <p><strong>Starter:</strong> Built for validation projects and low-volume research workflows. Includes core analysis and baseline extraction for teams beginning to operationalize website intelligence.</p>
              <p><strong>Growth:</strong> Designed for active sales and marketing operations. Provides broader throughput and richer extraction options, including browser-assisted behavior where applicable.</p>
              <p><strong>Scale:</strong> Supports agency and SaaS workloads with higher throughput, stronger operational controls, and deeper integration support for recurring automation jobs.</p>
              <p><strong>Enterprise:</strong> Tailored plans for organizations requiring custom throughput, governance controls, and workflow consultation around large-scale website intelligence programs.</p>
              <p>All plans focus on practical extraction value rather than vanity metrics. Contact us through your preferred channel to map volume and use-case requirements to the right tier.</p>
            </div>
          </div>
        """,
    },
    "/faq-page": {
        "title": "PageIQ FAQ - Website Intelligence API Questions",
        "description": "Answers to common questions about PageIQ endpoints, integration patterns, and production usage.",
        "keywords": "pageiq faq, website intelligence api faq, seo api questions",
        "hero_title": "Frequently Asked Questions",
        "hero_subtext": "Everything teams ask before integrating a website intelligence API into production workflows.",
        "content": """
          <div class="post">
            <h2>Frequently Asked Questions</h2>
            <div class="body">
              <p><strong>How quickly can we integrate PageIQ?</strong><br>Most teams can run meaningful tests in under one hour and ship first workflow automation within one sprint.</p>
              <p><strong>Can we process dynamic websites?</strong><br>Yes. Browser-assisted options are available on supported plans for better results on JavaScript-heavy pages.</p>
              <p><strong>What if we only need one use case?</strong><br>You can start with a single endpoint such as metadata or SEO audit, then expand into full analysis as needs grow.</p>
              <p><strong>Does the API support ongoing monitoring?</strong><br>Yes. Teams commonly run scheduled analysis jobs and compare outputs over time for trend detection.</p>
              <p><strong>Where can developers find endpoint references?</strong><br>Visit our complete documentation at <a href="/docs">/docs</a> and API reference at <a href="/docs">Developer Docs</a>.</p>
            </div>
          </div>
        """,
    },
    "/guestbook": {
        "title": "PageIQ Guestbook - Community Notes",
        "description": "Sign the PageIQ guestbook and share your website intelligence automation journey.",
        "keywords": "pageiq guestbook, api community guestbook, retro web guestbook",
        "hero_title": "PageIQ Community Guestbook",
        "hero_subtext": "Leave a note, share your build, and tell us how you are using website intelligence in production.",
        "content": """
          <div class="post">
            <h2>Sign Our Guestbook</h2>
            <div class="body">
              <p>Welcome to the PageIQ guestbook, inspired by the classic web era. We built this page to celebrate independent builders, automation engineers, and growth operators who are creating practical systems with APIs. Share your project, your biggest integration win, or a message to fellow builders.</p>
              <form>
                <p><label>Name:<br><input type="text" style="width:95%; padding:6px;"></label></p>
                <p><label>Company or Project:<br><input type="text" style="width:95%; padding:6px;"></label></p>
                <p><label>Your Message:<br><textarea style="width:95%; height:120px; padding:6px;"></textarea></label></p>
                <p><button type="button" class="button">Submit Entry (Demo UI)</button></p>
              </form>
              <p><strong>Recent Entries:</strong></p>
              <p>"Integrated PageIQ into our outbound ops stack and cut research time by 80 percent." - Growth Ops Team</p>
              <p>"Using the SEO audit endpoint to auto-generate client QA reports every Monday morning." - Agency Strategist</p>
              <p>"The tech stack endpoint helped our SDR team segment accounts faster than any previous workflow." - RevOps Manager</p>
            </div>
          </div>
        """,
    },
    "/blog-archive": {
        "title": "PageIQ Blog Archive - Website Intelligence Articles",
        "description": "Read long-form articles about website intelligence strategy, API operations, SEO automation, and growth systems.",
        "keywords": "website intelligence blog, api growth strategy blog, seo automation articles",
        "hero_title": "PageIQ Blog Archive",
        "hero_subtext": "Long-form notes on turning website data into repeatable growth systems.",
        "content": """
          <div class="post">
            <h2>Featured Article: From Manual Research to Automated Website Intelligence</h2>
            <div class="body">
              <p>Most teams begin website research with ad-hoc browser sessions and spreadsheet notes. Over time, this approach creates inconsistency, slows execution, and limits strategic visibility. A more scalable model starts by defining required signals, mapping them to consistent extraction fields, and running collection through repeatable API jobs. The result is a system where intelligence improves over time instead of getting lost in isolated docs.</p>
              <p>To make that transition, begin with one focused workflow. For example, automate metadata and technology extraction for your top account segment, then feed results into your CRM with timestamps. Once this process is stable, add SEO diagnostics and contact discovery. The compounding value appears when data from multiple endpoints converges into one account view that sales, marketing, and strategy teams can act on immediately.</p>
              <p>In practical terms, website intelligence becomes more than scraping. It becomes an operational layer: a repeatable process that helps teams prioritize effort, personalize outreach, and evaluate market movement with confidence. That is the shift we believe modern teams should make.</p>
            </div>
          </div>
          <div class="post">
            <h2>Archive Index</h2>
            <div class="body">
              <ul>
                <li>How to Build Intent-Based API Landing Pages for SEO Growth</li>
                <li>Operational Playbook: Automating Weekly Competitor Monitoring</li>
                <li>Designing Reliable Enrichment Pipelines with Structured API Contracts</li>
                <li>Choosing Between Single-Endpoint and Multi-Endpoint Intelligence Architectures</li>
              </ul>
            </div>
          </div>
        """,
    },
}


@router.get("/seo-audit-api", response_class=HTMLResponse)
@router.get("/website-scraper-api", response_class=HTMLResponse)
@router.get("/email-extractor-api", response_class=HTMLResponse)
@router.get("/tech-stack-detector-api", response_class=HTMLResponse)
@router.get("/website-metadata-api", response_class=HTMLResponse)
@router.get("/competitor-website-analysis-api", response_class=HTMLResponse)
@router.get("/about-pageiq", response_class=HTMLResponse)
@router.get("/pricing-plans", response_class=HTMLResponse)
@router.get("/faq-page", response_class=HTMLResponse)
@router.get("/guestbook", response_class=HTMLResponse)
@router.get("/blog-archive", response_class=HTMLResponse)
async def seo_entry_pages(request: Request):
    request_path = request.url.path
    if request_path.startswith("/api/v1/docs"):
        request_path = request_path[len("/api/v1/docs"):] or "/"

    page = SEO_ENTRY_PAGES.get(request_path)
    if not page:
        return HTMLResponse("Not found", status_code=404)

    return HTMLResponse(
        content=build_retro_page(
            title=page["title"],
            meta_description=page["description"],
            meta_keywords=page["keywords"],
            hero_title=page["hero_title"],
            hero_subtext=page["hero_subtext"],
            main_html=page["content"],
        )
    )

MODERN_DOCS_HTML = build_retro_page(
    title="PageIQ Developer Documentation - Retro Edition",
    meta_description="Comprehensive PageIQ API documentation with endpoint breakdowns, plan gating, request examples, response contracts, and integration guidance.",
    meta_keywords="pageiq api documentation, website intelligence api docs, seo audit api docs, metadata api docs, tech stack api docs",
    hero_title="PageIQ Developer Documentation Portal",
    hero_subtext="Complete endpoint reference, practical integration notes, rich examples, and production guidance in one place. Built in retro style, shipped with modern API detail.",
    main_html='''
      <div class="post">
        <h2>Documentation Overview</h2>
        <div class="body">
          <p>This documentation hub is designed for developers, technical founders, and GTM engineers integrating PageIQ into live systems. It goes beyond quickstart snippets and focuses on operational details that matter in production: response shape differences, feature-gating behavior, route aliasing, health checks, and failure handling patterns. If you are building an internal tool, public SaaS integration, or batch intelligence workflow, this page should function as your practical command center.</p>
          <p>PageIQ offers two primary response patterns: envelope-based responses for selected endpoints and direct model responses for extraction and SEO routes. Understanding this distinction early prevents integration bugs, especially when standardizing parsers across endpoint families. You should also handle plan-dependent capability controls for deep crawling and browser-assisted extraction, which can return explicit `403` constraints based on user tier.</p>
          <p>For full canonical reference and change notes, see <code>docs/API_DOCUMENTATION.md</code> in the repository. This page complements that file with a narrative integration view and richer examples for common workflows.</p>
        </div>
      </div>

      <div class="post">
        <h2>Endpoint Families and Practical Use</h2>
        <div class="body">
          <p><strong>Analyze endpoints:</strong> Use `/api/v1/analyze` when you need broad, multi-signal website intelligence in one request. Use `/api/v1/analyze/tech` when stack and web language classification are the primary outputs.</p>
          <p><strong>Extraction endpoints:</strong> Use `/api/v1/extract/emails`, `/schema`, and `/metadata` for focused retrieval tasks where response minimalism and specificity matter for downstream mapping.</p>
          <p><strong>SEO endpoints:</strong> Use `/api/v1/seo/seo-audit` for score-driven quality checks and `/api/v1/seo/broken-links` for structural link inventory and diagnostics.</p>
          <p><strong>Analytics and account endpoints:</strong> Use `/api/v1/analytics/*` for usage visibility and `/api/v1/account/*` for subscription/billing controls in authenticated contexts.</p>
          <p>The most resilient architecture is usually layered: run broad `/analyze` for account enrichment, then trigger targeted extraction or SEO endpoints only when deeper verification is needed.</p>
        </div>
      </div>

      <div class="post">
        <h2>Authentication, Headers, and Envelope Behavior</h2>
        <div class="body">
          <p>Include your API key in request headers. In most implementations, teams wrap requests in a shared HTTP client that injects auth and standard retry behavior. For endpoints that return envelope responses, parse `success`, `data`, and optional request metadata; for direct model endpoints, parse fields directly at root level.</p>
          <pre style="background:#111;color:#9ef;padding:10px;overflow:auto;">POST /api/v1/analyze
X-API-Key: YOUR_API_KEY
Content-Type: application/json

{
  "url": "https://example.com",
  "options": {
    "screenshot": true
  }
}</pre>
          <p>Operationally, always log `request_id` when present and surface it in support tooling. That one field cuts debugging time significantly when tracing user reports and platform issues.</p>
        </div>
      </div>

      <div class="post">
        <h2>Plan Gating and Feature Access</h2>
        <div class="body">
          <p>Certain high-cost capabilities are plan-gated in endpoint logic. For example, `deep_search` and browser-render extraction options are restricted to higher tiers. Your client should detect and classify feature-gate responses separately from generic authorization failures. This helps product UX communicate clear upgrade pathways instead of generic error messaging.</p>
          <p>A production-ready integration generally includes:</p>
          <ul>
            <li>Pre-flight capability checks tied to account plan metadata.</li>
            <li>Error translation layer that maps `403` feature gates to actionable UI copy.</li>
            <li>Fallback extraction path for lower-tier users when premium options are unavailable.</li>
            <li>Usage telemetry to identify which gated features users attempt most frequently.</li>
          </ul>
          <p>These practices improve conversion and reduce support load while preserving predictable user experience.</p>
        </div>
      </div>

      <div class="post">
        <h2>Failure Handling and Reliability Pattern</h2>
        <div class="body">
          <p>In live systems, website intelligence operations naturally encounter fetch anomalies, parsing edge cases, robots restrictions, and occasional upstream instability. Build your client with strong retry and classification logic: retry transient `5xx`, avoid retrying deterministic `4xx`, and isolate URL-level failures so batch jobs continue processing remaining records.</p>
          <p>Recommended reliability flow:</p>
          <ul>
            <li>Normalize URL inputs before dispatch.</li>
            <li>Apply request timeouts and exponential backoff.</li>
            <li>Capture response body + request ID for diagnostics.</li>
            <li>Store endpoint-specific failure reasons for analytics.</li>
            <li>Use dead-letter queues for repeat failures in async workers.</li>
          </ul>
          <p>These patterns are particularly valuable when integrating PageIQ into nightly enrichment runs or high-volume territory scans.</p>
        </div>
      </div>

      <div class="post">
        <h2>Developer Quick Links</h2>
        <div class="body">
          <ul>
            <li><a href="/api/v1/health">Live API health check</a></li>
            <li><a href="/api/v1/docs/">Versioned docs index alias</a></li>
            <li><a href="/seo-audit-api">SEO Audit API landing page</a></li>
            <li><a href="/website-scraper-api">Website Scraper API landing page</a></li>
            <li><a href="/email-extractor-api">Email Extractor API landing page</a></li>
            <li><a href="/tech-stack-detector-api">Tech Stack Detector API landing page</a></li>
            <li><a href="/website-metadata-api">Website Metadata API landing page</a></li>
            <li><a href="/competitor-website-analysis-api">Competitor Analysis API landing page</a></li>
          </ul>
          <p>For complete, line-by-line endpoint reference with examples and routing notes, use the maintained technical reference in `docs/API_DOCUMENTATION.md`.</p>
        </div>
      </div>
    '''
)
