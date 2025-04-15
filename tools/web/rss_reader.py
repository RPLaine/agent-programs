import feedparser
from bs4 import BeautifulSoup
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import summarization

def fetch_rss_feed(url):
    feed = feedparser.parse(url)
    return feed

def get_feed_entries(feed, limit=10):
    return feed.entries[:limit]

def extract_text_from_entry(entry):
    title = entry.title if hasattr(entry, 'title') else "No title"
    
    summary = ""
    if hasattr(entry, 'summary'):
        soup = BeautifulSoup(entry.summary, 'html.parser')
        summary = soup.get_text()
    
    content = ""
    if hasattr(entry, 'content'):
        soup = BeautifulSoup(entry.content[0].value, 'html.parser')
        content = soup.get_text()
    elif hasattr(entry, 'description'):
        soup = BeautifulSoup(entry.description, 'html.parser')
        content = soup.get_text()
    
    link = entry.link if hasattr(entry, 'link') else ""
    
    published = entry.published if hasattr(entry, 'published') else ""
    
    return {
        "title": title,
        "summary": summary,
        "content": content,
        "link": link,
        "published": published
    }

def read_rss_feed(url, limit=5):
    feed = fetch_rss_feed(url)
    entries = get_feed_entries(feed, limit)
    
    results = []
    for entry in entries:
        parsed_entry = extract_text_from_entry(entry)
        results.append(parsed_entry)
    
    return results

def main():
    rss_url = "https://feeds.yle.fi/uutiset/v1/recent.rss?publisherIds=YLE_UUTISET"
    feed_entries = read_rss_feed(rss_url, limit=5)
    
    for i, entry in enumerate(feed_entries, 1):        
        print(f"\n--- Entry {i} ---")
        print(f"Title: {entry['title']}")
        print(f"Published: {entry['published']}")
        print(f"Link: {entry['link']}")
        print(f"Summary: {summarization.summarization(entry['content'])}")
        print("-------------------")

if __name__ == "__main__":
    main()
