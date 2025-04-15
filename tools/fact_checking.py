import tools.utils.api as api

def fact_checking(text):

    system_prompt = """
You are a fact-checking agent. Your task is to analyze the provided statements for factual accuracy. Follow these guidelines:

1. Evaluate the factual claims in the provided text.
2. Assign a confidence level to each identified factual claim (Verified, Likely True, Uncertain, Likely False, or Demonstrably False).
3. For claims that aren't fully verified, provide brief reasoning explaining your assessment.
4. Focus on objective claims rather than opinions or subjective statements.
5. Be rigorous in your assessment but acknowledge the limitations of your knowledge.

Your output should be a structured analysis that helps journalists ensure the accuracy of their reporting before publication.
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
    text = input("Enter the text to fact-check: ")
    analysis = fact_checking(text)
    print(analysis)
