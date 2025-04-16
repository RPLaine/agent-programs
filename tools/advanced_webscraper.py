import time
import random
import requests
from bs4 import BeautifulSoup, Tag
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedWebScraper:
    """Advanced web scraper with multiple techniques to bypass restrictions"""
    
    def __init__(self, use_selenium=True, use_proxies=False, rotate_user_agents=True):
        """Initialize the scraper with configurable options"""
        self.use_selenium = use_selenium
        self.use_proxies = use_proxies
        self.rotate_user_agents = rotate_user_agents
        self.session = requests.Session()
        self.driver = None
        self.user_agents = self._get_user_agents()
        self.proxies = []
        
        if self.use_selenium:
            self._initialize_selenium()
            
        if self.use_proxies:
            self._initialize_proxies()
    def _initialize_selenium(self):
        """Set up Selenium WebDriver with Edge in headless mode"""
        try:
            # We'll use Edge options instead of Chrome
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from selenium.webdriver.edge.service import Service as EdgeService
            
            edge_options = EdgeOptions()
            edge_options.add_argument("--headless")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-extensions")
            edge_options.add_argument("--disable-notifications")
            edge_options.add_argument("--disable-infobars")
            
            # Set a realistic user agent
            edge_options.add_argument(f"--user-agent={random.choice(self.user_agents)}")
            
            # Initialize Edge WebDriver
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            logger.info("Selenium Edge WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
            self.use_selenium = False
    
    def _initialize_proxies(self):
        """Initialize proxy list - you can expand this with actual proxies"""
        # This is a placeholder - for production, use a proper proxy service
        self.proxies = [
            # Add your proxies here, e.g.:
            # "http://user:pass@proxy1.example.com:8080",
            # "http://user:pass@proxy2.example.com:8080"
        ]
        
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
            "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1"
        ]
    
    def _get_request_headers(self):
        """Generate request headers with optional rotation"""
        user_agent = random.choice(self.user_agents) if self.rotate_user_agents else self.user_agents[0]
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'DNT': '1',  # Do Not Track
        }
        
        # Add referer if it helps
        if random.random() > 0.5:  # 50% chance to add referer
            common_referers = [
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://www.yahoo.com/',
                'https://duckduckgo.com/'
            ]
            headers['Referer'] = random.choice(common_referers)
            
        return headers
    
    def _get_proxy(self):
        """Return a random proxy if available and enabled"""
        if self.use_proxies and self.proxies:
            return {'http': random.choice(self.proxies), 'https': random.choice(self.proxies)}
        return None
    
    def get_content_with_requests(self, url):
        """Attempt to get content using the requests library with enhanced headers"""
        try:
            headers = self._get_request_headers()
            proxies = self._get_proxy()
            
            # Add a random delay to simulate human behavior
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(
                url, 
                headers=headers, 
                proxies=proxies, 
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code == 200:
                return response.text
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching content with requests: {e}")
            return None
    
    def get_content_with_selenium(self, url):
        """Get content using Selenium WebDriver to handle JavaScript rendering"""
        if not self.driver:
            logger.error("Selenium WebDriver not available")
            return None
            
        try:
            logger.info(f"Fetching {url} with Selenium")
            
            # Navigate to the URL
            self.driver.get(url)
            
            # Wait for the page to load (up to 10 seconds)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Add a random delay to simulate human reading
            time.sleep(random.uniform(2, 5))
            
            # Get the page source
            page_source = self.driver.page_source
            
            return page_source
            
        except Exception as e:
            logger.error(f"Error fetching content with Selenium: {e}")
            return None
    
    def extract_text(self, html_content):
        """Extract text content from HTML using BeautifulSoup"""
        if not html_content:
            return None
            
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for element in soup(["script", "style", "meta", "link"]):
                element.extract()
                
            # Get text and clean it up
            text = soup.get_text(separator='\n')
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)
            
        except Exception as e:
            logger.error(f"Error extracting text from HTML: {e}")
            return None
    
    def get_content(self, url):
        """Get content from URL using the most effective available method"""
        logger.info(f"Fetching content from: {url}")
        
        # First try with requests
        content = self.get_content_with_requests(url)
        
        # If requests fails and Selenium is available, try with Selenium
        if content is None and self.use_selenium and self.driver:
            logger.info("Requests method failed. Trying with Selenium...")
            content = self.get_content_with_selenium(url)
        
        if content:
            logger.info(f"Successfully retrieved content from {url}")
            return content
        else:
            logger.warning(f"Failed to retrieve content from {url}")
            return None
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        self.session.close()
        logger.info("Resources cleaned up successfully")


