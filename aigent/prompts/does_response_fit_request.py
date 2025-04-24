system: str = """
Evaluate only how fitting the Response is for the Request.
Is the Response a good response in relation to the Request?

Respond in JSON format:
{
    "evaluation": float,
    "reasoning": string
}

Use only given keys.
"""

assistant_start: str = """
{
    "evaluation": """

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")