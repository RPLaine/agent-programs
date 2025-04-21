import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
    
    
def clean_response(response) -> str:
    if "<|im-assistant|>" in response:
        response = response.split("<|im-assistant|>")[-1]
    special_tokens = ["<|im-assistant|>", "<|im-end|>", "<|im-user|>", "<|im-system|>"]
    for token in special_tokens:
        response = response.replace(token, "")
    return response.strip()

# Create a name main test
if __name__ == "__main__":
    test_data = {
        "prompt": "What is the capital of France in json format?"
    }
    
    try:
        response = request(test_data)
        print("LLM Response:")
        print(response)
    except ConnectionError as e:
        print(f"Connection error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    finally:
        print("Finished LLM request process.")
        print("Exiting...")