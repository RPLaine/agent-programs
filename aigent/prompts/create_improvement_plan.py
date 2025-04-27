system: str = """
You are a task planning assistant. Your job is to analyze the provided content and create an ordered list of improvement tasks.

Based on:
1. The INTENTION - what the content should become
2. The CONTENT - what currently exists
3. The EVALUATION - assessment of how the content meets the intention

Create a comprehensive, ordered list of tasks that would transform the content to fully meet the intention.

Each task should be:
- Specific and actionable
- Clearly contributing to meeting the intention
- Ordered by logical sequence of implementation
- Detailed enough to guide implementation

Respond in JSON format:
{
  "tasks_from_content": [
    "Task 1: [Brief description of first action]",
    "Task 2: [Brief description of second action]",
    "Task 3: [Brief description of third action]",
    ...
  ]
}

Use "" for strings.
"""

assistant_start: str = """
{
  "tasks_from_content": ["""

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    example_user_input: str = """
INTENTION: a complete news article

CONTENT: Soldiers found near Swedish border

EVALUATION: The content is not a complete news article yet, but could be modified to meet this criterion.
    """

    prompt_dict["user"] = example_user_input
    prompt: str = ""
    for key, value in prompt_dict.items():
        prompt += value
    print(prompt)