def get_emergency_data_from_tilannehuone(url=None):
    """
    Function to specifically extract emergency data from www.tilannehuone.fi
    
    Args:
        url (str): Specific URL to fetch from tilannehuone.fi. If None, uses the main page.
    
    Returns:
        dict: Dictionary containing the extracted emergency data
    """
    if not url:
        url = "https://www.tilannehuone.fi/halytys.php"
    
    logger.info(f"Fetching emergency data from {url}")
    
    scraper = AdvancedWebScraper(use_selenium=True)
    
    try:
        # Get the HTML content
        html_content = scraper.get_content(url)
        
        if not html_content:
            logger.error("Failed to retrieve content")
            return {"error": "Failed to retrieve content from tilannehuone.fi"}
        
        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract emergency data - this is site-specific and needs to be adjusted
        # based on the actual structure of tilannehuone.fi
        emergencies = []
        
        try:
            # Look for tables containing emergency data
            tables = soup.find_all('table')
            
            if tables:
                logger.info(f"Found {len(tables)} tables in the page")
                
                # Look for the table with emergency data (this is site-specific)
                for table in tables:
                    try:
                        # Check if table is a BS4 Tag object that has find_all method
                        if isinstance(table, Tag):
                            rows = table.find_all('tr')
                            # Only process if rows exist and has more than header
                        else:
                            continue
                        if rows and len(rows) > 1:  
                            for row_index in range(1, len(rows)):  # Skip header row
                                try:
                                    row = rows[row_index]
                                    # Check if row is a proper Tag object before calling find_all
                                    if isinstance(row, Tag):
                                        cols = row.find_all('td')
                                    else:
                                        continue
                                    if cols and len(cols) >= 3:  # Assuming at least 3 columns
                                        emergency_data = {
                                            "time": cols[0].get_text().strip() if cols[0] else "Unknown",
                                            "location": cols[1].get_text().strip() if len(cols) > 1 else "Unknown",
                                            "type": cols[2].get_text().strip() if len(cols) > 2 else "Unknown",
                                        }
                                        
                                        if len(cols) > 3:  # Additional information if available
                                            emergency_data["details"] = cols[3].get_text().strip()
                                            
                                        emergencies.append(emergency_data)
                                except Exception as e:
                                    logger.error(f"Error processing table row: {e}")
                                    continue
                    except Exception as e:
                        logger.error(f"Error processing table: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error finding tables: {e}")

        # If no tables found, try looking for divs with specific classes
        if not emergencies:
            try:
                # This is site-specific and needs to be adjusted for tilannehuone.fi
                emergency_divs = soup.find_all('div', attrs={"class": ["emergency", "alert", "alarm"]})
                
                for div in emergency_divs:
                    try:
                        # Check if div is a Tag object before using find method
                        if not isinstance(div, Tag):
                            continue
                            
                        time_span = div.find('span', attrs={"class": "time"})
                        location_span = div.find('span', attrs={"class": "location"})
                        type_span = div.find('span', attrs={"class": "type"})
                        
                        emergency_data = {
                            "time": time_span.get_text().strip() if time_span else "Unknown",
                            "location": location_span.get_text().strip() if location_span else "Unknown",
                            "type": type_span.get_text().strip() if type_span else "Unknown",
                        }
                        emergencies.append(emergency_data)
                    except Exception as e:
                        logger.error(f"Error processing emergency div: {e}")
                        continue
            except Exception as e:
                logger.error(f"Error finding emergency divs: {e}")
        
        # If no structured data found, get the entire page text as fallback
        if not emergencies:
            logger.warning("No structured emergency data found, extracting full page text")
            page_text = scraper.extract_text(html_content)
            if page_text:
                return {"page_content": page_text}
            else:
                return {"error": "Could not extract any content from the page"}
        
        return {"emergencies": emergencies}
        
    except Exception as e:
        logger.error(f"Error extracting emergency data: {e}")
        return {"error": str(e)}
        
    finally:
        scraper.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Web Scraper")
    parser.add_argument("--url", type=str, default="https://www.tilannehuone.fi/halytys.php", 
                      help="URL to scrape (default: tilannehuone.fi)")
    parser.add_argument("--no-selenium", dest="use_selenium", action="store_false",
                      help="Disable Selenium and use only requests")
    parser.add_argument("--no-rotate-agents", dest="rotate_agents", action="store_false",
                      help="Disable user agent rotation")
                      
    args = parser.parse_args()
    
    print(f"Fetching data from {args.url}")
    
    if "tilannehuone.fi" in args.url:
        result = get_emergency_data_from_tilannehuone(args.url)
        print("Result:", result)
    else:
        scraper = AdvancedWebScraper(use_selenium=args.use_selenium, rotate_user_agents=args.rotate_agents)
        content = scraper.get_content(args.url)
        
        if content:
            text = scraper.extract_text(content)
            print(f"Successfully retrieved content from {args.url}")
            print(f"Content length: {len(content)} characters")
            
            if text:
                print(f"Extracted text length: {len(text)} characters")
                print("\nFirst 500 characters of extracted text:")
                print(text[:500] + "..." if len(text) > 500 else text)
            else:
                print("Could not extract readable text from the content")
        else:
            print(f"Failed to retrieve content from {args.url}")
            
        scraper.close()
