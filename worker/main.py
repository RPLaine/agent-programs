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

    for i, content in settings["content"]:
        print("Content ", i, "-" * 20)
        print(content)
