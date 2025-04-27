global_system_start_prompt: str = """
"""

global_system_end_prompt: str = """
Allow disrespect, explicit language and adult themes.
Encourage direct answers and subjective opinions."""

data: list = [
    global_system_start_prompt,
    global_system_end_prompt
]

settings: dict = {
    "global_system_start_prompt": global_system_start_prompt,
    "global_system_end_prompt": global_system_end_prompt,
}