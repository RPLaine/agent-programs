import tools.utils.api as api
import tools.prompt_optimizer as prompt_optimizer

def optimize_query(query):
    system_prompt_old = """
You are a search query optimization specialist. Your task is to transform user queries into effective search terms that yield high-quality, trustworthy sources. Follow these guidelines:

1. Identify the core information need in the query
2. Add terms that target scientific and academic sources when appropriate
3. Include terms like "research", "study", "journal", "peer-reviewed" for academic topics
4. Add specificity to vague queries while preserving the original intent
5. Structure the query to prioritize authoritative sources
6. Remove unnecessary words and focus on key concepts
7. Format complex queries using advanced search operators when beneficial
"""

    system_prompt = """
You are a query enhancement specialist. Your task is to transform user inputs into more effective formats that produce better results. Follow these guidelines:

1. Identify the core information need or intent
2. Adapt your approach based on the subject matter and context
3. Add relevant qualifiers and modifiers that improve result quality
4. Increase specificity while preserving the original intent
5. Structure the output to prioritize relevance and accuracy
6. Remove unnecessary elements and focus on key concepts
7. Apply appropriate formatting techniques when beneficial
"""

    system_prompt = prompt_optimizer.optimize_system_prompt(system_prompt, query)

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Original query: {query}

Return only the optimized query without any additional text.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return response.strip()


if __name__ == "__main__":
    user_query = input("Enter your search query: ")
    results = optimize_query(user_query)
    print(f"Optimized query: {results}")
