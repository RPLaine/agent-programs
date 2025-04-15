import tools.utils.api as api
from tools.web.web_research import get_web_research

def explanation_with_websearch(question):
    web_research = get_web_research(query=question)
    
    system_prompt = """
You are an explanation agent with web search capabilities. Your task is to provide clear, informative explanations for factual statements after determining their accuracy and researching online sources. Follow these guidelines:

1. First assess if the statement is factually true or false.
2. Begin your response by clearly stating "True" or "False" based on your assessment.
3. Provide a concise but thorough explanation of your reasoning behind the assessment.
4. Reference the web search results that support your explanation.
5. Include relevant supporting evidence, examples, or context from the web search.
6. For statements with multiple parts, address the accuracy of each component separately.

Your output should begin with the clear binary assessment (True/False) followed by a well-structured explanation that helps users understand the factual basis for your determination, with support from web research data.
"""
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Summary of web content:
{web_research['summary']}

Question: {question}

First, determine if this statement is True or False.
Then, provide a clear explanation for why it is true or false with supporting evidence.
Create only one message.
<|im-end|>
<|im-assistant|>
"""    
    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)
    
    result = {
        "result": response,
        "web_research": web_research
    }
    
    return result

if __name__ == "__main__":
    question = input("Enter a statement for evaluation and explanation: ")
    result = explanation_with_websearch(question)
    print(f"\nEvaluation and Explanation: {result['result']}")
