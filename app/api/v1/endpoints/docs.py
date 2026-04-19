"""
Website and documentation pages for PageIQ.
Serves modern 2015-style marketing and docs pages.
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()


def build_page(
    *,
    title: str,
    description: str,
    keywords: str,
    canonical_path: str,
    hero_title: str,
    hero_text: str,
    main_html: str,
) -> str:
    canonical_url = f"https://pageiq.pompora.dev{canonical_path}"
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <meta name="keywords" content="{keywords}">
  <meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
  <link rel="canonical" href="{canonical_url}">
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:site_name" content="PageIQ">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{description}">
  <style>
    :root {{
      --bg: #f3f6fb;
      --panel: #ffffff;
      --panel-muted: #f8fafc;
      --text: #1f2937;
      --muted: #6b7280;
      --primary: #2563eb;
      --primary-dark: #1d4ed8;
      --border: #dbe3ee;
      --success: #0f9d58;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.65;
    }}
    .site {{
      max-width: 1280px;
      margin: 0 auto;
      background: var(--panel);
      min-height: 100vh;
      border-left: 1px solid var(--border);
      border-right: 1px solid var(--border);
    }}
    .topbar {{
      background: #111827;
      color: #d1d5db;
      font-size: 12px;
      padding: 8px 22px;
      display: flex;
      justify-content: space-between;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .nav {{
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      padding: 14px 22px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
    }}
    .brand {{
      font-size: 24px;
      font-weight: 700;
      color: #0f172a;
      letter-spacing: 0.2px;
    }}
    .menu {{
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }}
    .menu a {{
      text-decoration: none;
      color: #1f2937;
      font-size: 14px;
      padding: 8px 10px;
      border-radius: 6px;
    }}
    .menu a:hover {{ background: #eef4ff; color: var(--primary-dark); }}
    .hero {{
      padding: 42px 28px 32px;
      background: linear-gradient(130deg, #eef5ff 0%, #f8fbff 50%, #eef2ff 100%);
      border-bottom: 1px solid var(--border);
    }}
    .hero h1 {{
      margin: 0 0 12px;
      font-size: 44px;
      line-height: 1.1;
      color: #0f172a;
      max-width: 980px;
    }}
    .hero p {{
      margin: 0 0 20px;
      color: #475569;
      font-size: 18px;
      max-width: 980px;
    }}
    .cta-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
    }}
    .btn {{
      display: inline-block;
      text-decoration: none;
      padding: 11px 16px;
      border-radius: 7px;
      font-weight: 600;
      font-size: 14px;
      border: 1px solid transparent;
    }}
    .btn-primary {{
      background: var(--primary);
      color: #fff;
    }}
    .btn-primary:hover {{ background: var(--primary-dark); }}
    .btn-secondary {{
      background: #fff;
      border-color: var(--border);
      color: #1f2937;
    }}
    .content {{
      display: grid;
      grid-template-columns: 270px 1fr;
      gap: 18px;
      padding: 20px 18px 28px;
    }}
    .sidebar {{
      background: var(--panel-muted);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      height: fit-content;
      position: sticky;
      top: 14px;
    }}
    .side-group {{
      margin-bottom: 14px;
      border-bottom: 1px dashed #d0dae8;
      padding-bottom: 12px;
    }}
    .side-group:last-child {{ margin-bottom: 0; border-bottom: 0; }}
    .side-group h3 {{
      margin: 0 0 8px;
      font-size: 14px;
      color: #0f172a;
    }}
    .side-group ul {{
      margin: 0;
      padding-left: 16px;
      color: var(--muted);
      font-size: 13px;
    }}
    .side-group li {{ margin-bottom: 6px; }}
    .main {{
      min-width: 0;
    }}
    .section {{
      border: 1px solid var(--border);
      border-radius: 8px;
      background: #fff;
      margin-bottom: 14px;
      overflow: hidden;
    }}
    .section h2 {{
      margin: 0;
      padding: 12px 14px;
      font-size: 20px;
      color: #0f172a;
      background: #f7faff;
      border-bottom: 1px solid var(--border);
    }}
    .section .body {{
      padding: 14px 15px 16px;
      font-size: 15px;
      color: #374151;
    }}
    .section p {{ margin: 0 0 12px; }}
    .section ul {{ margin: 0 0 10px 18px; }}
    .section li {{ margin-bottom: 6px; }}
    .grid-two {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
    }}
    .pill {{
      display: inline-block;
      background: #e6f4ea;
      color: var(--success);
      border: 1px solid #c6e9d1;
      padding: 4px 8px;
      font-size: 12px;
      border-radius: 999px;
      font-weight: 600;
    }}
    .pricing {{
      width: 100%;
      border-collapse: collapse;
      font-size: 14px;
    }}
    .pricing th, .pricing td {{
      border: 1px solid var(--border);
      padding: 10px;
      text-align: left;
      vertical-align: top;
    }}
    .pricing th {{
      background: #eff6ff;
      color: #1e3a8a;
    }}
    pre {{
      margin: 10px 0;
      background: #111827;
      color: #d1e8ff;
      padding: 10px;
      border-radius: 6px;
      overflow-x: auto;
      font-size: 13px;
    }}
    code {{
      background: #eef4ff;
      border: 1px solid #dae7ff;
      border-radius: 4px;
      padding: 1px 5px;
      color: #1e3a8a;
      font-family: Consolas, "Courier New", monospace;
    }}
    .footer {{
      padding: 18px 22px 26px;
      color: var(--muted);
      font-size: 13px;
      border-top: 1px solid var(--border);
      background: #fafcff;
    }}
    @media (max-width: 1024px) {{
      .content {{
        grid-template-columns: 1fr;
        padding: 14px;
      }}
      .sidebar {{ position: static; }}
      .hero h1 {{ font-size: 34px; }}
      .grid-two {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="site">
    <div class="topbar">
      <div>PageIQ Website Intelligence API</div>
      <div>Available exclusively via RapidAPI marketplace</div>
    </div>
    <nav class="nav">
      <div class="brand">PageIQ</div>
      <div class="menu">
        <a href="/">Home</a>
        <a href="/docs">Docs</a>
        <a href="/seo-audit-api">SEO Audit API</a>
        <a href="/website-scraper-api">Website Scraper API</a>
        <a href="/email-extractor-api">Email Extractor API</a>
        <a href="/tech-stack-detector-api">Tech Stack Detector API</a>
        <a href="/website-metadata-api">Metadata API</a>
        <a href="/pricing-plans">Pricing</a>
      </div>
    </nav>
    <header class="hero">
      <h1>{hero_title}</h1>
      <p>{hero_text}</p>
      <div class="cta-row">
        <a class="btn btn-primary" href="https://rapidapi.com" target="_blank" rel="noopener noreferrer">Try on RapidAPI</a>
        <a class="btn btn-secondary" href="/docs">Read Full Documentation</a>
        <a class="btn btn-secondary" href="/api/v1/health">API Health</a>
      </div>
    </header>
    <div class="content">
      <aside class="sidebar">
        <div class="side-group">
          <h3>Core API Pages</h3>
          <ul>
            <li><a href="/seo-audit-api">Website SEO Audit API</a></li>
            <li><a href="/website-scraper-api">Website Scraper API</a></li>
            <li><a href="/email-extractor-api">Find Business Emails API</a></li>
            <li><a href="/tech-stack-detector-api">Technology Detection API</a></li>
            <li><a href="/website-metadata-api">Metadata Scraper API</a></li>
            <li><a href="/competitor-website-analysis-api">Competitor Analysis API</a></li>
          </ul>
        </div>
        <div class="side-group">
          <h3>Platform Notes</h3>
          <ul>
            <li>RapidAPI-only distribution and billing</li>
            <li>Plan-gated deep search and JS rendering</li>
            <li>Production-grade endpoint contracts</li>
            <li>Built for agencies, SaaS, and RevOps teams</li>
          </ul>
        </div>
        <div class="side-group">
          <h3>Direct Links</h3>
          <ul>
            <li><a href="/pricing-plans">Pricing and Quotas</a></li>
            <li><a href="/faq-page">FAQ</a></li>
            <li><a href="/about-pageiq">About</a></li>
            <li><a href="/api/v1/docs/docs">Versioned Docs Alias</a></li>
          </ul>
        </div>
      </aside>
      <main class="main">
        {main_html}
      </main>
    </div>
    <footer class="footer">
      PageIQ is available only through RapidAPI. Access, quotas, and billing are managed on RapidAPI.
    </footer>
  </div>
</body>
</html>
"""


