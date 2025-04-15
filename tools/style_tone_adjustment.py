import tools.utils.api as api

def style_tone_adjustment(text, target_style):

    system_prompt = """
You are a style and tone adjustment agent. Your task is to rewrite the provided text to match a specified style or tone while preserving the original meaning. Follow these guidelines:

1. Adapt the language complexity, formality, and tone to match the target style.
2. Preserve all factual information and key points from the original text.
3. Adjust vocabulary, sentence structure, and phrasing to fit the desired style.
4. Maintain the original organization and flow of ideas.
5. Ensure the adjusted text reads naturally and professionally.

Your output should be a revised version of the text that matches the requested style while retaining the original content's essence and meaning.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Original text:
{text}

Target style:
{target_style}
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)

    return response

if __name__ == "__main__":
    text = input("Enter the text to adjust: ")
    style = input("Enter the target style (e.g., formal, casual, technical, etc.): ")
    adjusted_text = style_tone_adjustment(text, style)
    print(adjusted_text)
