import json
from aigent.agent import run_agent_process
from aigent.test_claim import main as test_claim

# DONE
async def create_task_list(data: dict = {}, iterations: int = 3) -> dict:
    user_prompt: str = f"""
    INTENTION: {data["intention"]}

    CONTENT: {data["content"]}

    EVALUATION: {data["evaluation"]}

    EVALUATION_TRUTH_VALUE: {data["evaluation_truth_value"]}

    ANALYSIS: {data["analysis"]}
    """
    task_list_dict: dict = {}
    i:  int = 0
    while True:
        try:
            task_list_dict = json.loads(await run_agent_process("create_task_list", user_prompt))
            return task_list_dict
        except:
            i += 1
            if i == iterations:
                return {
                    "error": "Failed to create task list after multiple attempts."
                }
            

async def sub_task_aggregation(data: dict = {}, iterations: int = 3) -> dict:
    data["message"] = "Sub-task aggregation is not implemented yet."
    return data
    

async def main(import_data: dict = {}, iterations_max: int = 3) -> dict:
    print("Creating task list...")
    task_list: dict = {}
    validation: dict = {}

    i: int = 0
    while i < iterations_max:
        task_list = await create_task_list(import_data)

        print("Validating task list...")
        validation = await test_claim(json.dumps(task_list), "a good task list", 3)

        rank: int = -1
        tasks: dict = {}

        if "final" in validation and "content" in validation["final"]:
            try:
                tasks["list"] = json.loads(validation["final"]["content"])
            except:
                print("Failed to parse task list.")
                tasks = {
                    "list": validation["final"]["content"],
                    "error": "Failed to parse task list."
                }

        if "final" in validation and "rank" in validation["final"] and isinstance(validation["final"]["rank"], int):
            rank: int = validation["final"]["rank"]
            if rank == 0:
                print("Task list is sufficient.")
                return {
                    "validation": validation,
                    "tasks": tasks,
                    "rank": rank
                }
            elif rank == 3:
                print("Task list is unimprovable.")
                return {
                    "validation": validation,
                    "rank": rank
                }
            else:
                print("Task list is improvable. Improving...")
                if "content" in validation["final"]:
                    task_list["content"] = validation["final"]["content"]
                    i += 1
                else:
                    return {
                        "validation": validation,
                        "error": "Validation content not found."
                    }
        else:
            return {
                "validation": validation,
                "error": "Validation not ranked or rank is not integer."
            }
    
    return {
        "validation": validation,
        "error": "Failed to create a valid task list after multiple attempts."
    }


if __name__ == "__main__":
    import asyncio # important for async functions

    data: dict = {
        "intention": "a good news article",
        "content": "I went to the city center. I talked to a few people. I took some pictures. I bought some souvenirs. I had a great time.",
        "evaluation": "The content is not a good news article yet, but could be modified to meet this criterion.",
        "evaluation_truth_value": 0.77,
        "analysis": "1. Shared between the sentiments: Both sentiments agree that the content seems to be a personal travelogue rather than a news article. They also acknowledge that the content could be modified to make it more suitable as a news article by adding relevant facts or events.\n\n2. Different between the sentiments: Although both sentiments share similarities, there is a slight difference in their phrasing and choice of words. The first sentiment suggests adding facts or events that occurred during the trip, while the second sentiment mentions adding a newsworthy angle or specific details that make the event or activities noteworthy. The second sentiment emphasizes the importance of finding a newsworthy angle in order to transform the content into a successful news article.",
        "rank": 0
    }

    if data != {}:
        print(json.dumps(asyncio.run(main(data)), indent=4))
    else:
        print("No data to process.")