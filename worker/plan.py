import json
from worker.agent import run_agent
from worker.tools.choose_tools import main as choose_tools


async def main(data: dict = {}) -> None:
    print(f"\n{'='*50}")
    print(f"📝 STARTING PLANNING MODULE")
    print(f"🎯 Planning improvements for claim: '{data['claim']}'")
    print(f"{'='*50}")
    
    user_prompt: str = f"""
    CLAIM: 
    {data["claim"]}

    CONTENT: 
    {data["content"][-1]}

    How can the content be improved to meet the claim?
    """

    print(f"🧠 Generating improvement tasks...")
    
    i = 0
    while i < data["iterations"]:
        try:
            print(f"  ├─ Attempt {i+1}/{data['iterations']} to generate tasks")
            task_list: dict = json.loads(await run_agent("plan", user_prompt))
            tasks: list = task_list["tasks"]
            data["tasks"] = tasks
            print(f"  ✅ Successfully generated {len(tasks)} tasks")
            break
        except Exception as e:
            print(f"  ❌ Attempt {i + 1} failed: {e}")
            i += 1
            continue

    if "tasks" in data and "tools" in data:
        print(f"🔧 Assigning tools to {len(data['tasks'])} tasks...")
        await choose_tools(data)
        print(f"✅ Tools assigned successfully")
    else:
        error_msg = "Failed to generate tasks after multiple attempts."
        data["error"] = error_msg
        print(f"❌ ERROR: {error_msg}")

    data["action"] = "work"
    print(f"🔄 Setting next action to: WORK")
    
    print(f"\n{'='*50}")
    print(f"🏁 PLANNING MODULE COMPLETED")
    print(f"{'='*50}")


if __name__ == "__main__":
    import asyncio
    import json

    data: dict = {
        "claim": "a good task list for improving the content towards a truth",
        "content": ["Insufferable", "The Earth is flat. The sky is green. The sun rises in the west."],
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