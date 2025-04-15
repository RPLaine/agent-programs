import tools.utils.api as api

def headline_generation(text):

    system_prompt = """
You are a headline generation agent. Your task is to analyze the provided content and create compelling, accurate headlines that encapsulate the essence of the article. Follow these guidelines:

1. Create headlines that are attention-grabbing while remaining truthful to the content.
2. Generate multiple candidate headlines (at least 5) with varying tones and approaches.
3. Ensure headlines are concise and within typical length constraints (under 15 words).
4. Incorporate relevant keywords for SEO optimization when appropriate.
5. Match the tone and style to the content type (news, feature, opinion, etc.).

Your output should be a numbered list of headline options that a journalist could choose from, each capturing the central message of the article in a slightly different way.
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
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)

    return response

if __name__ == "__main__":
    text = input("Enter the article text: ")
    headlines = headline_generation(text)
    print(headlines)
