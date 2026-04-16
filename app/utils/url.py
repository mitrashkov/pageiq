import re
from typing import Optional
from urllib.parse import urljoin, urlparse, unquote

import tldextract


def validate_url(url: str) -> bool:
    """
    Validate if a string is a valid URL.

    Args:
        url: The URL string to validate

    Returns:
        bool: True if valid URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # Basic regex for URL validation
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments, query params, and ensuring proper formatting.

    Args:
        url: The URL to normalize

    Returns:
        str: Normalized URL
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL: {url}")

    parsed = urlparse(url)

    # Reconstruct URL without fragment and query
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Remove trailing slash unless it's the root path
    if len(normalized) > len(f"{parsed.scheme}://{parsed.netloc}/"):
        normalized = normalized.rstrip('/')

    return normalized


def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.

    Args:
        url: The URL to extract domain from

    Returns:
        str: Domain name
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL: {url}")

    extracted = tldextract.extract(url)
    return f"{extracted.domain}.{extracted.suffix}"


def get_base_url(url: str) -> str:
    """
    Get the base URL (scheme + domain).

    Args:
        url: The URL to get base from

    Returns:
        str: Base URL
    """
    if not validate_url(url):
        raise ValueError(f"Invalid URL: {url}")

    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def resolve_url(base_url: str, relative_url: str) -> str:
    """
    Resolve a relative URL against a base URL.

    Args:
        base_url: The base URL
        relative_url: The relative URL to resolve

    Returns:
        str: Absolute URL
    """
    return urljoin(base_url, relative_url)


def extract_tld(url: str) -> Optional[str]:
    """
    Extract the top-level domain from a URL.

    Args:
        url: The URL to extract TLD from

    Returns:
        Optional[str]: TLD or None if invalid
    """
    try:
        extracted = tldextract.extract(url)
        return extracted.suffix or None
    except:
        return None


def is_valid_domain(domain: str) -> bool:
    """
    Check if a domain string is valid.

    Args:
        domain: Domain to validate

    Returns:
        bool: True if valid domain
    """
    try:
        extracted = tldextract.extract(domain)
        return bool(extracted.domain and extracted.suffix)
    except:
        return False