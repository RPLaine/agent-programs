import json
from worker.agent import run_agent

async def main(data: dict) -> None:
    """
    Keys needed in dictionary:
    - tasks: list of tasks
    - tools: list of tools
    """

    tasks_with_tools: list = []

    for task in data["tasks"]:
        user_prompt: str = f"""
        TASK:
        {task}

        TOOLS:
        {data["tools"]}

        What tools can help in improving the task?
        """

        i: int = 0
        while i < data["iterations"]:
            try:
                tools: str = await run_agent("tools", user_prompt)
                tools_list: list = json.loads(tools)
                tasks_with_tools.append({
                    "task": task,
                    "tools": tools_list
                })
                break
            except Exception as e:
                print(f"Attempt {i + 1} failed: {e}")
                i += 1
                continue

    data["tasks"] = tasks_with_tools


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