import json
import logging
import re
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup
from langdetect import detect
try:
    from langdetect.lang_detect_exception import LangDetectException as LangDetectError
except Exception:  # pragma: no cover
    LangDetectError = Exception  # type: ignore[assignment]
from rake_nltk import Rake

from app.utils.url import extract_tld, resolve_url

logger = logging.getLogger(__name__)


def extract_title(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the page title from HTML.

    Priority order:
    1. <title> tag
    2. Open Graph title
    3. First <h1> tag
    4. Twitter Card title
    5. First meaningful text in <body>
    """
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
        title = _clean_title(title)
        if title:
            return title

    og_title = soup.find("meta", {"property": "og:title"})
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()
        title = _clean_title(title)
        return title or None

    h1_tag = soup.find("h1")
    if h1_tag:
        title = h1_tag.get_text(strip=True)
        title = _clean_title(title)
        return title or None

    twitter_title = soup.find("meta", {"name": "twitter:title"})
    if twitter_title and twitter_title.get("content"):
        title = twitter_title["content"].strip()
        title = _clean_title(title)
        return title or None

    body = soup.find("body")
    if body:
        text = body.get_text(separator=" ", strip=True)
        if text:
            return _clean_title(text[:100]) or None

    return None


def extract_favicon(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Extract favicon URL from HTML.

    Priority order:
    1. Link rel="icon"
    2. Link rel="shortcut icon"
    3. Link rel="apple-touch-icon"
    4. Default /favicon.ico

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative paths

    Returns:
        Favicon URL or None
    """
    # Try various favicon link types
    favicon_selectors = [
        ('link', {'rel': 'icon'}),
        ('link', {'rel': 'shortcut icon'}),
        ('link', {'rel': 'apple-touch-icon'}),
        ('link', {'rel': 'apple-touch-icon-precomposed'}),
    ]

    for selector, attrs in favicon_selectors:
        link = soup.find(selector, attrs)
        if link and link.get('href'):
            favicon_url = link['href'].strip()
            if favicon_url:
                return resolve_url(base_url, favicon_url)

    # Default favicon location
    return resolve_url(base_url, '/favicon.ico')


def extract_logo(soup: BeautifulSoup, base_url: str) -> Optional[str]:
    """
    Extract logo URL from HTML.

    Priority order:
    1. Open Graph image
    2. Twitter Card image
    3. Logo classes/ids (common patterns)
    4. Header images
    5. Schema.org logo

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative paths

    Returns:
        Logo URL or None
    """
    # Try Open Graph image
    og_image = soup.find('meta', {'property': 'og:image'})
    if og_image and og_image.get('content'):
        return resolve_url(base_url, og_image['content'])

    # Try Twitter Card image
    twitter_image = soup.find('meta', {'name': 'twitter:image'})
    if twitter_image and twitter_image.get('content'):
        return resolve_url(base_url, twitter_image['content'])

    # Try Schema.org logo
    schema_logo = soup.find(attrs={'itemprop': 'logo'})
    if schema_logo and schema_logo.get('src'):
        return resolve_url(base_url, schema_logo['src'])

    # Try common logo selectors
    logo_selectors = [
        ('img', {'class': re.compile(r'logo', re.I)}),
        ('img', {'id': re.compile(r'logo', re.I)}),
        ('img', {'alt': re.compile(r'logo', re.I)}),
        ('a', {'class': re.compile(r'logo', re.I)}),
        ('div', {'class': re.compile(r'logo', re.I)}),
    ]

    for selector, attrs in logo_selectors:
        elements = soup.find_all(selector, attrs)
        for element in elements:
            # For img tags, get src
            if selector == 'img' and element.get('src'):
                src = element['src']
                if _is_likely_logo(src, base_url):
                    return resolve_url(base_url, src)
            # For a/div tags, look for img children
            elif selector in ['a', 'div']:
                img = element.find('img')
                if img and img.get('src'):
                    src = img['src']
                    if _is_likely_logo(src, base_url):
                        return resolve_url(base_url, src)

    # Try header images
    header = soup.find(['header', 'nav'])
    if header:
        imgs = header.find_all('img')
        for img in imgs:
            if img.get('src'):
                src = img['src']
                if _is_likely_logo(src, base_url):
                    return resolve_url(base_url, src)

    return None


def _is_likely_logo(src: str, base_url: str) -> bool:
    """
    Check if an image src is likely to be a logo based on URL patterns.

    Args:
        src: Image source URL
        base_url: Base URL for context

    Returns:
        bool: True if likely a logo
    """
    if not src:
        return False

    src_lower = src.lower()

    # Skip tiny images, tracking pixels, etc.
    if any(x in src_lower for x in ['1x1', 'pixel', 'spacer', 'tracking', 'analytics']):
        return False

    # Look for logo-related keywords in URL
    logo_keywords = ['logo', 'brand', 'icon', 'mark', 'symbol', 'emblem']
    if any(keyword in src_lower for keyword in logo_keywords):
        return True

    # Check file size patterns (logos are often small files)
    # This is a basic heuristic - could be improved
    if 'logo' in src_lower or 'brand' in src_lower:
        return True

    return False


def extract_emails(soup: BeautifulSoup) -> List[str]:
    """
    Extract email addresses from HTML content.

    Looks in:
    - mailto: links
    - Text content matching email patterns
    - Contact forms
    - Footer areas

    Args:
        soup: BeautifulSoup object

    Returns:
        List of unique email addresses
    """
    emails = set()

    # Extract from mailto links
    mailto_links = soup.find_all('a', href=re.compile(r'mailto:', re.I))
    for link in mailto_links:
        href = link.get('href', '')
        email_match = re.search(r'mailto:([^?]+)', href, re.I)
        if email_match:
            email = email_match.group(1).strip()
            if _validate_email(email):
                emails.add(email.lower())

    # Extract from text content
    text_content = soup.get_text()
    # Also search in the raw HTML string as emails are often in scripts, JSON-LD, or data attributes
    raw_html = str(soup)
    
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    # Combine search results from text and raw HTML
    found_emails = re.findall(email_pattern, text_content, re.IGNORECASE)
    found_emails_raw = re.findall(email_pattern, raw_html, re.IGNORECASE)
    
    # Advanced: Look for obfuscated emails (e.g., info [at] example.com)
    obfuscated_pattern = r'\b[A-Za-z0-9._%+-]+\s*[\(\[]\s*at\s*[\)\]]\s*[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    found_obfuscated = re.findall(obfuscated_pattern, text_content, re.IGNORECASE)
    for email in found_obfuscated:
        # Clean the obfuscated email
        cleaned = re.sub(r'\s*[\(\[]\s*at\s*[\)\]]\s*', '@', email, flags=re.I)
        if _validate_email(cleaned):
            emails.add(cleaned.lower())

    for email in set(found_emails + found_emails_raw):
        if _validate_email(email):
            emails.add(email.lower())

    # Look in common contact sections
    contact_selectors = [
        ('div', {'class': re.compile(r'contact', re.I)}),
        ('section', {'class': re.compile(r'contact', re.I)}),
        ('footer', {}),
        ('address', {}),
    ]

    for selector, attrs in contact_selectors:
        elements = soup.find_all(selector, attrs)
        for element in elements:
            text = element.get_text()
            found_emails = re.findall(email_pattern, text, re.IGNORECASE)
            for email in found_emails:
                if _validate_email(email):
                    emails.add(email.lower())

    return list(emails)


def extract_phones(soup: BeautifulSoup) -> List[str]:
    """
    Extract phone numbers from HTML content.

    Looks in:
    - tel: links
    - Text content matching phone patterns
    - Contact sections
    - Schema.org contact info

    Args:
        soup: BeautifulSoup object

    Returns:
        List of unique phone numbers
    """
    phones = set()

    # Extract from tel: links
    tel_links = soup.find_all('a', href=re.compile(r'tel:', re.I))
    for link in tel_links:
        href = link.get('href', '')
        phone_match = re.search(r'tel:([^\?]+)', href, re.I)
        if phone_match:
            phone = phone_match.group(1).strip()
            normalized_phone = _normalize_phone(phone)
            if normalized_phone:
                phones.add(normalized_phone)

    # Extract from text content
    text_content = soup.get_text()

    # Multiple phone number patterns
    phone_patterns = [
        r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format: 123-456-7890
        r'\(\d{3}\)\s*\d{3}[-.]?\d{4}',    # (123) 456-7890
        r'\+\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4}',  # International
        r'\d{1,4}[-.\s]\d{1,4}[-.\s]\d{1,4}[-.\s]\d{1,4}',  # General pattern
    ]

    for pattern in phone_patterns:
        found_phones = re.findall(pattern, text_content)
        for phone in found_phones:
            normalized_phone = _normalize_phone(phone)
            if normalized_phone:
                phones.add(normalized_phone)

    # Look in Schema.org contact info
    schema_contacts = soup.find_all(attrs={'itemtype': re.compile(r'ContactPoint', re.I)})
    for contact in schema_contacts:
        tel_elem = contact.find(attrs={'itemprop': 'telephone'})
        if tel_elem:
            phone = tel_elem.get_text().strip()
            normalized_phone = _normalize_phone(phone)
            if normalized_phone:
                phones.add(normalized_phone)

    return list(phones)


def _validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid format
    """
    if not email or '@' not in email:
        return False

    # Basic pattern check
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(pattern, email, re.IGNORECASE))


def _normalize_phone(phone: str) -> Optional[str]:
    """
    Normalize phone number by removing formatting.

    Args:
        phone: Raw phone number

    Returns:
        Normalized phone or None if invalid
    """
    if not phone:
        return None

    # Remove all non-digit characters except + for international
    normalized = re.sub(r'[^\d+]', '', phone)

    # Basic validation - should have at least 7 digits
    digits_only = re.sub(r'[^\d]', '', normalized)
    if len(digits_only) < 7:
        return None

    return normalized


def extract_social_profiles(soup: BeautifulSoup, base_url: str) -> dict:
    """
    Extract social media profiles from HTML.

    Looks for:
    - Open Graph social profiles
    - Twitter Card
    - Schema.org social links
    - Link rel attributes
    - Common social media link patterns

    Args:
        soup: BeautifulSoup object
        base_url: Base URL for resolving relative links

    Returns:
        Dict mapping platform to profile URL
    """
    social_profiles = {}

    # Define social media platforms and their patterns
    platforms = {
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com', 'lnkd.in'],
        'instagram': ['instagram.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'github': ['github.com'],
        'tiktok': ['tiktok.com'],
        'pinterest': ['pinterest.com'],
        'snapchat': ['snapchat.com'],
        'discord': ['discord.gg'],
    }

    # Extract from Open Graph
    og_social_props = ['og:site_name']
    for prop in og_social_props:
        meta = soup.find('meta', {'property': prop})
        if meta and meta.get('content'):
            content = meta['content'].lower()
            for platform, domains in platforms.items():
                if any(domain in content for domain in domains):
                    # This is just site name, not a profile URL
                    break

    # Extract from Twitter Card
    twitter_site = soup.find('meta', {'name': 'twitter:site'})
    if twitter_site and twitter_site.get('content'):
        twitter_handle = twitter_site['content'].lstrip('@')
        social_profiles['twitter'] = f"https://twitter.com/{twitter_handle}"

    # Extract from Schema.org
    schema_social = soup.find_all(attrs={'itemprop': re.compile(r'sameAs|url', re.I)})
    for item in schema_social:
        url = item.get('href') or item.get('content')
        if url:
            platform = _identify_social_platform(url)
            if platform and platform not in social_profiles:
                social_profiles[platform] = url

    # Extract from link tags
    link_tags = soup.find_all('link', rel=re.compile(r'me|author', re.I))
    for link in link_tags:
        href = link.get('href')
        if href:
            resolved_url = resolve_url(base_url, href)
            platform = _identify_social_platform(resolved_url)
            if platform and platform not in social_profiles:
                social_profiles[platform] = resolved_url

    # Extract from regular links
    all_links = soup.find_all('a', href=True)
    for link in all_links:
        href = link.get('href')
        if href and ('social' in href.lower() or any(platform in href.lower() for platform in platforms.keys())):
            resolved_url = resolve_url(base_url, href)
            platform = _identify_social_platform(resolved_url)
            if platform and platform not in social_profiles:
                social_profiles[platform] = resolved_url

    # Look for social media icons/links in common containers
    social_containers = soup.find_all(['div', 'ul', 'nav'], class_=re.compile(r'social|share|follow', re.I))
    for container in social_containers:
        links = container.find_all('a', href=True)
        for link in links:
            href = link.get('href')
            resolved_url = resolve_url(base_url, href)
            platform = _identify_social_platform(resolved_url)
            if platform and platform not in social_profiles:
                social_profiles[platform] = resolved_url

    return social_profiles


def _identify_social_platform(url: str) -> Optional[str]:
    """
    Identify social media platform from URL.

    Args:
        url: URL to check

    Returns:
        Platform name or None
    """
    if not url:
        return None

    url_lower = url.lower()

    platform_patterns = {
        'facebook': ['facebook.com', 'fb.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com', 'lnkd.in'],
        'instagram': ['instagram.com'],
        'youtube': ['youtube.com', 'youtu.be'],
        'github': ['github.com'],
        'tiktok': ['tiktok.com'],
        'pinterest': ['pinterest.com'],
        'snapchat': ['snapchat.com'],
        'discord': ['discord.gg'],
        'reddit': ['reddit.com'],
        'medium': ['medium.com'],
        'behance': ['behance.net'],
        'dribbble': ['dribbble.com'],
    }

    for platform, domains in platform_patterns.items():
        if any(domain in url_lower for domain in domains):
            return platform

    return None


def detect_language(soup: BeautifulSoup) -> Optional[str]:
    """
    Detect the primary language of the webpage content.

    Uses langdetect library on page text content.

    Args:
        soup: BeautifulSoup object

    Returns:
        ISO 639-1 language code or None
    """
    try:
        # Get text content from body
        body = soup.find('body')
        if not body:
            return None

        text_content = body.get_text(separator=' ', strip=True)

        # Need some text for detection (tests use short content)
        if len(text_content) < 20:
            return None

        # Detect language
        lang_code = detect(text_content)

        # Map to ISO 639-1 if needed (langdetect already returns ISO 639-1)
        return lang_code

    except LangDetectError:
        logger.warning("Language detection failed")
        return None
    except Exception as e:
        logger.error(f"Error in language detection: {str(e)}")
        return None


def detect_country(url: str, soup: BeautifulSoup) -> Optional[str]:
    """
    Detect the country associated with the website.

    Uses TLD mapping and content signals.

    Args:
        url: Website URL
        soup: BeautifulSoup object

    Returns:
        ISO 3166-1 alpha-2 country code or None
    """
    # TLD to country mapping (common ones)
    tld_country_map = {
        'us': 'US', 'uk': 'GB', 'de': 'DE', 'fr': 'FR', 'it': 'IT', 'es': 'ES',
        'ca': 'CA', 'au': 'AU', 'jp': 'JP', 'cn': 'CN', 'in': 'IN', 'br': 'BR',
        'mx': 'MX', 'nl': 'NL', 'se': 'SE', 'no': 'NO', 'fi': 'FI', 'dk': 'DK',
        'pl': 'PL', 'ru': 'RU', 'kr': 'KR', 'sg': 'SG', 'my': 'MY', 'th': 'TH',
        'id': 'ID', 'vn': 'VN', 'ph': 'PH', 'tr': 'TR', 'za': 'ZA', 'eg': 'EG',
        'ng': 'NG', 'ke': 'KE', 'ma': 'MA', 'tn': 'TN', 'il': 'IL', 'sa': 'SA',
        'ae': 'AE', 'qa': 'QA', 'kw': 'KW', 'bh': 'BH', 'om': 'OM', 'jo': 'JO',
        'lb': 'LB', 'sy': 'SY', 'iq': 'IQ', 'ir': 'IR', 'pk': 'PK', 'bd': 'BD',
        'lk': 'LK', 'np': 'NP', 'mm': 'MM', 'kh': 'KH', 'la': 'LA', 'vn': 'VN',
        'tw': 'TW', 'hk': 'HK', 'mo': 'MO', 'nz': 'NZ', 'fj': 'FJ', 'ws': 'WS',
        'to': 'TO', 'sb': 'SB', 'vu': 'VU', 'nc': 'NC', 'pf': 'PF', 'ck': 'CK',
        'nu': 'NU', 'tk': 'TK', 'wf': 'WF', 'tv': 'TV', 'as': 'AS', 'gu': 'GU',
        'mp': 'MP', 'pr': 'PR', 'vi': 'VI', 'ar': 'AR', 'cl': 'CL', 'co': 'CO',
        'pe': 'PE', 've': 'VE', 'uy': 'UY', 'py': 'PY', 'bo': 'BO', 'ec': 'EC',
        'gy': 'GY', 'sr': 'SR', 'gf': 'GF', 'aw': 'AW', 'cw': 'CW', 'bq': 'BQ',
        'sx': 'SX', 'tt': 'TT', 'jm': 'JM', 'ht': 'HT', 'do': 'DO', 'cu': 'CU',
        'gt': 'GT', 'hn': 'HN', 'ni': 'NI', 'cr': 'CR', 'pa': 'PA', 'sv': 'SV',
        'bz': 'BZ', 'gl': 'GL', 'is': 'IS', 'pt': 'PT', 'ch': 'CH', 'at': 'AT',
        'cz': 'CZ', 'sk': 'SK', 'hu': 'HU', 'si': 'SI', 'hr': 'HR', 'ba': 'BA',
        'me': 'ME', 'mk': 'MK', 'al': 'AL', 'ro': 'RO', 'md': 'MD', 'bg': 'BG',
        'gr': 'GR', 'cy': 'CY', 'mt': 'MT', 'ee': 'EE', 'lv': 'LV', 'lt': 'LT',
        'by': 'BY', 'ua': 'UA', 'ge': 'GE', 'am': 'AM', 'az': 'AZ', 'tm': 'TM',
        'tj': 'TJ', 'kg': 'KG', 'uz': 'UZ', 'kz': 'KZ', 'mn': 'MN',
    }

    # Try TLD-based detection first
    tld = extract_tld(url)
    if tld and tld in tld_country_map:
        return tld_country_map[tld]

    # Try content-based detection
    text_content = soup.get_text().lower()

    # Look for country-specific patterns (basic heuristics)
    country_indicators = {
        'US': ['united states', 'america', 'usa', 'u.s.a'],
        'GB': ['united kingdom', 'uk', 'britain', 'great britain'],
        'DE': ['deutschland', 'germany'],
        'FR': ['france', 'république française'],
        'IT': ['italia', 'italy'],
        'ES': ['españa', 'spain'],
        'CA': ['canada'],
        'AU': ['australia'],
        'JP': ['japan', 'nippon'],
        'CN': ['china', '中華人民共和国'],
        'IN': ['india', 'bharat'],
        'BR': ['brasil', 'brazil'],
        'MX': ['méxico', 'mexico'],
    }

    for country_code, indicators in country_indicators.items():
        if any(indicator in text_content for indicator in indicators):
            return country_code

    return None


def extract_schema_org(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """
    Extract Schema.org structured data from HTML.

    Looks for JSON-LD and microdata formats.

    Args:
        soup: BeautifulSoup object

    Returns:
        Schema.org data or None
    """
    # Try JSON-LD first (most common and reliable)
    json_ld_data = _extract_json_ld(soup)
    if json_ld_data:
        return json_ld_data

    # Try microdata format
    microdata = _extract_microdata(soup)
    if microdata:
        return microdata

    return None


def _extract_json_ld(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """
    Extract JSON-LD structured data.

    Args:
        soup: BeautifulSoup object

    Returns:
        Parsed JSON-LD data or None
    """
    script_tags = soup.find_all('script', {'type': 'application/ld+json'})

    for script in script_tags:
        try:
            data = json.loads(script.string.strip())
            # Handle both single objects and arrays
            if isinstance(data, list):
                # Return the first Organization or WebSite object, or first item
                for item in data:
                    if isinstance(item, dict) and item.get('@type') in ['Organization', 'WebSite', 'LocalBusiness']:
                        return item
                return data[0] if data else None
            elif isinstance(data, dict):
                return data
        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse JSON-LD: {str(e)}")
            continue

    return None


def _extract_microdata(soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
    """
    Extract microdata structured data.

    Args:
        soup: BeautifulSoup object

    Returns:
        Parsed microdata or None
    """
    # Look for items with itemscope
    items = soup.find_all(attrs={'itemscope': True})

    for item in items:
        try:
            data = _parse_microdata_item(item)
            if data and data.get('@type') in ['Organization', 'WebSite', 'LocalBusiness']:
                return data
        except Exception as e:
            logger.warning(f"Failed to parse microdata: {str(e)}")
            continue

    return None


def _parse_microdata_item(element) -> Dict[str, Any]:
    """
    Parse a single microdata item.

    Args:
        element: BeautifulSoup element with itemscope

    Returns:
        Parsed microdata dictionary
    """
    data = {}

    # Get item type
    item_type = element.get('itemtype', '')
    if item_type:
        data['@type'] = item_type.split('/')[-1]  # Get last part of URL

    # Get item properties
    properties = element.find_all(attrs={'itemprop': True})

    for prop in properties:
        prop_name = prop.get('itemprop')
        prop_value = None

        # Check for nested itemscope
        if prop.get('itemscope'):
            prop_value = _parse_microdata_item(prop)
        elif prop.name == 'meta':
            prop_value = prop.get('content', '')
        elif prop.name in ['a', 'link']:
            prop_value = prop.get('href', '')
        elif prop.name == 'time':
            prop_value = prop.get('datetime', prop.get_text().strip())
        else:
            prop_value = prop.get_text().strip()

        if prop_name and prop_value:
            # Handle multiple properties with same name
            if prop_name in data:
                if not isinstance(data[prop_name], list):
                    data[prop_name] = [data[prop_name]]
                data[prop_name].append(prop_value)
            else:
                data[prop_name] = prop_value

    return data


def extract_open_graph(soup: BeautifulSoup) -> Optional[Dict[str, str]]:
    """
    Extract Open Graph meta tags from HTML.

    Args:
        soup: BeautifulSoup object

    Returns:
        Dictionary of Open Graph properties or None
    """
    og_tags = {}

    # Find all Open Graph meta tags
    meta_tags = soup.find_all('meta', {'property': re.compile(r'^og:')})

    for tag in meta_tags:
        prop = tag.get('property', '')
        content = tag.get('content', '').strip()

        if prop and content:
            # Remove 'og:' prefix for cleaner keys
            key = prop.replace('og:', '')
            og_tags[key] = content

    return og_tags if og_tags else None


def extract_keywords(soup: BeautifulSoup, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from webpage content using RAKE algorithm.

    Args:
        soup: BeautifulSoup object
        max_keywords: Maximum number of keywords to return

    Returns:
        List of keywords
    """
    try:
        # Get text content
        body = soup.find('body')
        if not body:
            return []

        text_content = body.get_text(separator=' ', strip=True)

        # Minimum text length for keyword extraction
        if len(text_content) < 200:
            return []

        # Initialize RAKE
        r = Rake()

        # Extract keywords
        r.extract_keywords_from_text(text_content)

        # Get ranked keywords
        ranked_keywords = r.get_ranked_phrases()

        # Filter and clean keywords
        keywords = []
        for keyword in ranked_keywords[:max_keywords]:
            # Clean keyword
            clean_keyword = keyword.strip().lower()

            # Skip very short or very long keywords
            if 3 <= len(clean_keyword) <= 50:
                # Skip if contains only stop words or numbers
                if not re.match(r'^(\d+|\W+)$', clean_keyword):
                    keywords.append(clean_keyword)

        return keywords[:max_keywords]

    except Exception as e:
        # RAKE can fail if NLTK resources aren't present; keep endpoint resilient.
        logger.error(f"Error in keyword extraction: {str(e)}")
        return []


def extract_description(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract the page description from HTML.

    Priority order:
    1. Meta description
    2. Open Graph description
    3. Twitter Card description
    4. First paragraph with substantial content

    Args:
        soup: BeautifulSoup object

    Returns:
        Description string or None
    """
    meta_desc = soup.find("meta", {"name": "description"})
    if meta_desc and meta_desc.get("content"):
        desc = meta_desc["content"].strip()
        return desc or None

    og_desc = soup.find("meta", {"property": "og:description"})
    if og_desc and og_desc.get("content"):
        desc = og_desc["content"].strip()
        return desc or None

    twitter_desc = soup.find("meta", {"name": "twitter:description"})
    if twitter_desc and twitter_desc.get("content"):
        desc = twitter_desc["content"].strip()
        return desc or None

    # Try first paragraph with meaningful content
    paragraphs = soup.find_all('p')
    for p in paragraphs:
        text = p.get_text().strip()
        if len(text) > 20:
            return text[:300].strip() + '...' if len(text) > 300 else text

    # Try article summary or excerpt
    summary_tags = soup.find_all(['div', 'span'], class_=re.compile(r'summary|excerpt|description', re.I))
    for tag in summary_tags:
        text = tag.get_text().strip()
        if len(text) > 50:
            return text[:300].strip() + '...' if len(text) > 300 else text

    return None


def _clean_title(title: str) -> str:
    """
    Clean up title text by removing duplicates and extra whitespace.

    Args:
        title: Raw title

    Returns:
        Cleaned title
    """
    if not title:
        return ""

    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()

    # Remove common separators and duplicates
    # e.g., "Page Title | Site Name | Site Name" -> "Page Title | Site Name"
    parts = [part.strip() for part in re.split(r'[|—–-]', title) if part.strip()]
    if len(parts) > 1:
        # Remove duplicate parts
        unique_parts = []
        for part in parts:
            if part.lower() not in [p.lower() for p in unique_parts]:
                unique_parts.append(part)
        title = ' | '.join(unique_parts)

    return title