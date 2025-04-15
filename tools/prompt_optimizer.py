import tools.utils.api as api
import tools.topic_classification as topic_classification

def optimize_system_prompt(prompt_input, query):
    query_context = topic_classification.topic_classification_with_websearch(query)
    print(f"[INFO] 🔍 Query context: {query_context}")
    if not query_context:
        query_context = "No relevant context found."

    system_prompt = """
You are a system prompt optimization specialist. Your task is to enhance and refine system prompts to increase their effectiveness, clarity, and impact. Follow these guidelines:

1. Improve the structure and organization of the prompt for better readability
2. Enhance the clarity of instructions and guidelines
3. Add specific, actionable directions that lead to better outputs
4. Remove ambiguous or redundant language
5. Ensure the prompt covers all necessary aspects of the task
6. Add relevant constraints or parameters that improve output quality
7. Format the prompt for optimal understanding and implementation
8. Preserve the original intent and core functionality
9. Balance conciseness with completeness
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Original system prompt:
{prompt_input}

Query context:
{query_context}

Change the original system prompt to make better search queries based on the query context and topic classification.
Create only one message.
<|im-end|>
<|im-assistant|>
"""

    data = {"prompt": prompt, "max_length": 5000}
    response = api.request(data)
    
    return response.strip()


if __name__ == "__main__":
    print("System Prompt Optimizer")
    print("----------------------")
    print("This tool optimizes system prompts to improve clarity, effectiveness, and impact.")
    print()
      # Get user inputs
    original_prompt = """
You are a query enhancement specialist. Your task is to transform user inputs into more effective formats that produce better results. Follow these guidelines:

1. Identify the core information need or intent
2. Adapt your approach based on the subject matter and context
3. Add relevant qualifiers and modifiers that improve result quality
4. Increase specificity while preserving the original intent
5. Structure the output to prioritize relevance and accuracy
6. Remove unnecessary elements and focus on key concepts
7. Apply appropriate formatting techniques when beneficial
"""
    query = input("Enter a query to provide context (optional): ")
    
    # Use default query if none provided
    if not query:
        query = "Who is Jesus Christ?"
        print(f"Using default query: '{query}'")
    
    print("\nOptimizing prompt, please wait...")
    optimized_prompt = optimize_system_prompt(original_prompt, query)
    
    print("\nOptimized Prompt:")
    print("-----------------")
    print(optimized_prompt)