#!/usr/bin/env python3

import os
import json
import logging
import argparse
from datetime import datetime
from urllib.parse import urlparse, urljoin
from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
import random
import time

logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("webget.selenium_handler")

class SeleniumHandler:
    def __init__(self, headless=True, wait_time=10):
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
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
    
    def get_page(self, url):
        try:
            logger.info(f"Fetching {url} with Selenium")
            
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                return None
                
            self.driver.get(url)
            
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(random.uniform(1, 3))
            
            page_source = self.driver.page_source
            logger.info(f"Successfully retrieved content from {url}")
            
            return page_source
            
        except Exception as e:
            logger.error(f"Error fetching content with Selenium: {e}")
            return None
    
    def extract_data(self, html_content, url):
        if not html_content:
            return {"success": False, "error": "No HTML content provided"}
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        result = {
            "url": url,
            "extraction_time": datetime.now().isoformat(),
            "domain": urlparse(url).netloc,
            "content_type": "text/html",
            "success": True
        }
        
        result["title"] = self._get_text(soup.title)
        result["html_length"] = len(html_content)
        
        text_content = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])
        result["text_content"] = text_content[:2000] + "..." if len(text_content) > 2000 else text_content
        result["text_length"] = len(text_content)
        
        result["headings"] = self._extract_headings(soup)
        result["links"] = self._extract_links(soup, url)
        result["link_count"] = len(result["links"])
        result["images"] = self._extract_images(soup, url)
        result["image_count"] = len(result["images"])
        result["tables"] = self._extract_tables(soup)
        result["table_count"] = len(result["tables"])
        
        return result
    
    def _get_text(self, element):
        if element is None:
            return ""
        return element.get_text(strip=True)
    
    def _extract_headings(self, soup):
        headings = {}
        for level in range(1, 7):
            tag = f'h{level}'
            elements = soup.find_all(tag)
            if elements:
                headings[tag] = [self._get_text(h) for h in elements]
        return headings
    
    def _extract_links(self, soup, base_url):
        links = []
        base_domain = urlparse(base_url).netloc
        
        for a in soup.find_all('a'):
            href = a.get('href')
            if not href:
                continue
                
            if href.startswith('/') or not urlparse(href).netloc:
                full_url = urljoin(base_url, href)
            else:
                full_url = href
                
            if not full_url.startswith(('http://', 'https://')):
                continue
                
            link_domain = urlparse(full_url).netloc
            link_info = {
                'url': full_url,
                'text': self._get_text(a),
                'is_internal': link_domain == base_domain
            }
            links.append(link_info)
            
        return links
    
    def _extract_images(self, soup, base_url):
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
                
            if src.startswith('/') or not urlparse(src).netloc:
                full_url = urljoin(base_url, src)
            else:
                full_url = src
                
            image_info = {
                'url': full_url,
                'alt': img.get('alt', ''),
                'width': img.get('width', ''),
                'height': img.get('height', '')
            }
            images.append(image_info)
            
        return images
    
    def _extract_tables(self, soup):
        tables = []
        for table in soup.find_all('table'):
            try:
                headers = []
                header_row = table.find('thead')
                if header_row:
                    headers = [self._get_text(th) for th in header_row.find_all('th')]
                
                if not headers and table.find('tr'):
                    headers = [self._get_text(th) for th in table.find('tr').find_all(['th', 'td'])]
                
                rows = []
                for tr in table.find_all('tr')[1:] if headers else table.find_all('tr'):
                    row = [self._get_text(td) for td in tr.find_all(['td', 'th'])]
                    if row:
                        rows.append(row)
                
                table_data = {
                    'headers': headers,
                    'rows': rows,
                    'row_count': len(rows),
                    'column_count': len(headers) if headers else len(rows[0]) if rows else 0
                }
                tables.append(table_data)
                
            except Exception as e:
                tables.append({
                    'html': str(table)[:500] + "..." if len(str(table)) > 500 else str(table)
                })
                
        return tables
    
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

def get_with_selenium(url, output=None, headless=True, take_screenshot=False):
    # Set default output directory to webget/output/
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_output_dir = os.path.join(script_dir, "output")
    
    if output:
        output_dir = os.path.dirname(output)
    else:
        output_dir = default_output_dir
        # Generate default filename if none provided
        domain = urlparse(url).netloc.replace(".", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output = os.path.join(output_dir, f"{domain}_{timestamp}.json")
    
    os.makedirs(output_dir, exist_ok=True)
    
    handler = SeleniumHandler(headless=headless)
    
    try:
        html_content = handler.get_page(url)
        
        if not html_content:
            result = {"url": url, "success": False, "error": f"Failed to retrieve content from {url}"}
            # Save error result as JSON
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                logger.info(f"Error data saved to {output}")
                result["output_file"] = output
            except Exception as e:
                logger.error(f"Error saving error data to {output}: {e}")
            return result
        
        data = handler.extract_data(html_content, url)
        
        if take_screenshot:
            screenshot_dir = os.path.dirname(output)
            domain = urlparse(url).netloc.replace(".", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(screenshot_dir, f"screenshot_{domain}_{timestamp}.png")
            if handler.take_screenshot(screenshot_path):
                data["screenshot"] = screenshot_path
        
        # Always save JSON output
        if data.get("success", False):
            try:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                logger.info(f"Data saved to {output}")
                data["output_file"] = output
            except Exception as e:
                logger.error(f"Error saving data to {output}: {e}")
        
        return data
        
    finally:
        handler.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract web data using Selenium")
    parser.add_argument("url", help="URL to extract data from")
    parser.add_argument("--output", "-o", help="Path to save output JSON file")
    parser.add_argument("--no-headless", dest="headless", action="store_false", help="Show browser window")
    parser.add_argument("--screenshot", "-s", action="store_true", help="Take screenshot of the page")
    
    args = parser.parse_args()
    
    print(f"Extracting data from {args.url}...")
    
    data = get_with_selenium(
        args.url, 
        output=args.output,
        headless=args.headless,
        take_screenshot=args.screenshot
    )
    
    print("\n=== Extraction Summary ===")
    print(f"URL: {data['url']}")
    print(f"Status: {'Success' if data.get('success', False) else 'Failed'}")
    
    if data.get("success", False):
        print(f"Title: {data.get('title', 'Unknown')}")
        print(f"Text length: {data.get('text_length', 0)} characters")
        
        if "table_count" in data:
            print(f"Tables found: {data['table_count']}")
            
        if "link_count" in data:
            internal_count = sum(1 for link in data.get('links', []) if link.get('is_internal', False))
            external_count = sum(1 for link in data.get('links', []) if not link.get('is_internal', True))
            print(f"Links found: {data['link_count']} ({internal_count} internal, {external_count} external)")
        
        print(f"Images found: {data.get('image_count', 0)}")
        
        if "screenshot" in data:
            print(f"\nScreenshot saved to: {data['screenshot']}")
            
        if args.output:
            print(f"\nFull data saved to: {data['output_file']}")
    else:
        print(f"Error: {data.get('error', 'Unknown error')}")
