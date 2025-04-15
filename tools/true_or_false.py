import tools.utils.api as api
from tools.utils.parsing import enforce_binary_output

def true_or_false(question):

    system_prompt = """
You are a binary verification agent. Your task is to evaluate statements and determine if they are factually correct or incorrect. Follow these guidelines:

1. Assess each statement carefully, considering only verifiable facts.
2. Respond with exactly one word - either "True" or "False".
3. Make your determination based on established knowledge and facts.
4. Do not include any explanations, qualifications, or additional context.
5. For ambiguous cases, apply logical reasoning to arrive at the most accurate conclusion.

Your output should be exactly one word, providing a clear binary assessment of the statement's accuracy.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{question}
<|im-end|>
<|im-assistant|>
"""    
    
    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return enforce_binary_output(response)


if __name__ == "__main__":
    question = input("Enter a question: ")
    answer = true_or_false(question)
    print(answer)