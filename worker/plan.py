import json
from worker.agent import run_agent
from worker.tools.choose_tools import main as choose_tools


async def main(data: dict = {}) -> None:
    user_prompt: str = f"""
    CLAIM: 
    {data["claim"]}

    CONTENT: 
    {data["content"]}

    How can the content be improved to meet the claim?
    """

    i = 0
    while i < data["iterations"]:
        try:
            task_list: dict = json.loads(await run_agent("plan", user_prompt))
            tasks: list = task_list["tasks"]
            data["tasks"] = tasks
            break
        except Exception as e:
            print(f"Attempt {i + 1} failed: {e}")
            i += 1
            continue

    if "tasks" in data and "tools" in data:
        await choose_tools(data)
    else:
        data["error"] = "Failed to generate tasks after multiple attempts."


if __name__ == "__main__":
    import asyncio
    import json

    data: dict = {
        "claim": "a good task list for improving the content towards a truth",
        "content": "The Earth is flat. The sky is green. The sun rises in the west.",
        "iterations": 3,
        "tools": [
            "Let AI do a web search",
            "Let AI search RSS feeds",
            "Let a journalist take a photo",
            "Let a journalist interview a person"
            ]
    }

    asyncio.run(main(data))
    print(json.dumps(data, indent=4))