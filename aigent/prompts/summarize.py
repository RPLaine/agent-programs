system: str = """
Summarize the user message into informative text.
What is shared between different sentiments?
What are the main differences between the sentiments?
"""

user: str = """
Summarize the following content:
"""

assistant_start: str = """
"""

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")