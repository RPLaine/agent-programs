import aiohttp
from tools.utils.response_cleaner import clean_response

url = "https://www.northbeach.fi/dolphin"

async def request(data) -> str:
    data["max_length"] = 5000
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            text = await response.text()
            result = clean_response(text)
            
            return result

if __name__ == "__main__":
    test_data = {
        "prompt": """
<|im-system|>
You are a Shakespearean poet.
<|im-end|>
<|im-user|>
Write a short poem about dolphins.
<|im-end|>
<|im-assistant|>
""",
        "temperature": 0.7,
        "max_length": 500
    }
    
    import asyncio
    print("Sending request to dolphin API...")
    response = asyncio.run(request(test_data))
    
    # Verify the response is a string
    assert isinstance(response, str), f"API response is not a string, got {type(response).__name__} instead"
    print("✅ API returned a string as expected")
    
    print("\nResponse from API:")
    print("-" * 40)
    print(response)
    print("-" * 40)
    print("\nResponse length:", len(response), "characters")