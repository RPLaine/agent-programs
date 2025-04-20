"""
Browser and driver management utilities for web crawling.
"""

import logging
import random
from typing import List, Optional, Any

from selenium import webdriver
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger("web_crawler.browser")


class BrowserManager:
    """Manages browser instances and interactions for web crawling."""
    
    def __init__(self, headless: bool = True, wait_time: int = 10):
        self.headless = headless
        self.wait_time = wait_time
        self.driver = None
        self.user_agents = self._get_user_agents()
    
    def _get_user_agents(self) -> List[str]:
        """Return a list of modern user agent strings."""
        return [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.58",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0",
        ]
    
    def initialize_driver(self) -> None:
        """Initialize the Selenium WebDriver with appropriate settings."""
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
    
    def wait_for_element(self, locator, timeout=None) -> Optional[Any]:
        """Wait for a specific element to be present in the DOM."""
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
    
    def wait_for_elements(self, locator, timeout=None) -> List[Any]:
        """Wait for multiple elements to be present in the DOM."""
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
    
    def wait_for_page_load(self) -> None:
        """Wait for the page to fully load."""
        self.wait_for_element((By.TAG_NAME, "body"))
        
        try:
            if self.driver is None:
                logger.error("WebDriver is not initialized")
                return
            WebDriverWait(self.driver, self.wait_time).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            logger.warning("Timeout waiting for page to fully load")
    
    def take_screenshot(self, url: str, output_path: str) -> bool:
        """Take a screenshot of a URL."""
        try:
            if self.driver is None:
                self.initialize_driver()
                if self.driver is None:
                    return False
            
            self.driver.get(url)
            self.wait_for_page_load()
            self.driver.save_screenshot(output_path)
            logger.info(f"Screenshot saved to {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    def close(self) -> None:
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed successfully")
