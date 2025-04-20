"""
Web content analysis utilities.
"""

import logging
from typing import Dict, List, Any
from collections import Counter
from urllib.parse import urlparse

logger = logging.getLogger("web_crawler.analyzer")


def analyze_web_content(crawl_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze crawled web content to extract insights.
    """
    analysis = {
        "summary": {
            "total_pages": len(crawl_data.get("crawl_results", [])),
            "crawl_time": crawl_data.get("start_time", ""),
            "domains": crawl_data.get("domains_visited", [])
        },
        "content_analysis": {
            "common_topics": [],
            "word_frequencies": {},
            "sentiment": {},
            "readability": {}
        },
        "structure_analysis": {
            "link_graph": {},
            "depth_distribution": {},
            "content_type_distribution": {}
        },
        "metadata_analysis": {
            "common_meta_tags": {},
            "schema_types": {},
            "seo_compliance": {}
        }
    }
    
    # Implement basic word frequency analysis
    if crawl_data.get("crawl_results"):
        all_words = []
        for page in crawl_data["crawl_results"]:
            if page.get("text_content"):
                content = page.get("text_content", "")
                words = [w.lower() for w in content.split() if len(w) > 3]
                all_words.extend(words)
        
        # Get most common words
        word_counts = Counter(all_words)
        analysis["content_analysis"]["word_frequencies"] = dict(word_counts.most_common(50))
    
    # Analyze meta tags
    meta_tag_names = []
    for page in crawl_data.get("crawl_results", []):
        if page.get("meta_tags"):
            meta_tag_names.extend(page["meta_tags"].keys())
    
    meta_tag_counts = Counter(meta_tag_names)
    analysis["metadata_analysis"]["common_meta_tags"] = dict(meta_tag_counts.most_common(20))
    
    # Analyze schema.org types
    schema_types = []
    for page in crawl_data.get("crawl_results", []):
        for schema in page.get("structured_data", []):
            if isinstance(schema, dict) and "@type" in schema:
                schema_types.append(schema["@type"])
    
    schema_type_counts = Counter(schema_types)
    analysis["metadata_analysis"]["schema_types"] = dict(schema_type_counts.most_common(10))
    
    # Create link graph
    link_graph = {}
    for page in crawl_data.get("crawl_results", []):
        from_url = page.get("url")
        if from_url:
            link_graph[from_url] = []
            for link in page.get("links", []):
                to_url = link.get("url")
                if to_url:
                    link_graph[from_url].append(to_url)
    
    analysis["structure_analysis"]["link_graph"] = link_graph
    
    return analysis


def analyze_seo_compliance(page_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze SEO compliance for a single page.
    """
    seo_results = {
        "title_length": 0,
        "has_meta_description": False,
        "has_h1": False,
        "image_alt_text_percentage": 0,
        "canonical_url_present": False,
        "has_structured_data": False,
        "url_length": 0,
        "issues": [],
        "score": 0
    }
    
    # Check title
    title = page_data.get("title", "")
    seo_results["title_length"] = len(title)
    if not title:
        seo_results["issues"].append("Missing page title")
    elif len(title) < 10:
        seo_results["issues"].append("Title too short (less than 10 characters)")
    elif len(title) > 70:
        seo_results["issues"].append("Title too long (more than 70 characters)")
    
    # Check meta description
    meta_tags = page_data.get("meta_tags", {})
    seo_results["has_meta_description"] = "description" in meta_tags
    if not seo_results["has_meta_description"]:
        seo_results["issues"].append("Missing meta description")
    
    # Check H1
    headings = page_data.get("headings", {})
    h1_tags = headings.get("h1", [])
    seo_results["has_h1"] = len(h1_tags) > 0
    if not seo_results["has_h1"]:
        seo_results["issues"].append("Missing H1 heading")
    elif len(h1_tags) > 1:
        seo_results["issues"].append("Multiple H1 headings (should have only one)")
    
    # Check image alt text
    images = page_data.get("images", [])
    if images:
        images_with_alt = sum(1 for img in images if img.get("alt"))
        seo_results["image_alt_text_percentage"] = (images_with_alt / len(images)) * 100
        if seo_results["image_alt_text_percentage"] < 80:
            seo_results["issues"].append("Less than 80% of images have alt text")
    
    # Check canonical URL
    seo_results["canonical_url_present"] = "canonical" in meta_tags
    if not seo_results["canonical_url_present"]:
        seo_results["issues"].append("Missing canonical URL")
    
    # Check structured data
    structured_data = page_data.get("structured_data", [])
    seo_results["has_structured_data"] = len(structured_data) > 0
    if not seo_results["has_structured_data"]:
        seo_results["issues"].append("No structured data (schema.org) found")
    
    # Check URL length
    url = page_data.get("url", "")
    seo_results["url_length"] = len(url)
    if seo_results["url_length"] > 100:
        seo_results["issues"].append("URL too long (more than 100 characters)")
    
    # Calculate overall score (simple heuristic)
    max_score = 100
    deductions = len(seo_results["issues"]) * 10
    seo_results["score"] = max(0, max_score - deductions)
    
    return seo_results
