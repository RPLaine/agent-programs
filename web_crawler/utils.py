"""
Utility functions for web crawling.
"""

import os
import re
import time
import random
import logging
from typing import Set, List, Dict, Any, Optional
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse, urlencode
from datetime import datetime

logger = logging.getLogger("web_crawler.utils")


def setup_output_directory(output_dir: Optional[str] = None) -> str:
    """Set up and ensure the output directory exists."""
    if not output_dir:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "output")
    
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def random_wait(min_time=1, max_time=3) -> None:
    """Introduce random wait time to mimic human behavior."""
    time.sleep(random.uniform(min_time, max_time))


def generate_filename(url: str) -> str:
    """Generate a standardized filename for saving crawl data."""
    parsed = urlparse(url)
    domain = parsed.netloc.replace('.', '_')
    path = parsed.path.replace('/', '_')
    if not path:
        path = '_index'
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{domain}{path}_{timestamp}.json"


def is_allowed_by_robots(driver, url: str, robots_disallowed: Set[str], respect_robots: bool = True) -> bool:
    """Check if a URL is allowed by robots.txt."""
    if not respect_robots:
        return True
    
    domain = urlparse(url).netloc
    
    if domain in robots_disallowed:
        return False
    
    try:
        if driver is None:
            logger.error("Failed to initialize WebDriver")
            return True  # Default to allowing access if we can't check robots.txt
            
        robots_url = urljoin(url, "/robots.txt")
        driver.get(robots_url)
        robots_text = driver.page_source
        
        path = urlparse(url).path
        
        disallow_patterns = re.findall(r"Disallow:\s*(.+)", robots_text)
        for pattern in disallow_patterns:
            pattern = pattern.strip()
            if pattern and (path.startswith(pattern) or pattern == '/'):
                robots_disallowed.add(domain)
                return False
        
        return True
    except Exception as e:
        logger.error(f"Error checking robots.txt: {e}")
        return True


def can_fetch(url: str, visited_urls: Set[str], robots_disallowed: Set[str], driver, respect_robots: bool) -> bool:
    """Determine if a URL can be fetched based on various rules."""
    if url in visited_urls:
        return False
    
    if not url.startswith(('http://', 'https://')):
        return False
    
    return is_allowed_by_robots(driver, url, robots_disallowed, respect_robots)


def should_follow_link(link_url: str, base_url: str, visited_urls: Set[str], 
                      robots_disallowed: Set[str], driver, same_domain_only: bool, 
                      respect_robots: bool) -> bool:
    """Determine if a link should be followed during crawling."""
    if not can_fetch(link_url, visited_urls, robots_disallowed, driver, respect_robots):
        return False
        
    base_domain = urlparse(base_url).netloc
    link_domain = urlparse(link_url).netloc
    
    if same_domain_only and link_domain != base_domain:
        return False
        
    return True


def detect_pagination_pattern(url: str, soup) -> Optional[str]:
    """Detect pagination pattern to find the next page."""
    from bs4 import BeautifulSoup
    
    current_page_num = None
    next_page_url = None
    
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Check for pagination in query parameters
    for param, values in query_params.items():
        if param.lower() in ['page', 'p', 'pg']:
            try:
                current_page_num = int(values[0])
                next_page_num = current_page_num + 1
                
                next_query = query_params.copy()
                next_query[param] = [str(next_page_num)]
                
                next_query_str = urlencode(next_query, doseq=True)
                next_parsed = parsed_url._replace(query=next_query_str)
                next_page_url = urlunparse(next_parsed)
                
                return next_page_url
            except (ValueError, IndexError):
                pass
    
    # Use helper function to find pagination links
    from .extractor import find_pagination_links
    pagination_links = find_pagination_links(soup, url)
    
    if pagination_links:
        for link in pagination_links:
            if re.search(r'[?&/](page|p|pg)[=/](\d+)', link):
                parsed_link = urlparse(link)
                link_params = parse_qs(parsed_link.query)
                
                for param, values in link_params.items():
                    if param.lower() in ['page', 'p', 'pg']:
                        try:
                            link_page_num = int(values[0])
                            if current_page_num is None or link_page_num > current_page_num:
                                next_page_url = link
                                current_page_num = link_page_num
                        except (ValueError, IndexError):
                            pass
    
    return next_page_url
