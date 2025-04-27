from aigent.make_plan import main as make_plan

async def main(data: dict = {}) -> dict:
    if not data:
        data["error"] = "No data."
        return data
    
    planning_data: dict = {
            "intention": data["desired_product"],
            "content": data["user_input"],
            "evaluation": data["evaluation"],
            "rank": data["test"]["result"]["final"]["rank"],
            "iterations_max": data["iteration_count"]
            }

    result: dict = await make_plan(planning_data, data["iteration_count"])
    data["plan"] = result

    return data