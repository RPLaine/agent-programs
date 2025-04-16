#!/usr/bin/env python3
"""
Selenium-based web scraper for handling modern websites with anti-scraping measures.
This module provides a dedicated solution for sites that block traditional HTTP requests.
"""

import time
import random
import logging
import argparse
import json
from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.microsoft import EdgeChromiumDriverManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SeleniumScraper:
    """A dedicated Selenium-based web scraper designed to handle sites with anti-scraping measures."""
    
    def __init__(self, headless=True, user_agent=None, proxy=None, wait_time=10):
        """
        Initialize the Selenium scraper.
        
        Args:
            headless (bool): Whether to run the browser in headless mode (default: True)
            user_agent (str): Custom user agent string (default: None, uses a random modern UA)
            proxy (str): Proxy server to use (default: None)
            wait_time (int): Default wait time for page elements in seconds (default: 10)
        """
        self.headless = headless
        self.custom_user_agent = user_agent
        self.proxy = proxy
        self.wait_time = wait_time
        self.driver = None
        self.user_agents = self._get_user_agents()
        
        # Initialize the WebDriver
        self._initialize_driver()
        
    def _get_user_agents(self):
        """Return a list of modern and realistic user agents"""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
        ]
        
    def _initialize_driver(self):
        """Initialize the Selenium WebDriver with Edge"""
        try:
            # Configure Edge options
            edge_options = EdgeOptions()
            
            # Set headless mode if specified
            if self.headless:
                edge_options.add_argument("--headless")
                
            # Common options to improve performance and stability
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-extensions")
            edge_options.add_argument("--disable-notifications")
            edge_options.add_argument("--disable-infobars")
            
            # Set user agent
            user_agent = self.custom_user_agent or random.choice(self.user_agents)
            edge_options.add_argument(f"--user-agent={user_agent}")
            
            # Add proxy if specified
            if self.proxy:
                edge_options.add_argument(f"--proxy-server={self.proxy}")
            
            # Initialize Edge WebDriver
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logger.info("Selenium Edge WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            raise
    
    def get_page(self, url, wait_for_element=None, wait_time=None):
        """
        Load a web page in the browser and return the page source.
        
        Args:
            url (str): The URL to load
            wait_for_element (tuple): Element to wait for, e.g. (By.ID, "main-content")
            wait_time (int): Time to wait for element in seconds (overrides default)
            
        Returns:
            str: The page source HTML
        """
        try:
            logger.info(f"Fetching {url} with Selenium")
            
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                raise RuntimeError("WebDriver is not initialized. Check for errors during driver initialization.")
                
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for a specific element if specified
            if wait_for_element:
                selector_type, selector = wait_for_element
                wait = WebDriverWait(self.driver, wait_time or self.wait_time)
                wait.until(EC.presence_of_element_located((selector_type, selector)))
            else:
                # Default: wait for the body element
                WebDriverWait(self.driver, wait_time or self.wait_time).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            
            # Add a small random delay to simulate human behavior
            time.sleep(random.uniform(1, 3))
            
            # Get the page source
            page_source = self.driver.page_source
            logger.info(f"Successfully retrieved content from {url}")
            
            return page_source
            
        except Exception as e:
            logger.error(f"Error fetching content with Selenium: {e}")
            return None
    
    def extract_text(self, html_content):
        """
        Extract clean text from HTML content using BeautifulSoup.
        
        Args:
            html_content (str): The HTML content to process
            
        Returns:
            str: Extracted text content
        """
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements that might contain non-content text
            for element in soup(["script", "style", "meta", "link", "noscript"]):
                element.extract()
                
            # Get text and clean it up
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return None
            
    def find_elements(self, html_content, selector_type, selector):
        """
        Find elements in HTML content using BeautifulSoup.
        
        Args:
            html_content (str): The HTML content to search
            selector_type (str): Type of selector ('id', 'class', 'tag', 'css', 'xpath')
            selector (str): The selector value
            
        Returns:
            list: Matching elements
        """
        if not html_content:
            logger.warning("Empty HTML content provided to find_elements")
            return []
            
        if not selector_type or not selector:
            logger.warning(f"Invalid selector parameters: type={selector_type}, selector={selector}")
            return []
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            if selector_type == 'id':
                element = soup.find(id=selector)
                return [element] if element else []
            elif selector_type == 'class':
                return soup.find_all(class_=selector)
            elif selector_type == 'tag':
                return soup.find_all(selector)
            elif selector_type == 'css':
                return soup.select(selector)
            else:
                logger.warning(f"Unsupported selector type: {selector_type}")
                return []
                
        except Exception as e:
            logger.error(f"Error finding elements: {e}")
            return []
            
    def extract_structured_data(self, html_content, config):
        """
        Extract structured data from HTML based on a configuration.
        
        Args:
            html_content (str): The HTML content to process
            config (dict): Configuration dictionary with selectors
            
        Returns:
            dict: Extracted structured data
        """
        if not html_content:
            logger.warning("Empty HTML content provided to extract_structured_data")
            return None
            
        if not config or not isinstance(config, dict):
            logger.warning(f"Invalid config provided to extract_structured_data: {type(config)}")
            return None
            
        # Helper function to parse HTML tables into structured arrays
        def parse_table_to_array(table_element):
            if not isinstance(table_element, Tag) or table_element.name != 'table':
                return None
                
            table_data = []
            # Process table rows
            for row in table_element.find_all('tr'):
                if isinstance(row, Tag):  # Ensure row is a Tag object
                    # Get all cells (th or td) in the row
                    row_data = []
                    for cell in row.find_all(['th', 'td']):
                        if isinstance(cell, Tag):  # Ensure cell is a Tag object
                            row_data.append(cell.get_text().strip())
                    if row_data:  # Only add non-empty rows
                        table_data.append(row_data)
            return table_data
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            result = {}
            for key, selector_info in config.items():
                if not selector_info or not isinstance(selector_info, dict):
                    logger.warning(f"Invalid selector info for key '{key}': {selector_info}")
                    result[key] = None
                    continue
                    
                selector_type = selector_info.get('type', 'css')
                selector = selector_info.get('selector', '')
                attribute = selector_info.get('attribute', None)
                
                if not selector:
                    logger.warning(f"Empty selector for key '{key}'")
                    result[key] = None
                    continue
                
                if selector_type == 'css':
                    elements = soup.select(selector)
                elif selector_type == 'id':
                    element = soup.find(id=selector)
                    elements = [element] if element else []
                elif selector_type == 'class':
                    elements = soup.find_all(class_=selector)
                elif selector_type == 'tag':
                    elements = soup.find_all(selector)
                else:
                    logger.warning(f"Unsupported selector type '{selector_type}' for key '{key}'")
                    elements = []
                
                # Extract data from elements
                if elements and len(elements) > 0 and elements[0] is not None:
                    if selector_info.get('multiple', False):
                        # Handle multiple elements
                        result[key] = []
                        for e in elements:
                            if e is None:
                                result[key].append(None)
                            # Special handling for table elements
                            elif key == 'tables' and isinstance(e, Tag) and e.name == 'table':
                                parsed_table = parse_table_to_array(e)
                                result[key].append(parsed_table)
                            elif attribute:
                                # Safe attribute access
                                try:
                                    # Try direct dictionary-style access first (for Tag objects)
                                    if isinstance(e, Tag) and attribute in getattr(e, 'attrs', {}):
                                        result[key].append(e.attrs[attribute])
                                    # Try other fallback methods
                                    elif isinstance(e, Tag) and hasattr(e, attribute):
                                        result[key].append(getattr(e, attribute))
                                    else:
                                        result[key].append(None)
                                except Exception:
                                    result[key].append(None)
                            else:
                                # Get text content
                                try:
                                    if isinstance(e, Tag) and hasattr(e, 'get_text'):
                                        result[key].append(e.get_text().strip())
                                    else:
                                        result[key].append(str(e) if e is not None else None)
                                except Exception:
                                    result[key].append(None)
                    else:
                        # Handle single element
                        e = elements[0]
                        if e is None:
                            result[key] = None
                        # Special handling for table elements
                        elif key == 'tables' and isinstance(e, Tag) and e.name == 'table':
                            result[key] = parse_table_to_array(e)
                        elif attribute:
                            # Safe attribute access
                            try:
                                # Try direct dictionary-style access first (for Tag objects)
                                if isinstance(e, Tag) and attribute in getattr(e, 'attrs', {}):
                                    result[key] = e.attrs[attribute]
                                # Try other fallback methods
                                elif isinstance(e, Tag) and hasattr(e, attribute):
                                    result[key] = getattr(e, attribute)
                                else:
                                    result[key] = None
                            except Exception:
                                result[key] = None
                        else:
                            # Get text content
                            try:
                                if isinstance(e, Tag) and hasattr(e, 'get_text'):
                                    result[key] = e.get_text().strip()
                                else:
                                    result[key] = str(e) if e is not None else None
                            except Exception:
                                result[key] = None
                else:
                    result[key] = None
                    
            return result
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
            return None
    
    def screenshot(self, output_path):
        """
        Take a screenshot of the current page.
        
        Args:
            output_path (str): Path to save the screenshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.driver is None:
                logger.error("Cannot take screenshot: WebDriver is not initialized")
                return False
                
            self.driver.save_screenshot(output_path)
            logger.info(f"Screenshot saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def execute_javascript(self, script):
        """
        Execute JavaScript on the page.
        
        Args:
            script (str): JavaScript to execute
            
        Returns:
            object: Result of the JavaScript execution
        """
        try:
            if self.driver is None:
                logger.error("Cannot execute JavaScript: WebDriver is not initialized")
                return None
                
            return self.driver.execute_script(script)
        except Exception as e:
            logger.error(f"Error executing JavaScript: {e}")
            return None
    
    def click_element(self, selector_type, selector, wait_time=None):
        """
        Click an element on the page.
        
        Args:
            selector_type (By): Selenium By selector type (e.g., By.ID)
            selector (str): The selector value
            wait_time (int): Time to wait for the element in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.driver is None:
                logger.error("Cannot click element: WebDriver is not initialized")
                return False
                
            wait = WebDriverWait(self.driver, wait_time or self.wait_time)
            element = wait.until(EC.element_to_be_clickable((selector_type, selector)))
            element.click()
            return True
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return False
    
    def fill_form(self, form_data):
        """
        Fill out a form on the page.
        
        Args:
            form_data (dict): Dictionary mapping selector tuples to values
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.driver is None:
                logger.error("Cannot fill form: WebDriver is not initialized")
                return False
                
            for (selector_type, selector), value in form_data.items():
                element = WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((selector_type, selector))
                )
                element.clear()
                element.send_keys(value)
            return True
        except Exception as e:
            logger.error(f"Error filling form: {e}")
            return False
    
    def close(self):
        """Close the browser and clean up resources."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed successfully")


