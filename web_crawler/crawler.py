#!/usr/bin/env python3
"""
A systematic web crawler and content analyzer with elegant architecture
inspired by clean code principles.
"""

import os
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse
from collections import deque
from bs4 import BeautifulSoup

from .browser import BrowserManager
from .utils import setup_output_directory, random_wait, generate_filename, should_follow_link, detect_pagination_pattern
from .extractor import extract_page_data, extract_links
from .analyzer import analyze_web_content

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("web_crawler.crawler")


class WebCrawler:
    """
    Systematic web crawler that extracts, analyzes and organizes web content.
    """
    
    def __init__(
        self,
        headless: bool = True,
        wait_time: int = 10,
        max_pages: int = 5,
        same_domain_only: bool = True,
        depth_first: bool = False,
        respect_robots: bool = True,
        output_dir: Optional[str] = None
    ):
        self.headless = headless
        self.wait_time = wait_time
        self.max_pages = max_pages
        self.same_domain_only = same_domain_only
        self.depth_first = depth_first
        self.respect_robots = respect_robots
        self.visited_urls: Set[str] = set()
        self.robots_disallowed: Set[str] = set()
        self.output_dir = setup_output_directory(output_dir)
        self.browser = BrowserManager(headless=headless, wait_time=wait_time)
    
    def crawl(self, start_url: str) -> Dict[str, Any]:
        """Crawl a website from a starting URL."""
        from .utils import can_fetch
        
        if not can_fetch(start_url, self.visited_urls, self.robots_disallowed, 
                        self.browser.driver, self.respect_robots):
            return {"success": False, "error": "URL not allowed by robots.txt"}
        
        # Ensure driver is initialized
        if self.browser.driver is None:
            try:
                self.browser.initialize_driver()
            except Exception as e:
                return {"success": False, "error": f"Failed to initialize WebDriver: {str(e)}"}
        
        url_queue = deque([(start_url, 0)])  # (url, depth)
        crawled_data = {}
        visited_count = 0
        start_domain = urlparse(start_url).netloc
        
        while url_queue and visited_count < self.max_pages:
            current_url, depth = url_queue.popleft() if not self.depth_first else url_queue.pop()
            
            logger.info(f"Crawling {current_url} (depth: {depth}, count: {visited_count+1}/{self.max_pages})")
            
            try:
                if self.browser.driver is None:
                    raise ValueError("WebDriver is not initialized or has been closed")
                
                self.browser.driver.get(current_url)
                self.browser.wait_for_page_load()
                
                html_content = self.browser.driver.page_source
                soup = BeautifulSoup(html_content, 'html.parser')
                
                page_data = extract_page_data(soup, current_url)
                crawled_data[current_url] = page_data
                self.visited_urls.add(current_url)
                visited_count += 1
                
                # Save individual page data
                page_filename = generate_filename(current_url)
                page_path = os.path.join(self.output_dir, page_filename)
                with open(page_path, 'w', encoding='utf-8') as f:
                    json.dump(page_data, f, indent=2, ensure_ascii=False)
                
                # Check for pagination
                next_page = detect_pagination_pattern(current_url, soup)
                if next_page and should_follow_link(next_page, current_url, self.visited_urls, 
                                                  self.robots_disallowed, self.browser.driver, 
                                                  self.same_domain_only, self.respect_robots):
                    url_queue.appendleft((next_page, depth))  # Always prioritize pagination
                
                # Extract and queue other links
                if depth < 2:  # Limit crawl depth
                    links = extract_links(soup, current_url, self.same_domain_only)
                    for link_info in links:
                        link_url = link_info['url']
                        if should_follow_link(link_url, current_url, self.visited_urls, 
                                            self.robots_disallowed, self.browser.driver, 
                                            self.same_domain_only, self.respect_robots):
                            if self.depth_first:
                                url_queue.append((link_url, depth + 1))
                            else:
                                url_queue.append((link_url, depth + 1))
                
                random_wait(2, 5)  # Be respectful with delays between requests
                
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
            "end_time": datetime.now().isoformat(),
            "domains_visited": list(set(urlparse(url).netloc for url in self.visited_urls)),
            "crawl_stats": {
                "success_count": sum(1 for data in crawled_data.values() if data.get("success", False)),
                "error_count": sum(1 for data in crawled_data.values() if not data.get("success", False)),
                "average_content_length": sum(data.get("text_length", 0) for data in crawled_data.values() 
                                           if data.get("success", False)) / max(1, len(crawled_data)),
                "total_links_found": sum(data.get("link_count", 0) for data in crawled_data.values() 
                                      if data.get("success", False)),
                "total_images_found": sum(data.get("image_count", 0) for data in crawled_data.values() 
                                       if data.get("success", False))
            },
            "crawl_results": list(crawled_data.values())
        }
        
        summary_filename = f"crawl_summary_{urlparse(start_url).netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path = os.path.join(self.output_dir, summary_filename)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)
        
        return summary_data
    
    def take_screenshot(self, url: str, output_path: Optional[str] = None) -> bool:
        """Take a screenshot of a URL."""
        if output_path is None:
            filename = f"screenshot_{urlparse(url).netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            output_path = os.path.join(self.output_dir, filename)
        
        return self.browser.take_screenshot(url, output_path)
    
    def close(self) -> None:
        """Close the WebDriver."""
        self.browser.close()


