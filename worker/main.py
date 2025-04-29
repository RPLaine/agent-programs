from worker.test import main as test_action
from worker.plan import main as plan_action
from worker.work import main as work_action

from worker.tools.file_handler import save_data


async def main(data: dict = {}) -> None:
    if "action" not in data:
        data["action"] = "test"

    while data["action"] != "exit":

        if data["action"] == "test":
            await test_action(data)

        elif data["action"] == "work":
            await work_action(data)
            break

        elif "pass_value" in data and "test" in data and "value" in data["test"] and data["test"]["value"] < data["pass_value"]:
            await plan_action(data)

        else:
            print("Content value is more than pass value. Operation complete.")
            break

        await save_data(data)

    await save_data(data)
        

if __name__ == "__main__":
    import asyncio
    import json
    from worker.settings import settings

    asyncio.run(main(settings))

    print(json.dumps(settings, indent=4))

    # Display content progress in a more visual way
    print("\n===== CONTENT PROGRESS =====")
    for i, content in enumerate(settings["content"]):
        value = content.get("value", 0)
        max_value = settings.get("pass_value", 100)
        progress = min(int((value / max_value) * 20), 20) if max_value > 0 else 0
        
        bar = "█" * progress + "░" * (20 - progress)
        percentage = (value / max_value * 100) if max_value > 0 else 0
        
        print(f"Content {i}: [{bar}] {value}/{max_value} ({percentage:.1f}%)")
        if "title" in content:
            print(f"  Title: {content['title']}")
        print(f"  Details: {content}")
        print()
