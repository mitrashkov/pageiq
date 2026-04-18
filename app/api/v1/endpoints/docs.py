"""
Web-based documentation and comprehensive interactive test suite for PageIQ API.
Accessible at /docs for documentation and /tests for manual testing all endpoints.
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

TEST_PAGE_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIQ API - Interactive Test Suite</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #333;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 32px;
        }
        
        .subtitle {
            color: #666;
            font-size: 16px;
        }
        
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .sidebar {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-height: 600px;
            overflow-y: auto;
        }
        
        .endpoint-list {
            list-style: none;
        }
        
        .endpoint-item {
            padding: 12px 15px;
            margin-bottom: 8px;
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            cursor: pointer;
            border-radius: 4px;
            transition: all 0.2s ease;
            font-weight: 500;
            font-size: 14px;
        }
        
        .endpoint-item:hover {
            background: #e8e8ff;
            border-left-color: #764ba2;
            transform: translateX(5px);
        }
        
        .endpoint-item.active {
            background: #667eea;
            color: white;
            border-left-color: #764ba2;
        }
        
        .method-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: bold;
            margin-right: 8px;
        }
        
        .method-get { background: #4CAF50; color: white; }
        .method-post { background: #2196F3; color: white; }
        .method-delete { background: #f44336; color: white; }
        
        .tester-panel {
            background: white;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 6px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            transition: border-color 0.2s ease;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        textarea {
            resize: vertical;
            min-height: 100px;
            font-family: 'Courier New', monospace;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }
        
        button {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        button:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        
        .btn-secondary {
            background: #666;
        }
        
        .btn-secondary:hover {
            background: #555;
        }
        
        .results-panel {
            margin-top: 30px;
            background: #f5f5f5;
            border-radius: 10px;
            padding: 20px;
            border: 2px solid #e0e0e0;
        }
        
        .result-section {
            margin-bottom: 20px;
            display: none;
        }
        
        .result-section.active {
            display: block;
        }
        
        .status-badge {
            display: inline-block;
            padding: 6px 12px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 15px;
        }
        
        .status-success { background: #4CAF50; color: white; }
        .status-error { background: #f44336; color: white; }
        .status-loading { background: #FF9800; color: white; }
        
        .request-display {
            background: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 15px;
            border-left: 4px solid #2196F3;
        }
        
        .response-display {
            background: white;
            padding: 15px;
            border-radius: 6px;
            border-left: 4px solid #4CAF50;
        }
        
        .response-display.error {
            border-left-color: #f44336;
        }
        
        .code-box {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 6px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            border-top: 4px solid #667eea;
        }
        
        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .test-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .filter-btn {
            padding: 8px 16px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .filter-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        @media (max-width: 1024px) {
            .main-grid { grid-template-columns: 1fr; }
            .sidebar { max-height: none; }
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .form-row { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🚀 PageIQ API - Interactive Test Suite</h1>
            <p class="subtitle">Test every endpoint in real-time. Make requests, see responses. Full control.</p>
        </header>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number" id="total-tests">0</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="passed-tests">0</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="failed-tests">0</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avg-time">0ms</div>
                <div class="stat-label">Avg Response</div>
            </div>
        </div>
        
        <div class="main-grid">
            <div class="sidebar">
                <h3 style="margin-bottom: 15px; color: #333;">Endpoints</h3>
                <ul class="endpoint-list" id="endpoint-list"></ul>
            </div>
            
            <div class="tester-panel">
                <div class="test-controls">
                    <button class="filter-btn active" onclick="filterEndpoints('all')">All</button>
                    <button class="filter-btn" onclick="filterEndpoints('health')">Health</button>
                    <button class="filter-btn" onclick="filterEndpoints('analyze')">Analysis</button>
                    <button class="filter-btn" onclick="filterEndpoints('extract')">Extraction</button>
                    <button class="filter-btn" onclick="filterEndpoints('batch')">Batch</button>
                </div>
                
                <div id="endpoint-form"></div>
                
                <div class="button-group">
                    <button onclick="sendTestRequest()">🚀 Send Request</button>
                    <button class="btn-secondary" onclick="clearForm()">Clear</button>
                    <button class="btn-secondary" onclick="clearResults()">Clear Results</button>
                </div>
                
                <div class="results-panel">
                    <div class="result-section active" id="results-placeholder">
                        <p style="color: #999; text-align: center;">Results will appear here...</p>
                    </div>
                    <div class="result-section" id="results-content"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const ENDPOINTS = [
            {
                name: 'Health Check',
                path: '/api/v1/ping',
                method: 'GET',
                category: 'health',
                description: 'Simple health check',
                params: []
            },
            {
                name: 'API Status',
                path: '/api/v1/',
                method: 'GET',
                category: 'health',
                description: 'Get API status information',
                params: []
            },
            {
                name: 'Analyze Website',
                path: '/api/v1/analyze',
                method: 'POST',
                category: 'analyze',
                description: 'Analyze a website and extract comprehensive data',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' },
                    { name: 'wait_for_js', type: 'checkbox', required: false, default: false }
                ]
            },
            {
                name: 'Batch Analyze',
                path: '/api/v1/batch-analyze',
                method: 'POST',
                category: 'batch',
                description: 'Analyze multiple websites in one request',
                params: [
                    { name: 'urls', type: 'textarea', required: true, placeholder: 'https://example.com\\nhttps://example.org' }
                ]
            },
            {
                name: 'Extract Emails',
                path: '/api/v1/extract/emails',
                method: 'POST',
                category: 'extract',
                description: 'Extract email addresses from a website',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' }
                ]
            },
            {
                name: 'Extract Schema',
                path: '/api/v1/extract/schema',
                method: 'POST',
                category: 'extract',
                description: 'Extract structured data (Schema.org)',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' }
                ]
            },
            {
                name: 'Extract Metadata',
                path: '/api/v1/extract/metadata',
                method: 'POST',
                category: 'extract',
                description: 'Extract metadata from website',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' }
                ]
            },
            {
                name: 'SEO Audit',
                path: '/api/v1/seo/seo-audit',
                method: 'POST',
                category: 'analyze',
                description: 'Perform SEO audit on a website',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' }
                ]
            },
            {
                name: 'Broken Links',
                path: '/api/v1/seo/broken-links',
                method: 'POST',
                category: 'analyze',
                description: 'Find broken links on a website',
                params: [
                    { name: 'url', type: 'text', required: true, placeholder: 'https://example.com' }
                ]
            }
        ];
        
        let currentEndpoint = null;
        let testStats = { total: 0, passed: 0, failed: 0, times: [] };
        
        function initEndpointList() {
            const list = document.getElementById('endpoint-list');
            list.innerHTML = ENDPOINTS.map((ep, idx) => `
                <li class="endpoint-item ${idx === 0 ? 'active' : ''}" onclick="selectEndpoint(${idx})">
                    <span class="method-badge method-${ep.method.toLowerCase()}">${ep.method}</span>
                    ${ep.name}
                </li>
            `).join('');
            selectEndpoint(0);
        }
        
        function selectEndpoint(idx) {
            currentEndpoint = ENDPOINTS[idx];
            document.querySelectorAll('.endpoint-item').forEach((el, i) => {
                el.classList.toggle('active', i === idx);
            });
            renderForm();
            clearResults();
        }
        
        function renderForm() {
            if (!currentEndpoint) return;
            
            let html = `<h3>${currentEndpoint.name}</h3>
                        <p style="color: #666; margin-bottom: 15px; font-size: 14px;">${currentEndpoint.description}</p>
                        <div class="code-box">${currentEndpoint.method} ${currentEndpoint.path}</div>`;
            
            if (currentEndpoint.params.length > 0) {
                html += '<div style="margin-top: 20px;">';
                currentEndpoint.params.forEach(param => {
                    if (param.type === 'checkbox') {
                        html += `<div class="form-group">
                            <label><input type="checkbox" id="param-${param.name}" ${param.default ? 'checked' : ''}> ${param.name}</label>
                        </div>`;
                    } else if (param.type === 'textarea') {
                        html += `<div class="form-group">
                            <label>${param.name}</label>
                            <textarea id="param-${param.name}" placeholder="${param.placeholder}"></textarea>
                        </div>`;
                    } else {
                        html += `<div class="form-group">
                            <label>${param.name} ${param.required ? '<span style="color:red;">*</span>' : ''}</label>
                            <input type="text" id="param-${param.name}" placeholder="${param.placeholder}">
                        </div>`;
                    }
                });
                html += '</div>';
            }
            
            document.getElementById('endpoint-form').innerHTML = html;
        }
        
        async function sendTestRequest() {
            if (!currentEndpoint) return;
            
            const startTime = performance.now();
            let body = null;
            
            if (currentEndpoint.method === 'POST') {
                body = {};
                currentEndpoint.params.forEach(param => {
                    const input = document.getElementById(`param-${param.name}`);
                    if (input) {
                        if (param.type === 'checkbox') {
                            body[param.name] = input.checked;
                        } else if (param.type === 'textarea') {
                            const lines = input.value.trim().split('\\n');
                            body[param.name] = param.name.includes('url') ? lines : input.value;
                        } else {
                            body[param.name] = input.value;
                        }
                    }
                });
            }
            
            try {
                const options = {
                    method: currentEndpoint.method,
                    headers: { 'Content-Type': 'application/json' }
                };
                
                if (body) options.body = JSON.stringify(body);
                
                const response = await fetch(currentEndpoint.path, options);
                const data = await response.json();
                const elapsed = performance.now() - startTime;
                
                testStats.total++;
                testStats.times.push(elapsed);
                
                if (response.ok) {
                    testStats.passed++;
                } else {
                    testStats.failed++;
                }
                
                updateStats();
                displayResults(response, data, body, elapsed);
            } catch (error) {
                testStats.total++;
                testStats.failed++;
                updateStats();
                displayError(error);
            }
        }
        

        function displayResults(response, data, body, elapsed) {
            const resultsContent = document.getElementById('results-content');
            const placeholder = document.getElementById('results-placeholder');
            placeholder.classList.remove('active');
            resultsContent.classList.add('active');
            const statusClass = response.ok ? 'success' : 'error';
            let diagnosticsHtml = '';
            if (data && data.diagnostics) {
                diagnosticsHtml = `<div class="diagnostics-box"><h4>Diagnostics</h4><div class="code-box">${escapeHtml(JSON.stringify(data.diagnostics, null, 2))}</div></div>`;
            } else if (data && data.data && data.data.diagnostics) {
                diagnosticsHtml = `<div class="diagnostics-box"><h4>Diagnostics</h4><div class="code-box">${escapeHtml(JSON.stringify(data.data.diagnostics, null, 2))}</div></div>`;
            }
            resultsContent.innerHTML = `
                <div class="status-badge status-${statusClass}">
                    Status: ${response.status} ${response.statusText} • Response time: ${elapsed.toFixed(0)}ms
                </div>
                <div class="request-display">
                    <h4 style="margin-bottom: 10px;">Request</h4>
                    <div class="code-box">${escapeHtml(JSON.stringify({ method: currentEndpoint.method, path: currentEndpoint.path, body }, null, 2))}</div>
                </div>
                <div class="response-display ${statusClass === 'error' ? 'error' : ''}">
                    <h4 style="margin-bottom: 10px;">Response</h4>
                    <div class="code-box">${escapeHtml(JSON.stringify(data, null, 2))}</div>
                </div>
                ${diagnosticsHtml}
            `;
        }
        
        function displayError(error) {
            const resultsContent = document.getElementById('results-content');
            const placeholder = document.getElementById('results-placeholder');
            
            placeholder.classList.remove('active');
            resultsContent.classList.add('active');
            
            resultsContent.innerHTML = `
                <div class="status-badge status-error">Error</div>
                <div class="response-display error">
                    <h4 style="margin-bottom: 10px;">Error</h4>
                    <div class="code-box">${escapeHtml(error.message)}</div>
                </div>
            `;
        }
        
        function updateStats() {
            document.getElementById('total-tests').textContent = testStats.total;
            document.getElementById('passed-tests').textContent = testStats.passed;
            document.getElementById('failed-tests').textContent = testStats.failed;
            
            if (testStats.times.length > 0) {
                const avg = testStats.times.reduce((a, b) => a + b) / testStats.times.length;
                document.getElementById('avg-time').textContent = avg.toFixed(0) + 'ms';
            }
        }
        
        function clearForm() {
            currentEndpoint?.params.forEach(param => {
                const input = document.getElementById(`param-${param.name}`);
                if (input) {
                    if (param.type === 'checkbox') {
                        input.checked = param.default || false;
                    } else {
                        input.value = '';
                    }
                }
            });
        }
        
        function clearResults() {
            document.getElementById('results-content').classList.remove('active');
            document.getElementById('results-placeholder').classList.add('active');
        }
        
        function filterEndpoints(category) {
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Initialize on load
        window.addEventListener('load', initEndpointList);
    </script>
</body>
</html>
"""


