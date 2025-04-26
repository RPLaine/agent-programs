system: str = f"""
Give a float value between 0.00 and 1.00.
If CLAIM is exactly true about the CONTENT, then the score should be 1.00.
If CLAIM is not true about the CONTENT, then the score should be 0.00.
If CLAIM is partially true about the CONTENT, then the score should be between 0.00 and 1.00.

Return ONLY the float value, without any additional text or explanation.
"""

assistant_start: str = """"""

prompt_dict: dict = {
    "system": system,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    for key, value in prompt_dict.items():
        print(f"{key}: {value}")