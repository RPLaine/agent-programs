import asyncio
import json

from aigent.test import main as request_test
from aigent.plan import main as request_plan
from aigent.work import main as request_work


async def get_action(data: dict) -> dict:
    try:
        if data["test"]["result"]["final"]["rank"] == 0:
            data["message"] = "The user input is the desired product."
            data["action"] = "done"
            print(data["message"])
            return data
        elif data["test"]["result"]["final"]["rank"] == 1:
            data["message"] = "The user input is the desired product but can be improved."
            data["action"] = "plan"
            print(data["message"])
        elif data["test"]["result"]["final"]["rank"] == 2:
            data["message"] = "The user input is not the desired product but can be improved."
            data["action"] = "plan"
            print(data["message"])
        elif data["test"]["result"]["final"]["rank"] == 3:
            data["message"] = "The user input is unrelated to desired product."
            data["action"] = "done"
            print(data["message"])
            return data
        else:
            data["error"] = "Unexpected rank."
            print(data["error"])
            return data
    except:
        if "test" not in data:
            data["error"] = "No test data."
            return data
        else:
            if "result" not in data["test"]:
                data["error"] = "No result."
                return data
            else:
                if "final" not in data["test"]["result"]:
                    data["error"] = "No final result."
                    return data
                else:
                    if "rank" not in data["test"]["result"]["final"]:
                        data["error"] = "No rank."
                        return data
        data["error"] = "Unknown error."
    return data


async def test(data: dict) -> dict:
    try:
        test_data: dict = {
            "desired_product": data["desired_product"],
            "user_input": data["user_input"],
            "iteration_count": data["iteration_count"]
        }
    except:
        data["error"] = "No data."
        return data
    
    data["test"] = await request_test(test_data)

    return data

async def plan(data: dict) -> dict:
    try:
        plan_data: dict = {
            "desired_product": data["desired_product"],
            "user_input": data["user_input"],
            "evaluation": data["test"]["result"]["final"]["evaluation"],
            "iteration_count": data["iteration_count"],
            "rank": data["test"]["result"]["final"]["rank"]
        }
    except:
        data["error"] = "No data."
        return data
    
    data["plan"] = await request_plan(plan_data)

    return data


async def main(data: dict = {}) -> dict:

    data["action"] = "test"

    while True:

        if data["action"] == "test": 
            data = await test(data)
            return data
        elif data["action"] == "plan": data = await plan(data)
        elif data["action"] == "work":
            # data = await work(data)
            data["message"] = "Working is not implemented yet."
            print(data["message"])
            return data
        elif data["action"] == "done":
            data["message"] = "Done."
            print(data["message"])
            break
        else:
            data["error"] = "Unknown action."
            break

        data = await get_action(data)

    return data



if __name__ == "__main__":
    desired_product: str = "a complete news article"
    user_input: str = "Soldiers found near Swedish border"

    data: dict = {
        "desired_product": desired_product,
        "user_input": user_input,
        "iteration_count": 5
    }

    print(json.dumps((asyncio.run(main(data))), indent=4))