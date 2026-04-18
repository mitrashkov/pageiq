"""
Web-based documentation and comprehensive interactive test suite for PageIQ API.
Accessible at /docs for documentation and /tests for manual testing all endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Serve the modern, comprehensive documentation page"""
    return HTMLResponse(content=MODERN_DOCS_HTML)

MODERN_DOCS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIQ Documentation — Website Intelligence API</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-dark: #4f46e5;
            --primary-light: #eef2ff;
            --bg: #ffffff;
            --sidebar-bg: #f8fafc;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
            --code-bg: #0f172a;
            --success: #10b981;
            --error: #ef4444;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text-main); line-height: 1.6; display: flex; }

        /* Sidebar - ReadTheDocs Style */
        .sidebar {
            width: 300px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
            height: 100vh;
            position: sticky;
            top: 0;
            overflow-y: auto;
            padding: 2rem 1.5rem;
        }

        .logo { 
            font-size: 1.4rem; 
            font-weight: 800; 
            color: var(--text-main); 
            margin-bottom: 2.5rem; 
            display: flex; 
            align-items: center; 
            gap: 0.75rem;
            text-decoration: none;
        }
        .logo span { color: var(--primary); }
        
        .nav-group { margin-bottom: 2rem; }
        .nav-title { 
            font-size: 0.75rem; 
            font-weight: 700; 
            text-transform: uppercase; 
            color: var(--text-muted); 
            letter-spacing: 0.1em; 
            margin-bottom: 0.75rem;
            padding-left: 0.5rem;
        }
        .nav-link { 
            display: block; 
            padding: 0.5rem 0.75rem; 
            color: var(--text-main); 
            text-decoration: none; 
            font-size: 0.95rem; 
            border-radius: 0.375rem;
            transition: all 0.2s;
        }
        .nav-link:hover { background: #f1f5f9; color: var(--primary); }
        .nav-link.active { background: var(--primary-light); color: var(--primary); font-weight: 600; }

        /* Main Content */
        .main { flex: 1; padding: 4rem 5rem; max-width: 1000px; }
        
        section { margin-bottom: 5rem; scroll-margin-top: 4rem; }
        h1 { font-size: 2.75rem; font-weight: 800; margin-bottom: 1.5rem; letter-spacing: -0.02em; color: #0f172a; }
        h2 { font-size: 1.75rem; font-weight: 700; margin-bottom: 1.25rem; margin-top: 3rem; color: #0f172a; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
        h3 { font-size: 1.25rem; font-weight: 700; margin-top: 2rem; margin-bottom: 1rem; color: #334155; }
        p { margin-bottom: 1.25rem; color: #475569; font-size: 1.05rem; }

        /* Method Badges */
        .method { font-size: 0.7rem; font-weight: 800; padding: 0.25rem 0.5rem; border-radius: 0.25rem; color: white; margin-right: 0.5rem; text-transform: uppercase; vertical-align: middle; }
        .post { background: var(--primary); }
        .get { background: var(--success); }

        /* Code Blocks */
        pre[class*="language-"] { border-radius: 0.75rem !important; margin: 1.5rem 0 !important; background: var(--code-bg) !important; font-size: 0.9rem !important; }
        code { font-family: 'JetBrains Mono', monospace !important; }

        /* Info Boxes */
        .admonition { padding: 1.25rem; border-radius: 0.75rem; margin: 1.5rem 0; border-left: 4px solid; }
        .note { background: #f0f9ff; border-color: #0ea5e9; color: #0369a1; }
        .warning { background: #fffbeb; border-color: #f59e0b; color: #b45309; }

        table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; }
        th { text-align: left; padding: 0.75rem; border-bottom: 2px solid var(--border); font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); }
        td { padding: 0.75rem; border-bottom: 1px solid var(--border); font-size: 0.95rem; }
        
        .type { font-family: monospace; color: var(--primary); font-size: 0.85rem; }
        .required { color: var(--error); font-weight: 700; font-size: 0.75rem; }

        @media (max-width: 1024px) {
            .sidebar { display: none; }
            .main { padding: 2rem; }
        }
    </style>
</head>
<body>
    <aside class="sidebar">
        <a href="/" class="logo"><span>🚀</span> PageIQ Docs</a>
        
        <div class="nav-group">
            <div class="nav-title">Getting Started</div>
            <a href="#welcome" class="nav-link">Introduction</a>
            <a href="#authentication" class="nav-link">Authentication</a>
            <a href="#plans" class="nav-link">Pricing & Quotas</a>
        </div>

        <div class="nav-group">
            <div class="nav-title">Analysis Endpoints</div>
            <a href="#analyze" class="nav-link">Full Website Analysis</a>
            <a href="#tech-detection" class="nav-link">Tech Detection</a>
            <a href="#seo-audit" class="nav-link">SEO Audit</a>
        </div>

        <div class="nav-group">
            <div class="nav-title">Extraction Endpoints</div>
            <a href="#extract-emails" class="nav-link">Email Discovery</a>
            <a href="#extract-schema" class="nav-link">Schema.org (JSON-LD)</a>
        </div>

        <div class="nav-group">
            <div class="nav-title">Support</div>
            <a href="#errors" class="nav-link">Error Codes</a>
            <a href="https://rapidapi.com" class="nav-link">RapidAPI Portal ↗</a>
        </div>
    </aside>

    <main class="main">
        <section id="welcome">
            <h1>Introduction</h1>
            <p>Welcome to the PageIQ API. Our engine provides deep website intelligence, transforming any URL into structured data. Whether you need to find business emails, audit SEO performance, or detect a website's full technology stack, PageIQ is built for developers who need speed and accuracy.</p>
            
            <div class="admonition note">
                <strong>Note:</strong> All requests should be made to <code>https://pageiq.pompora.dev/api/v1</code>
            </div>
        </section>

        <section id="authentication">
            <h2>Authentication</h2>
            <p>Authenticate your account by including your API Key in the <code>X-API-Key</code> header for all requests.</p>
            <pre><code class="language-http">POST /api/v1/analyze HTTP/1.1
Host: pageiq.pompora.dev
X-API-Key: YOUR_API_KEY_HERE
Content-Type: application/json</code></pre>
        </section>

        <section id="analyze">
            <h2><span class="method post">POST</span> Website Analysis</h2>
            <p>The core analysis endpoint. It extracts metadata, social profiles, contacts, and technical signals in one request.</p>
            <h3>Parameters</h3>
            <table>
                <thead><tr><th>Field</th><th>Type</th><th>Description</th></tr></thead>
                <tbody>
                    <tr><td>url <span class="required">REQUIRED</span></td><td><span class="type">string</span></td><td>The target URL to analyze.</td></tr>
                    <tr><td>use_browser</td><td><span class="type">boolean</span></td><td>Enable JS rendering for React/SPA sites. (PRO+)</td></tr>
                    <tr><td>screenshot</td><td><span class="type">boolean</span></td><td>Capture a full-page screenshot.</td></tr>
                </tbody>
            </table>
        </section>

        <section id="tech-detection">
            <h2><span class="method post">POST</span> Tech Detection</h2>
            <p>Instantly identify the CMS, frameworks, analytics tools, and tracking pixels used by any website.</p>
            <pre><code class="language-json">// Request Body
{
  "url": "https://mikso.net"
}

// Example Output
{
  "success": true,
  "data": {
    "cms": ["WordPress"],
    "frameworks": ["React", "Next.js"],
    "analytics": ["Google Analytics", "Facebook Pixel"],
    "infrastructure": ["Cloudflare", "Nginx"]
  }
}</code></pre>
        </section>

        <section id="extract-emails">
            <h2><span class="method post">POST</span> Email Discovery</h2>
            <p>Find verified email addresses. Use <code>deep_search</code> to crawl internal pages and find hidden contacts.</p>
            <div class="admonition warning">
                <strong>Premium Feature:</strong> Deep Search is only available on PRO, ULTRA, and MEGA plans.
            </div>
        </section>

        <section id="extract-schema">
            <h2><span class="method post">POST</span> Schema.org Extraction</h2>
            <p>Extract and parse structured data (JSON-LD and Microdata) to understand a site's semantic meaning.</p>
            <pre><code class="language-json">{
  "url": "https://example.com/product",
  "use_browser": true
}</code></pre>
        </section>

        <footer style="margin-top: 10rem; border-top: 1px solid var(--border); padding-top: 2rem; color: var(--text-muted); font-size: 0.9rem;">
            &copy; 2026 PageIQ Website Intelligence Engine.
        </footer>
    </main>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-http.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-bash.min.js"></script>
</body>
</html>
"""