HOME_HTML = build_page(
    title="PageIQ | Turn Any Website Into Actionable Business Data",
    description="Extract SEO score, tech stack, metadata, verified emails, socials, and hidden business intelligence from any URL. Available on RapidAPI.",
    keywords="website intelligence api, seo audit api, website scraper api, email extractor api, tech stack detector api, metadata api",
    canonical_path="/",
    hero_title="Turn Any Website Into Actionable Business Data",
    hero_text="Extract SEO score, tech stack, metadata, verified emails, socials, and hidden business intelligence from any URL. PageIQ gives growth teams and developers an operational data engine that scales from ad-hoc research to high-volume automation.",
    main_html="""
      <section class="section">
        <h2>Why Teams Use PageIQ</h2>
        <div class="body">
          <p>PageIQ is built for practical execution. Instead of stitching together multiple scraping tools and custom scripts, teams call one API and receive structured outputs designed for CRM enrichment, competitor tracking, SEO diagnostics, and outbound personalization. The objective is speed to value: less manual research and more action-ready context.</p>
          <p>Across agencies, SaaS GTM teams, and operations functions, PageIQ consistently reduces research time while improving consistency. Every response is built to be machine-readable and integration-friendly, allowing you to power internal dashboards, enrichment jobs, alerting workflows, and intelligence reports with stable endpoint behavior.</p>
          <div class="grid-two">
            <div>
              <span class="pill">Use Case: Sales & RevOps</span>
              <p>Detect technologies, collect metadata, and extract contact signals to prioritize accounts and personalize outbound messaging at scale.</p>
            </div>
            <div>
              <span class="pill">Use Case: SEO & Content</span>
              <p>Run repeatable audit checks and monitor on-page quality trends without manual spreadsheet-heavy processes.</p>
            </div>
          </div>
        </div>
      </section>
      <section class="section">
        <h2>Multi-Entry SEO Pages</h2>
        <div class="body">
          <p>PageIQ follows intent-based page architecture so each workflow can rank and convert independently. Use dedicated pages to match search intent and send traffic to the exact API capability:</p>
          <ul>
            <li><a href="/seo-audit-api">Website SEO Audit API</a></li>
            <li><a href="/website-scraper-api">Website Scraper API</a></li>
            <li><a href="/email-extractor-api">Find Business Emails from Website API</a></li>
            <li><a href="/tech-stack-detector-api">Website Technology Detection API</a></li>
            <li><a href="/website-metadata-api">Website Metadata Scraper API</a></li>
            <li><a href="/competitor-website-analysis-api">Competitor Website Analysis API</a></li>
          </ul>
        </div>
      </section>
      <section class="section">
        <h2>RapidAPI Access and Pricing</h2>
        <div class="body">
          <p>PageIQ is distributed exclusively through RapidAPI. Access provisioning, usage metering, and billing are handled on RapidAPI. There is no public repository access for customers and no alternate distribution channel.</p>
          <p>For plan details, quotas, deep email search limits, and add-on pricing, visit the <a href="/pricing-plans">Pricing page</a> on this site.</p>
        </div>
      </section>
    """,
)


