from tools.web.google_search import get_content

def test_page(url):
    print(f"Attempting to fetch: {url}")
    content = get_content(url)
    
    if content:
        print(f"Success! Retrieved {len(content)} characters.")
        print(f"First 200 characters of content:\n{content[:200]}...")
    else:
        print(f"Failed to retrieve content from {url}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_page(sys.argv[1])
    else:
        print("Usage: python test_get_page.py <url>")
        print("Example: python test_get_page.py https://www.example.com")
