"""
Documentation and Testing Pages
Serves interactive documentation and test suite
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

DOCS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIQ API - Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
        }

        .navbar {
            background: rgba(255,255,255,0.95);
            padding: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .navbar .container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .logo {
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }

        .nav-links {
            display: flex;
            gap: 30px;
        }

        .nav-links a {
            color: #333;
            text-decoration: none;
            font-weight: 500;
            cursor: pointer;
            padding: 5px 10px;
            border-radius: 5px;
            transition: background 0.3s;
        }

        .nav-links a:hover {
            background: #f0f0f0;
        }

        .nav-links a.active {
            color: #667eea;
            border-bottom: 2px solid #667eea;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }

        .section {
            display: none;
            animation: fadeIn 0.3s ease-in;
        }

        .section.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .hero {
            background: white;
            padding: 60px 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            text-align: center;
        }

        .hero h1 {
            color: #667eea;
            font-size: 42px;
            margin-bottom: 15px;
        }

        .hero p {
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
        }

        .cta-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }

        .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
        }

        .btn-secondary {
            background: #f0f0f0;
            color: #333;
        }

        .btn-secondary:hover {
            background: #e0e0e0;
        }

        .endpoint-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .endpoint-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .method {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 5px;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }

        .method.get {
            background: #61affe;
            color: white;
        }

        .method.post {
            background: #49cc90;
            color: white;
        }

        .method.put {
            background: #fca130;
            color: white;
        }

        .method.delete {
            background: #f93e3e;
            color: white;
        }

        .endpoint-path {
            font-family: 'Monaco', monospace;
            font-size: 14px;
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 10px;
        }

        .endpoint-desc {
            color: #666;
            margin-bottom: 15px;
        }

        .code-block {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
            font-family: 'Monaco', monospace;
            font-size: 13px;
        }

        .code-block.json {
            border-left: 3px solid #667eea;
        }

        .try-button {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            margin-top: 10px;
        }

        .try-button:hover {
            background: #5568d3;
        }

        .test-panel {
            background: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
            border: 1px solid #eee;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            font-size: 14px;
        }

        .form-group input,
        .form-group textarea,
        .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: 'Monaco', monospace;
            font-size: 13px;
        }

        .response-box {
            background: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            margin-top: 10px;
            max-height: 300px;
            overflow-y: auto;
        }

        .response-success {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
        }

        .response-error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }

        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .stat-card h3 {
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            margin-bottom: 10px;
        }

        .stat-card .value {
            color: #667eea;
            font-size: 32px;
            font-weight: bold;
        }

        .status-badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 15px;
        }

        .status-online {
            background: #d4edda;
            color: #155724;
        }

        .test-list {
            list-style: none;
        }

        .test-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            align-items: center;
            gap: 15px;
            cursor: pointer;
            border-left: 4px solid #ddd;
            transition: all 0.3s;
        }

        .test-item:hover {
            border-left-color: #667eea;
            background: #f9f9f9;
        }

        .test-item.passed {
            border-left-color: #28a745;
        }

        .test-item.failed {
            border-left-color: #dc3545;
        }

        .test-icon {
            font-size: 20px;
        }

        .test-name {
            flex: 1;
        }

        .test-result {
            font-size: 12px;
            font-weight: 600;
            padding: 5px 10px;
            border-radius: 5px;
        }

        .test-result.pass {
            background: #d4edda;
            color: #155724;
        }

        .test-result.fail {
            background: #f8d7da;
            color: #721c24;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 200;
            align-items: center;
            justify-content: center;
        }

        .modal.active {
            display: flex;
        }

        .modal-content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }

        .modal-close {
            float: right;
            font-size: 24px;
            cursor: pointer;
            color: #999;
        }

        .modal-close:hover {
            color: #333;
        }

        @media (max-width: 768px) {
            .nav-links {
                gap: 15px;
            }

            .hero h1 {
                font-size: 28px;
            }

            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="navbar">
        <div class="container">
            <div class="logo">🚀 PageIQ API</div>
            <div class="nav-links">
                <a class="nav-link active" onclick="showSection('overview')">Overview</a>
                <a class="nav-link" onclick="showSection('endpoints')">Endpoints</a>
                <a class="nav-link" onclick="showSection('auth')">Auth</a>
                <a class="nav-link" onclick="showSection('testing')">Testing</a>
            </div>
        </div>
    </div>

    <!-- Overview Section -->
    <div id="overview" class="section active">
        <div class="container">
            <div class="hero">
                <h1>PageIQ API Documentation</h1>
                <p>Website Intelligence API - Turn any URL into structured business data</p>
                <span class="status-badge status-online">🟢 API Online</span>
                <div style="margin-top: 20px;">
                    <p>Base URL: <code style="background: #f0f0f0; padding: 5px 10px; border-radius: 3px;">https://pageiq.pompora.dev/api/v1</code></p>
                </div>
                <div class="cta-buttons">
                    <button class="btn btn-primary" onclick="showSection('endpoints')">View Endpoints</button>
                    <button class="btn btn-secondary" onclick="showSection('testing')">Try It Out</button>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Status</h3>
                    <div class="value">✓ Online</div>
                </div>
                <div class="stat-card">
                    <h3>Version</h3>
                    <div class="value">1.0.0</div>
                </div>
                <div class="stat-card">
                    <h3>Response Time</h3>
                    <div class="value">&lt;100ms</div>
                </div>
                <div class="stat-card">
                    <h3>Uptime</h3>
                    <div class="value">99.9%</div>
                </div>
            </div>

            <div class="endpoint-card">
                <h2 style="margin-bottom: 20px;">Quick Start</h2>
                <p style="margin-bottom: 15px;"><strong>1. Test the API with a simple health check:</strong></p>
                <div class="code-block">
curl https://pageiq.pompora.dev/api/v1/ping
                </div>
                <p style="margin-bottom: 15px;"><strong>2. Analyze a website:</strong></p>
                <div class="code-block">
curl -X POST https://pageiq.pompora.dev/api/v1/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
  "url": "https://example.com",
  "options": {
    "extract_emails": true,
    "detect_technology": true
  }
}'
                </div>
                <p style="margin-bottom: 15px;"><strong>3. Try the interactive tester below!</strong></p>
                <button class="btn btn-primary" onclick="showSection('testing')">Go to Testing →</button>
            </div>
        </div>
    </div>

    <!-- Endpoints Section -->
    <div id="endpoints" class="section">
        <div class="container">
            <h1 style="margin-bottom: 30px; color: white;">API Endpoints</h1>

            <!-- Health Endpoints -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method get">GET</span>
                        <span style="margin-left: 10px; font-weight: 600;">/ping</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/ping</div>
                <div class="endpoint-desc">Simple health check to verify API is running</div>
                <strong>Response:</strong>
                <div class="code-block json">
{
  "status": "ok",
  "message": "pong"
}
                </div>
            </div>

            <!-- Analysis Endpoint -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method post">POST</span>
                        <span style="margin-left: 10px; font-weight: 600;">/analyze</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/analyze</div>
                <div class="endpoint-desc">Analyze a website and return structured business data</div>
                <strong>Request:</strong>
                <div class="code-block json">
{
  "url": "https://example.com",
  "options": {
    "screenshot": false,
    "extract_emails": true,
    "detect_technology": true,
    "detect_industry": true,
    "analyze_seo": false
  }
}
                </div>
                <strong>Response:</strong>
                <div class="code-block json">
{
  "success": true,
  "data": {
    "url": "https://example.com",
    "title": "Example Domain",
    "description": "Example Domain. This domain is for use...",
    "technologies": [...],
    "industry": "Technology",
    "emails": [...],
    "seo": {...}
  },
  "request_id": "req_abc123",
  "processing_time_ms": 2450,
  "quota_remaining": 999
}
                </div>
                <button class="try-button" onclick="testEndpoint('analyze')">Try This Endpoint →</button>
            </div>

            <!-- Extraction Endpoint -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method post">POST</span>
                        <span style="margin-left: 10px; font-weight: 600;">/extract/emails</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/extract/emails</div>
                <div class="endpoint-desc">Extract email addresses from a webpage</div>
                <strong>Request:</strong>
                <div class="code-block json">
{
  "url": "https://example.com"
}
                </div>
                <strong>Response:</strong>
                <div class="code-block json">
{
  "url": "https://example.com",
  "emails": ["info@example.com", "support@example.com"],
  "count": 2,
  "processing_time_ms": 450
}
                </div>
                <button class="try-button" onclick="testEndpoint('extract')">Try This Endpoint →</button>
            </div>

            <!-- Batch Analysis -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method post">POST</span>
                        <span style="margin-left: 10px; font-weight: 600;">/batch-analyze</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/batch-analyze</div>
                <div class="endpoint-desc">Analyze multiple websites in one request</div>
                <strong>Request:</strong>
                <div class="code-block json">
{
  "urls": ["https://example.com", "https://example.org"]
}
                </div>
                <button class="try-button" onclick="testEndpoint('batch')">Try This Endpoint →</button>
            </div>

            <!-- Account Endpoints -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method get">GET</span>
                        <span style="margin-left: 10px; font-weight: 600;">/account/quota</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/account/quota</div>
                <div class="endpoint-desc">Check your API quota and usage</div>
                <button class="try-button" onclick="testEndpoint('quota')">Try This Endpoint →</button>
            </div>

            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method get">GET</span>
                        <span style="margin-left: 10px; font-weight: 600;">/account/keys</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/account/keys</div>
                <div class="endpoint-desc">List all API keys for your account</div>
                <button class="try-button" onclick="testEndpoint('keys')">Try This Endpoint →</button>
            </div>

            <!-- Analytics -->
            <div class="endpoint-card">
                <div class="endpoint-header">
                    <div>
                        <span class="method get">GET</span>
                        <span style="margin-left: 10px; font-weight: 600;">/analytics/summary</span>
                    </div>
                </div>
                <div class="endpoint-path">/api/v1/analytics/summary</div>
                <div class="endpoint-desc">Get analytics summary of your API usage</div>
                <button class="try-button" onclick="testEndpoint('analytics')">Try This Endpoint →</button>
            </div>
        </div>
    </div>

    <!-- Authentication Section -->
    <div id="auth" class="section">
        <div class="container">
            <h1 style="margin-bottom: 30px; color: white;">Authentication</h1>

            <div class="endpoint-card">
                <h2 style="margin-bottom: 20px;">API Key Authentication</h2>
                <p>Use the Authorization header with Bearer token:</p>
                <div class="code-block">
Authorization: Bearer YOUR_API_KEY
                </div>

                <h3 style="margin-top: 25px; margin-bottom: 15px;">cURL Example:</h3>
                <div class="code-block">
curl -H "Authorization: Bearer sk_live_123..." \\
  https://pageiq.pompora.dev/api/v1/account/quota
                </div>

                <h3 style="margin-top: 25px; margin-bottom: 15px;">JavaScript Example:</h3>
                <div class="code-block">
fetch('https://pageiq.pompora.dev/api/v1/analyze', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://example.com'
  })
})
.then(r => r.json())
.then(data => console.log(data))
                </div>

                <h3 style="margin-top: 25px; margin-bottom: 15px;">Python Example:</h3>
                <div class="code-block">
import requests

headers = {
    'Authorization': 'Bearer YOUR_API_KEY'
}
response = requests.post(
    'https://pageiq.pompora.dev/api/v1/analyze',
    json={'url': 'https://example.com'},
    headers=headers
)
print(response.json())
                </div>

                <h2 style="margin-top: 30px; margin-bottom: 20px;">Anonymous Access</h2>
                <p>Some endpoints work without authentication:</p>
                <ul style="margin-left: 20px; margin-top: 10px;">
                    <li>GET /ping - Health check</li>
                    <li>GET / - API status</li>
                </ul>
            </div>
        </div>
    </div>

    <!-- Testing Section -->
    <div id="testing" class="section">
        <div class="container">
            <h1 style="margin-bottom: 30px; color: white;">Interactive Testing</h1>

            <div class="endpoint-card">
                <h2 style="margin-bottom: 20px;">Test Endpoints</h2>

                <div style="margin-bottom: 25px;">
                    <h3 style="margin-bottom: 15px;">Configuration</h3>
                    <div class="form-group">
                        <label>API Key (Optional)</label>
                        <input type="password" id="apiKey" placeholder="sk_live_..." value="">
                    </div>
                </div>

                <h3 style="margin-bottom: 15px;">Quick Tests</h3>
                <ul class="test-list">
                    <li class="test-item" onclick="runTest('health')">
                        <span class="test-icon">⚡</span>
                        <span class="test-name">
                            <strong>Health Check</strong>
                            <div style="font-size: 12px; color: #999;">GET /ping</div>
                        </span>
                        <span id="health-result"></span>
                    </li>
                    <li class="test-item" onclick="runTest('analyze')">
                        <span class="test-icon">🔍</span>
                        <span class="test-name">
                            <strong>Analyze Website</strong>
                            <div style="font-size: 12px; color: #999;">POST /analyze</div>
                        </span>
                        <span id="analyze-result"></span>
                    </li>
                    <li class="test-item" onclick="runTest('extract')">
                        <span class="test-icon">📧</span>
                        <span class="test-name">
                            <strong>Extract Emails</strong>
                            <div style="font-size: 12px; color: #999;">POST /extract/emails</div>
                        </span>
                        <span id="extract-result"></span>
                    </li>
                    <li class="test-item" onclick="runTest('batch')">
                        <span class="test-icon">📦</span>
                        <span class="test-name">
                            <strong>Batch Analysis</strong>
                            <div style="font-size: 12px; color: #999;">POST /batch-analyze</div>
                        </span>
                        <span id="batch-result"></span>
                    </li>
                    <li class="test-item" onclick="runTest('quota')">
                        <span class="test-icon">📊</span>
                        <span class="test-name">
                            <strong>Get Quota</strong>
                            <div style="font-size: 12px; color: #999;">GET /account/quota</div>
                        </span>
                        <span id="quota-result"></span>
                    </li>
                </ul>

                <h3 style="margin-top: 30px; margin-bottom: 15px;">Manual Test</h3>
                <div class="test-panel">
                    <div class="form-group">
                        <label>Endpoint</label>
                        <select id="endpoint" style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                            <option value="POST /analyze">POST /analyze</option>
                            <option value="POST /extract/emails">POST /extract/emails</option>
                            <option value="POST /batch-analyze">POST /batch-analyze</option>
                            <option value="GET /account/quota">GET /account/quota</option>
                            <option value="GET /ping">GET /ping</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>URL to Analyze</label>
                        <input type="text" id="testUrl" value="https://example.com" placeholder="https://example.com">
                    </div>
                    <button class="try-button" onclick="runManualTest()" style="width: 100%; padding: 12px;">Send Request</button>
                    <div id="manual-result"></div>
                </div>
            </div>

            <h2 style="margin-top: 40px; margin-bottom: 20px; color: white;">Run Full Test Suite</h2>
            <div class="endpoint-card">
                <button class="btn btn-primary" onclick="runFullTestSuite()" style="width: 100%; padding: 15px; font-size: 16px;">
                    ▶ Start Full Test Suite
                </button>
                <div id="suite-results" style="margin-top: 20px;"></div>
            </div>
        </div>
    </div>

    <script>
        const BASE_URL = 'https://pageiq.pompora.dev/api/v1';

        function showSection(sectionId) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

            // Show selected section
            document.getElementById(sectionId).classList.add('active');
            event.target.classList.add('active');
        }

        async function runTest(testName) {
            const resultId = testName + '-result';
            const resultEl = document.getElementById(resultId);
            resultEl.innerHTML = '<span class="test-result pass" style="width: 60px; text-align: center;">Loading...</span>';

            try {
                let response;
                let time = 0;

                const start = Date.now();

                switch(testName) {
                    case 'health':
                        response = await fetch(`${BASE_URL}/ping`);
                        break;
                    case 'analyze':
                        response = await fetch(`${BASE_URL}/analyze`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url: 'https://example.com'})
                        });
                        break;
                    case 'extract':
                        response = await fetch(`${BASE_URL}/extract/emails`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({url: 'https://example.com'})
                        });
                        break;
                    case 'batch':
                        response = await fetch(`${BASE_URL}/batch-analyze`, {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({urls: ['https://example.com']})
                        });
                        break;
                    case 'quota':
                        response = await fetch(`${BASE_URL}/account/quota`);
                        break;
                }

                time = Date.now() - start;
                const status = response.ok ? 'pass' : 'fail';
                const statusText = response.ok ? '✓ PASS' : '✗ FAIL';
                resultEl.innerHTML = `<span class="test-result ${status}" style="width: auto; min-width: 80px; text-align: center;">${statusText} (${time}ms)</span>`;
            } catch(e) {
                resultEl.innerHTML = '<span class="test-result fail" style="width: auto;">✗ ERROR</span>';
            }
        }

        async function runManualTest() {
            const resultEl = document.getElementById('manual-result');
            const endpoint = document.getElementById('endpoint').value;
            const url = document.getElementById('testUrl').value;
            const apiKey = document.getElementById('apiKey').value;

            resultEl.innerHTML = '<div class="response-box" style="background: #d1ecf1; color: #0c5460; padding: 10px;">Loading...</div>';

            try {
                const [method, path] = endpoint.split(' ');
                const headers = {'Content-Type': 'application/json'};

                if (apiKey) {
                    headers['Authorization'] = `Bearer ${apiKey}`;
                }

                let options = {method, headers};
                if (method === 'POST') {
                    if (path.includes('batch')) {
                        options.body = JSON.stringify({urls: [url]});
                    } else if (path.includes('extract')) {
                        options.body = JSON.stringify({url});
                    } else {
                        options.body = JSON.stringify({url, options: {}});
                    }
                }

                const response = await fetch(`${BASE_URL}${path}`, options);
                const data = await response.json();

                const className = response.ok ? 'response-success' : 'response-error';
                resultEl.innerHTML = `<div class="response-box ${className}"><pre>${JSON.stringify(data, null, 2)}</pre></div>`;
            } catch(e) {
                resultEl.innerHTML = `<div class="response-box response-error"><pre>Error: ${e.message}</pre></div>`;
            }
        }

        async function runFullTestSuite() {
            const resultsEl = document.getElementById('suite-results');
            resultsEl.innerHTML = '<div style="padding: 20px; text-align: center; color: #667eea;"><div style="font-size: 20px; margin-bottom: 10px;">⏳ Running tests...</div><p>This will take a moment</p></div>';

            const tests = [
                {name: 'Health Check', endpoint: '/ping', method: 'GET'},
                {name: 'Analyze Example', endpoint: '/analyze', method: 'POST', body: {url: 'https://example.com'}},
                {name: 'Extract Emails', endpoint: '/extract/emails', method: 'POST', body: {url: 'https://example.com'}},
                {name: 'Batch Analysis', endpoint: '/batch-analyze', method: 'POST', body: {urls: ['https://example.com']}},
                {name: 'Get Quota', endpoint: '/account/quota', method: 'GET'}
            ];

            let results = '<ul class="test-list">';
            let passed = 0;
            let failed = 0;

            for (const test of tests) {
                try {
                    const options = {method: test.method, headers: {'Content-Type': 'application/json'}};
                    if (test.body) options.body = JSON.stringify(test.body);

                    const response = await fetch(`${BASE_URL}${test.endpoint}`, options);
                    const success = response.ok;

                    if (success) passed++;
                    else failed++;

                    const status = success ? 'passed' : 'failed';
                    const icon = success ? '✓' : '✗';
                    results += `<li class="test-item ${status}"><span class="test-icon">${icon}</span><span class="test-name">${test.name}</span><span class="test-result ${success ? 'pass' : 'fail'}">${success ? 'PASS' : 'FAIL'}</span></li>`;
                } catch(e) {
                    failed++;
                    results += `<li class="test-item failed"><span class="test-icon">✗</span><span class="test-name">${test.name}</span><span class="test-result fail">ERROR</span></li>`;
                }
            }

            results += '</ul>';
            resultsEl.innerHTML = `<div style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;"><h3>Results: ${passed}/${tests.length} Passed</h3><p>✓ Passed: ${passed} | ✗ Failed: ${failed}</p></div>${results}`;
        }

        // Run tests on page load
        window.addEventListener('load', function() {
            console.log('Docs loaded');
        });
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def docs_page():
    """Serve interactive API documentation"""
    return DOCS_HTML
