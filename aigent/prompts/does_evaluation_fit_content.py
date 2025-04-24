evaluation_concept: str = "truthful"

system: str = f"""
Assess how """ + evaluation_concept + """ the EVALUATION is of the CONTENT.
Does the EVALUATION describe the CONTENT well?

Respond in JSON format:
{
    "assessment": float, # A value between 0.0 and 1.0 where 0.0 means not """ + evaluation_concept + """ at all and 1.0 means perfectly """ + evaluation_concept + """.
    "reasoning": string
}

Use only given keys.
"""

assistant_start: str = """
{
    "assessment": """

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")