# --- /docs: Serve real documentation (placeholder for now) ---
DOCS_PAGE_HTML = """
<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>PageIQ API Documentation</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: #f8f9fa; color: #222; margin: 0; }
        .container { max-width: 900px; margin: 40px auto; background: #fff; border-radius: 10px; box-shadow: 0 2px 16px rgba(0,0,0,0.07); padding: 40px; }
        h1 { color: #667eea; }
        h2 { color: #333; margin-top: 2em; }
        code, pre { background: #f4f4f4; border-radius: 4px; padding: 2px 6px; font-size: 15px; }
        .endpoint { margin-bottom: 2em; }
        .endpoint-method { font-weight: bold; color: #fff; background: #667eea; border-radius: 4px; padding: 2px 10px; margin-right: 8px; }
        .endpoint-path { font-family: 'Courier New', monospace; color: #222; }
        .param-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        .param-table th, .param-table td { border: 1px solid #eee; padding: 8px; text-align: left; }
        .param-table th { background: #f8f8f8; }
        .example-box { background: #f4f4f4; border-radius: 4px; padding: 12px; margin-top: 10px; font-family: 'Courier New', monospace; font-size: 14px; }
        .section { margin-bottom: 2.5em; }
    </style>
</head>
<body>
    <div class=\"container\">
        <h1>PageIQ API Documentation</h1>
        <p>Welcome to the official documentation for the PageIQ API. Here you'll find details on all endpoints, parameters, example requests and responses, and technical/product overview. For interactive testing, visit <a href=\"/tests\">/tests</a>.</p>
        <div class=\"section\">
            <h2>Overview</h2>
            <p>PageIQ is a robust, production-grade API for website analysis, extraction, and intelligence. It supports advanced crawling, batch processing, anti-bot, and more. See the <b>plan/README.md</b> for the full product and technical vision.</p>
        </div>
        <div class=\"section\">
            <h2>Endpoints</h2>
            <div class=\"endpoint\">
                <span class=\"endpoint-method\">GET</span>
                <span class=\"endpoint-path\">/api/v1/ping</span>
                <div>Health check endpoint.</div>
            </div>
            <div class=\"endpoint\">
                <span class=\"endpoint-method\">GET</span>
                <span class=\"endpoint-path\">/api/v1/</span>
                <div>API status information.</div>
            </div>
            <div class=\"endpoint\">
                <span class=\"endpoint-method\">POST</span>
                <span class=\"endpoint-path\">/api/v1/analyze</span>
                <div>Analyze a website and extract comprehensive data.</div>
                <table class=\"param-table\">
                    <tr><th>Parameter</th><th>Type</th><th>Required</th><th>Description</th></tr>
                    <tr><td>url</td><td>string</td><td>Yes</td><td>Website URL to analyze</td></tr>
                    <tr><td>wait_for_js</td><td>boolean</td><td>No</td><td>Wait for JS rendering</td></tr>
                </table>
                <div class=\"example-box\"><b>Example Request:</b><br>POST /api/v1/analyze<br>{"url": "https://example.com", "wait_for_js": false}</div>
            </div>
            <!-- More endpoints to be added dynamically from plan/README.md and codebase -->
        </div>
        <div class=\"section\">
            <h2>Batch, Extraction, SEO, and More</h2>
            <p>See the full list of endpoints and features in the technical plan. This documentation will be expanded to cover all endpoints, parameters, and advanced features.</p>
        </div>
        <div class=\"section\">
            <h2>Product & Technical Vision</h2>
            <p>PageIQ is built for reliability, scalability, and intelligence. It leverages Playwright, BeautifulSoup, Wappalyzer, Redis, PostgreSQL, Celery, Docker, and more. For details, see <b>plan/README.md</b>.</p>
        </div>
    </div>
</body>
</html>
"""


