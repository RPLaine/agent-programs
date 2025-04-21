import llm.api as api

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

def send_llm_request(prompt: str) -> str:
    data = {"prompt": prompt}
    
    try:
        response = api.request(data)
        return response
    except Exception:
        raise
