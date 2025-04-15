import tools.utils.api as api

def enhance_input(input_text):
    system_prompt = """
You are an input enhancement specialist. Your task is to analyze a user's input statement or question and improve it for better search effectiveness and factual verification. Follow these guidelines:

1. Make the statement more specific and precise
2. Remove ambiguity and vague language
3. Rewrite the input to be a clear factual statement that can be verified
4. Maintain the original intent and meaning
5. Remove unnecessary words and improve clarity
6. Do not add new facts or change the meaning
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Input: {input_text}

Please enhance this input to be more precise, specific, and suitable for factual verification. Return only the enhanced statement without any additional text.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)
    
    return response.strip()

def enhance_and_verify(input_text):
    from binary_websearch import binary_websearch
    
    enhanced_input = enhance_input(input_text)
    print(f"Original input: {input_text}")
    print(f"Enhanced input: {enhanced_input}")
    
    result = binary_websearch(enhanced_input)
    
    return {
        "original_input": input_text,
        "enhanced_input": enhanced_input,
        "verification_result": result
    }

if __name__ == "__main__":
    user_input = input("Enter a statement or question for verification: ")
    result = enhance_and_verify(user_input)
    print(f"\nVerification result: {result['verification_result']}")
