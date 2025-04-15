from googlesearch import search
from bs4 import BeautifulSoup
from tools.web.handle_files import get_file_content
import re


def google_search(query, num_results=5):
    results = []
    seen_links = set()
    for j in search(query, num_results=num_results):
        if j not in seen_links:
            seen_links.add(j)
            results.append({"link": j})
    return results

def get_content(link):
    content, content_type = get_file_content(link)
    
    if content is None or content_type == "error":
        return None
        
    if content_type in ["pdf", "binary"]:
        return content
        
    return content
    
def extract_text_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    raw_text = soup.get_text()
    
    lines = raw_text.splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    cleaned_text = '\n'.join(non_empty_lines)
    
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    
    return cleaned_text

if __name__ == "__main__":
    query = "https://en.wikipedia.org/wiki/Seawise_Giant"
    results = google_search(query, num_results=5)
    
    print("List of links:")
    for result in results:
        print(result["link"])
    
    if results:
        print("\nGetting content from the first link...")
        first_link = results[0]["link"]
        html_content = get_content(first_link)
        if html_content:
            plain_text = extract_text_from_html(html_content)
            print(f"Content from {first_link}:\n")
            print(plain_text)
        else:
            print(f"Failed to retrieve content from {first_link}")