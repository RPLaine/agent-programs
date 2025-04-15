import tools.utils.api as api

def task_extraction(text):
    system_prompt = """
You are a task extraction specialist. Your task is to analyze natural language descriptions and transform them into clear, actionable task lists. Follow these guidelines:

1. Identify distinct actions, steps, or activities in the provided text
2. Transform each identified element into a concise task statement
3. Preserve the hierarchical structure and logical flow of the original content
4. Format tasks with clear numbering or bullet points when appropriate
5. Group related tasks together under meaningful categories
6. Ensure each task is specific, actionable, and self-contained
7. Preserve any timing or sequence information from the original text

Your output should be a well-structured list of tasks that captures all the actions implied in the original description while making them explicit and actionable.
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
    data = {"prompt": prompt, "max_length": 2048}
    response = api.request(data)
    
    return response

def extract_and_prioritize(text):
    tasks = task_extraction(text)
    
    system_prompt = """
You are a task prioritization specialist. Your task is to analyze a list of tasks and prioritize them based on logical sequence, dependencies, and importance. Follow these guidelines:

1. Identify dependencies between tasks (which tasks must be completed before others)
2. Assign priority levels (High, Medium, Low) to each task
3. Group tasks by category or project phase when appropriate
4. Highlight any critical path tasks that may become bottlenecks
5. Preserve the essential content and meaning of each task

Your output should be the same list of tasks, but reorganized and annotated with priority levels to create an optimal execution sequence.
"""

    prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Task List:
{tasks}
<|im-end|>
<|im-assistant|>
"""
    data = {"prompt": prompt, "max_length": 2048}
    response = api.request(data)
    
    return {
        "original_text": text,
        "extracted_tasks": tasks,
        "prioritized_tasks": response
    }

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Task Extraction Tool")
    parser.add_argument("--file", type=str, help="Path to a file containing the description text")
    parser.add_argument("--prioritize", action="store_true", help="Also prioritize the extracted tasks")
    
    args = parser.parse_args()
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading file: {e}")
            text = input("Enter the description text: ")
    else:
        text = input("Enter the description text: ")
    
    if args.prioritize:
        result = extract_and_prioritize(text)
        print("\n=== EXTRACTED TASKS ===")
        print(result["extracted_tasks"])
        print("\n=== PRIORITIZED TASKS ===")
        print(result["prioritized_tasks"])
    else:
        tasks = task_extraction(text)
        print("\n=== EXTRACTED TASKS ===")
        print(tasks)