def crawl_website(
    url: str,
    output: Optional[str] = None,
    max_pages: int = 5,
    headless: bool = True,
    same_domain: bool = True,
    depth_first: bool = False,
    respect_robots: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to crawl a website with default settings.
    """
    if output:
        output_dir = os.path.dirname(output) if '.' in os.path.basename(output) else output
    else:
        output_dir = None
    
    crawler = WebCrawler(
        headless=headless,
        max_pages=max_pages,
        same_domain_only=same_domain,
        depth_first=depth_first,
        respect_robots=respect_robots,
        output_dir=output_dir
    )
    
    try:
        result = crawler.crawl(url)
        return result
    finally:
        crawler.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Systematic web crawler and content analyzer")
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument("--output", "-o", help="Directory to save crawled data")
    parser.add_argument("--max-pages", "-m", type=int, default=5, help="Maximum number of pages to crawl")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--all-domains", dest="same_domain", action="store_false", help="Crawl pages from all domains")
    parser.add_argument("--depth-first", "-d", action="store_true", help="Use depth-first crawling instead of breadth-first")
    parser.add_argument("--ignore-robots", dest="respect_robots", action="store_false", help="Ignore robots.txt restrictions")
    parser.add_argument("--analyze", "-a", action="store_true", help="Perform analysis on crawled data")
    parser.add_argument("--screenshot", "-s", action="store_true", help="Take screenshots of crawled pages")
    
    args = parser.parse_args()
    
    print(f"Starting crawl at {args.url}...")
    print(f"Will crawl up to {args.max_pages} pages")
    
    result = crawl_website(
        args.url,
        output=args.output,
        max_pages=args.max_pages,
        headless=args.headless,
        same_domain=args.same_domain,
        depth_first=args.depth_first,
        respect_robots=args.respect_robots
    )
    
    if args.analyze and result.get("success", True):        
        print("\nAnalyzing crawled content...")
        analysis = analyze_web_content(result)
        analysis_filename = f"analysis_{urlparse(args.url).netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_dir = args.output or os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        os.makedirs(output_dir, exist_ok=True)  # Ensure output directory exists
        analysis_path = os.path.join(output_dir, analysis_filename)
        
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to {analysis_path}")
    
    if args.screenshot and result.get("success", True):
        print("\nTaking screenshots of crawled pages...")
        output_dir = args.output or os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
        screenshots_dir = os.path.join(output_dir, "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Create a new crawler just for screenshots
        crawler = WebCrawler(
            headless=args.headless,
            output_dir=screenshots_dir
        )
        
        try:
            # Take screenshots for each successfully crawled page
            for page in result.get('crawl_results', []):
                if page.get('success', False) and 'url' in page:
                    url = page['url']
                    filename = f"screenshot_{urlparse(url).netloc.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    output_path = os.path.join(screenshots_dir, filename)
                    
                    if crawler.take_screenshot(url, output_path):
                        print(f"Screenshot saved for {url}")
                    else:
                        print(f"Failed to take screenshot for {url}")
            
            print(f"Screenshots saved to: {screenshots_dir}")
        finally:
            crawler.close()
            
    print("\n=== Crawl Summary ===")
    print(f"Started at: {args.url}")
    print(f"Pages crawled: {len(result.get('crawl_results', []))}")
    
    output_dir = args.output or os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    print(f"Crawl data saved to: {output_dir}")