def scrape_website(url, headless=True, screenshot=False, output_text=True):
    """
    Utility function to scrape a website using the SeleniumScraper.
    
    Args:
        url (str): The URL to scrape
        headless (bool): Whether to run in headless mode
        screenshot (bool): Whether to take a screenshot
        output_text (bool): Whether to output extracted text
        
    Returns:
        dict: Results including HTML, text content, and metadata
    """
    scraper = SeleniumScraper(headless=headless)
    
    try:
        html_content = scraper.get_page(url)
        
        if not html_content:
            return {"error": f"Failed to retrieve content from {url}"}
        
        result = {
            "url": url,
            "html_length": len(html_content) if html_content else 0,
            "success": bool(html_content)
        }
        
        if output_text and html_content:
            text_content = scraper.extract_text(html_content)
            result["text"] = text_content
            result["text_length"] = len(text_content) if text_content else 0
        
        if screenshot:
            import os
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"screenshot_{url.replace('://', '_').replace('/', '_').replace('.', '_')}.png"
            screenshot_path = os.path.join(output_dir, filename)
            if scraper.screenshot(screenshot_path):
                result["screenshot"] = screenshot_path
        
        return result
    
    except Exception as e:
        logger.error(f"Error in scrape_website: {e}")
        return {"error": str(e)}
    
    finally:
        scraper.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selenium Web Scraper")
    parser.add_argument("--url", type=str, required=True, help="URL to scrape")
    parser.add_argument("--no-headless", dest="headless", action="store_false", 
                        help="Disable headless mode (show browser window)")
    parser.add_argument("--screenshot", action="store_true", 
                        help="Take a screenshot of the page")
    parser.add_argument("--no-text", dest="output_text", action="store_false", 
                        help="Don't output extracted text")
    parser.add_argument("--output", type=str, 
                        help="Path to save structured JSON data (automatically extracts structured data)")
    
    args = parser.parse_args()
    print(f"Scraping {args.url}...")
    
    # Setup for structured data extraction if output is specified
    extract_structured_data = bool(args.output)
    
    # Default config for structured data extraction
    config = None
    if extract_structured_data:
        # Use a default config that extracts common structured data from websites
        config = {
            "title": {"type": "css", "selector": "title"},
            "headings": {"type": "css", "selector": "h1, h2", "multiple": True},
            "links": {"type": "css", "selector": "a", "attribute": "href", "multiple": True},
            "images": {"type": "css", "selector": "img", "attribute": "src", "multiple": True},
            "meta_description": {"type": "css", "selector": "meta[name=description]", "attribute": "content"},
            "meta_keywords": {"type": "css", "selector": "meta[name=keywords]", "attribute": "content"},
            "paragraphs": {"type": "css", "selector": "p", "multiple": True},
            "tables": {"type": "css", "selector": "table", "multiple": True}
        }
        print("Using default config for structured data extraction")
            
    # Initialize the scraper
    scraper = SeleniumScraper(headless=args.headless)
    
    try:
        # Get the page content
        print(f"Fetching content from {args.url}...")
        html_content = scraper.get_page(args.url)
        
        if not html_content:
            print(f"Error: Failed to retrieve content from {args.url}")
            import sys
            sys.exit(1)
        
        result = {
            "url": args.url,
            "html_length": len(html_content) if html_content else 0,
            "success": bool(html_content)
        }
          # Extract structured data if requested
        if extract_structured_data and config:
            print("Extracting structured data...")
            structured_data = scraper.extract_structured_data(html_content, config)
            result["structured_data"] = structured_data
            
            if args.output:
                try:
                    output_path = args.output
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(structured_data, f, indent=2, ensure_ascii=False)
                    print(f"Structured data saved to {output_path}")
                except Exception as e:
                    print(f"Error saving JSON data: {e}")
        
        # Extract text if requested
        if args.output_text:
            print("Extracting text content...")
            text_content = scraper.extract_text(html_content)
            result["text"] = text_content
            result["text_length"] = len(text_content) if text_content else 0
        
        # Take screenshot if requested
        if args.screenshot:
            import os
            print("Taking screenshot...")
            output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            filename = f"screenshot_{args.url.replace('://', '_').replace('/', '_').replace('.', '_')}.png"
            screenshot_path = os.path.join(output_dir, filename)
            if scraper.screenshot(screenshot_path):
                result["screenshot"] = screenshot_path
    
    except Exception as e:
        import traceback
        print(f"Error during scraping: {e}")
        traceback.print_exc()
        import sys
        sys.exit(1)
        
    finally:
        # Clean up resources
        scraper.close()      
        
    print(f"\nStatus: {'Success' if result.get('success', False) else 'Failed'}")
    print(f"HTML size: {result.get('html_length', 0)} bytes")
    
    # Display structured data statistics if available
    if extract_structured_data and "structured_data" in result:
        structured_data = result["structured_data"]
        print("\n--- Structured Data Statistics ---")
        
        if structured_data:
            # Count fields with actual values
            filled_fields = sum(1 for v in structured_data.values() if v is not None)
            print(f"Fields extracted: {filled_fields}/{len(structured_data)}")
            
            # Count items in list fields
            list_fields = {k: len(v) for k, v in structured_data.items() 
                          if isinstance(v, list) and v}
            if list_fields:
                print("\nList fields:")
                for field, count in list_fields.items():
                    print(f"  - {field}: {count} items")
              # Show a preview of the data
            print("\nData preview:")
            for key, value in structured_data.items():
                if isinstance(value, list) and value:
                    print(f"  {key}: [{value[0]}, ...] ({len(value)} items)")
                elif isinstance(value, str) and len(value) > 50:
                    print(f"  {key}: {value[:50]}... ({len(value)} chars)")
                else:
                    print(f"  {key}: {value}")
                    
            # Show path to saved JSON if applicable
            if args.output:
                print(f"\nStructured data saved to: {args.output}")
        else:
            print("No structured data was extracted.")
    
    # Display text statistics if available
    if args.output_text:
        print(f"\nText size: {result.get('text_length', 0)} bytes")
        text = result.get('text', '')
        if text:
            print("\nFirst 500 characters of extracted text:")
            print(text[:500] + "..." if len(text) > 500 else text)
    
    # Display screenshot path if available
    if args.screenshot and "screenshot" in result:
        print(f"\nScreenshot saved to: {result['screenshot']}")
