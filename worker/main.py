from worker.test import main as test_action
from worker.plan import main as plan_action
from worker.work import main as work_action

from worker.tools.file_handler import save_data


async def main(data: dict = {}) -> None:
    if "action" not in data:
        data["action"] = "test"

    print(f"\n{'='*50}")
    print(f"📋 STARTING AGENT PROGRAM - {data.get('claim', 'No claim specified')}")
    print(f"🔄 Initial action: {data['action']}")
    print(f"{'='*50}")

    i = 0
    while data["action"] != "exit" and i < data["iterations"]:
        print(f"\n{'*'*40}")
        print(f"🔄 ITERATION {i+1}/{data['iterations']} - Action: {data['action'].upper()}")
        print(f"{'*'*40}")

        if data["action"] == "test":
            await test_action(data)
            print(f"✅ Test action completed. Value: {data.get('test', {}).get('value', 'N/A')}")

        elif data["action"] == "work":
            print(f"🛠️ Starting work action...")
            await work_action(data)
            print(f"✅ Work action completed")
            break

        elif "pass_value" in data and "test" in data and "value" in data["test"] and data["test"]["value"] < data["pass_value"]:
            print(f"📝 Content value ({data['test']['value']}) below pass threshold ({data['pass_value']})")
            print(f"🧠 Planning improvements...")
            await plan_action(data)
            print(f"✅ Plan action completed")

        else:
            print(f"🎉 Content value ({data.get('test', {}).get('value', 'N/A')}) meets or exceeds pass threshold ({data.get('pass_value', 'N/A')})")
            print(f"✅ Operation complete.")
            break

        await save_data(data)
        i += 1
        print(f"💾 Progress saved after iteration {i}")

    await save_data(data)
    print(f"\n{'='*50}")
    print(f"🏁 AGENT PROGRAM COMPLETED - Processed {i} iterations")
    print(f"{'='*50}")
        

if __name__ == "__main__":
    import asyncio
    import json
    from worker.settings import settings

    asyncio.run(main(settings))

    print(json.dumps(settings, indent=4))

    # Display content progress in a more visual way
    print("\n💼 CONTENT PROGRESS 💼")
    print("="*30)
    # All items in settings["content"] are strings
    for i, content in enumerate(settings["content"]):
        print(f"📄 Content #{i+1}:")
        print("-"*30)
        print(content)
        print("-"*30)