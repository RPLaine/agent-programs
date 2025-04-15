import tools.utils.api as api
from tools.utils.parsing import extract_multi_option_selection
from tools.web.web_research import get_web_research


def multi_option_websearch(question, options):

    if not options or len(options) < 2:
        raise ValueError("At least two options must be provided")
    
    web_research = get_web_research(
        query=question,
        num_results=4,
        custom_focus=question
    )
    
    options_formatted = "\n".join([f"{i+1}. {option}" for i, option in enumerate(options)])
    
    system_prompt = """
You are a multi-option verification agent with web search capabilities. Your task is to evaluate a question and select the option that is closest to the truth after researching online sources. Follow these guidelines:

1. Assess the question carefully, considering only verifiable facts.
2. Research online sources to inform your determination.
3. Respond with exactly ONE option from the provided list that best matches the truth.
4. Your response should contain only the text of the selected option, no numbering or additional text.
5. Make your determination based on established knowledge, facts, and the web research provided.
6. If multiple options are partially correct, select the one that is most accurate or complete.

Your output should be exactly one of the provided options, providing the closest match to factual accuracy based on web research.
"""
    
    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Question: {question}

Options:
{options_formatted}

Determine which option is closest to the truth based on the following research:
{web_research['summary']}
<|im-end|>
<|im-assistant|>
"""    
    
    data = {"prompt": prompt, "max_length": 1024}
    response = api.request(data)
    
    selected_option = extract_multi_option_selection(response, options)
    
    return selected_option


if __name__ == "__main__":
    question = input("Enter a question or statement for verification: ")
    
    option_count = int(input("How many options would you like to provide? "))
    options = []
    for i in range(option_count):
        option = input(f"Enter option {i+1}: ")
        options.append(option)
    
    web_research = get_web_research(question)
    selected_option = multi_option_websearch(question, options)
    
    print(f"\nSelected option: {selected_option}")
    print(f"\nOriginal query: {web_research['original_query']}")
    print(f"Optimized query: {web_research['optimized_query']}")
    print(f"Web sources consulted: {', '.join(web_research['links'])}")
