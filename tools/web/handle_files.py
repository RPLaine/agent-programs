import io
import os
import mimetypes
import PyPDF2
from urllib.parse import urlparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import ftplib
from contextlib import closing


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
                         '(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
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
        }
    
    # Handle different URL protocols
    if url.startswith(('http://', 'https://')):
        return _get_web_content(url, headers)
    elif url.startswith('file://'):
        return _get_local_file_content(url[7:])
    elif url.startswith(('ftp://', 'sftp://')):
        return _get_ftp_content(url)
    else:
        # Assume http if no protocol specified
        return _get_web_content(f"http://{url}", headers)
        
def _get_local_file_content(file_path):
    """
    Read content from a local file
    """
    try:
        if not os.path.exists(file_path):
            print(f"Local file not found: {file_path}")
            return None, "error"
        
        # Handle PDF files
        if file_path.lower().endswith('.pdf'):
            with open(file_path, 'rb') as f:
                pdf_content = f.read()
            text = extract_pdf_text(pdf_content)
            return text, "pdf"
        
        # Handle binary files
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type and any(btype in mime_type for btype in ['image/', 'audio/', 'video/', 'application/']):
            return f"[Binary content detected: {mime_type}]", "binary"
        
        # Handle text files with multiple encoding attempts
        encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings_to_try:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                
                # Determine file type
                if file_path.lower().endswith(('.html', '.htm')):
                    return content, "html"
                elif file_path.lower().endswith('.xml'):
                    return content, "xml"
                else:
                    return content, "text"
            except UnicodeDecodeError:
                continue
        
        # If we get here, none of the encodings worked - try binary mode as last resort
        with open(file_path, 'rb') as f:
            content = f.read()
        return f"[Binary content: {len(content)} bytes]", "binary"
            
    except Exception as e:
        print(f"Error accessing local file {file_path}: {e}")
        return None, "error"

def _get_ftp_content(url):
    """
    Get content from an FTP server
    """
    try:
        parsed_url = urlparse(url)
        
        # Parse the URL components
        hostname = parsed_url.hostname
        port = parsed_url.port or 21
        username = parsed_url.username or 'anonymous'
        password = parsed_url.password or 'guest@example.com'
        path = parsed_url.path
        
        if not hostname:
            print(f"Invalid FTP URL: {url}")
            return None, "error"
            
        # Connect to FTP server
        with closing(ftplib.FTP()) as ftp:
            ftp.connect(hostname, port)
            ftp.login(username, password)
            
            # Create a BytesIO object to hold the file data
            memory_file = io.BytesIO()
            
            # Retrieve the file
            try:
                ftp.retrbinary(f'RETR {path}', memory_file.write)
                memory_file.seek(0)
                content = memory_file.read()
                
                # Determine content type
                mime_type = mimetypes.guess_type(path)[0] or ""
                
                if path.lower().endswith('.pdf'):
                    text = extract_pdf_text(content)
                    return text, "pdf"
                elif mime_type and any(btype in mime_type for btype in ['image/', 'audio/', 'video/', 'application/']):
                    return f"[Binary content detected: {mime_type}]", "binary"
                else:
                    # Try to decode as text with multiple encodings
                    encodings_to_try = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
                    
                    for encoding in encodings_to_try:
                        try:
                            text_content = content.decode(encoding)
                            
                            if path.lower().endswith(('.html', '.htm')):
                                return text_content, "html"
                            elif path.lower().endswith('.xml'):
                                return text_content, "xml"
                            else:
                                return text_content, "text"
                        except UnicodeDecodeError:
                            continue
                    
                    # If no encoding worked, return as binary
                    return f"[Binary content: {len(content)} bytes]", "binary"
                    
            except ftplib.error_perm as e:
                print(f"FTP permission error: {e}")
                return None, "error"
    except Exception as e:
        print(f"FTP error: {e}")
        return None, "error"

