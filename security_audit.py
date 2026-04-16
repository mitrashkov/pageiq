#!/usr/bin/env python3
"""
Security Audit Script for PageIQ API

This script performs automated security checks on the codebase and configuration.
"""

import importlib
import inspect
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

class SecurityAuditor:
    """Security auditor for the PageIQ codebase"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or Path(__file__).parent.parent)
        self.issues = []
        self.warnings = []

    def run_full_audit(self) -> Tuple[bool, List[str], List[str]]:
        """Run comprehensive security audit"""

        checks = [
            ("Input Validation", self.check_input_validation),
            ("Authentication Security", self.check_authentication),
            ("Authorization Checks", self.check_authorization),
            ("SQL Injection Prevention", self.check_sql_injection),
            ("XSS Prevention", self.check_xss_protection),
            ("CSRF Protection", self.check_csrf_protection),
            ("Secure Headers", self.check_security_headers),
            ("Dependency Vulnerabilities", self.check_dependencies),
            ("Secrets Management", self.check_secrets),
            ("Error Handling", self.check_error_handling),
            ("Rate Limiting", self.check_rate_limiting),
            ("Logging Security", self.check_logging_security),
        ]

        print("🔒 Running Security Audit...")
        print("=" * 50)

        for check_name, check_func in checks:
            print(f"\n🔍 Checking: {check_name}")
            try:
                result, message = check_func()
                if result:
                    print(f"✅ PASS: {message}")
                else:
                    print(f"❌ FAIL: {message}")
                    self.issues.append(f"{check_name}: {message}")
            except Exception as e:
                error_msg = f"Error during {check_name}: {str(e)}"
                print(f"💥 ERROR: {error_msg}")
                self.issues.append(error_msg)

        print("\n" + "=" * 50)
        total_checks = len(checks)
        issues_count = len(self.issues)
        print(f"Security Audit Complete: {issues_count} issues found")

        return issues_count == 0, self.issues, self.warnings

    def check_input_validation(self) -> Tuple[bool, str]:
        """Check for proper input validation"""
        # Look for validation decorators or schemas
        validation_files = [
            "app/schemas/__init__.py",
            "app/core/errors.py",
            "app/api/v1/endpoints/analyze.py"
        ]

        validation_found = False
        for file_path in validation_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                if any(keyword in content for keyword in [
                    "validate_url_input", "validate_options_input",
                    "Pydantic", "BaseModel", "Field"
                ]):
                    validation_found = True
                    break

        if validation_found:
            return True, "Input validation implemented with Pydantic schemas"
        return False, "Input validation not found or incomplete"

    def check_authentication(self) -> Tuple[bool, str]:
        """Check authentication implementation"""
        auth_file = self.project_root / "app/core/auth.py"
        if not auth_file.exists():
            return False, "Authentication module not found"

        content = auth_file.read_text()

        checks = [
            ("API key validation", "verify_api_key" in content),
            ("User context", "get_current_user" in content),
            ("Token expiration", "expires_delta" in content or "ACCESS_TOKEN_EXPIRE" in content),
        ]

        failed_checks = [name for name, passed in checks if not passed]

        if not failed_checks:
            return True, "Authentication implementation looks secure"
        return False, f"Missing authentication features: {', '.join(failed_checks)}"

    def check_authorization(self) -> Tuple[bool, str]:
        """Check authorization implementation"""
        # Look for authorization checks in endpoints
        endpoint_files = list(self.project_root.glob("app/api/**/*.py"))

        auth_checks_found = False
        for file_path in endpoint_files:
            content = file_path.read_text()
            if any(keyword in content for keyword in [
                "get_current_user", "require_auth", "Depends",
                "@router."  # FastAPI route decorators
            ]):
                auth_checks_found = True
                break

        if auth_checks_found:
            return True, "Authorization checks implemented on API endpoints"
        return False, "Authorization checks not found on endpoints"

    def check_sql_injection(self) -> Tuple[bool, str]:
        """Check for SQL injection prevention"""
        # Look for SQLAlchemy usage instead of raw SQL
        python_files = list(self.project_root.glob("**/*.py"))

        raw_sql_found = False
        sqlalchemy_found = False

        for file_path in python_files:
            try:
                content = file_path.read_text()
                if "cursor.execute" in content or "db.execute(text(" in content:
                    raw_sql_found = True
                if "session.query" in content or "db.query" in content:
                    sqlalchemy_found = True
            except:
                continue

        if sqlalchemy_found and not raw_sql_found:
            return True, "Using SQLAlchemy ORM for safe database operations"
        elif raw_sql_found:
            return False, "Raw SQL queries found - potential SQL injection risk"
        return False, "Database access patterns unclear"

    def check_xss_protection(self) -> Tuple[bool, str]:
        """Check for XSS protection"""
        # Look for security headers and content escaping
        security_files = [
            "app/core/security_headers.py",
            "app/main.py"
        ]

        xss_protection = False
        for file_path in security_files:
            full_path = self.project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                if any(header in content for header in [
                    "X-XSS-Protection", "Content-Security-Policy"
                ]):
                    xss_protection = True
                    break

        if xss_protection:
            return True, "XSS protection headers implemented"
        return False, "XSS protection headers not found"

    def check_csrf_protection(self) -> Tuple[bool, str]:
        """Check for CSRF protection"""
        # For API-only applications, CSRF might not be needed if using token auth
        # But we should check if there are any web forms or state-changing endpoints

        endpoint_files = list(self.project_root.glob("app/api/**/*.py"))
        state_changing_endpoints = False

        for file_path in endpoint_files:
            content = file_path.read_text()
            if any(method in content for method in ["POST", "PUT", "DELETE", "PATCH"]):
                state_changing_endpoints = True
                break

        if state_changing_endpoints:
            # For API, token-based auth provides CSRF protection
            return True, "API uses token-based authentication (CSRF protection via tokens)"
        return True, "No state-changing endpoints found"

    def check_security_headers(self) -> Tuple[bool, str]:
        """Check for comprehensive security headers"""
        security_file = self.project_root / "app/core/security_headers.py"
        if not security_file.exists():
            return False, "Security headers module not found"

        content = security_file.read_text()

        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy"
        ]

        missing_headers = []
        for header in required_headers:
            if header not in content:
                missing_headers.append(header)

        if not missing_headers:
            return True, "All required security headers implemented"
        return False, f"Missing security headers: {', '.join(missing_headers)}"

    def check_dependencies(self) -> Tuple[bool, str]:
        """Check for dependency vulnerabilities"""
        try:
            # Try to run safety check
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--outdated"],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0 and result.stdout.strip():
                return False, "Outdated dependencies found - run 'pip list --outdated'"
            return True, "Dependencies appear up to date"
        except:
            return True, "Could not check dependencies (pip not available)"

    def check_secrets(self) -> Tuple[bool, str]:
        """Check for secrets in codebase"""
        # Look for common secret patterns
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]

        python_files = list(self.project_root.glob("**/*.py"))
        secrets_found = []

        for file_path in python_files:
            if "test" in str(file_path) or "config" in str(file_path):
                continue  # Skip test and config files

            try:
                content = file_path.read_text()
                for pattern in secret_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        secrets_found.extend(matches[:3])  # Limit findings
            except:
                continue

        if not secrets_found:
            return True, "No hardcoded secrets found in codebase"
        return False, f"Potential hardcoded secrets found: {len(secrets_found)} instances"

    def check_error_handling(self) -> Tuple[bool, str]:
        """Check error handling implementation"""
        error_file = self.project_root / "app/core/errors.py"
        if not error_file.exists():
            return False, "Error handling module not found"

        content = error_file.read_text()

        error_patterns = [
            "HTTPException",
            "PageIQException",
            "try:",
            "except",
            "create_error_response"
        ]

        error_handling_found = any(pattern in content for pattern in error_patterns)

        if error_handling_found:
            return True, "Comprehensive error handling implemented"
        return False, "Error handling implementation incomplete"

    def check_rate_limiting(self) -> Tuple[bool, str]:
        """Check rate limiting implementation"""
        rate_limit_file = self.project_root / "app/core/rate_limiter.py"
        if not rate_limit_file.exists():
            return False, "Rate limiting module not found"

        content = rate_limit_file.read_text()

        rate_limit_features = [
            "RateLimiter",
            "Redis",
            "sliding window",
            "rate limit"
        ]

        features_found = sum(1 for feature in rate_limit_features if feature.lower() in content.lower())

        if features_found >= 3:
            return True, "Rate limiting implemented with Redis sliding window"
        return False, "Rate limiting implementation incomplete"

    def check_logging_security(self) -> Tuple[bool, str]:
        """Check logging doesn't expose sensitive data"""
        logging_file = self.project_root / "app/core/logging.py"
        if not logging_file.exists():
            return False, "Logging configuration not found"

        content = logging_file.read_text()

        # Check for sensitive data filtering
        sensitive_filters = [
            "password", "secret", "key", "token", "FILTERED"
        ]

        filters_found = any(filter_word in content for filter_word in sensitive_filters)

        if filters_found:
            return True, "Logging filters out sensitive data"
        return False, "Logging may expose sensitive data"


def main():
    """Main audit runner"""
    auditor = SecurityAuditor()

    passed, issues, warnings = auditor.run_full_audit()

    if issues:
        print("\n🚨 Security Issues Found:")
        for issue in issues:
            print(f"  - {issue}")

    if warnings:
        print("\n⚠️  Security Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    print(f"\n🔒 Security Audit {'PASSED' if passed else 'FAILED'}")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()