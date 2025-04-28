import json
from worker.agent import run_agent

async def main(data: dict = {}, new_data: str = "", task: str = "") -> str:
    """
    Keys needed in dictionary:
    - claim: string with claim
    - content: string with content
    - new_data: dictionary with new data
    - task: string with task
    - iterations: int with number of iterations
    """

    if "claim" not in data or "content" not in data or "iterations" not in data or not new_data or not task:
        print("ERROR: Missing required keys in data dictionary or new_data or task is empty.")
        return ""

    print(f"Improving content: {task}")

    user_prompt: str = f"""
CLAIM:
{data["claim"]}

CONTENT:
{data["content"]}

DATA:
{new_data}

TASK:
{task}

How can the CONTENT be improved to better match the CLAIM by incorporating factual information from the DATA according to the TASK?
"""

    improved_content: str = ""
    i: int = 0
    while i < data["iterations"]:
        try:
            improved_content: str = await run_agent("improve_content", user_prompt)
            break
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            i += 1
            continue

    print(f"Improved content created: {improved_content}")

    return improved_content


if __name__ == "__main__":
    import asyncio
    import json

    data: dict = {
        "tasks": [
            "Change the statement about the Earth's shape to align with scientific consensus.",
            "Replace 'The sky is green' with a more accurate and descriptive phrase about the sky's color.",
            "Revise the statement about the sun's direction to match the correct observation."
            ],
        "tools": [
            "Let AI do a web search", 
            "Let AI do search RSS feeds", 
            "Let a journalist to take a photo", 
            "Let a journalist to interview a person"
            ],
        "iterations": 3
    }

    asyncio.run(main(data))
    print(json.dumps(data, indent=4))