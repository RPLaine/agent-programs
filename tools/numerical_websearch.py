import tools.utils.api as api
from tools.utils.parsing import enforce_number_output
from tools.web.web_research import get_web_research


def numerical_websearch(question):    # Call the refactored get_web_research with parameters specific to numerical websearch
    web_research = get_web_research(
        query=question, 
        num_results=3,
        custom_focus=question  # Focus summarization on the numerical query
    )
    
    system_prompt = """
You are a numerical response agent with web search capabilities. Your task is to analyze questions and provide a single numerical answer based on web research. Follow these guidelines:

1. Carefully analyze the web research to determine the numerical value being requested.
2. Respond with only a number - no units, explanations, or additional text.
3. For questions with definitive numerical answers in the web research, provide the exact value.
4. For estimation questions, provide a reasonable numerical estimate based on the web research.
5. If a range is mentioned in the web research, provide the middle value of that range.
6. Use the most recent, accurate data available in the provided web research.
7. If multiple numbers are found, determine which one most directly answers the question.

Your output should be exactly one number, providing a clear numerical response to the question based on web research.
"""
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Question: {question}

Please provide a numerical answer based on the following web research:
{web_research['summary']}
<|im-end|>
<|im-assistant|>
"""    
    
    data = {"prompt": prompt, "max_length": 512}
    response = api.request(data)
    
    return enforce_number_output(response)


if __name__ == "__main__":
    question = input("Enter a question that requires a numerical answer from web search: ")
    answer = numerical_websearch(question)
    print(f"Numerical answer: {answer}")
