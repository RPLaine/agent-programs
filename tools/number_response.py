import tools.utils.api as api
from tools.utils.parsing import enforce_number_output

def get_number(question):
    system_prompt = """
You are a numerical response agent. Your task is to analyze questions and provide a single numerical answer. Follow these guidelines:

1. Analyze the question to determine what numerical value is being requested.
2. Respond with only a number - no units, explanations, or additional text.
3. For questions with definitive numerical answers, provide the exact value.
4. For estimation questions, provide a reasonable numerical estimate.
5. If a range would be appropriate, provide the middle value of that range.

Your output should be exactly one number, providing a clear numerical response to the question.
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
    
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)
    
    return enforce_number_output(response)

if __name__ == "__main__":
    question = input("Enter a question that requires a numerical answer: ")
    answer = get_number(question)
    print(answer)
