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

@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Serve the documentation page"""
    return TEST_PAGE_HTML

@router.get("/tests", response_class=HTMLResponse)
async def get_tests():
    """Serve the interactive testing page"""
    return TEST_PAGE_HTML
