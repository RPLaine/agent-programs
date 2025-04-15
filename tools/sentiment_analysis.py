import tools.utils.api as api

def sentiment_analysis(text):

    system_prompt = """
You are a sentiment analysis agent. Your task is to analyze the emotional tone and sentiment of the provided text. Follow these guidelines:

1. Identify the overall sentiment of the text (Positive, Negative, Neutral, or Mixed).
2. Rate the intensity of the sentiment on a scale from 1-5 (1 being subtle, 5 being extreme).
3. Highlight specific words or phrases that strongly indicate sentiment.
4. Identify any shifts in sentiment throughout the text.
5. Note any sarcasm, irony, or other complex emotional elements that may affect sentiment interpretation.

Your output should provide a nuanced understanding of the emotional context and tone of the text, helping journalists understand how their content might be perceived by readers.
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
    text = input("Enter the text for sentiment analysis: ")
    analysis = sentiment_analysis(text)
    print(analysis)
