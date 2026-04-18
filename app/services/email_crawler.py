import asyncio
import logging
import re
from typing import List, Set, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
import tldextract

from app.services.fetcher import html_fetcher
from app.services.extractors import extract_emails
from app.services.robots_checker import robots_checker

logger = logging.getLogger(__name__)

class EmailCrawler:
    """Service for crawling a website to find email addresses across multiple pages."""

    def __init__(self, max_pages: int = 10, timeout: int = 30):
        self.max_pages = max_pages
        self.timeout = timeout
        self.visited_urls: Set[str] = set()
        self.emails: Set[str] = set()
        self.base_domain = ""

    async def crawl_website(self, start_url: str, max_pages: Optional[int] = None, use_browser: bool = False) -> List[str]:
        """
        Crawl a website starting from start_url and extract emails from all visited pages.
        Supports high-volume crawling (500+ pages) with concurrency.
        """
        if max_pages:
            self.max_pages = max_pages

        self.visited_urls = set()
        self.emails = set()
        
        parsed_start = urlparse(start_url)
        if not parsed_start.scheme or not parsed_start.netloc:
            logger.error(f"Invalid start URL: {start_url}")
            return []

        ext = tldextract.extract(start_url)
        self.base_domain = f"{ext.domain}.{ext.suffix}"
        
        queue = [start_url]
        pages_crawled = 0
        
        # Concurrency control for MEGA/ULTRA plans
        concurrency_limit = 5 if self.max_pages > 50 else 2
        semaphore = asyncio.Semaphore(concurrency_limit)

        async def process_url(url: str):
            nonlocal pages_crawled
            if pages_crawled >= self.max_pages:
                return []

            async with semaphore:
                if url in self.visited_urls:
                    return []
                
                if not robots_checker.can_fetch(url):
                    return []

                self.visited_urls.add(url)
                try:
                    # Fetch with a slightly longer timeout for deep crawls
                    html, error, _ = await html_fetcher.fetch_html_async(url, timeout=self.timeout, use_browser=use_browser)
                    if error or not html:
                        return []

                    soup = html_fetcher.parse_html(html)
                    if soup is None:
                        return []

                    page_emails = extract_emails(soup)
                    for email in page_emails:
                        self.emails.add(email.lower())

                    pages_crawled += 1
                    
                    # Return new internal links found on this page
                    return self._extract_internal_links(soup, url)
                except Exception as e:
                    logger.error(f"Error crawling {url}: {str(e)}")
                    return []

        # Start with the initial URL
        while queue and pages_crawled < self.max_pages:
            # Take a batch of URLs to process concurrently
            batch_size = concurrency_limit
            current_batch = []
            while queue and len(current_batch) < batch_size:
                u = queue.pop(0)
                if u not in self.visited_urls:
                    current_batch.append(u)
            
            if not current_batch:
                break

            # Process batch concurrently
            tasks = [process_url(u) for u in current_batch]
            results = await asyncio.gather(*tasks)
            
            # Collect new links and prioritize them
            new_discovered_links = []
            for links in results:
                new_discovered_links.extend(links)
            
            # Prioritize contact-like pages in the queue
            contact_patterns = [r'contact', r'about', r'team', r'staff', r'support', r'legal', r'privacy', r'info']
            priority_links = []
            other_links = []
            
            for link in set(new_discovered_links):
                if link in self.visited_urls or link in queue:
                    continue
                
                is_priority = any(re.search(pattern, link, re.I) for pattern in contact_patterns)
                if is_priority:
                    priority_links.append(link)
                else:
                    other_links.append(link)
            
            # Update queue: Priority first, then existing queue, then others
            queue = priority_links + queue + other_links
            
            # Log progress for deep crawls
            if pages_crawled % 10 == 0:
                logger.info(f"Progress: {pages_crawled}/{self.max_pages} pages crawled. Emails found: {len(self.emails)}")

        return sorted(list(self.emails))

    def _extract_internal_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract internal links from a page."""
        links = []
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(current_url, href)
            
            # Clean URL (remove fragments)
            full_url = full_url.split('#')[0].rstrip('/')
            
            if self._is_internal(full_url):
                links.append(full_url)
        
        return list(set(links))

    def _is_internal(self, url: str) -> bool:
        """Check if a URL belongs to the same base domain."""
        try:
            ext = tldextract.extract(url)
            domain = f"{ext.domain}.{ext.suffix}"
            return domain == self.base_domain
        except Exception:
            return False

# Global instance
email_crawler = EmailCrawler()
