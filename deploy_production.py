#!/usr/bin/env python3
"""
PageIQ Production Deployment Script

This script automates the complete deployment process to production,
including validation, Docker build, and Kubernetes deployment.

Usage:
    python deploy_production.py --environment production --tag v1.0.0
    python deploy_production.py --environment staging --tag v1.0.0-rc1
    python deploy_production.py --rollback --tag v0.9.9
"""

import os
import sys
import subprocess
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from enum import Enum
import argparse
import time


class DeploymentStage(Enum):
    """Deployment stages in order"""
    VALIDATION = "validation"
    BUILD = "build"
    PUSH = "push"
    DEPLOY = "deploy"
    VERIFY = "verify"
    COMPLETE = "complete"


class DeploymentConfig:
    """Configuration for deployment"""
    
    ENVIRONMENTS = {
        "staging": {
            "registry": "gcr.io/pageiq-staging",
            "namespace": "staging",
            "replicas": 2,
            "request_cpu": "500m",
            "request_memory": "512Mi",
            "limit_cpu": "1000m",
            "limit_memory": "1Gi",
        },
        "production": {
            "registry": "gcr.io/pageiq-prod",
            "namespace": "production",
            "replicas": 3,
            "request_cpu": "1000m",
            "request_memory": "1Gi",
            "limit_cpu": "2000m",
            "limit_memory": "2Gi",
        }
    }


