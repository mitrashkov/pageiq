import logging
import re
from typing import List, Set

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class TechStackDetector:
    """Service for detecting website technology stack."""

    def __init__(self):
        # Technology fingerprints (simplified Wappalyzer-like detection)
        self.technologies = {
            'React': {
                'html': [r'react', r'data-react'],
                'scripts': [r'react\.js', r'react-dom', r'/static/js/'],
                'headers': ['x-powered-by']
            },
            'Vue.js': {
                'html': [r'vue', r'v-'],
                'scripts': [r'vue\.js', r'vue\.min\.js'],
            },
            'Angular': {
                'html': [r'ng-', r'angular'],
                'scripts': [r'angular\.js', r'angular\.min\.js'],
            },
            'Next.js': {
                'html': [r'next/head', r'__next'],
                'scripts': [r'/_next/'],
            },
            'Nuxt.js': {
                'html': [r'nuxt', r'__nuxt'],
                'scripts': [r'/_nuxt/'],
            },
            'WordPress': {
                'html': [r'wp-content', r'wp-includes', r'wordpress'],
                'headers': ['x-powered-by'],
                'meta': ['generator']
            },
            'Shopify': {
                'html': [r'shopify', r'myshopify\.com'],
                'scripts': [r'shopify'],
            },
            'Squarespace': {
                'html': [r'squarespace', r'static\.squarespace'],
            },
            'Wix': {
                'html': [r'wix', r'wix\.com'],
            },
            'Bootstrap': {
                'html': [r'bootstrap', r'col-md-', r'container-fluid'],
                'css': [r'bootstrap\.css', r'bootstrap\.min\.css'],
            },
            'Tailwind CSS': {
                'html': [r'tailwind', r'flex', r'grid'],
                'css': [r'tailwind'],
            },
            'jQuery': {
                'scripts': [r'jquery', r'jquery\.min\.js'],
            },
            'Node.js': {
                'headers': ['x-powered-by'],
            },
            'PHP': {
                'headers': ['x-powered-by', 'server'],
                'html': [r'php'],
            },
            'Python': {
                'headers': ['server'],
            },
            'Ruby': {
                'headers': ['server', 'x-powered-by'],
            },
            'Go': {
                'headers': ['server'],
            },
            'Apache': {
                'headers': ['server'],
            },
            'Nginx': {
                'headers': ['server'],
            },
            'Cloudflare': {
                'headers': ['server', 'cf-ray'],
            },
            'HubSpot': {
                'html': [r'hubspot', r'hs-script'],
                'scripts': [r'js\.hs-scripts\.com', r'js\.hsadspixel\.net', r'js\.hs-analytics\.net'],
            },
            'Salesforce': {
                'html': [r'salesforce', r'sf-'],
                'scripts': [r'force\.com'],
            },
            'Intercom': {
                'scripts': [r'widget\.intercom\.io'],
            },
            'Zendesk': {
                'scripts': [r'static\.zdassets\.com', r'zendesk\.com'],
            },
            'Stripe': {
                'scripts': [r'js\.stripe\.com'],
            },
            'Google Analytics': {
                'scripts': [r'google-analytics\.com', r'googletagmanager\.com/gtag/js', r'ua-'],
                'html': [r'gtag'],
            },
            'Facebook Pixel': {
                'scripts': [r'connect\.facebook\.net/en_US/fbevents\.js'],
                'html': [r'fbq'],
            },
            'Hotjar': {
                'scripts': [r'static\.hotjar\.com'],
            },
            'Mailchimp': {
                'html': [r'mailchimp'],
                'scripts': [r'chimpstatic\.com'],
            },
            'Segment': {
                'scripts': [r'cdn\.segment\.com'],
            },
            'Mixpanel': {
                'scripts': [r'cdn\.mxpnl\.com'],
            },
            'Sentry': {
                'scripts': [r'browser\.sentry-cdn\.com'],
            },
            'AWS': {
                'headers': ['server', 'x-amz-'],
            },
            'Google Cloud': {
                'headers': ['server', 'x-goog-'],
            },
            'Microsoft Azure': {
                'headers': ['server', 'x-azure-'],
            },
        }

    def detect_technologies(
        self,
        soup: BeautifulSoup,
        html_content: str,
        headers: dict = None
    ) -> List[str]:
        """
        Detect technologies used on a website.

        Args:
            soup: BeautifulSoup object
            html_content: Raw HTML content
            headers: HTTP response headers

        Returns:
            List of detected technologies
        """
        detected: Set[str] = set()
        headers = headers or {}

        # Convert headers to lowercase for matching
        headers_lower = {str(k).lower(): str(v).lower() for k, v in headers.items()}

        for tech_name, fingerprints in self.technologies.items():
            confidence = 0

            # Check HTML content
            if 'html' in fingerprints:
                for pattern in fingerprints['html']:
                    if re.search(pattern, html_content, re.IGNORECASE):
                        confidence += 1

            # Check script tags
            if 'scripts' in fingerprints:
                scripts = soup.find_all('script')
                for script in scripts:
                    src = script.get('src', '')
                    # Check src attribute
                    for pattern in fingerprints['scripts']:
                        if src and re.search(pattern, src, re.IGNORECASE):
                            confidence += 2
                    
                    # Check inline script content if small enough
                    if not src and script.string:
                        content = script.string
                        if len(content) < 1000: # Only check small inline scripts for performance
                            for pattern in fingerprints['scripts']:
                                if re.search(pattern, content, re.IGNORECASE):
                                    confidence += 1

            # Check CSS links
            if 'css' in fingerprints:
                links = soup.find_all('link', {'rel': 'stylesheet', 'href': True})
                for link in links:
                    href = link.get('href', '')
                    for pattern in fingerprints['css']:
                        if re.search(pattern, href, re.IGNORECASE):
                            confidence += 1

            # Check meta tags
            if 'meta' in fingerprints:
                for meta_name in fingerprints['meta']:
                    meta = soup.find('meta', {'name': meta_name})
                    if meta and meta.get('content'):
                        content = meta['content'].lower()
                        for pattern in fingerprints['meta']:
                            if re.search(pattern, content, re.IGNORECASE):
                                confidence += 2

            # Check headers
            if 'headers' in fingerprints:
                for header_name in fingerprints['headers']:
                    if header_name in headers_lower:
                        header_value = headers_lower[header_name]
                        # Technology-specific header checks
                        if tech_name == 'WordPress' and 'wordpress' in header_value:
                            confidence += 3
                        elif tech_name == 'Node.js' and 'node' in header_value:
                            confidence += 3
                        elif tech_name == 'PHP' and 'php' in header_value:
                            confidence += 3
                        elif tech_name == 'Apache' and 'apache' in header_value:
                            confidence += 2
                        elif tech_name == 'Nginx' and 'nginx' in header_value:
                            confidence += 2
                        elif tech_name == 'Cloudflare' and header_name == 'cf-ray':
                            confidence += 3
                        else:
                            confidence += 1

            # If we have enough confidence, add the technology
            if confidence >= 2:  # Require at least 2 matches
                detected.add(tech_name)

        # Sort and return
        return sorted(list(detected))

    def detect_web_languages(self, soup: BeautifulSoup, html_content: str) -> List[str]:
        """
        Detect foundational web languages present in a page.

        Returns:
            List of language names such as HTML, CSS, JavaScript.
        """
        languages: Set[str] = set()

        if html_content.strip():
            languages.add("HTML")

        has_stylesheet_link = bool(soup.find("link", {"rel": "stylesheet", "href": True}))
        has_style_tag = bool(soup.find("style"))
        has_inline_style = bool(soup.find(attrs={"style": True}))
        if has_stylesheet_link or has_style_tag or has_inline_style:
            languages.add("CSS")

        has_script_tag = bool(soup.find("script"))
        has_inline_event_handlers = bool(re.search(r"\son\w+\s*=", html_content, re.IGNORECASE))
        if has_script_tag or has_inline_event_handlers:
            languages.add("JavaScript")

        return sorted(list(languages))


# Global instance
tech_detector = TechStackDetector()