DOCS_HTML = build_page(
    title="PageIQ Developer Docs | API Reference and Integration Guide",
    description="Comprehensive PageIQ docs covering endpoint behavior, payload contracts, plan gating, and production integration practices.",
    keywords="pageiq docs, website intelligence api docs, rapidapi endpoint reference, seo api integration",
    canonical_path="/docs",
    hero_title="Developer Documentation",
    hero_text="Complete endpoint coverage, payload examples, integration architecture guidance, and plan-aware implementation notes for production teams.",
    main_html="""
      <section class="section">
        <h2>Platform Access Model</h2>
        <div class="body">
          <p>PageIQ is available only through RapidAPI. Your API credentials, quotas, and billing lifecycle are managed on RapidAPI. Integration should assume RapidAPI as the source of truth for subscription state and account-level entitlements.</p>
          <p>Core request base URL: <code>https://pageiq.pompora.dev/api/v1</code></p>
          <pre>POST /api/v1/analyze
X-API-Key: YOUR_API_KEY
Content-Type: application/json

{"url":"https://example.com","options":{"screenshot":true}}</pre>
        </div>
      </section>
      <section class="section">
        <h2>Endpoint Families</h2>
        <div class="body">
          <ul>
            <li><strong>Analyze:</strong> <code>/api/v1/analyze</code>, <code>/api/v1/analyze/tech</code></li>
            <li><strong>Extract:</strong> <code>/api/v1/extract/emails</code>, <code>/api/v1/extract/schema</code>, <code>/api/v1/extract/metadata</code></li>
            <li><strong>SEO:</strong> <code>/api/v1/seo/seo-audit</code>, <code>/api/v1/seo/broken-links</code></li>
            <li><strong>Analytics:</strong> <code>/api/v1/analytics</code>, <code>/api/v1/analytics/performance</code>, <code>/api/v1/analytics/endpoints</code></li>
            <li><strong>Account:</strong> <code>/api/v1/account/*</code></li>
          </ul>
          <p>See full technical reference in <code>docs/API_DOCUMENTATION.md</code> for detailed contracts and route notes.</p>
        </div>
      </section>
      <section class="section">
        <h2>Integration Guidance</h2>
        <div class="body">
          <p>In production clients, normalize endpoint parsing by response style. Some routes return an envelope (<code>success/data</code>) while others return direct model JSON. Implement a route-aware parser or map handlers by endpoint group.</p>
          <ul>
            <li>Retry transient <code>5xx</code> with exponential backoff.</li>
            <li>Handle <code>403</code> feature gates separately from auth failures.</li>
            <li>Store <code>request_id</code> and response bodies for support diagnostics.</li>
            <li>Use queue-based workers for high-volume enrichment and nightly scans.</li>
          </ul>
        </div>
      </section>
      <section class="section">
        <h2>Pricing and Plan Constraints</h2>
        <div class="body">
          <p>Deep search and JS rendering are plan-gated. Align your product UX and fallback behavior to the plan currently active on RapidAPI. Use your account page and billing workflows to prevent invalid requests on lower tiers.</p>
          <p>Exact plan and quota details are listed on the <a href="/pricing-plans">Pricing page</a>.</p>
        </div>
      </section>
    """,
)


