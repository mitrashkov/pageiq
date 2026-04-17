"""
Web-based documentation and interactive test suite for PageIQ API.
Accessible at /docs for documentation and /tests for interactive testing.
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import os

router = APIRouter()

DOCS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PageIQ API Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        nav {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        
        nav button {
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            background: #f0f0f0;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        nav button:hover {
            background: #667eea;
            color: white;
        }
        
        nav button.active {
            background: #667eea;
            color: white;
        }
        
        .header {
            background: white;
            padding: 40px;
            border-radius: 8px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 36px;
        }
        
        .header p {
            color: #666;
            font-size: 16px;
        }
        
        .content {
            background: white;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .section {
            display: none;
        }
        
        .section.active {
            display: block;
        }
        
        .endpoint {
            margin-bottom: 30px;
            padding: 20px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }
        
        .endpoint-title {
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .method {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-right: 10px;
        }
        
        .method.get {
            background: #4CAF50;
            color: white;
        }
        
        .method.post {
            background: #2196F3;
            color: white;
        }
        
        .method.delete {
            background: #f44336;
            color: white;
        }
        
        .endpoint-path {
            font-family: 'Courier New', monospace;
            background: white;
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
            overflow-x: auto;
        }
        
        .endpoint-description {
            color: #666;
            margin: 10px 0;
            font-size: 14px;
        }
        
        .code-block {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            margin: 10px 0;
            font-family: 'Courier New', monospace;
            font-size: 13px;
        }
        
        .test-btn {
            background: #667eea;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 10px;
            font-size: 14px;
            transition: background 0.3s ease;
        }
        
        .test-btn:hover {
            background: #764ba2;
        }
        
        .test-result {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 4px;
            margin-top: 10px;
            border-left: 4px solid #4CAF50;
        }
        
        .test-result.error {
            border-left-color: #f44336;
            background: #ffebee;
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .feature-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #e0e0e0;
        }
        
        .feature-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .feature-card p {
            color: #666;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .tabs {
            display: flex;
            gap: 10px;
            margin: 20px 0;
            border-bottom: 2px solid #e0e0e0;
        }
        
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            background: none;
            border: none;
            font-size: 14px;
            color: #666;
            border-bottom: 3px solid transparent;
            transition: all 0.3s ease;
        }
        
        .tab:hover {
            color: #667eea;
        }
        
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        input, textarea, select {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            width: 100%;
        }
        
        label {
            display: block;
            margin-top: 10px;
            font-weight: 500;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <nav>
            <button class="nav-btn active" onclick="switchSection('overview')">📖 Overview</button>
            <button class="nav-btn" onclick="switchSection('endpoints')">🔌 Endpoints</button>
            <button class="nav-btn" onclick="switchSection('auth')">🔐 Authentication</button>
            <button class="nav-btn" onclick="switchSection('testing')">🧪 Testing</button>
            <button class="nav-btn" onclick="switchSection('examples')">💡 Examples</button>
        </nav>
        
        <div class="header">
            <h1>🚀 PageIQ API Documentation</h1>
            <p>Professional website analysis and data extraction API</p>
        </div>
        
        <!-- Overview Section -->
        <div id="overview" class="section active">
            <div class="content">
                <h2>Welcome to PageIQ API</h2>
                <p style="margin: 20px 0; color: #666; line-height: 1.8;">
                    PageIQ is a comprehensive API for analyzing websites, extracting data, and gaining insights about web pages.
                    Our API provides powerful tools for developers and businesses to understand and interact with web content programmatically.
                </p>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">Key Features</h3>
                <div class="feature-grid">
                    <div class="feature-card">
                        <h3>🔍 Website Analysis</h3>
                        <p>Analyze any website to extract metadata, technology stack, performance metrics, and more.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📧 Email Extraction</h3>
                        <p>Automatically extract email addresses from websites for lead generation and data collection.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📊 Batch Processing</h3>
                        <p>Process multiple websites simultaneously with our powerful batch API for bulk analysis.</p>
                    </div>
                    <div class="feature-card">
                        <h3>⚡ Real-time Results</h3>
                        <p>Get instant responses with real-time website analysis and data extraction.</p>
                    </div>
                    <div class="feature-card">
                        <h3>🔒 Secure & Reliable</h3>
                        <p>Enterprise-grade security with rate limiting, API keys, and HTTPS encryption.</p>
                    </div>
                    <div class="feature-card">
                        <h3>📈 Analytics</h3>
                        <p>Track your API usage with detailed analytics and performance metrics.</p>
                    </div>
                </div>
                
                <h3 style="color: #667eea; margin: 30px 0 10px;">Quick Start</h3>
                <div class="code-block">curl -X POST https://pageiq.pompora.dev/analyze \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: your_api_key_here" \\
  -d '{"url": "https://example.com"}'
                </div>
                
                <p style="color: #666; margin: 20px 0;">
                    Navigate to the <strong>Endpoints</strong> tab to see all available API endpoints,
                    visit <strong>Authentication</strong> to learn about securing your requests,
                    or jump to <strong>Testing</strong> to try endpoints directly from your browser.
                </p>
            </div>
        </div>
        
        <!-- Endpoints Section -->
        <div id="endpoints" class="section">
            <div class="content">
                <h2>API Endpoints</h2>
                
                <div class="endpoint">
                    <div class="endpoint-title">
                        <span class="method get">GET</span> Health Check
                    </div>
                    <div class="endpoint-path">/ping</div>
                    <div class="endpoint-description">
                        Simple health check endpoint. Returns 200 OK if the API is running.
                    </div>
                    <button class="test-btn" onclick="testEndpoint('GET', '/ping', {})">Test Endpoint</button>
                    <div id="ping-result"></div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-title">
                        <span class="method post">POST</span> Analyze Website
                    </div>
                    <div class="endpoint-path">/analyze</div>
                    <div class="endpoint-description">
                        Analyze a website and extract comprehensive information including metadata, technology stack, performance metrics, and more.
                    </div>
                    <div class="code-block">{
  "url": "https://example.com",
  "wait_for_js": true,
  "extract_emails": false
}
                    </div>
                    <button class="test-btn" onclick="testEndpoint('POST', '/analyze', {'url': 'https://example.com'})">Test Endpoint</button>
                    <div id="analyze-result"></div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-title">
                        <span class="method post">POST</span> Batch Analyze
                    </div>
                    <div class="endpoint-path">/batch-analyze</div>
                    <div class="endpoint-description">
                        Analyze multiple websites in a single batch request. Returns a batch ID for tracking progress.
                    </div>
                    <div class="code-block">{
  "urls": ["https://example.com", "https://example.org"],
  "wait_for_js": true
}
                    </div>
                    <button class="test-btn" onclick="testEndpoint('POST', '/batch-analyze', {'urls': ['https://example.com']})">Test Endpoint</button>
                    <div id="batch-result"></div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-title">
                        <span class="method post">POST</span> Extract Emails
                    </div>
                    <div class="endpoint-path">/extract/emails</div>
                    <div class="endpoint-description">
                        Extract email addresses from a website. Scans the page content and returns all found email addresses.
                    </div>
                    <div class="code-block">{
  "url": "https://example.com"
}
                    </div>
                    <button class="test-btn" onclick="testEndpoint('POST', '/extract/emails', {'url': 'https://example.com'})">Test Endpoint</button>
                    <div id="extract-result"></div>
                </div>
                
                <div class="endpoint">
                    <div class="endpoint-title">
                        <span class="method get">GET</span> API Status
                    </div>
                    <div class="endpoint-path">/</div>
                    <div class="endpoint-description">
                        Get the current status of the PageIQ API including version and basic information.
                    </div>
                    <button class="test-btn" onclick="testEndpoint('GET', '/', {})">Test Endpoint</button>
                    <div id="status-result"></div>
                </div>
            </div>
        </div>
        
        <!-- Authentication Section -->
        <div id="auth" class="section">
            <div class="content">
                <h2>Authentication</h2>
                <p style="margin: 20px 0; color: #666; line-height: 1.8;">
                    PageIQ API uses API key-based authentication. All requests (except health checks) must include a valid API key.
                </p>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">API Key Header</h3>
                <p style="color: #666; margin: 10px 0;">
                    Include your API key in the <code>X-API-Key</code> header:
                </p>
                <div class="code-block">curl -X POST https://pageiq.pompora.dev/analyze \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}'
                </div>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">Getting Your API Key</h3>
                <p style="color: #666; margin: 10px 0;">
                    1. Sign up for a PageIQ account<br>
                    2. Navigate to your dashboard<br>
                    3. Go to API Keys section<br>
                    4. Click "Generate New Key"<br>
                    5. Copy your key and keep it secure
                </p>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">Rate Limiting</h3>
                <p style="color: #666; margin: 10px 0;">
                    API requests are rate limited based on your account tier:
                </p>
                <ul style="color: #666; margin: 10px 0 10px 20px;">
                    <li>Free Tier: 100 requests per day</li>
                    <li>Pro Tier: 10,000 requests per day</li>
                    <li>Enterprise Tier: Unlimited requests</li>
                </ul>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">Security Best Practices</h3>
                <ul style="color: #666; margin: 10px 0 10px 20px;">
                    <li>Never share your API key publicly</li>
                    <li>Use environment variables to store your API key</li>
                    <li>Rotate your API keys regularly</li>
                    <li>Use HTTPS for all requests</li>
                    <li>Monitor your API usage for suspicious activity</li>
                </ul>
            </div>
        </div>
        
        <!-- Testing Section -->
        <div id="testing" class="section">
            <div class="content">
                <h2>Interactive API Testing</h2>
                <p style="margin: 20px 0; color: #666;">
                    Test the PageIQ API directly from your browser. Note: Health checks don't require authentication.
                </p>
                
                <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #333; margin-bottom: 15px;">🧪 Test Panel</h3>
                    
                    <label for="test-url">Website URL:</label>
                    <input type="text" id="test-url" placeholder="https://example.com" value="https://example.com">
                    
                    <label for="test-apikey">API Key (optional for health checks):</label>
                    <input type="password" id="test-apikey" placeholder="Leave empty for health checks">
                    
                    <label for="test-endpoint">Select Endpoint:</label>
                    <select id="test-endpoint">
                        <option value="ping">GET /ping (Health Check)</option>
                        <option value="status">GET / (API Status)</option>
                        <option value="analyze">POST /analyze (Analyze Website)</option>
                        <option value="extract">POST /extract/emails (Extract Emails)</option>
                        <option value="batch">POST /batch-analyze (Batch Analyze)</option>
                    </select>
                    
                    <button class="test-btn" onclick="runCustomTest()" style="margin-top: 15px; width: 100%;">
                        ⚡ Run Test
                    </button>
                    
                    <div id="custom-result" style="margin-top: 20px;"></div>
                </div>
                
                <h3 style="color: #667eea; margin: 30px 0 15px;">Quick Test Buttons</h3>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
                    <button class="test-btn" onclick="testEndpoint('GET', '/ping', {})" style="width: 100%;">
                        Test Health Check
                    </button>
                    <button class="test-btn" onclick="testEndpoint('GET', '/', {})" style="width: 100%;">
                        Test API Status
                    </button>
                    <button class="test-btn" onclick="testEndpoint('POST', '/analyze', {'url': 'https://example.com'})" style="width: 100%;">
                        Test Analyze
                    </button>
                    <button class="test-btn" onclick="testEndpoint('POST', '/extract/emails', {'url': 'https://example.com'})" style="width: 100%;">
                        Test Email Extract
                    </button>
                </div>
            </div>
        </div>
        
        <!-- Examples Section -->
        <div id="examples" class="section">
            <div class="content">
                <h2>Code Examples</h2>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">Python</h3>
                <div class="code-block">import requests

api_key = "your_api_key_here"
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

# Analyze a website
response = requests.post(
    "https://pageiq.pompora.dev/analyze",
    headers=headers,
    json={"url": "https://example.com"}
)
print(response.json())

# Extract emails
response = requests.post(
    "https://pageiq.pompora.dev/extract/emails",
    headers=headers,
    json={"url": "https://example.com"}
)
print(response.json())
                </div>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">JavaScript</h3>
                <div class="code-block">const apiKey = "your_api_key_here";

// Analyze a website
fetch("https://pageiq.pompora.dev/analyze", {
    method: "POST",
    headers: {
        "X-API-Key": apiKey,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        url: "https://example.com"
    })
})
.then(res => res.json())
.then(data => console.log(data));

// Extract emails
fetch("https://pageiq.pompora.dev/extract/emails", {
    method: "POST",
    headers: {
        "X-API-Key": apiKey,
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        url: "https://example.com"
    })
})
.then(res => res.json())
.then(data => console.log(data));
                </div>
                
                <h3 style="color: #667eea; margin: 20px 0 10px;">cURL</h3>
                <div class="code-block"># Analyze a website
curl -X POST https://pageiq.pompora.dev/analyze \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}'

# Extract emails
curl -X POST https://pageiq.pompora.dev/extract/emails \\
  -H "X-API-Key: your_api_key_here" \\
  -H "Content-Type: application/json" \\
  -d '{"url": "https://example.com"}'

# Health check
curl https://pageiq.pompora.dev/ping
                </div>
            </div>
        </div>
    </div>
    
    <script>
        async function switchSection(section) {
            // Hide all sections
            document.querySelectorAll('.section').forEach(el => {
                el.classList.remove('active');
            });
            
            // Show selected section
            const selectedSection = document.getElementById(section);
            if (selectedSection) {
                selectedSection.classList.add('active');
            }
            
            // Update nav buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            event.target.classList.add('active');
        }
        
        async function testEndpoint(method, path, data = {}) {
            const resultDivId = path.replace('/', '').replace('-', '-') + '-result';
            const resultDiv = document.getElementById(resultDivId);
            
            if (!resultDiv) return;
            
            resultDiv.innerHTML = '<p style="color: #666;">Loading...</p>';
            
            try {
                const options = {
                    method: method,
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                if (method === 'POST' && Object.keys(data).length > 0) {
                    options.body = JSON.stringify(data);
                }
                
                const response = await fetch(path, options);
                const result = await response.json();
                
                resultDiv.className = response.ok ? 'test-result' : 'test-result error';
                resultDiv.innerHTML = `
                    <strong>Status: ${response.status} ${response.statusText}</strong><br>
                    <pre style="margin-top: 10px; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
                `;
            } catch (error) {
                resultDiv.className = 'test-result error';
                resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }
        
        async function runCustomTest() {
            const url = document.getElementById('test-url').value;
            const apiKey = document.getElementById('test-apikey').value;
            const endpoint = document.getElementById('test-endpoint').value;
            const resultDiv = document.getElementById('custom-result');
            
            resultDiv.innerHTML = '<p style="color: #666;">Loading...</p>';
            
            try {
                const options = {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                };
                
                let path = '';
                
                if (endpoint === 'ping') {
                    path = '/ping';
                } else if (endpoint === 'status') {
                    path = '/';
                } else if (endpoint === 'analyze') {
                    options.method = 'POST';
                    options.body = JSON.stringify({ url: url });
                    path = '/analyze';
                } else if (endpoint === 'extract') {
                    options.method = 'POST';
                    options.body = JSON.stringify({ url: url });
                    path = '/extract/emails';
                } else if (endpoint === 'batch') {
                    options.method = 'POST';
                    options.body = JSON.stringify({ urls: [url] });
                    path = '/batch-analyze';
                }
                
                if (apiKey) {
                    options.headers['X-API-Key'] = apiKey;
                }
                
                const response = await fetch(path, options);
                const result = await response.json();
                
                resultDiv.className = response.ok ? 'test-result' : 'test-result error';
                resultDiv.innerHTML = `
                    <strong>Status: ${response.status} ${response.statusText}</strong><br>
                    <pre style="margin-top: 10px; overflow-x: auto;">${JSON.stringify(result, null, 2)}</pre>
                `;
            } catch (error) {
                resultDiv.className = 'test-result error';
                resultDiv.innerHTML = `<strong>Error:</strong> ${error.message}`;
            }
        }
    </script>
</body>
</html>
"""

@router.get("/docs", response_class=HTMLResponse)
async def get_docs():
    """Serve the documentation page"""
    return DOCS_HTML

@router.get("/tests", response_class=HTMLResponse)
async def get_tests():
    """Serve the interactive testing page"""
    return DOCS_HTML
