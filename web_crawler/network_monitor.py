#!/usr/bin/env python3
"""
Network monitor for web crawler to capture and analyze network traffic,
particularly focusing on API calls made by JavaScript on web pages.
"""

import json
import time
import logging
from typing import Dict, List, Any, Optional, Set
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options

logger = logging.getLogger("web_crawler.network_monitor")


class NetworkMonitor:
    def __init__(self, driver: Optional[WebDriver] = None):
        self.driver = driver
        self.captured_requests: List[Dict[str, Any]] = []
        self.api_endpoints: Set[str] = set()
        self.json_content_urls: Set[str] = set()

    def setup_performance_logging(self, driver_options: Options) -> None:
        driver_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        driver_options.add_argument("--disable-background-networking")
        driver_options.add_argument("--disable-background-timer-throttling")
        driver_options.add_argument("--disable-renderer-backgrounding")

    def start_monitoring(self, url: str, wait_time: int = 5) -> None:
        if not self.driver:
            return
            
        try:
            self.driver.get(url)
            time.sleep(wait_time)  # Allow time for network requests to occur
            
            performance_logs = self.driver.get_log("performance")
            for log_entry in performance_logs:
                try:
                    log_data = json.loads(log_entry["message"])["message"]
                    
                    if "Network.responseReceived" == log_data["method"]:
                        request_data = self._process_response(log_data["params"])
                        if request_data:
                            self.captured_requests.append(request_data)
                            
                            if request_data.get("is_api", False):
                                self.api_endpoints.add(request_data["url"])
                                
                            if request_data.get("is_json", False):
                                self.json_content_urls.add(request_data["url"])
                                
                except (KeyError, json.JSONDecodeError):
                    continue
                    
        except Exception as e:
            logger.error(f"Error monitoring network traffic: {e}")

    def _process_response(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            request_id = response_data.get("requestId")
            response = response_data.get("response", {})
            url = response.get("url", "")
            
            if not url or url.startswith("data:"):
                return None
                
            content_type = response.get("headers", {}).get("content-type", "").lower()
            status = response.get("status", 0)
            
            is_api = any(pattern in url for pattern in ["/api/", "graphql", ".json", "/data/"])
            is_json = "json" in content_type
            is_xml = "xml" in content_type
            
            return {
                "request_id": request_id,
                "url": url,
                "method": response.get("requestMethod", "GET"),
                "status": status,
                "content_type": content_type,
                "is_api": is_api or is_json or is_xml,
                "is_json": is_json,
                "is_xml": is_xml,
                "timestamp": time.time()
            }
                
        except Exception as e:
            logger.debug(f"Error processing response: {e}")
            return None

    def fetch_json_contents(self) -> Dict[str, Any]:
        if not self.driver:
            return {}
            
        json_contents = {}
        
        for url in self.json_content_urls:
            try:
                script = f"""
                var xhr = new XMLHttpRequest();
                xhr.open('GET', '{url}', false);
                xhr.send(null);
                return xhr.responseText;
                """
                response_text = self.driver.execute_script(script)
                try:
                    json_contents[url] = json.loads(response_text)
                except json.JSONDecodeError:
                    logger.warning(f"Could not parse JSON from {url}")
                    
            except Exception as e:
                logger.error(f"Error fetching JSON content from {url}: {e}")
                
        return json_contents

    def get_results(self) -> Dict[str, Any]:
        return {
            "captured_requests": self.captured_requests,
            "api_endpoints": list(self.api_endpoints),
            "json_content_urls": list(self.json_content_urls),
            "json_contents": self.fetch_json_contents() if self.driver else {}
        }


if __name__ == "__main__":
    from selenium import webdriver
    
    options = Options()
    options.add_argument("--headless")
    
    # Create monitor instance
    monitor = NetworkMonitor()
    
    # Apply performance logging setup
    monitor.setup_performance_logging(options)
    
    # Initialize driver with configured options
    driver = webdriver.Chrome(options=options)
    monitor.driver = driver
    
    try:
        test_url = "https://github.com"
        print(f"Starting network monitoring for {test_url}")
        
        # Monitor network traffic
        monitor.start_monitoring(test_url, wait_time=8)
        
        # Get results
        results = monitor.get_results()
        
        print(f"Captured {len(results['captured_requests'])} network requests")
        print(f"Found {len(results['api_endpoints'])} API endpoints")
        print(f"Found {len(results['json_content_urls'])} JSON content URLs")
        
        # Print some example API endpoints
        for i, endpoint in enumerate(results['api_endpoints'][:5]):
            print(f"API endpoint {i+1}: {endpoint}")
            
        # Print JSON contents
        for url, content in list(results['json_contents'].items())[:2]:
            print(f"\nJSON content from {url}:")
            print(json.dumps(content, indent=2)[:500] + "..." if len(json.dumps(content)) > 500 else json.dumps(content, indent=2))
            
    finally:
        driver.quit()
