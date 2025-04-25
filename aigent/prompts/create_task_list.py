system: str = """
Create a task list from the request.
In what ordered tasks can be derived?

Respond in JSON format:
{
  "tasks_from_content": [
    string,
    string,
    string,
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
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")