import inspect
import importlib
from fastapi.routing import APIRoute
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from app.api.v1.endpoints import analyze, extract, seo, billing, health, analytics

def generate_endpoint_docs():
    # Collect all routers
    routers = [analyze.router, extract.router, seo.router, billing.router, health.router, analytics.router]
    endpoint_docs = []
    for router in routers:
        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue
            doc = {
                "path": route.path,
                "methods": list(route.methods),
                "name": route.name,
                "summary": route.summary or route.endpoint.__doc__ or "",
                "response_model": getattr(route, "response_model", None),
                "endpoint": route.endpoint,
                "parameters": [],
            }
            # Get parameter info
            sig = inspect.signature(route.endpoint)
            for name, param in sig.parameters.items():
                if name in ("user", "db", "background_tasks"):  # skip injected deps
                    continue
                param_info = {
                    "name": name,
                    "annotation": str(param.annotation),
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                }
                doc["parameters"].append(param_info)
            endpoint_docs.append(doc)
    return endpoint_docs

def render_docs_html():
    endpoint_docs = generate_endpoint_docs()
    html = ["<html><head><title>PageIQ API Documentation</title><style>body{font-family:sans-serif;background:#f8f9fa;color:#222;margin:0;} .container{max-width:900px;margin:40px auto;background:#fff;border-radius:10px;box-shadow:0 2px 16px rgba(0,0,0,0.07);padding:40px;} h1{color:#667eea;} h2{color:#333;margin-top:2em;} code,pre{background:#f4f4f4;border-radius:4px;padding:2px 6px;font-size:15px;} .endpoint{margin-bottom:2em;} .endpoint-method{font-weight:bold;color:#fff;background:#667eea;border-radius:4px;padding:2px 10px;margin-right:8px;} .endpoint-path{font-family:'Courier New',monospace;color:#222;} .param-table{width:100%;border-collapse:collapse;margin-top:10px;} .param-table th,.param-table td{border:1px solid #eee;padding:8px;text-align:left;} .param-table th{background:#f8f8f8;} .example-box{background:#f4f4f4;border-radius:4px;padding:12px;margin-top:10px;font-family:'Courier New',monospace;font-size:14px;} .section{margin-bottom:2.5em;}</style></head><body><div class='container'>"]
    html.append("<h1>PageIQ API Documentation</h1>")
    html.append("<p>Auto-generated documentation for all endpoints. For interactive testing, visit <a href='/tests'>/tests</a>.</p>")
    html.append("<div class='section'><h2>Endpoints</h2>")
    for doc in endpoint_docs:
        html.append(f"<div class='endpoint'><span class='endpoint-method'>{','.join(doc['methods'])}</span> <span class='endpoint-path'>{doc['path']}</span><div>{doc['summary'] or ''}</div>")
        if doc['parameters']:
            html.append("<table class='param-table'><tr><th>Name</th><th>Type</th><th>Default</th></tr>")
            for p in doc['parameters']:
                html.append(f"<tr><td>{p['name']}</td><td>{p['annotation']}</td><td>{p['default']}</td></tr>")
            html.append("</table>")
        html.append("</div>")
    html.append("</div>")
    html.append("<div class='section'><h2>Product & Technical Vision</h2><p>PageIQ is built for reliability, scalability, and intelligence. It leverages Playwright, BeautifulSoup, Wappalyzer, Redis, PostgreSQL, Celery, Docker, and more. For details, see <b>plan/README.md</b>.</p></div>")
    html.append("</div></body></html>")
    return "".join(html)