PAGES = {
    "/seo-audit-api": {
        "title": "Website SEO Audit API | Automated On-Page and Technical Checks",
        "description": "Automate website SEO audits with score-based diagnostics for title, metadata, headings, schema, and technical factors.",
        "keywords": "seo audit api, technical seo api, on page seo score api, website audit automation",
        "hero_title": "Website SEO Audit API",
        "hero_text": "Run structured, repeatable SEO diagnostics across any website URL and transform audits into actionable engineering and content tasks.",
        "main_html": """
          <section class="section"><h2>Automated SEO Diagnostics at Scale</h2><div class="body">
          <p>This endpoint is built for teams who need repeatable SEO quality control. Instead of manual checklists, you get API-level scoring across title quality, metadata coverage, heading structure, structured data signals, social graph readiness, and technical indexing factors. The response is deterministic and easy to map into scorecards, dashboards, and QA reports.</p>
          <p>Agencies use this API to deliver standardized client audits. Product teams use it before publishing large content batches. Operations teams trigger re-audits when pages are updated so quality drift is detected before it impacts acquisition performance.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/seo/seo-audit</code></p></div></section>
        """,
    },
    "/website-scraper-api": {
        "title": "Website Scraper API | Structured Business Data from Any Domain",
        "description": "Extract structured website intelligence including metadata, contact indicators, social profiles, and technical context with one API.",
        "keywords": "website scraper api, website data extraction api, domain intelligence api",
        "hero_title": "Website Scraper API",
        "hero_text": "Convert unstructured websites into clean, actionable JSON records for automation, enrichment, and market intelligence.",
        "main_html": """
          <section class="section"><h2>One Request, Multi-Signal Output</h2><div class="body">
          <p>The Website Scraper API powers workflows where speed and consistency matter. You can collect title and description quality, schema context, social links, email indicators, and technology signals in a single call. This reduces system complexity and removes the need for fragmented scraping stacks.</p>
          <p>Teams deploy this endpoint in lead enrichment pipelines, account intelligence systems, and internal research tooling where every minute of manual browsing is a bottleneck. The result is faster decision cycles with cleaner records.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/analyze</code></p></div></section>
        """,
    },
    "/email-extractor-api": {
        "title": "Find Business Emails from Website API | Contact Discovery",
        "description": "Extract deduplicated business emails from websites with plan-based deep search options for broader discovery.",
        "keywords": "email extractor api, website email finder api, business contact api",
        "hero_title": "Find Business Emails from Website API",
        "hero_text": "Discover high-value contact emails from websites with automation-ready output for outbound and enrichment workflows.",
        "main_html": """
          <section class="section"><h2>Contact Discovery for Growth Teams</h2><div class="body">
          <p>The email extraction endpoint is optimized for practical outbound and enrichment operations. It returns normalized, deduplicated email lists and supports deep search for higher-tier plans when broader site coverage is required. This lets teams move from slow manual discovery to scalable, repeatable contact collection.</p>
          <p>For best results, pair email extraction with metadata and technology signals so every contact is tied to richer account context and better segmentation strategy.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/extract/emails</code></p></div></section>
        """,
    },
    "/tech-stack-detector-api": {
        "title": "Website Technology Detection API | Framework and Stack Intelligence",
        "description": "Identify frameworks, platforms, analytics tools, and web language signals including HTML, CSS, and JavaScript.",
        "keywords": "tech stack detector api, framework detection api, website technology api",
        "hero_title": "Website Technology Detection API",
        "hero_text": "Detect technology fingerprints and language signals to improve qualification, segmentation, and competitive research.",
        "main_html": """
          <section class="section"><h2>Technology Context that Drives Better Targeting</h2><div class="body">
          <p>Technology intelligence is a high-leverage signal for GTM teams. This endpoint detects frameworks, CMS patterns, analytics footprint, and web language indicators from website artifacts. These outputs can feed account scoring logic, segmentation rules, and campaign personalization.</p>
          <p>The endpoint now returns explicit language fields and combined technology lists so downstream systems can classify websites quickly and consistently.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/analyze/tech</code></p></div></section>
        """,
    },
    "/website-metadata-api": {
        "title": "Website Metadata Scraper API | Title, Description, Schema, Open Graph",
        "description": "Extract website metadata and semantic tags in one call for SEO tooling, enrichment, and analytics workflows.",
        "keywords": "metadata scraper api, website metadata api, schema api, open graph api",
        "hero_title": "Website Metadata Scraper API",
        "hero_text": "Capture title, description, schema.org entities, and Open Graph tags to power cleaner records and stronger SEO workflows.",
        "main_html": """
          <section class="section"><h2>Metadata Extraction Built for Production</h2><div class="body">
          <p>Metadata is often the fastest way to understand website positioning and technical maturity. This endpoint provides focused extraction for key fields used by SEO tools, enrichment layers, cataloging systems, and competitor tracking workflows.</p>
          <p>Because response shape is stable and compact, it is easy to wire into existing data models while preserving semantic detail from schema and Open Graph sources.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/extract/metadata</code></p></div></section>
        """,
    },
    "/competitor-website-analysis-api": {
        "title": "Competitor Website Analysis API | Multi-Signal Competitive Intelligence",
        "description": "Analyze competitor websites with SEO, metadata, technology, and contact signals to support strategy and GTM execution.",
        "keywords": "competitor website analysis api, competitive intelligence api, market research api",
        "hero_title": "Competitor Website Analysis API",
        "hero_text": "Track competitor website signals with consistent, machine-readable data and turn research into repeatable strategy workflows.",
        "main_html": """
          <section class="section"><h2>Competitive Research That Scales</h2><div class="body">
          <p>Manual competitor research does not scale. This endpoint-first model produces repeatable snapshots of SEO, metadata, and technology behavior so teams can track movement over time instead of relying on occasional static reports.</p>
          <p>Product marketing, sales strategy, and leadership teams can use these signals to benchmark market posture, identify shifts, and refine positioning based on current evidence.</p>
          </div></section>
          <section class="section"><h2>Primary Endpoint</h2><div class="body"><p><code>POST /api/v1/analyze</code></p></div></section>
        """,
    },
    "/about-pageiq": {
        "title": "About PageIQ | Website Intelligence API for Execution-Focused Teams",
        "description": "Learn how PageIQ helps teams transform websites into structured, actionable business data.",
        "keywords": "about pageiq, website intelligence platform, data extraction api company",
        "hero_title": "About PageIQ",
        "hero_text": "A website intelligence platform designed for teams who care about execution speed, data quality, and operational reliability.",
        "main_html": """
          <section class="section"><h2>Platform Mission</h2><div class="body">
          <p>PageIQ exists to remove the friction of website intelligence gathering. Instead of maintaining fragile in-house scraping stacks, teams can call stable endpoints and route structured outputs directly into operational systems. We prioritize pragmatic value: data that can immediately support decisions, not just technical novelty.</p>
          <p>Our product direction is grounded in real implementation needs from agencies, SaaS teams, and RevOps operators who need high-signal outputs and predictable behavior under production load.</p>
          </div></section>
        """,
    },
    "/pricing-plans": {
        "title": "PageIQ Pricing and Plans | RapidAPI Subscription Tiers",
        "description": "Official PageIQ pricing tiers available on RapidAPI, including Basic, Pro, Ultra, and Mega plans.",
        "keywords": "pageiq pricing, rapidapi pricing, seo api plans, website intelligence api plans",
        "hero_title": "Pricing and Plans (RapidAPI)",
        "hero_text": "PageIQ is sold through RapidAPI. Use this pricing matrix to align monthly volume, deep email search limits, and rendering capability with your workflow.",
        "main_html": """
          <section class="section">
            <h2>Current Plan Matrix</h2>
            <div class="body">
              <table class="pricing">
                <thead>
                  <tr>
                    <th>Plan</th>
                    <th>Price</th>
                    <th>Deep Email Search</th>
                    <th>Requests</th>
                    <th>Feature Access</th>
                    <th>Rate / Bandwidth</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td><strong>Basic</strong></td>
                    <td><strong>$0.00 / month</strong></td>
                    <td>-</td>
                    <td>10 / month (Hard Limit)</td>
                    <td>Deep Email Search: No<br>JS Rendering: No</td>
                    <td>Rate: 1000 req/hour<br>Bandwidth: 10240MB/month + $0.001 per MB</td>
                  </tr>
                  <tr>
                    <td><strong>Pro</strong> (Recommended)</td>
                    <td><strong>$25.00 / month</strong></td>
                    <td>50 / month (+ $0.01)</td>
                    <td>10,000 / month (+ $0.05)</td>
                    <td>Deep Email Search: Yes<br>JS Rendering: Yes</td>
                    <td>Rate: Platform controlled<br>Bandwidth: 10240MB/month + $0.001 per MB</td>
                  </tr>
                  <tr>
                    <td><strong>Ultra</strong></td>
                    <td><strong>$75.00 / month</strong></td>
                    <td>150 / month (+ $0.005)</td>
                    <td>200,000 / month (+ $0.03)</td>
                    <td>Deep Email Search: Yes<br>JS Rendering: Yes</td>
                    <td>Rate: Platform controlled<br>Bandwidth: 10240MB/month + $0.001 per MB</td>
                  </tr>
                  <tr>
                    <td><strong>Mega</strong></td>
                    <td><strong>$125.00 / month</strong></td>
                    <td>500 / month (+ $0.001)</td>
                    <td>500,000 / month (+ $0.01)</td>
                    <td>Deep Email Search: Yes<br>JS Rendering: Yes</td>
                    <td>Rate: Platform controlled<br>Bandwidth: 10240MB/month + $0.001 per MB</td>
                  </tr>
                </tbody>
              </table>
              <p>All billing, usage metering, and subscription actions are handled on RapidAPI.</p>
            </div>
          </section>
        """,
    },
    "/faq-page": {
        "title": "PageIQ FAQ | Website Intelligence API Questions",
        "description": "Answers to common questions about PageIQ endpoint behavior, pricing, access, and implementation.",
        "keywords": "pageiq faq, website intelligence api faq, rapidapi integration faq",
        "hero_title": "Frequently Asked Questions",
        "hero_text": "Implementation-first answers for teams deploying PageIQ in real sales, marketing, and operations workflows.",
        "main_html": """
          <section class="section"><h2>FAQ</h2><div class="body">
          <p><strong>How is PageIQ accessed?</strong><br>PageIQ is accessible via RapidAPI only. API key management, plan upgrades, and billing are handled there.</p>
          <p><strong>Can we use JS rendering?</strong><br>Yes, on supported plans. Basic does not include JS rendering; Pro/Ultra/Mega include it.</p>
          <p><strong>What is the best endpoint for broad website intelligence?</strong><br>Use <code>POST /api/v1/analyze</code> for full-signal output and targeted extract endpoints for specialized workflows.</p>
          <p><strong>How should we handle errors?</strong><br>Implement route-aware parsing, retry transient 5xx responses, and classify 403 feature-gate responses separately for better UX.</p>
          </div></section>
        """,
    },
}


