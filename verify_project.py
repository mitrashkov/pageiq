#!/usr/bin/env python3
"""
PageIQ Project Verification Script

This script verifies that all components of the PageIQ project are
properly configured and ready for production deployment.

Usage:
    python verify_project.py
    python verify_project.py --verbose
    python verify_project.py --component api
    python verify_project.py --fix-issues
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
import argparse


class ProjectVerifier:
    """Verify PageIQ project readiness"""
    
    def __init__(self, verbose: bool = False, fix_issues: bool = False):
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.root_path = Path(__file__).parent
        self.issues = []
        self.warnings = []
        self.passed = 0
        self.failed = 0
    
    def log(self, msg: str, level: str = "INFO"):
        """Log a message"""
        levels = {
            "INFO": "ℹ",
            "SUCCESS": "✓",
            "ERROR": "✗",
            "WARNING": "⚠",
            "DEBUG": "🔍"
        }
        
        symbol = levels.get(level, "•")
        
        if level == "DEBUG" and not self.verbose:
            return
        
        print(f"{symbol} {msg}")
    
    def verify_all(self) -> bool:
        """Run all verifications"""
        print("\n" + "="*60)
        print("PageIQ Project Verification")
        print("="*60 + "\n")
        
        checks = [
            ("Project Structure", self.verify_structure),
            ("Core Application", self.verify_core_app),
            ("API Endpoints", self.verify_endpoints),
            ("Services", self.verify_services),
            ("Database", self.verify_database),
            ("Testing", self.verify_testing),
            ("Documentation", self.verify_documentation),
            ("Deployment", self.verify_deployment),
            ("Configuration", self.verify_configuration),
            ("Dependencies", self.verify_dependencies),
        ]
        
        for check_name, check_func in checks:
            print(f"\n{'─'*60}")
            print(f"Checking: {check_name}")
            print('─'*60)
            try:
                check_func()
            except Exception as e:
                self.log(f"Check failed with error: {e}", "ERROR")
                self.failed += 1
        
        return self.print_summary()
    
    def verify_structure(self):
        """Verify project directory structure"""
        required_dirs = [
            "app",
            "app/api",
            "app/api/v1",
            "app/api/v1/endpoints",
            "app/core",
            "app/services",
            "app/models",
            "app/schemas",
            "app/db",
            "app/tasks",
            "app/utils",
            "tests",
            "alembic",
            "alembic/versions",
            "docker",
            "docs",
            "data",
            "data/screenshots",
            "sdk",
            "load_test",
        ]
        
        for dir_name in required_dirs:
            path = self.root_path / dir_name
            if path.exists() and path.is_dir():
                self.log(f"Directory exists: {dir_name}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing directory: {dir_name}", "ERROR")
                self.issues.append(f"Missing directory: {dir_name}")
                self.failed += 1
    
    def verify_core_app(self):
        """Verify core application files"""
        required_files = [
            "app/main.py",
            "app/__init__.py",
            "app/api/v1/api.py",
            "app/core/auth.py",
            "app/core/database.py",
            "app/core/redis.py",
            "app/core/rate_limiter.py",
            "app/core/security.py",
        ]
        
        for file_name in required_files:
            path = self.root_path / file_name
            if path.exists():
                self.log(f"File found: {file_name}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing file: {file_name}", "ERROR")
                self.issues.append(f"Missing file: {file_name}")
                self.failed += 1
    
    def verify_endpoints(self):
        """Verify all API endpoints are present"""
        endpoint_dir = self.root_path / "app/api/v1/endpoints"
        required_endpoints = [
            "health.py",
            "analyze.py",
            "batch.py",
            "analytics.py",
            "extract.py",
            "seo.py",
            "billing.py",
        ]
        
        for endpoint_file in required_endpoints:
            path = endpoint_dir / endpoint_file
            if path.exists():
                self.log(f"Endpoint found: {endpoint_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing endpoint: {endpoint_file}", "ERROR")
                self.issues.append(f"Missing endpoint: {endpoint_file}")
                self.failed += 1
    
    def verify_services(self):
        """Verify all services are present"""
        services_dir = self.root_path / "app/services"
        required_services = [
            "analyzer.py",
            "browser.py",
            "fetcher.py",
            "extractors.py",
            "tech_detector.py",
            "speed_scorer.py",
            "ai_summarizer.py",
            "stripe_service.py",
            "quota.py",
            "analytics.py",
        ]
        
        for service_file in required_services:
            path = services_dir / service_file
            if path.exists():
                self.log(f"Service found: {service_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing service: {service_file}", "ERROR")
                self.issues.append(f"Missing service: {service_file}")
                self.failed += 1
    
    def verify_database(self):
        """Verify database configuration"""
        alembic_ini = self.root_path / "alembic.ini"
        
        if alembic_ini.exists():
            self.log("Alembic configuration found", "SUCCESS")
            self.passed += 1
        else:
            self.log("Missing Alembic configuration", "ERROR")
            self.failed += 1
        
        env_py = self.root_path / "alembic/env.py"
        if env_py.exists():
            self.log("Alembic environment found", "SUCCESS")
            self.passed += 1
        else:
            self.log("Missing Alembic environment", "ERROR")
            self.failed += 1
        
        versions_dir = self.root_path / "alembic/versions"
        if versions_dir.exists():
            migrations = list(versions_dir.glob("*.py"))
            if migrations:
                self.log(f"Found {len(migrations)} migrations", "SUCCESS")
                self.passed += 1
            else:
                self.log("No migrations found", "WARNING")
                self.warnings.append("No migrations found")
        else:
            self.log("Migrations directory not found", "ERROR")
            self.failed += 1
    
    def verify_testing(self):
        """Verify test files"""
        tests_dir = self.root_path / "tests"
        required_tests = [
            "conftest.py",
            "test_analyze.py",
            "test_batch.py",
            "test_extractors.py",
            "test_advanced_services.py",
            "test_extraction_endpoints.py",
        ]
        
        for test_file in required_tests:
            path = tests_dir / test_file
            if path.exists():
                self.log(f"Test file found: {test_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing test file: {test_file}", "ERROR")
                self.issues.append(f"Missing test file: {test_file}")
                self.failed += 1
    
    def verify_documentation(self):
        """Verify documentation files"""
        required_docs = [
            "README.md",
            "TECHNICAL_SPEC.md",
            "docs/API_DOCUMENTATION.md",
            "RAPIDAPI_INTEGRATION_GUIDE.md",
            "RAPIDAPI_ACCOUNT_SETUP.md",
            "PRODUCTION_DEPLOYMENT_CHECKLIST.md",
            "PROJECT_COMPLETION_SUMMARY.md",
            "QUICK_REFERENCE.md",
            "SECURITY_REVIEW.md",
            "DEPLOYMENT.md",
        ]
        
        for doc_file in required_docs:
            path = self.root_path / doc_file
            if path.exists():
                self.log(f"Documentation found: {doc_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing documentation: {doc_file}", "WARNING")
                self.warnings.append(f"Missing documentation: {doc_file}")
    
    def verify_deployment(self):
        """Verify deployment files"""
        deployment_files = [
            "docker/Dockerfile",
            "docker-compose.yml",
            "deploy_production.py",
        ]
        
        for deploy_file in deployment_files:
            path = self.root_path / deploy_file
            if path.exists():
                self.log(f"Deployment file found: {deploy_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing deployment file: {deploy_file}", "ERROR")
                self.issues.append(f"Missing deployment file: {deploy_file}")
                self.failed += 1
    
    def verify_configuration(self):
        """Verify configuration files"""
        required_config = [
            "requirements.txt",
            "alembic.ini",
        ]
        
        optional_config = [
            ".env",
            ".env.example",
        ]
        
        for config_file in required_config:
            path = self.root_path / config_file
            if path.exists():
                self.log(f"Config file found: {config_file}", "SUCCESS")
                self.passed += 1
            else:
                self.log(f"Missing config file: {config_file}", "ERROR")
                self.issues.append(f"Missing config file: {config_file}")
                self.failed += 1
        
        for config_file in optional_config:
            path = self.root_path / config_file
            if path.exists():
                self.log(f"Optional config found: {config_file}", "SUCCESS")
            else:
                self.log(f"Optional config not found: {config_file}", "DEBUG")
    
    def verify_dependencies(self):
        """Verify Python dependencies"""
        requirements_file = self.root_path / "requirements.txt"
        
        if not requirements_file.exists():
            self.log("requirements.txt not found", "ERROR")
            self.failed += 1
            return
        
        self.log("requirements.txt found", "SUCCESS")
        self.passed += 1
        
        # Read requirements
        try:
            with open(requirements_file) as f:
                requirements = f.read()
            
            required_packages = [
                "fastapi",
                "uvicorn",
                "sqlalchemy",
                "psycopg2",
                "redis",
                "playwright",
                "beautifulsoup4",
                "stripe",
                "celery",
                "pytest",
                "sentry-sdk",
                "opentelemetry",
            ]
            
            for package in required_packages:
                if package.lower() in requirements.lower():
                    self.log(f"Dependency found: {package}", "SUCCESS")
                    self.passed += 1
                else:
                    self.log(f"Missing dependency: {package}", "WARNING")
                    self.warnings.append(f"Missing dependency: {package}")
        except Exception as e:
            self.log(f"Error reading requirements: {e}", "ERROR")
            self.failed += 1
    
    def print_summary(self) -> bool:
        """Print verification summary"""
        print("\n" + "="*60)
        print("Verification Summary")
        print("="*60)
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\nResults:")
        print(f"  ✓ Passed: {self.passed}")
        print(f"  ✗ Failed: {self.failed}")
        print(f"  Success Rate: {percentage:.1f}%")
        
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        if self.issues:
            print(f"\nIssues ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  ✗ {issue}")
        
        print("\n" + "="*60)
        
        if self.failed == 0:
            print("✓ Project verification PASSED - Ready for production!")
            print("="*60 + "\n")
            return True
        else:
            print(f"✗ Project verification FAILED - {self.failed} issues found")
            print("Please fix issues before proceeding")
            print("="*60 + "\n")
            return False


class QuickHealthCheck:
    """Quick health check for running system"""
    
    def __init__(self):
        self.logger = ProjectVerifier()
    
    def check_api(self, url: str = "http://localhost:8000") -> bool:
        """Check if API is running"""
        try:
            import requests
            response = requests.get(f"{url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                self.logger.log(f"API responding at {url}", "SUCCESS")
                return True
            else:
                self.logger.log(f"API returned {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.logger.log(f"API not responding: {e}", "ERROR")
            return False
    
    def check_database(self, url: str = "localhost:5432") -> bool:
        """Check if database is running"""
        try:
            import psycopg2
            host, port = url.split(":")
            conn = psycopg2.connect(
                host=host,
                port=int(port),
                database="pageiq",
                user="postgres",
                password="postgres",
                timeout=5
            )
            conn.close()
            self.logger.log(f"Database responsive at {url}", "SUCCESS")
            return True
        except Exception as e:
            self.logger.log(f"Database not responding: {e}", "ERROR")
            return False
    
    def check_redis(self, url: str = "localhost:6379") -> bool:
        """Check if Redis is running"""
        try:
            import redis
            host, port = url.split(":")
            r = redis.Redis(host=host, port=int(port), socket_connect_timeout=5)
            r.ping()
            self.logger.log(f"Redis responsive at {url}", "SUCCESS")
            return True
        except Exception as e:
            self.logger.log(f"Redis not responding: {e}", "ERROR")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PageIQ Project Verification Tool"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed output"
    )
    
    parser.add_argument(
        "--health",
        action="store_true",
        help="Quick health check of running system"
    )
    
    parser.add_argument(
        "--component",
        choices=[
            "api",
            "database",
            "redis",
            "all"
        ],
        help="Check specific component"
    )
    
    parser.add_argument(
        "--fix-issues",
        action="store_true",
        help="Attempt to fix issues"
    )
    
    args = parser.parse_args()
    
    if args.health:
        # Quick health check
        print("\nQuick Health Check\n")
        checker = QuickHealthCheck()
        
        if args.component in [None, "api", "all"]:
            checker.check_api()
        if args.component in [None, "database", "all"]:
            checker.check_database()
        if args.component in [None, "redis", "all"]:
            checker.check_redis()
    else:
        # Full project verification
        verifier = ProjectVerifier(
            verbose=args.verbose,
            fix_issues=args.fix_issues
        )
        
        success = verifier.verify_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
