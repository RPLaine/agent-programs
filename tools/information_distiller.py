import tools.utils.api as api

def detect_extraction_goal(input_text):

    system_prompt = """
You are a text analysis specialist. Your task is to identify what information should be extracted from this text.
The text may contain an explicit question, request, or information need. 
Analyze the text and determine a clear, concise extraction goal that reflects what information is being sought.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Text: {input_text}

Please determine what extraction goal should be used for this text. 
Respond with a clear, concise statement of what information should be extracted.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return response

def distill_text(input_text, extraction_goal=None):

    if extraction_goal is None:
        extraction_goal = detect_extraction_goal(input_text)
    
    system_prompt = """
You are a text distillation specialist. Your task is to extract specific information from text that contains additional or irrelevant content. Follow these guidelines:

1. Focus only on the specific information requested in the extraction goal
2. Remove all irrelevant content, padding, and unnecessary text
3. Preserve the exact wording of the relevant information when possible
4. Structure your output to be clean and direct
5. If the requested information is not present, return None
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Text: {input_text}

Extraction goal: {extraction_goal}

Please extract only the specific information requested from the text. Remove all irrelevant content and provide only what was requested.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return response.strip()

def extract_key_information(input_text, extraction_goal=None):

    if extraction_goal is None:
        extraction_goal = detect_extraction_goal(input_text)
        
    distilled_result = distill_text(input_text, extraction_goal)
    
    return {
        "original_text": input_text,
        "extraction_goal": extraction_goal,
        "distilled_result": distilled_result
    }

if __name__ == "__main__":
    user_text = input("Enter the text to process: ")
    
    result = extract_key_information(user_text)
    
    print(f"\nAutomatically detected extraction goal: {result['extraction_goal']}")
    print(f"Distilled result: {result['distilled_result']}")
