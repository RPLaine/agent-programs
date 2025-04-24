concept: str = "'VALUE'"

system: str = """
Create a list of possiblities from the """ + concept + """.

Respond in JSON format:
{
    "possibilities": [
        "The content is """ + concept + """ and fully meets the requirements.",
        "The content is """ + concept + """ but needs some improvements.",
        "The content is not """ + concept + """ yet, but could be modified to meet this criterion.",
        "The content is not """ + concept + """ and cannot be reasonably modified to meet this criterion."
    ]
}

Change only the """ + concept + """ to the given KEY.
"""

assistant_start: str = """
{
    "possibilities": [
        "It is TRUE that content is"""

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")