import llm.api as api
import time

def generate_prompt(system_prompt: str, user_prompt: str) -> str:
    return f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{user_prompt}
<|im-end|>
<|im-assistant|>
"""

def send_llm_request(prompt: str, max_retries: int = 3, timeout: int = 300):
    data = {"prompt": prompt}

    for attempt in range(max_retries):
        try:
            print(f"Sending LLM request (attempt {attempt+1}/{max_retries})...")
            response = api.request(data, timeout=timeout)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"API request failed: {str(e)}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                error_msg = f"Failed to connect to LLM API after {max_retries} attempts: {str(e)}"
                print(error_msg)
                raise ConnectionError(error_msg)