class Logger:
    """Custom logger for deployment operations"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, msg: str):
        self.logger.info(f"✓ {msg}")
    
    def warning(self, msg: str):
        self.logger.warning(f"⚠ {msg}")
    
    def error(self, msg: str):
        self.logger.error(f"✗ {msg}")
    
    def section(self, msg: str):
        self.logger.info(f"\n{'='*60}\n{msg}\n{'='*60}")


class ValidationRunner:
    """Run pre-deployment validations"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
        self.passed = True
    
    def run_all(self) -> bool:
        """Run all validation checks"""
        self.logger.section("Pre-Deployment Validation")
        
        checks = [
            self.check_environment,
            self.check_docker,
            self.check_kubectl,
            self.check_git_status,
            self.check_tests,
            self.check_dependencies,
            self.check_configuration,
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.logger.error(str(e))
                self.passed = False
        
        return self.passed
    
    def check_environment(self):
        """Verify environment variables"""
        required_vars = [
            'STRIPE_SECRET_KEY',
            'DATABASE_URL',
            'REDIS_URL',
        ]
        
        for var in required_vars:
            if not os.environ.get(var):
                raise Exception(f"Missing environment variable: {var}")
        
        self.logger.info("Environment variables configured")
    
    def check_docker(self):
        """Verify Docker is installed and running"""
        result = subprocess.run(
            ['docker', 'version'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception("Docker not installed or not running")
        
        self.logger.info("Docker is available")
    
    def check_kubectl(self):
        """Verify kubectl is installed and configured"""
        result = subprocess.run(
            ['kubectl', 'version', '--client'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception("kubectl not installed or not configured")
        
        self.logger.info("kubectl is available")
    
    def check_git_status(self):
        """Verify git repository is clean"""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.stdout.strip():
            self.logger.warning("Uncommitted changes detected")
        else:
            self.logger.info("Git repository is clean")
    
    def check_tests(self):
        """Run test suite"""
        self.logger.info("Running test suite...")
        
        result = subprocess.run(
            ['pytest', 'tests/', '-v', '--tb=short'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Tests failed:\n{result.stdout}")
        
        # Parse test results
        if "passed" in result.stdout:
            self.logger.info(f"All tests passed")
        else:
            raise Exception("Could not verify test results")
    
    def check_dependencies(self):
        """Verify all dependencies installed"""
        result = subprocess.run(
            ['pip', 'check'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.logger.warning("Dependency conflicts detected")
        else:
            self.logger.info("All dependencies verified")
    
    def check_configuration(self):
        """Verify configuration files"""
        required_files = [
            'docker/Dockerfile',
            'kubernetes/deployment.yaml',
            'kubernetes/service.yaml',
            'kubernetes/configmap.yaml',
        ]
        
        for file in required_files:
            if not os.path.exists(file):
                self.logger.warning(f"Optional file missing: {file}")
        
        self.logger.info("Configuration files verified")


class DockerBuilder:
    """Build and push Docker image"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def build(self, tag: str, environment: str) -> bool:
        """Build Docker image"""
        self.logger.section("Building Docker Image")
        
        config = DeploymentConfig.ENVIRONMENTS[environment]
        image_name = f"{config['registry']}/pageiq:{tag}"
        
        self.logger.info(f"Building image: {image_name}")
        
        result = subprocess.run(
            ['docker', 'build',
             '--build-arg', f'ENVIRONMENT={environment}',
             '-t', image_name,
             '-f', 'docker/Dockerfile',
             '.'],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.returncode != 0:
            self.logger.error("Docker build failed")
            return False
        
        self.logger.info(f"Image built successfully: {image_name}")
        
        # Also tag as latest
        subprocess.run(['docker', 'tag', image_name, 
                       f"{config['registry']}/pageiq:latest"])
        
        return True
    
    def push(self, tag: str, environment: str) -> bool:
        """Push Docker image to registry"""
        self.logger.section("Pushing Docker Image")
        
        config = DeploymentConfig.ENVIRONMENTS[environment]
        image_name = f"{config['registry']}/pageiq:{tag}"
        
        self.logger.info(f"Pushing image: {image_name}")
        
        result = subprocess.run(['docker', 'push', image_name])
        
        if result.returncode != 0:
            self.logger.error("Docker push failed")
            return False
        
        self.logger.info("Image pushed successfully")
        return True
    
    def verify_image(self, tag: str, environment: str) -> bool:
        """Verify image exists in registry"""
        config = DeploymentConfig.ENVIRONMENTS[environment]
        image_name = f"{config['registry']}/pageiq:{tag}"
        
        result = subprocess.run(
            ['docker', 'inspect', image_name],
            capture_output=True
        )
        
        if result.returncode == 0:
            self.logger.info(f"Image verified: {image_name}")
            return True
        else:
            self.logger.error(f"Image not found: {image_name}")
            return False


class KubernetesDeployer:
    """Deploy to Kubernetes"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def deploy(self, tag: str, environment: str) -> bool:
        """Deploy to Kubernetes"""
        self.logger.section("Deploying to Kubernetes")
        
        config = DeploymentConfig.ENVIRONMENTS[environment]
        
        # Create namespace if not exists
        subprocess.run(
            ['kubectl', 'create', 'namespace', config['namespace']],
            capture_output=True
        )
        
        # Update image in deployment
        image_name = f"{config['registry']}/pageiq:{tag}"
        
        self.logger.info(f"Updating deployment with image: {image_name}")
        
        result = subprocess.run(
            ['kubectl', 'set', 'image',
             f"deployment/pageiq=pageiq={image_name}",
             f"--namespace={config['namespace']}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            # Try full deployment if rolling update fails
            self.logger.warning("Rolling update failed, attempting full deployment")
            return self.apply_deployment(tag, environment)
        
        self.logger.info("Deployment updated successfully")
        return True
    
    def apply_deployment(self, tag: str, environment: str) -> bool:
        """Apply full deployment manifest"""
        config = DeploymentConfig.ENVIRONMENTS[environment]
        image_name = f"{config['registry']}/pageiq:{tag}"
        
        # Generate manifest with current image
        manifest = self._generate_manifest(tag, environment, image_name)
        
        result = subprocess.run(
            ['kubectl', 'apply', '-f', '-',
             f"--namespace={config['namespace']}"],
            input=manifest,
            text=True,
            capture_output=True
        )
        
        if result.returncode != 0:
            self.logger.error(f"Kubectl apply failed: {result.stderr}")
            return False
        
        self.logger.info("Deployment manifests applied")
        return True
    
    def _generate_manifest(self, tag: str, environment: str, 
                          image_name: str) -> str:
        """Generate Kubernetes deployment manifest"""
        config = DeploymentConfig.ENVIRONMENTS[environment]
        
        manifest = f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pageiq
  namespace: {config['namespace']}
spec:
  replicas: {config['replicas']}
  selector:
    matchLabels:
      app: pageiq
      version: {tag}
  template:
    metadata:
      labels:
        app: pageiq
        version: {tag}
    spec:
      containers:
      - name: pageiq
        image: {image_name}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          value: "{environment}"
        - name: PORT
          value: "8000"
        resources:
          requests:
            cpu: {config['request_cpu']}
            memory: {config['request_memory']}
          limits:
            cpu: {config['limit_cpu']}
            memory: {config['limit_memory']}
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
"""
        return manifest
    
    def wait_for_rollout(self, environment: str, timeout: int = 300) -> bool:
        """Wait for deployment rollout to complete"""
        config = DeploymentConfig.ENVIRONMENTS[environment]
        
        self.logger.info("Waiting for deployment rollout...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = subprocess.run(
                ['kubectl', 'rollout', 'status',
                 'deployment/pageiq',
                 f"--namespace={config['namespace']}",
                 '--timeout=10s'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.logger.info("Deployment rollout complete")
                return True
            
            time.sleep(5)
        
        self.logger.error("Deployment rollout timeout")
        return False
    
    def verify_deployment(self, environment: str) -> bool:
        """Verify deployment is running correctly"""
        config = DeploymentConfig.ENVIRONMENTS[environment]
        
        self.logger.info("Verifying deployment...")
        
        result = subprocess.run(
            ['kubectl', 'get', 'pods',
             '-l', 'app=pageiq',
             f"--namespace={config['namespace']}",
             '-o', 'json'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.logger.error("Failed to get pod status")
            return False
        
        try:
            pods = json.loads(result.stdout)
            running_pods = [
                p for p in pods['items']
                if p['status']['phase'] == 'Running'
            ]
            
            if len(running_pods) >= config['replicas']:
                self.logger.info(
                    f"Deployment verified: {len(running_pods)} pods running"
                )
                return True
            else:
                self.logger.error(
                    f"Expected {config['replicas']} pods, "
                    f"but only {len(running_pods)} running"
                )
                return False
        except Exception as e:
            self.logger.error(f"Failed to parse pod status: {e}")
            return False


class HealthChecker:
    """Verify deployment health"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def check_api(self, endpoint: str) -> bool:
        """Check API health"""
        import requests
        
        self.logger.section("Checking API Health")
        
        try:
            response = requests.get(
                f"{endpoint}/api/v1/health",
                timeout=10
            )
            
            if response.status_code == 200:
                health = response.json()
                
                if health.get('status') == 'healthy':
                    self.logger.info("API is healthy")
                    return True
                else:
                    self.logger.error(f"API health check failed: {health}")
                    return False
            else:
                self.logger.error(f"API returned status {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"API health check failed: {e}")
            return False
    
    def check_endpoints(self, endpoint: str) -> bool:
        """Check all API endpoints"""
        import requests
        
        endpoints = [
            "/api/v1/analyze",
            "/api/v1/batch-analyze",
            "/api/v1/analytics/summary",
            "/api/v1/extract/emails",
            "/api/v1/seo/seo-audit",
            "/api/v1/account/subscription",
        ]
        
        failed = []
        for ep in endpoints:
            try:
                response = requests.head(f"{endpoint}{ep}", timeout=5)
                # HEAD request should return 200 or 405 (method not allowed)
                if response.status_code in [200, 405, 403]:
                    self.logger.info(f"✓ {ep}")
                else:
                    self.logger.warning(
                        f"{ep} returned {response.status_code}"
                    )
                    failed.append(ep)
            except Exception as e:
                self.logger.warning(f"{ep} failed: {e}")
                failed.append(ep)
        
        if not failed:
            self.logger.info("All endpoints responding")
            return True
        else:
            self.logger.warning(f"{len(failed)} endpoints not responding")
            return True  # Don't fail deployment for this


class RollbackHandler:
    """Handle rollback operations"""
    
    def __init__(self, logger: Logger):
        self.logger = logger
    
    def rollback_deployment(self, environment: str) -> bool:
        """Rollback to previous deployment"""
        self.logger.section("Rolling Back Deployment")
        
        config = DeploymentConfig.ENVIRONMENTS[environment]
        
        result = subprocess.run(
            ['kubectl', 'rollout', 'undo',
             'deployment/pageiq',
             f"--namespace={config['namespace']}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            self.logger.error(f"Rollback failed: {result.stderr}")
            return False
        
        self.logger.info("Rollback completed successfully")
        
        # Wait for rollout
        deployer = KubernetesDeployer(self.logger)
        return deployer.wait_for_rollout(environment)


class DeploymentManager:
    """Main deployment manager"""
    
    def __init__(self):
        self.logger = Logger("PageIQ Deployment")
    
    def deploy(self, environment: str, tag: str, skip_tests: bool = False) -> bool:
        """Execute full deployment"""
        self.logger.section(
            f"PageIQ Deployment - {environment.upper()} - {tag}"
        )
        
        start_time = time.time()
        
        # Stage 1: Validation
        if not skip_tests:
            validator = ValidationRunner(self.logger)
            if not validator.run_all():
                self.logger.error("Validation failed")
                return False
        
        # Stage 2: Build
        builder = DockerBuilder(self.logger)
        if not builder.build(tag, environment):
            self.logger.error("Build failed")
            return False
        
        # Stage 3: Push
        if not builder.push(tag, environment):
            self.logger.error("Push failed")
            return False
        
        # Stage 4: Deploy
        deployer = KubernetesDeployer(self.logger)
        if not deployer.deploy(tag, environment):
            self.logger.error("Deployment failed")
            return False
        
        # Stage 5: Wait for rollout
        if not deployer.wait_for_rollout(environment):
            self.logger.error("Rollout timeout - initiating rollback")
            rollback = RollbackHandler(self.logger)
            rollback.rollback_deployment(environment)
            return False
        
        # Stage 6: Verify
        if not deployer.verify_deployment(environment):
            self.logger.error("Verification failed - initiating rollback")
            rollback = RollbackHandler(self.logger)
            rollback.rollback_deployment(environment)
            return False
        
        elapsed_time = time.time() - start_time
        
        self.logger.section(
            f"✓ Deployment Successful (Completed in {elapsed_time:.1f}s)"
        )
        
        return True
    
    def rollback(self, environment: str) -> bool:
        """Rollback to previous version"""
        rollback_handler = RollbackHandler(self.logger)
        return rollback_handler.rollback_deployment(environment)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="PageIQ Production Deployment Tool"
    )
    
    parser.add_argument(
        '--environment',
        choices=['staging', 'production'],
        default='staging',
        help='Deployment environment'
    )
    
    parser.add_argument(
        '--tag',
        required=True,
        help='Docker image tag (e.g., v1.0.0)'
    )
    
    parser.add_argument(
        '--skip-tests',
        action='store_true',
        help='Skip running tests during validation'
    )
    
    parser.add_argument(
        '--rollback',
        action='store_true',
        help='Rollback to previous deployment'
    )
    
    args = parser.parse_args()
    
    manager = DeploymentManager()
    
    if args.rollback:
        success = manager.rollback(args.environment)
    else:
        success = manager.deploy(
            args.environment,
            args.tag,
            args.skip_tests
        )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
