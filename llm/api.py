# filepath: d:\git\agent-programs\llm\api.py
import requests
from tools.utils.response_cleaner import clean_response

url = "https://www.northbeach.fi/dolphin"

def request(data, timeout=300) -> str:
    data["max_length"] = data.get("max_length", 64000)
    
    try:
        response = requests.post(url, json=data, timeout=timeout)
        response.raise_for_status()
        response.encoding = 'utf-8'
        result = clean_response(response.text)
        return result
    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 502:
            raise ConnectionError(f"LLM API server returned 502 Bad Gateway. The service may be down or overloaded.")
        raise ConnectionError(f"HTTP Error: {err}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError(f"Failed to connect to LLM API at {url}. Check your internet connection or the API endpoint.")
    except requests.exceptions.Timeout:
        raise ConnectionError(f"Request to LLM API timed out after {timeout} seconds.")
    except requests.exceptions.RequestException as err:
        raise ConnectionError(f"Request error: {err}")

if __name__ == "__main__":
    test_data = {
        "prompt": """
<|im-system|>
You are a Shakespearean poet.
<|im-end|>
<|im-user|>
Write a very long poem about dolphins.
<|im-end|>
<|im-assistant|>
"""
    }
    
    print("Sending request to dolphin API...")
    response = request(test_data)
    
    # Verify the response is a string
    assert isinstance(response, str), f"API response is not a string, got {type(response).__name__} instead"
    print("✅ API returned a string as expected")
    
    print("\nResponse from API:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    print("\nResponse length:", len(response), "characters")