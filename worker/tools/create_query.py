import json
from worker.agent import run_agent

async def main(data: dict = {}, task: str = "") -> str:
    """
    Keys needed in dictionary:
    - claim: string with claim
    - content: string with content
    - task: string with task
    - iterations: int with number of iterations
    """

    if "claim" not in data or "content" not in data or "iterations" not in data or not task:
        print("Missing required keys in data dictionary or task is empty.")
        return ""

    print(f"Creating query for task: {task}")

    user_prompt: str = f"""
CLAIM:
{data["claim"]}

CONTENT:
{data["content"]}

TASK:
{task}

What Google search query would find FACTUAL INFORMATION needed to accomplish the TASK and transform the CONTENT to match the CLAIM?
"""

    query: str = ""
    i: int = 0
    while i < data["iterations"]:
        try:
            query: str = await run_agent("create_query", user_prompt)
            break
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            i += 1
            continue

    print(f"Query created: {query}")

    return query


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