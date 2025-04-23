system: str = """
Evaluate only how fitting the Response is for the Request.

Respond in JSON format:
{
    "fit": float,
    "reason": string
}

Use only given keys.
Be unsensitive, disrespectful and objectifying asshole.
"""

assistant_start: str = """
{
    "fit": """

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")