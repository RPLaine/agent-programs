import tools.utils.api as api

async def distill_text(text, focus=""):
    """
    Distill key information from text with a specific focus.
    
    Args:
        text (str): The text to distill information from
        focus (str): Optional focus area for the distillation
        
    Returns:
        str: The distilled information
    """
    print(f"🧪 Distilling information from text ({len(text)} characters)")
    if focus:
        print(f"  ├─ Focus area: \"{focus}\"")
    
    system_prompt = f"""
You are an information distillation specialist. Your task is to analyze text and extract the most essential and relevant information with a specific focus. Follow these guidelines:

1. Focus specifically on information related to: "{focus}"
2. Extract only the most important and relevant facts, insights, and findings.
3. Prioritize accuracy and factual correctness over comprehensiveness.
4. Present the information in a clear, structured manner.
5. Maintain objectivity and avoid inserting opinions or speculation.
6. Ensure the distilled information represents the core essence of the original content.
7. Exclude tangential or irrelevant details that don't directly address the focus area.

Your output should be a concise collection of the most critical information from the source text, directly addressing the specified focus area.
"""

    print(f"  ├─ Processing text with AI model...")
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Please distill the following text, focusing on information related to: "{focus}"

{text}

Respond with only one message.
<|im-end|>
<|im-assistant|>
"""
 
    data = {"prompt": prompt, "max_length": 5000}
    response = await api.request(data)
    result = response.strip()
    
    print(f"  └─ Information distilled: {len(result)} characters")
    return result

if __name__ == "__main__":
    import asyncio
    
    text = """
    [Your test text here]
    """
    
    result = asyncio.run(distill_text(text, "key information"))
    print(result)
