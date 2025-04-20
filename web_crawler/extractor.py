"""
Content extraction utilities for web crawling.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger("web_crawler.extractor")


def extract_text_content(soup: BeautifulSoup) -> str:
    """Extract main text content from the page."""
    main_content = soup.find('main') or soup.find('article') or soup.find('div', id='content') or soup.find('div', class_='content')
    
    if main_content and isinstance(main_content, Tag):
        paragraphs = main_content.find_all('p')
    else:
        paragraphs = soup.find_all('p')
    
    text_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
    return text_content


def find_pagination_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find pagination links on the page."""
    pagination_links = set()
    
    pagination_elements = [
        soup.find('div', class_=re.compile(r'pag(ing|ination)')),
        soup.find('nav', class_=re.compile(r'pag(ing|ination)')),
        soup.find('ul', class_=re.compile(r'pag(ing|ination)'))
    ]
    
    for pagination in [p for p in pagination_elements if p]:
        if isinstance(pagination, Tag):
            for a in pagination.find_all('a', href=True):
                if not isinstance(a, Tag):
                    continue
                href = str(a.get('href', ''))
                if href and not href.startswith('#'):
                    full_url = urljoin(base_url, href)
                    pagination_links.add(full_url)
    
    if not pagination_links:
        for a in soup.find_all('a', href=True):
            if not isinstance(a, Tag):
                continue
            href = str(a.get('href', ''))
            text = a.get_text(strip=True).lower()
            
            if any(pattern in text for pattern in ['next', 'page', 'more', 'continue', 'forward']):
                if href and not href.startswith('#'):
                    full_url = urljoin(base_url, href)
                    pagination_links.add(full_url)
    
    return list(pagination_links)


def extract_links(soup: BeautifulSoup, base_url: str, same_domain_only: bool = True) -> List[Dict[str, Any]]:
    """Extract all links from the page with metadata."""
    links = []
    base_domain = urlparse(base_url).netloc
    
    for a in soup.find_all('a', href=True):
        if not isinstance(a, Tag):
            continue
            
        href = str(a.get('href', ''))
        
        if not href or href.startswith('#'):
            continue
            
        if href.startswith('/') or not urlparse(href).netloc:
            full_url = urljoin(base_url, href)
        else:
            full_url = href
            
        if not full_url.startswith(('http://', 'https://')):
            continue
            
        link_domain = urlparse(full_url).netloc
        is_internal = link_domain == base_domain
        
        if same_domain_only and not is_internal:
            continue
            
        link_info = {
            'url': full_url,
            'text': a.get_text(strip=True),
            'is_internal': is_internal
        }
        links.append(link_info)
        
    return links


def extract_page_data(soup: BeautifulSoup, url: str) -> Dict[str, Any]:
    """Extract structured data from a page."""
    from datetime import datetime
    
    result = {
        "url": url,
        "extraction_time": datetime.now().isoformat(),
        "domain": urlparse(url).netloc,
        "success": True
    }
    
    # Extract title
    result["title"] = soup.title.get_text(strip=True) if soup.title else ""
    
    # Extract main content
    text_content = extract_text_content(soup)
    result["text_content"] = text_content[:5000] + "..." if len(text_content) > 5000 else text_content
    result["text_length"] = len(text_content)
    
    # Extract metadata
    meta_tags = {}
    for meta in soup.find_all('meta'):
        if not isinstance(meta, Tag):
            continue
        name = meta.get('name', meta.get('property', ''))
        content = meta.get('content', '')
        if name and content:
            meta_tags[name] = content
    result["meta_tags"] = meta_tags
    
    # Extract headings
    headings = {}
    for level in range(1, 7):
        tag = f'h{level}'
        elements = soup.find_all(tag)
        if elements:
            headings[tag] = [h.get_text(strip=True) for h in elements]
    result["headings"] = headings
    
    # Extract links
    links = extract_links(soup, url)
    result["links"] = links
    result["link_count"] = len(links)
    
    # Extract images
    images = []
    for img in soup.find_all('img'):
        if not isinstance(img, Tag):
            continue
        src = img.get('src')
        if not src:
            continue
            
        src = str(src)
        if src.startswith('/') or not urlparse(src).netloc:
            full_url = urljoin(url, src)
        else:
            full_url = src
            
        image_info = {
            'url': full_url,
            'alt': img.get('alt', ''),
            'width': img.get('width', ''),
            'height': img.get('height', '')
        }
        images.append(image_info)
        
    result["images"] = images
    result["image_count"] = len(images)
    
    # Social media metadata
    og_tags = {}
    for og in soup.find_all('meta', property=re.compile(r'^og:')):
        if not isinstance(og, Tag):
            continue
        prop = og.get('property', '')
        content = og.get('content', '')
        if prop and content:
            og_tags[prop] = content
    result["opengraph"] = og_tags
    
    # Twitter card data
    twitter_tags = {}
    for tw in soup.find_all('meta', attrs={"name": re.compile(r'^twitter:')}):
        if not isinstance(tw, Tag):
            continue
        name = tw.get('name', '')
        content = tw.get('content', '')
        if name and content:
            twitter_tags[name] = content
    result["twitter_card"] = twitter_tags
    
    # Schema.org structured data
    schema_data = []
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            if isinstance(script, Tag):
                script_content = script.get_text()
                if script_content:
                    data = json.loads(script_content)
                    schema_data.append(data)
        except (json.JSONDecodeError, TypeError):
            pass
    result["structured_data"] = schema_data
    
    return result
