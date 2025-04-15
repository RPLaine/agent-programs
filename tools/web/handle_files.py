import io
import mimetypes
import PyPDF2
from urllib.parse import urlparse
import requests


def is_pdf_url(url):
    parsed = urlparse(url)
    path = parsed.path.lower()
    return path.endswith('.pdf') or 'pdf' in path


def is_binary_content_type(content_type):
    binary_types = ['image/', 'audio/', 'video/', 'application/']
    return any(btype in content_type for btype in binary_types)


def extract_pdf_text(pdf_content):
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text() + "\n"
        
        return text
    except Exception as e:
        print(f"Failed to extract PDF content: {e}")
        return None


def get_file_content(url, headers=None):
    if headers is None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                         '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    try:
        response = requests.get(url, headers=headers, timeout=10, stream=True)
        if response.status_code != 200:
            return None, "error"
        
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'application/pdf' in content_type or is_pdf_url(url):
            text = extract_pdf_text(response.content)
            return text, "pdf"
        
        elif is_binary_content_type(content_type):
            return f"[Binary content detected: {content_type}]", "binary"
        
        else:
            return response.text, "html"
            
    except Exception as e:
        print(f"Error fetching content: {e}")
        return None, "error"


def guess_file_type_from_url(url):
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    guess_type = mimetypes.guess_type(path)
    if guess_type[0]:
        return guess_type[0]
    
    extensions_map = {
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    }
    
    for ext, mime_type in extensions_map.items():
        if path.lower().endswith(ext):
            return mime_type
    
    return None


if __name__ == "__main__":
    # Test is_pdf_url function
    test_urls = [
        "https://example.com/document.pdf",
        "https://example.com/files/sample.pdf?download=true",
        "https://example.com/download/pdf/123",
        "https://example.com/document.html"
    ]
    
    print("Testing is_pdf_url function:")
    for url in test_urls:
        print(f"{url}: {is_pdf_url(url)}")
    print()
    
    # Test guess_file_type_from_url function
    test_urls_for_mime = [
        "https://example.com/document.pdf",
        "https://example.com/spreadsheet.xlsx",
        "https://example.com/presentation.pptx",
        "https://example.com/document.docx",
        "https://example.com/image.jpg",
        "https://example.com/unknown"
    ]
    
    print("Testing guess_file_type_from_url function:")
    for url in test_urls_for_mime:
        print(f"{url}: {guess_file_type_from_url(url)}")
    print()
    
    # Test get_file_content function with a real URL
    # Uncomment the following code to test with actual URLs
    """
    test_url = "https://www.example.com"
    print(f"Testing get_file_content with {test_url}")
    content, content_type = get_file_content(test_url)
    print(f"Content type: {content_type}")
    print(f"Content preview: {content[:200]}..." if content else "No content retrieved")
    
    # Test with a PDF URL
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    print(f"\nTesting PDF extraction with {pdf_url}")
    pdf_content, pdf_type = get_file_content(pdf_url)
    print(f"Content type: {pdf_type}")
    print(f"PDF content preview: {pdf_content[:200]}..." if pdf_content else "No PDF content extracted")
    """
