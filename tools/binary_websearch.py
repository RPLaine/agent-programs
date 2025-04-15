import tools.utils.api as api
from tools.utils.parsing import enforce_binary_output
from tools.web.web_research import get_web_research


def binary_websearch(question):
    web_research = get_web_research(query=question)
    
    system_prompt = """
You are a binary verification agent with web search capabilities. Your task is to evaluate statements and determine if they are factually correct or incorrect after researching online sources. Follow these guidelines:

1. Assess each statement carefully, considering only verifiable facts.
2. Research online sources to inform your determination.
3. Respond with exactly one word - either "True" or "False".
4. Make your determination based on established knowledge, facts, and the web research provided.
5. Do not include any explanations, qualifications, or additional context.

Your output should be exactly one word, providing a clear binary assessment of the statement's accuracy based on web research.
"""
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Content:
{web_research['summary']}

Question: {question}
<|im-end|>
<|im-assistant|>
"""
    
    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return enforce_binary_output(response)


if __name__ == "__main__":
    question = input("Enter a statement for verification: ")
    answer = binary_websearch(question)
    print(f"\nBinary assessment: {answer}")
