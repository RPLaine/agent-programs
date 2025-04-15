import tools.utils.api as api

def quote_extraction(text):

    system_prompt = """
You are a quote extraction agent. Your task is to identify and extract meaningful quotations from interviews, speeches, or articles. Follow these guidelines:

1. Extract all direct quotes from the text, preserving their exact wording.
2. For each quote, identify the speaker when available.
3. Provide brief context for each quote to enhance understanding.
4. Prioritize quotes that are impactful, insightful, or highlight key points.
5. Organize quotes thematically or chronologically when appropriate.

Your output should be a structured collection of the most significant quotes from the text, making it easy for journalists to incorporate compelling human voices into their stories.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{text}
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)

    return response

if __name__ == "__main__":
    text = input("Enter the text for quote extraction: ")
    quotes = quote_extraction(text)
    print(quotes)