def _get_web_content(url, headers):
    try:
        # Add custom session with retry mechanism
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        # Try to get the content, with specific handling for PHP pages
        response = session.get(url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        content_type = response.headers.get('Content-Type', '').lower()
        url_path = urlparse(url).path.lower()
        
        # Handle different content types
        if 'application/pdf' in content_type or url_path.endswith('.pdf') or 'pdf' in url_path:
            text = extract_pdf_text(response.content)
            return text, "pdf"
            
        elif 'text/html' in content_type or url_path.endswith(('.html', '.htm', '.php', '.asp', '.aspx', '.jsp')):
            # Special handling for PHP and dynamic pages
            # Ensure proper encoding detection
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                # Try to detect encoding from content
                response.encoding = response.apparent_encoding
                
            # For PHP pages specifically
            if url_path.endswith('.php'):
                # Make sure we didn't get redirected to a login page
                if "login" in response.url.lower() and "login" not in url.lower():
                    print(f"Warning: PHP page redirected to login page: {response.url}")
                
                # Try to handle session-based PHP pages
                cookies = session.cookies.get_dict()
                if cookies:
                    print(f"Session cookies found: {len(cookies)} cookies")
                    # Make a second request with established cookies if needed
                    if len(response.text) < 1000:  # If response is suspiciously short
                        try:
                            print("Short response detected, trying with established cookies...")
                            response = session.get(url, headers=headers, cookies=cookies, timeout=15)
                            response.raise_for_status()
                        except Exception as e:
                            print(f"Second request failed: {e}")
            
            return response.text, "html"
            
        elif any(txt in content_type for txt in ['text/plain', 'text/css', 'text/javascript', 'application/javascript', 'application/json']):
            return response.text, "text"
            
        elif 'text/xml' in content_type or 'application/xml' in content_type or url_path.endswith('.xml'):
            return response.text, "xml"
            
        elif is_binary_content_type(content_type):
            return f"[Binary content detected: {content_type}]", "binary"
            
        else:
            # Default to treating as HTML for unknown content types
            # Force encoding to UTF-8 as a fallback
            response.encoding = 'utf-8'
            return response.text, "html"
            
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None, "error"
    except requests.exceptions.ConnectionError as e:
        print(f"Connection Error: {e}")
        return None, "error"
    except requests.exceptions.Timeout as e:
        print(f"Timeout Error: {e}")
        return None, "error"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching content: {e}")
        return None, "error"
    except Exception as e:
        print(f"Unexpected error: {e}")
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
        '.php': 'application/x-httpd-php',
        '.asp': 'application/asp',
        '.aspx': 'application/aspx',
        '.jsp': 'application/jsp',
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
        "https://example.com/unknown",
        "https://example.com/script.php"  # Added PHP URL test
    ]
    
    print("Testing guess_file_type_from_url function:")
    for url in test_urls_for_mime:
        print(f"{url}: {guess_file_type_from_url(url)}")
    print()
    
    # Test get_file_content function with a real URL
    # Uncomment the following code to test with actual URLs
    """
    # Test with a regular HTML URL
    test_url = "https://www.example.com"
    print(f"Testing get_file_content with {test_url}")
    content, content_type = get_file_content(test_url)
    print(f"Content type: {content_type}")
    print(f"Content preview: {content[:200]}..." if content else "No content retrieved")
    
    # Test with a PHP URL
    php_url = "https://www.php.net/manual/en/function.file-get-contents.php"
    print(f"\nTesting PHP page with {php_url}")
    php_content, php_content_type = get_file_content(php_url)
    print(f"Content type: {php_content_type}")
    print(f"PHP content preview: {php_content[:200]}..." if php_content else "No PHP content retrieved")
    
    # Test with a PDF URL
    pdf_url = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
    print(f"\nTesting PDF extraction with {pdf_url}")
    pdf_content, pdf_type = get_file_content(pdf_url)
    print(f"Content type: {pdf_type}")
    print(f"PDF content preview: {pdf_content[:200]}..." if pdf_content else "No PDF content extracted")
    
    # Test with a local file (create a test.txt file first)
    # local_path = "file://d:/git/agent-programs/test.txt"  # Adjust path as needed
    # print(f"\nTesting local file with {local_path}")
    # local_content, local_type = get_file_content(local_path)
    # print(f"Content type: {local_type}")
    # print(f"Local file content: {local_content[:200]}..." if local_content else "No local content retrieved")
    
    # Test with an FTP URL (use a public FTP server)
    # ftp_url = "ftp://ftp.gnu.org/gnu/README"  # Example public FTP
    # print(f"\nTesting FTP content with {ftp_url}")
    # ftp_content, ftp_type = get_file_content(ftp_url)
    # print(f"Content type: {ftp_type}")
    # print(f"FTP content preview: {ftp_content[:200]}..." if ftp_content else "No FTP content retrieved")
    """
