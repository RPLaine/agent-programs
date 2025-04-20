#!/usr/bin/env python3
"""
Structured data extractor for web crawler that identifies and extracts structured data
from websites, including JSON-LD, Microdata, RDFa, and other structured formats.
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger("web_crawler.structured_data_extractor")


class StructuredDataExtractor:
    def __init__(self):
        self.structured_data_formats = {
            'json_ld': self._extract_json_ld,
            'microdata': self._extract_microdata,
            'rdfa': self._extract_rdfa,
            'meta_tags': self._extract_meta_tags,
            'open_graph': self._extract_open_graph,
            'twitter_cards': self._extract_twitter_cards,
            'tables': self._extract_table_data,
        }

    def extract_all_structured_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        result = {
            'url': url,
            'structured_data': {}
        }
        
        for format_name, extractor_func in self.structured_data_formats.items():
            try:
                data = extractor_func(soup)
                if data:
                    result['structured_data'][format_name] = data
            except Exception as e:
                logger.error(f"Error extracting {format_name} data: {e}")
        
        return result

    def _extract_json_ld(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        json_ld = []
        
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    json_ld.append(data)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON-LD script")
        
        return json_ld

    def _extract_microdata(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        microdata = []
        
        for element in soup.find_all(itemscope=True):
            item_type = element.get('itemtype', '')
            item_props = {}
            
            for prop in element.find_all(itemprop=True):
                prop_name = prop.get('itemprop', '')
                
                if prop.name == 'meta':
                    prop_value = prop.get('content', '')
                elif prop.name == 'a':
                    prop_value = prop.get('href', '')
                elif prop.name == 'img':
                    prop_value = prop.get('src', '')
                elif prop.name == 'time':
                    prop_value = prop.get('datetime', '')
                else:
                    prop_value = prop.get_text(strip=True)
                
                item_props[prop_name] = prop_value
            
            if item_props:
                microdata.append({
                    'type': item_type,
                    'properties': item_props
                })
        
        return microdata

    def _extract_rdfa(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        rdfa_data = []
        
        for element in soup.find_all(property=True):
            property_name = element.get('property', '')
            content = element.get('content', '') or element.get_text(strip=True)
            
            if property_name and content:
                rdfa_data.append({
                    'property': property_name,
                    'content': content
                })
        
        return rdfa_data

    def _extract_meta_tags(self, soup: BeautifulSoup) -> Dict[str, str]:
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name', '')
            content = meta.get('content', '')
            
            if name and content:
                meta_tags[name] = content
        
        return meta_tags

    def _extract_open_graph(self, soup: BeautifulSoup) -> Dict[str, str]:
        og_data = {}
        
        for meta in soup.find_all('meta', property=lambda x: x and x.startswith('og:')):
            property_name = meta.get('property', '')[3:]  # Remove 'og:' prefix
            content = meta.get('content', '')
            
            if property_name and content:
                og_data[property_name] = content
        
        return og_data

    def _extract_twitter_cards(self, soup: BeautifulSoup) -> Dict[str, str]:
        twitter_data = {}
        
        for meta in soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')}):
            name = meta.get('name', '')[8:]  # Remove 'twitter:' prefix
            content = meta.get('content', '')
            
            if name and content:
                twitter_data[name] = content
        
        return twitter_data

    def _extract_table_data(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        table_data = []
        
        for table in soup.find_all('table'):
            headers = []
            
            # Try to extract headers
            thead = table.find('thead')
            if thead:
                header_row = thead.find('tr')
                if header_row:
                    headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # If no headers found in thead, try the first row
            if not headers:
                first_row = table.find('tr')
                if first_row:
                    headers = [th.get_text(strip=True) for th in first_row.find_all(['th', 'td'])]
            
            # Process rows
            rows = []
            for tr in table.find_all('tr')[1:] if headers else table.find_all('tr'):
                row_data = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                
                if headers and len(row_data) == len(headers):
                    rows.append(dict(zip(headers, row_data)))
                else:
                    rows.append(row_data)
            
            if rows:
                table_info = {
                    'headers': headers,
                    'rows': rows,
                    'row_count': len(rows)
                }
                table_data.append(table_info)
        
        return table_data


if __name__ == "__main__":
    import requests
    from bs4 import BeautifulSoup
    
    test_urls = [
        "https://schema.org",
        "https://www.imdb.com/title/tt0068646/",  # The Godfather movie
        "https://www.amazon.com/product-reviews/B08N5LM1K3/"
    ]
    
    extractor = StructuredDataExtractor()
    
    for url in test_urls:
        try:
            print(f"\nTesting structured data extraction on {url}")
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = extractor.extract_all_structured_data(soup, url)
            
            print("Structured data found:")
            for format_name, data in result['structured_data'].items():
                if isinstance(data, list):
                    print(f"- {format_name}: {len(data)} items")
                elif isinstance(data, dict):
                    print(f"- {format_name}: {len(data)} properties")
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
