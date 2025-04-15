import requests
from tools.utils.api import request, url
import sys

def test_encoding():
    """
    Test how the API handles Finnish characters and fix encoding issues
    """
    print(f"System default encoding: {sys.getdefaultencoding()}")
    
    # Test with Finnish characters
    test_data = {
        "prompt": "Write a short sentence with Finnish characters: ä, ö, å",
        "max_tokens": 100
    }
    
    # Method 1: Using the existing API function
    print("\nMethod 1: Using existing API function")
    result = request(test_data)
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    
    # Method 2: Direct API call with explicit encoding
    print("\nMethod 2: Direct API call with explicit encoding")
    response = requests.post(url, json=test_data)
    print(f"Response encoding: {response.encoding}")
    response.encoding = 'utf-8'  # Force UTF-8 encoding
    content = response.text.split("<|im-assistant|>")[-1].strip()
    if "<|im-end|>" in content:
        content = content.split("<|im-end|>")[0].strip()
    print(f"Result: {content}")
    
    # Method 3: Using bytes and explicit encoding
    print("\nMethod 3: Using bytes and explicit decoding")
    response = requests.post(url, json=test_data)
    raw_bytes = response.content
    decoded_text = raw_bytes.decode('utf-8')
    content = decoded_text.split("<|im-assistant|>")[-1].strip()
    if "<|im-end|>" in content:
        content = content.split("<|im-end|>")[0].strip()
    print(f"Result: {content}")
    
    return {
        "original": result,
        "force_utf8": content
    }

def improved_request(data):
    """
    Enhanced version of the request function with proper encoding handling
    """
    response = requests.post(url, json=data)
    # Force UTF-8 encoding for proper handling of Finnish characters
    response.encoding = 'utf-8'
    content = response.text.split("<|im-assistant|>")[-1].strip()
    if "<|im-end|>" in content:
        content = content.split("<|im-end|>")[0].strip()
    return content

if __name__ == "__main__":
    print("Testing LLM API with Finnish characters")
    results = test_encoding()
    
    print("\n--- Testing the improved request function ---")
    test_data = {
        "prompt": "Say 'Hello' in Finnish",
        "max_tokens": 50
    }
    result = improved_request(test_data)
    print(f"Improved result: {result}")
