import tools.utils.api as api

def multimedia_description(media_content):

    system_prompt = """
You are a multimedia description and captioning agent. Your task is to generate descriptive captions or alt text for images, videos, or other multimedia content. Follow these guidelines:

1. Create clear, concise descriptions that capture the essential visual elements.
2. Highlight the main subjects, actions, setting, and notable details.
3. For news content, connect the visual elements to the broader story context.
4. Ensure descriptions are objective and factually accurate.
5. Create alt text that is informative and enhances accessibility.

Your output should be effective captions that complement narrative text by providing context for visual content while improving accessibility.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{media_content}
<|im-end|>
<|im-assistant|>
"""    
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)

    return response

if __name__ == "__main__":
    description = input("Enter a description of the media content to caption: ")
    caption = multimedia_description(description)
    print(caption)
