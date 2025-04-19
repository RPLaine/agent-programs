#!/usr/bin/env python3

import os
import json
import logging
import argparse
import re
from datetime import datetime
from urllib.parse import urlparse, urljoin, parse_qs, urlunparse, urlencode
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import random
import time
from collections import deque

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("webget.advanced_crawler")

class AdvancedCrawler:
    def __init__(self, headless=True, wait_time=10, max_pages=5, same_domain_only=True, 
                 depth_first=False, respect_robots=True):
        self.headless = headless
        self.wait_time = wait_time
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.depth_first = depth_first
        self.respect_robots = respect_robots
        self.driver = None
        self.visited_urls = set()
        self.robots_disallowed = set()
        self.user_agents = self._get_user_agents()
        self._initialize_driver()
        
    def _get_user_agents(self):
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
        ]
    
    def _initialize_driver(self):
        try:
            edge_options = EdgeOptions()
            
            if self.headless:
                edge_options.add_argument("--headless")
                
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-extensions")
            edge_options.add_argument("--disable-notifications")
            edge_options.add_argument("--disable-infobars")
            
            user_agent = random.choice(self.user_agents)
            edge_options.add_argument(f"--user-agent={user_agent}")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logger.info("Selenium Edge WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            raise
    
    def _wait_for_element(self, locator, timeout=None):
        timeout = timeout or self.wait_time
        try:
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                return None
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(locator)
            )
            return element
        except TimeoutException:
            logger.warning(f"Timeout waiting for element: {locator}")
            return None
        
    def _wait_for_elements(self, locator, timeout=None):
        timeout = timeout or self.wait_time
        try:
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                return []
            elements = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
            return elements
        except TimeoutException:
            logger.warning(f"Timeout waiting for elements: {locator}")
            return []
        
    def _wait_for_page_load(self):
        self._wait_for_element((By.TAG_NAME, "body"))
        
        try:
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                return
            WebDriverWait(self.driver, self.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("Timeout waiting for page to fully load")
        
        self._random_wait(1, 2)
    
    def _random_wait(self, min_time=1, max_time=3):
        time.sleep(random.uniform(min_time, max_time))
    
    def _is_allowed_by_robots(self, url):
        if not self.respect_robots:
            return True
        
        domain = urlparse(url).netloc
        
        if domain in self.robots_disallowed:
            return False
        
        try:
            if self.driver is None:
                self._initialize_driver()
                
            # Verify driver was successfully initialized
            if self.driver is None:
                logger.error("Failed to initialize WebDriver")
                return True  # Default to allowing access if we can't check robots.txt
                
            robots_url = urljoin(url, "/robots.txt")
            self.driver.get(robots_url)
            robots_text = self.driver.page_source
            
            path = urlparse(url).path
            
            disallow_patterns = re.findall(r"Disallow:\s*(.+)", robots_text)
            for pattern in disallow_patterns:
                pattern = pattern.strip()
                if pattern and (path.startswith(pattern) or pattern == '/'):
                    self.robots_disallowed.add(domain)
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error checking robots.txt: {e}")
            return True
    
    def _can_fetch(self, url):
        if url in self.visited_urls:
            return False
        
        if not url.startswith(('http://', 'https://')):
            return False
        
        return self._is_allowed_by_robots(url)
    
    def _extract_text_content(self, soup):
        main_content = soup.find('main') or soup.find('article') or soup.find('div', id='content') or soup.find('div', class_='content')
        
        if main_content:
            paragraphs = main_content.find_all('p')
        else:
            paragraphs = soup.find_all('p')
        
        text_content = ' '.join([p.get_text(strip=True) for p in paragraphs])
        return text_content
    
    def _find_pagination_links(self, soup, base_url):
        pagination_links = set()
        
        pagination_elements = [
            soup.find('div', class_=re.compile(r'pag(ing|ination)')),
            soup.find('nav', class_=re.compile(r'pag(ing|ination)')),
            soup.find('ul', class_=re.compile(r'pag(ing|ination)'))
        ]
        
        for pagination in [p for p in pagination_elements if p]:
            for a in pagination.find_all('a', href=True):
                href = a.get('href', '')
                if href and not href.startswith('#'):
                    full_url = urljoin(base_url, href)
                    pagination_links.add(full_url)
        
        if not pagination_links:
            for a in soup.find_all('a', href=True):
                href = a.get('href', '')
                text = a.get_text(strip=True).lower()
                
                if any(pattern in text for pattern in ['next', 'page', 'more', 'continue', 'forward']):
                    if href and not href.startswith('#'):
                        full_url = urljoin(base_url, href)
                        pagination_links.add(full_url)
        
        return list(pagination_links)
    
    def _detect_pagination_pattern(self, url, soup):
        current_page_num = None
        next_page_url = None
        
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        
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
        
        pagination_links = self._find_pagination_links(soup, url)
        if pagination_links:
            for link in pagination_links:
                # Check if it has sequence like page/2 or page=2
                if re.search(r'[?&/](page|p|pg)[=/](\d+)', link):
                    # Check if it's a "next" link
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
    
    def _extract_links(self, soup, base_url):
        links = []
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '')
            
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
            
            if self.same_domain_only and not is_internal:
                continue
                
            link_info = {
                'url': full_url,
                'text': a.get_text(strip=True),
                'is_internal': is_internal
            }
            links.append(link_info)
            
        return links
    
    def _should_follow_link(self, link_url, base_url):
        if not self._can_fetch(link_url):
            return False
            
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link_url).netloc
        
        if self.same_domain_only and link_domain != base_domain:
            return False
            
        return True
    
    def crawl(self, start_url, output_dir=None):
        if not self._can_fetch(start_url):
            return {"success": False, "error": "URL not allowed by robots.txt"}
        
        # Ensure driver is initialized
        if self.driver is None:
            try:
                self._initialize_driver()
            except Exception as e:
                return {"success": False, "error": f"Failed to initialize WebDriver: {str(e)}"}
        
        if not output_dir:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(script_dir, "crawl_output")
            
        os.makedirs(output_dir, exist_ok=True)
        
        url_queue = deque([(start_url, 0)])  # (url, depth)
        crawled_data = {}
        visited_count = 0
        start_domain = urlparse(start_url).netloc
        
        while url_queue and visited_count < self.max_pages:
            current_url, depth = url_queue.popleft()  # Get the next URL and its depth
            
            logger.info(f"Crawling {current_url} (depth: {depth}, count: {visited_count+1}/{self.max_pages})")
            
            try:
                if self.driver is None:
                    raise ValueError("WebDriver is not initialized or has been closed")
            except Exception as e:
                logger.error(f"Error initializing WebDriver: {e}")
                return {"success": False, "error": str(e)}
            
            try:
                self.driver.get(current_url)
                self._wait_for_page_load()
                
                html_content = self.driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                page_data = self._extract_page_data(soup, current_url)
                crawled_data[current_url] = page_data
                self.visited_urls.add(current_url)
                visited_count += 1
                
                # Save individual page data
                page_filename = self._generate_filename(current_url)
                page_path = os.path.join(output_dir, page_filename)
                with open(page_path, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                # Check for pagination
                next_page = self._detect_pagination_pattern(current_url, soup)
                if next_page and self._should_follow_link(next_page, current_url):
                    url_queue.appendleft((next_page, depth))  # Prioritize pagination
                
                # Extract and queue other links
                if depth < 2:  # Limit crawl depth
                    links = self._extract_links(soup, current_url)
                    for link_info in links:
                        link_url = link_info['url']
                        if self._should_follow_link(link_url, current_url):
                            url_queue.append((link_url, depth + 1))
                
                self._random_wait(2, 5)  # Be respectful with delays between requests
                
            except Exception as e:
                logger.error(f"Error crawling {current_url}: {e}")
                crawled_data[current_url] = {
                    "url": current_url,
                    "success": False,
                    "error": str(e)
                }
                self.visited_urls.add(current_url)
        
        # Save crawl summary
        summary_data = {
            "start_url": start_url,
            "pages_crawled": visited_count,
            "start_time": datetime.now().isoformat(),
            "crawl_results": list(crawled_data.values())
        }
        
        summary_filename = f"crawl_summary_{urlparse(start_url).netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path = os.path.join(output_dir, summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return summary_data
    
    def _generate_filename(self, url):
        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '_')
        path = parsed.path.replace('/', '_')
        if not path:
            path = '_index'
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{domain}{path}_{timestamp}.json"
    def _extract_page_data(self, soup, url):
        result = {
            "url": url,
            "extraction_time": datetime.now().isoformat(),
            "domain": urlparse(url).netloc,
            "success": True
        }
        
        result["title"] = soup.title.get_text(strip=True) if soup.title else ""
        
        # Extract main content
        text_content = self._extract_text_content(soup)
        result["text_content"] = text_content[:5000] + "..." if len(text_content) > 5000 else text_content
        result["text_length"] = len(text_content)
        
        # Extract metadata
        meta_tags = {}
        for meta in soup.find_all('meta'):
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
        links = self._extract_links(soup, url)
        result["links"] = links
        result["link_count"] = len(links)
        
        # Extract images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
                
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
        
        return result
    
    def take_screenshot(self, output_path):
        try:
            if self.driver is None:
                return False
                
            self.driver.save_screenshot(output_path)
            logger.info(f"Screenshot saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def close(self):
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed successfully")

def crawl_website(url, output=None, max_pages=5, headless=True, same_domain=True, depth_first=False):
    if output:
        output_dir = os.path.dirname(output) if '.' in os.path.basename(output) else output
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(script_dir, "crawl_output")
    
    os.makedirs(output_dir, exist_ok=True)
    
    crawler = AdvancedCrawler(
        headless=headless,
        max_pages=max_pages,
        same_domain_only=same_domain,
        depth_first=depth_first
    )
    
    try:
        result = crawler.crawl(url, output_dir)
        return result
    finally:
        crawler.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl websites with advanced features")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--output", "-o", help="Directory to save crawled data")
    parser.add_argument("--max-pages", "-m", type=int, default=5, help="Maximum number of pages to crawl")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--all-domains", dest="same_domain", action="store_false", help="Crawl pages from all domains")
    parser.add_argument("--depth-first", "-d", action="store_true", help="Use depth-first crawling instead of breadth-first")
    
    args = parser.parse_args()
    
    print(f"Starting crawl at {args.url}...")
    print(f"Will crawl up to {args.max_pages} pages")
    
    result = crawl_website(
        args.url,
        output=args.output,
        max_pages=args.max_pages,
        headless=args.headless,
        same_domain=args.same_domain,
        depth_first=args.depth_first
    )
    
    print("\n=== Crawl Summary ===")
    print(f"Started at: {args.url}")
    print(f"Pages crawled: {len(result.get('crawl_results', []))}")
    print(f"Crawl data saved to: {args.output or 'webget/crawl_output/'}")