@router.get("/", response_class=HTMLResponse)
@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Serve the modern, comprehensive documentation page"""
    return HTMLResponse(content=MODERN_DOCS_HTML)

@router.get("/tests", response_class=HTMLResponse)
async def get_tests():
    """Serve the interactive testing page"""
    return TEST_PAGE_HTML


MODERN_DOCS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIQ API Documentation | Developer Portal</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg: #f8fafc;
            --sidebar-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --code-bg: #1e293b;
            --border: #e2e8f0;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, system-ui, sans-serif; background: var(--bg); color: var(--text-main); line-height: 1.6; }

        .layout { display: flex; min-height: 100vh; }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--border);
            padding: 2rem;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }

        .logo { font-size: 1.5rem; font-weight: 800; color: var(--primary); margin-bottom: 2rem; display: flex; align-items: center; gap: 0.5rem; }
        .nav-group { margin-bottom: 2rem; }
        .nav-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: var(--text-muted); letter-spacing: 0.05em; margin-bottom: 0.75rem; }
        .nav-link { display: block; padding: 0.5rem 0; color: var(--text-main); text-decoration: none; font-size: 0.9rem; transition: color 0.2s; }
        .nav-link:hover { color: var(--primary); }

        /* Content */
        .content { flex: 1; padding: 3rem 4rem; max-width: 1000px; }
        section { margin-bottom: 4rem; scroll-margin-top: 2rem; }
        h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 1.5rem; letter-spacing: -0.02em; }
        h2 { font-size: 1.75rem; font-weight: 700; margin-bottom: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; }
        h3 { font-size: 1.25rem; font-weight: 600; margin-top: 2rem; margin-bottom: 0.75rem; }
        p { margin-bottom: 1.25rem; color: #475569; }

        /* Badges */
        .method { font-size: 0.75rem; font-weight: 700; padding: 0.25rem 0.5rem; border-radius: 0.375rem; margin-right: 0.5rem; color: white; }
        .post { background: #2563eb; }
        .get { background: #059669; }

        /* Code Blocks */
        pre[class*="language-"] { border-radius: 0.75rem; margin: 1.5rem 0; font-size: 0.9rem; }
        
        .endpoint-card {
            background: white;
            border: 1px solid var(--border);
            border-radius: 1rem;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
        }

        .endpoint-header { display: flex; align-items: center; margin-bottom: 1rem; font-family: monospace; font-size: 1.1rem; }
        
        table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.9rem; }
        th { text-align: left; padding: 0.75rem; border-bottom: 2px solid var(--border); color: var(--text-muted); }
        td { padding: 0.75rem; border-bottom: 1px solid var(--border); }

        .tag { font-size: 0.7rem; background: #f1f5f9; padding: 0.2rem 0.5rem; border-radius: 1rem; color: var(--text-muted); }

        @media (max-width: 768px) {
            .layout { flex-direction: column; }
            .sidebar { width: 100%; height: auto; position: static; }
            .content { padding: 2rem; }
        }
    </style>
</head>
<body>
    <div class="layout">
        <aside class="sidebar">
            <div class="logo"><span>🚀</span> PageIQ</div>
            
            <nav class="nav-group">
                <div class="nav-title">Getting Started</div>
                <a href="#introduction" class="nav-link">Introduction</a>
                <a href="#authentication" class="nav-link">Authentication</a>
                <a href="#errors" class="nav-link">Error Handling</a>
            </nav>

            <nav class="nav-group">
                <div class="nav-title">Endpoints</div>
                <a href="#analyze" class="nav-link">Website Analysis</a>
                <a href="#extract" class="nav-link">Data Extraction</a>
                <a href="#seo" class="nav-link">SEO Audit</a>
                <a href="#health" class="nav-link">System Health</a>
            </nav>

            <nav class="nav-group">
                <div class="nav-title">Tools</div>
                <a href="/tests" class="nav-link">Interactive Tester ↗</a>
            </nav>
        </aside>

        <main class="content">
            <section id="introduction">
                <h1>API Documentation</h1>
                <p>PageIQ is a powerful website intelligence engine that transforms any URL into structured, actionable business data. Built for developers, our API provides comprehensive tools for metadata extraction, contact discovery, SEO auditing, and technology stack detection.</p>
                <div class="endpoint-card" style="background: #eef2ff; border-color: #c7d2fe;">
                    <h3 style="margin-top:0">Key Features</h3>
                    <ul style="margin-left: 1.5rem; color: #4338ca;">
                        <li>Headless Browser Rendering (Playwright)</li>
                        <li>Advanced Anti-Bot Evasion</li>
                        <li>Deep Email & Contact Crawling</li>
                        <li>Detailed SEO Performance Auditing</li>
                        <li>Technology & CMS Detection</li>
                    </ul>
                </div>
            </section>

            <section id="authentication">
                <h2>Authentication</h2>
                <p>Authenticate your requests by including your API Key in the <code>X-API-Key</code> header.</p>
                <pre><code class="language-http">GET /api/v1/analyze HTTP/1.1
Host: pageiq.pompora.dev
X-API-Key: your_api_key_here</code></pre>
            </section>

            <section id="analyze">
                <h2>Website Analysis</h2>
                <p>The core analysis engine that extracts metadata, social profiles, and technical details.</p>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method post">POST</span> /api/v1/analyze
                    </div>
                    <p>Perform a comprehensive analysis of a single URL.</p>
                    
                    <h3>Parameters</h3>
                    <table>
                        <thead>
                            <tr><th>Field</th><th>Type</th><th>Description</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>url</td><td>string</td><td>The target website URL (required).</td></tr>
                            <tr><td>use_browser</td><td>boolean</td><td>Enable JS rendering for SPA/React apps. <span class="tag">PRO+</span></td></tr>
                            <tr><td>screenshot</td><td>boolean</td><td>Capture a full-page screenshot.</td></tr>
                        </tbody>
                    </table>

                    <h3>Example Request</h3>
                    <pre><code class="language-json">{
  "url": "https://mikso.net",
  "use_browser": true,
  "screenshot": true
}</code></pre>
                </div>
            </section>

            <section id="extract">
                <h2>Data Extraction</h2>
                <p>Specialized endpoints for deep data discovery.</p>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method post">POST</span> /api/v1/extract/emails
                    </div>
                    <p>Discover email addresses. Supports deep crawling of internal pages.</p>
                    
                    <h3>Options</h3>
                    <table>
                        <thead>
                            <tr><th>Field</th><th>Type</th><th>Description</th></tr>
                        </thead>
                        <tbody>
                            <tr><td>deep_search</td><td>boolean</td><td>Crawl internal pages for more emails. <span class="tag">PRO+</span></td></tr>
                            <tr><td>pages_limit</td><td>integer</td><td>Max pages to crawl (up to 500). <span class="tag">MEGA</span></td></tr>
                        </tbody>
                    </table>
                </div>
            </section>

            <section id="seo">
                <h2>SEO Audit</h2>
                <p>Get professional SEO insights and scores for any webpage.</p>
                
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method post">POST</span> /api/v1/seo/seo-audit
                    </div>
                    <p>Returns a weighted SEO score (1-100) and detailed improvement advice.</p>
                </div>
            </section>

            <section id="health">
                <h2>System Health</h2>
                <div class="endpoint-card">
                    <div class="endpoint-header">
                        <span class="method get">GET</span> /api/v1/ping
                    </div>
                    <p>Returns <code>{"status": "ok"}</code> if the service is operational.</p>
                </div>
            </section>

            <footer style="margin-top: 8rem; padding-top: 2rem; border-top: 1px solid var(--border); color: var(--text-muted); font-size: 0.8rem;">
                &copy; 2026 PageIQ Intelligence Engine. All rights reserved.
            </footer>
        </main>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-http.min.js"></script>
</body>
</html>
"""