@router.get("/", response_class=HTMLResponse)
async def get_landing():
    return HTMLResponse(content=HOME_HTML)


@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    return HTMLResponse(content=DOCS_HTML)


@router.get("/seo-audit-api", response_class=HTMLResponse)
@router.get("/website-scraper-api", response_class=HTMLResponse)
@router.get("/email-extractor-api", response_class=HTMLResponse)
@router.get("/tech-stack-detector-api", response_class=HTMLResponse)
@router.get("/website-metadata-api", response_class=HTMLResponse)
@router.get("/competitor-website-analysis-api", response_class=HTMLResponse)
@router.get("/about-pageiq", response_class=HTMLResponse)
@router.get("/pricing-plans", response_class=HTMLResponse)
@router.get("/faq-page", response_class=HTMLResponse)
async def content_pages(request: Request):
    request_path = request.url.path
    if request_path.startswith("/api/v1/docs"):
        request_path = request_path[len("/api/v1/docs"):] or "/"
    page = PAGES.get(request_path)
    if not page:
        return HTMLResponse("Not found", status_code=404)
    return HTMLResponse(
        content=build_page(
            title=page["title"],
            description=page["description"],
            keywords=page["keywords"],
            canonical_path=request_path,
            hero_title=page["hero_title"],
            hero_text=page["hero_text"],
            main_html=page["main_html"],
        )
    )
