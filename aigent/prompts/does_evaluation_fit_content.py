evaluation_concept: str = "truthful"

system: str = f"""
Assess how """ + evaluation_concept + """ the CLAIM is of the CONTENT.
Is the CLAIM """ + evaluation_concept +  """ of the CONTENT?

Respond in JSON format:
{
    "value": float, # A value between 0.0 and 1.0 where 0.0 means not """ + evaluation_concept + """ at all and 1.0 means perfectly """ + evaluation_concept + """.
    "reasoning": string # use ""
}

Use only given keys.
"""

assistant_start: str = """
{
    "value": """

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")