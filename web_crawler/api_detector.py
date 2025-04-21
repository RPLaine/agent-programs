#!/usr/bin/env python3
"""
API endpoint detector for web crawler that identifies and extracts API endpoints
from JavaScript files and network traffic.
"""

import re
import os
import json
import logging
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urljoin, urlparse
from datetime import datetime
from bs4 import BeautifulSoup, Tag

from selenium.webdriver.chrome.webdriver import WebDriver

logger = logging.getLogger("web_crawler.api_detector")


class ApiDetector:
    def __init__(self, driver: Optional[WebDriver] = None):
        self.driver = driver
        self.found_endpoints: Set[str] = set()

    def extract_api_endpoints_from_js(self, js_content: str, base_url: str) -> List[Dict[str, Any]]:
        endpoints = []
        
        fetch_pattern = r'fetch\([\'"]([^\'"]+)[\'"](,|\))'
        ajax_pattern = r'\$\.(?:get|post|ajax)\(\s*[\'"]([^\'"]+)[\'"]'
        axios_pattern = r'axios\.(?:get|post|put|delete|patch)\([\'"]([^\'"]+)[\'"](,|\))'
        url_pattern = r'(?:url|URI|endpoint):\s*[\'"]([^\'"]+\.(?:json|xml|api|php))[\'"]'
        
        patterns = [fetch_pattern, ajax_pattern, axios_pattern, url_pattern]
        
        for pattern in patterns:
            matches = re.finditer(pattern, js_content, re.IGNORECASE)
            
            for match in matches:
                endpoint = match.group(1)
                if endpoint and not endpoint.startswith(('http://', 'https://')):
                    full_url = urljoin(base_url, endpoint)
                else:
                    full_url = endpoint
                
                if full_url not in self.found_endpoints:
                    self.found_endpoints.add(full_url)
                    endpoints.append({
                        'url': full_url,
                        'type': 'api_endpoint',
                        'source': 'javascript',
                        'pattern_matched': pattern
                    })
        
        return endpoints
        
    def extract_js_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        js_links = []
        
        for script in soup.find_all('script'):
            # Check if script is a Tag and has src attribute
            if isinstance(script, Tag) and script.has_attr('src'):
                src = script['src']
                # Handle relative URLs
                if isinstance(src, str) and not src.startswith(('http://', 'https://')):
                    full_url = urljoin(base_url, src)
                else:
                    full_url = src
                
                # Only add JS files
                if isinstance(full_url, str) and full_url.endswith('.js'):
                    js_links.append(full_url)
        
        return js_links
        
    def fetch_js_content(self, js_url: str) -> Optional[str]:
        if not self.driver:
            return None
            
        try:
            script = f"""
            var xhr = new XMLHttpRequest();
            xhr.open('GET', '{js_url}', false);
            xhr.send(null);
            return xhr.responseText;
            """
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Error fetching JS content from {js_url}: {e}")
            return None
            
    def detect_api_endpoints(self, soup: BeautifulSoup, url: str) -> List[Dict[str, Any]]:
        all_endpoints = []
        
        js_links = self.extract_js_links(soup, url)
        
        for js_url in js_links:
            js_content = self.fetch_js_content(js_url)
            if js_content:
                endpoints = self.extract_api_endpoints_from_js(js_content, url)
                all_endpoints.extend(endpoints)
        
        inline_scripts = soup.find_all('script')
        for script in inline_scripts:
            # Get script text safely by using get_text() instead of string attribute
            script_text = script.get_text()
            if script_text:
                endpoints = self.extract_api_endpoints_from_js(script_text, url)
                all_endpoints.extend(endpoints)
        
        return all_endpoints
        
    def monitor_network_requests(self, timeout: int = 5) -> List[Dict[str, Any]]:
        if not self.driver:
            return []
            
        try:
            script = """
            return window.performance.getEntries()
                .filter(entry => entry.initiatorType === 'xmlhttprequest')
                .map(entry => {
                    return {
                        url: entry.name,
                        type: 'api_endpoint',
                        source: 'network_monitor',
                        duration: entry.duration,
                        size: entry.transferSize
                    };
                });
            """
            network_entries = self.driver.execute_script(script) or []
            
            for entry in network_entries:
                if entry['url'] not in self.found_endpoints:
                    self.found_endpoints.add(entry['url'])
                else:
                    network_entries.remove(entry)
                    
            return network_entries
            
        except Exception as e:
            logger.error(f"Error monitoring network requests: {e}")
            return []
            
    def save_endpoints_to_json(self, url: str, js_endpoints: List[Dict[str, Any]], 
                            network_endpoints: List[Dict[str, Any]], output_dir: str = "output") -> str:
        """
        Save detected API endpoints to a JSON file in the specified output directory.
        
        Args:
            url: The base URL that was scanned
            js_endpoints: List of endpoints detected from JavaScript
            network_endpoints: List of endpoints detected from network monitoring
            output_dir: Directory to save the JSON output file
        
        Returns:
            The path to the saved JSON file
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare data to save
        data = {
            "url": url,
            "scan_time": datetime.now().isoformat(),
            "total_endpoints_found": len(self.found_endpoints),
            "js_endpoints": js_endpoints,
            "network_endpoints": network_endpoints,
            "all_endpoints": list(self.found_endpoints)
        }
        
        # Create a filename based on the domain and timestamp
        parsed = urlparse(url)
        domain = parsed.netloc.replace('.', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"api_endpoints_{domain}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        
        # Save data to JSON file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"API endpoints saved to {filepath}")
        return filepath


if __name__ == "__main__":
    import time
    import argparse
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    
    # Create argument parser
    parser = argparse.ArgumentParser(description='API endpoint detector for websites')
    parser.add_argument('--url', '-u', type=str, default="https://github.com",
                        help='URL to scan for API endpoints')
    parser.add_argument('--output-dir', '-o', type=str, default="output",
                        help='Directory to save the output JSON file')
    parser.add_argument('--wait-time', '-w', type=int, default=5,
                        help='Time to wait for page to load in seconds')
    args = parser.parse_args()
    
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    
    url = args.url
    output_dir = args.output_dir
    
    try:
        print(f"Testing API detector on {url}")
        driver.get(url)
        time.sleep(args.wait_time)  # Allow page to fully load
        api_detector = ApiDetector(driver)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        
        print("\nDetecting API endpoints from JavaScript...")
        js_endpoints = api_detector.detect_api_endpoints(soup, url)
        for endpoint in js_endpoints:
            print(f"Found endpoint: {endpoint['url']}")
        
        print("\nMonitoring network requests...")
        network_endpoints = api_detector.monitor_network_requests()
        for endpoint in network_endpoints:
            print(f"Network request: {endpoint['url']}")
        
        print(f"\nTotal unique endpoints found: {len(api_detector.found_endpoints)}")
        
        # Save results to JSON file
        json_file = api_detector.save_endpoints_to_json(url, js_endpoints, network_endpoints, output_dir)
        print(f"\nAPI endpoints saved to: {json_file}")
        
    finally:
        driver.quit()
