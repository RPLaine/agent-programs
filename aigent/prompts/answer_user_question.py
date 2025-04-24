system: str = """
Answer the question.
What is the best answer for the question?

Respond in JSON format:
{
    "answer_for_the_user": string
}

Use only given keys.
"""

assistant_start: str = """
{
    "answer_for_the_user": """

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")