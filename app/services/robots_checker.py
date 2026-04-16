import logging
import re
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests

from app.utils.url import get_base_url

logger = logging.getLogger(__name__)


class RobotsChecker:
    """Service for checking robots.txt compliance."""

    def __init__(self, user_agent: str = "PageIQ/1.0"):
        self.user_agent = user_agent
        self.cache = {}  # Simple in-memory cache

    def can_fetch(self, url: str) -> bool:
        """
        Check if we can fetch a URL according to robots.txt.

        Args:
            url: URL to check

        Returns:
            True if allowed to fetch, False otherwise
        """
        try:
            base_url = get_base_url(url)
            robots_url = urljoin(base_url, '/robots.txt')

            # Check cache first
            if robots_url in self.cache:
                rules = self.cache[robots_url]
            else:
                rules = self._fetch_robots_txt(robots_url)
                self.cache[robots_url] = rules

            if rules is None:
                # No robots.txt found, assume allowed
                return True

            return self._check_rules(rules, url)

        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {str(e)}")
            # On error, allow crawling (fail open)
            return True

    def _fetch_robots_txt(self, robots_url: str) -> Optional[dict]:
        """
        Fetch and parse robots.txt.

        Args:
            robots_url: URL of robots.txt

        Returns:
            Parsed rules or None if not found
        """
        try:
            response = requests.get(robots_url, timeout=10)
            if response.status_code == 200:
                return self._parse_robots_txt(response.text)
            else:
                return None
        except requests.RequestException:
            return None

    def _parse_robots_txt(self, content: str) -> dict:
        """
        Parse robots.txt content into rules.

        Args:
            content: Raw robots.txt content

        Returns:
            Dictionary of rules by user agent
        """
        rules = {}
        current_agent = None
        current_rules = []

        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Check for User-agent directive
            if line.lower().startswith('user-agent:'):
                # Save previous agent rules
                if current_agent and current_rules:
                    rules[current_agent] = current_rules

                current_agent = line.split(':', 1)[1].strip()
                current_rules = []
            # Check for Disallow directive
            elif line.lower().startswith('disallow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                current_rules.append(('disallow', path))
            # Check for Allow directive
            elif line.lower().startswith('allow:') and current_agent:
                path = line.split(':', 1)[1].strip()
                current_rules.append(('allow', path))

        # Save last agent rules
        if current_agent and current_rules:
            rules[current_agent] = current_rules

        return rules

    def _check_rules(self, rules: dict, url: str) -> bool:
        """
        Check if URL is allowed based on parsed rules.

        Args:
            rules: Parsed robots.txt rules
            url: URL to check

        Returns:
            True if allowed
        """
        # Get path from URL
        parsed_url = urlparse(url)
        path = parsed_url.path
        if parsed_url.query:
            path += '?' + parsed_url.query

        # Check rules for our user agent first, then wildcard
        agents_to_check = [self.user_agent, '*']

        for agent in agents_to_check:
            if agent in rules:
                agent_rules = rules[agent]

                # Check each rule
                allowed = True  # Default to allowed
                for rule_type, rule_path in agent_rules:
                    if self._path_matches(path, rule_path):
                        if rule_type == 'disallow':
                            allowed = False
                        elif rule_type == 'allow':
                            allowed = True

                return allowed

        # No specific rules found, default to allowed
        return True

    def _path_matches(self, url_path: str, rule_path: str) -> bool:
        """
        Check if a URL path matches a robots.txt rule path.

        Args:
            url_path: URL path to check
            rule_path: Rule path pattern

        Returns:
            True if matches
        """
        if not rule_path:
            return True  # Empty path matches everything

        # Simple pattern matching (robots.txt uses simple prefix matching)
        # More sophisticated implementations would handle wildcards
        if rule_path.endswith('*'):
            return url_path.startswith(rule_path[:-1])
        elif rule_path.endswith('/'):
            return url_path.startswith(rule_path) or url_path == rule_path[:-1]
        else:
            return url_path.startswith(rule_path)


# Global instance
robots_checker = RobotsChecker()