"""
Security headers and protections middleware
"""

import hashlib
import hmac
import time
from typing import Dict, List, Optional, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding comprehensive security headers"""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Add security headers
        self._add_security_headers(response)

        # Add CSP header if configured
        csp = self._get_content_security_policy()
        if csp:
            response.headers["Content-Security-Policy"] = csp

        # Add HSTS for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        return response

    def _add_security_headers(self, response: Response):
        """Add standard security headers"""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            # Relaxed for public API access
            "Cross-Origin-Embedder-Policy": "unsafe-none",
            "Cross-Origin-Opener-Policy": "unsafe-none",
            "Cross-Origin-Resource-Policy": "cross-origin",
        }

        for header, value in headers.items():
            response.headers[header] = value

    def _get_content_security_policy(self) -> Optional[str]:
        """Generate Content Security Policy header"""
        # Allow docs/tests pages to use inline styles and scripts
        # Production: Use external CSS/JS files
        return (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Middleware for enhanced request validation and security"""

    def __init__(self, app, max_body_size: int = 10 * 1024 * 1024):  # 10MB
        super().__init__(app)
        self.max_body_size = max_body_size
        self.suspicious_patterns = [
            r'<\s*script',  # Script tags
            r'javascript:',  # JavaScript URLs
            r'data:\s*text/html',  # Data URLs with HTML
            r'vbscript:',  # VBScript
            r'on\w+\s*=',  # Event handlers
        ]

    async def dispatch(self, request: Request, call_next):
        # Validate request size
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.max_body_size:
                    return self._create_error_response(
                        413, "Request too large",
                        f"Maximum request size is {self.max_body_size} bytes"
                    )
            except ValueError:
                pass

        # Check for suspicious content in headers
        if self._contains_suspicious_content(str(request.headers)):
            return self._create_error_response(
                400, "Bad Request", "Suspicious content detected"
            )

        # Validate User-Agent
        user_agent = request.headers.get("user-agent", "")
        if self._is_suspicious_user_agent(user_agent):
            return self._create_error_response(
                403, "Forbidden", "Suspicious user agent"
            )

        response = await call_next(request)
        return response

    def _contains_suspicious_content(self, content: str) -> bool:
        """Check if content contains suspicious patterns"""
        import re
        content_lower = content.lower()

        for pattern in self.suspicious_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True

        return False

    def _is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent looks suspicious"""
        if not user_agent:
            return False

        suspicious_indicators = [
            "sqlmap", "nmap", "nikto", "dirbuster", "gobuster",
            "masscan", "zgrab", "nessus", "acunetix", "openvas",
            "qualysguard", "rapid7", "metasploit", "burp", "owasp",
            "postman", "insomnia"  # Development tools might be suspicious in production
        ]

        ua_lower = user_agent.lower()
        for indicator in suspicious_indicators:
            if indicator in ua_lower:
                return True

        return False

    def _create_error_response(self, status_code: int, title: str, detail: str):
        """Create security error response"""
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error": {
                    "code": "SECURITY_VIOLATION",
                    "message": title,
                    "detail": detail
                }
            }
        )


class SSRFProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware to prevent Server-Side Request Forgery attacks"""

    def __init__(self, app, allowed_schemes: List[str] = None, blocked_hosts: List[str] = None):
        super().__init__(app)
        self.allowed_schemes = allowed_schemes or ["http", "https"]
        self.blocked_hosts = blocked_hosts or [
            "localhost", "127.0.0.1", "0.0.0.0",
            "169.254.169.254",  # AWS metadata
            "metadata.google.internal",  # GCP metadata
            "169.254.169.254",  # Azure metadata
        ]
        # Private IP ranges
        self.private_ranges = [
            ("10.0.0.0", "10.255.255.255"),
            ("172.16.0.0", "172.31.255.255"),
            ("192.168.0.0", "192.168.255.255"),
            ("127.0.0.0", "127.255.255.255"),
        ]

    async def dispatch(self, request: Request, call_next):
        # This middleware would primarily be used for protecting against
        # SSRF in cases where user input is used to make requests.
        # For now, we'll add it as a placeholder for future implementation.

        response = await call_next(request)
        return response

    def is_allowed_url(self, url: str) -> bool:
        """Check if URL is allowed (no SSRF)"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in self.allowed_schemes:
                return False

            # Check hostname
            hostname = parsed.hostname
            if not hostname:
                return False

            # Block specific hosts
            if hostname.lower() in self.blocked_hosts:
                return False

            # Block private IP ranges
            if self._is_private_ip(hostname):
                return False

            return True
        except Exception:
            return False

    def _is_private_ip(self, hostname: str) -> bool:
        """Check if hostname resolves to private IP"""
        import ipaddress
        import socket

        try:
            # Resolve hostname to IP
            ip = socket.gethostbyname(hostname)
            ip_obj = ipaddress.ip_address(ip)

            # Check against private ranges
            for start, end in self.private_ranges:
                if ipaddress.ip_address(start) <= ip_obj <= ipaddress.ip_address(end):
                    return True

            # Check if it's localhost
            if ip_obj.is_loopback:
                return True

        except Exception:
            # If we can't resolve, err on the side of caution
            return True

        return False


class RateLimitBypassDetection:
    """Detect and mitigate rate limit bypass attempts"""

    def __init__(self):
        self.suspicious_patterns = {
            'header_rotation': [],  # Track header variations
            'ip_rotation': [],      # Track IP changes for same API key
            'timing_patterns': [],  # Track request timing patterns
        }

    def analyze_request(self, request: Request) -> Dict[str, float]:
        """Analyze request for bypass patterns"""
        scores = {
            'header_manipulation': 0.0,
            'ip_rotation': 0.0,
            'timing_attack': 0.0,
            'automation_indicators': 0.0,
        }

        # Check for header manipulation
        headers = dict(request.headers)
        suspicious_headers = [
            'x-forwarded-for', 'x-real-ip', 'x-client-ip',
            'cf-connecting-ip', 'true-client-ip'
        ]

        for header in suspicious_headers:
            if header in headers and len(headers[header].split(',')) > 1:
                scores['header_manipulation'] += 0.3

        # Check user agent for automation
        user_agent = headers.get('user-agent', '').lower()
        automation_indicators = [
            'python-requests', 'curl', 'wget', 'postman', 'axios'
        ]

        for indicator in automation_indicators:
            if indicator in user_agent:
                scores['automation_indicators'] += 0.2

        # Check for timing patterns (too regular)
        # This would require storing previous request times

        return scores

    def should_block_request(self, scores: Dict[str, float], threshold: float = 0.7) -> bool:
        """Determine if request should be blocked based on scores"""
        total_score = sum(scores.values())
        return total_score > threshold


# Global security instances
ssrf_protection = SSRFProtectionMiddleware(None)
rate_limit_bypass_detection = RateLimitBypassDetection()

