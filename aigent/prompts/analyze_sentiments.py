system: str = """
Analyze the list of sentiments.
What is shared between the sentiments?
What is different between the sentiments?
"""

user: str = """"""

assistant_start: str = """"""

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")