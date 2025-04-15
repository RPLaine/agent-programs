import tools.utils.api as api
from tools.true_or_false import true_or_false

def explanation(question):

    system_prompt = """
You are an explanation agent. Your task is to provide clear, informative explanations for factual statements after determining their accuracy. Follow these guidelines:

1. First assess if the statement is factually true or false.
2. Begin your response by clearly stating "True" or "False" based on your assessment.
3. Provide a concise but thorough explanation of your reasoning behind the assessment.
4. Include relevant supporting evidence, examples, or context where applicable.
5. For statements with multiple parts, address the accuracy of each component separately.

Your output should begin with the clear binary assessment (True/False) followed by a well-structured explanation that helps users understand the factual basis for your determination.
"""

    binary_result = true_or_false(question)
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Statement: {question}

First, determine if this statement is True or False.
Then, provide a clear explanation for why it is true or false with supporting evidence.
<|im-end|>
<|im-assistant|>
"""    
    
    data = {"prompt": prompt, "max_length": 1024}
    explanation_response = api.request(data)
    
    result = {
        "binary_result": binary_result,
        "explanation": explanation_response
    }
    
    return result

if __name__ == "__main__":
    question = input("Enter a statement for evaluation and explanation: ")
    result = explanation(question)
    print(f"Binary assessment: {result['binary_result']}")
    print(f"\nExplanation:\n{result['explanation']}")
