import json
from aigent.agent import Agent
from aigent.tools.get_prompt_info import get_prompt_dict, get_prompt_data, get_prompt_filenames
import aigent.settings as settings

async def main(agent_name: str, user_input: str = "") -> str:
    prompt_dict: dict = get_prompt_dict(agent_name)
    agent: Agent = Agent(prompt_dict)
    if user_input == "":
        user_input = input("Enter your input: ")
    response = await agent.process(user_input)
    
    parsed_response: dict = {}
    try:
        parsed_response = json.loads(response)
    except json.JSONDecodeError:
        print("Failed to parse the response as JSON.")
    if parsed_response != {}: response = json.dumps(parsed_response, indent=4)

    return response

async def aggregation(count: int, data: dict) -> dict:
    response_dict = {}
    response_dict["responses"] = []
    i = 0
    while i < count:
        response = await main(data["agent_name"], data["user_input"])
        try:
            parsed_response = json.loads(response)
            response_dict["responses"].append(parsed_response)
        except json.JSONDecodeError:
            pass
        i += 1

    response_dict["keys"] = list(set([key for response in response_dict["responses"] for key in response.keys()]))

    response_dict["values"] = {}
    for key in response_dict["keys"]:
        response_dict["values"][key] = []
        for response in response_dict["responses"]:
            if key in response.keys():
                response_dict["values"][key].append(response[key])

    for key in response_dict["keys"]:
        if all(isinstance(value, (int, float)) for value in response_dict["values"][key]):
            values_list = response_dict["values"][key]
            
            # For floats, cap maximum value at 1.0
            if all(isinstance(value, float) for value in values_list):
                values_list = [min(value, 1.0) for value in values_list]
                
            response_dict["values"][key] = {
                "values": values_list,
                "average": round(sum(values_list) / len(values_list), 2), # Limited to 2 decimal places
                "median": sorted(values_list)[len(values_list) // 2],
                "mode": max(set(values_list), key=values_list.count),
                "min": min(values_list),
                "max": max(values_list)
            }
        else:
            summary_response = await main("analyze_sentiments", json.dumps(response_dict["values"][key]))
            response_dict["values"][key] = {
                "values": response_dict["values"][key],
                "analysis": summary_response
            }

    return response_dict

def create_system_prompt(prompt_dict: dict) -> str:
    system_prompt: str = settings.data[0]
    system_prompt += prompt_dict['system'] if 'system' in prompt_dict else ""
    system_prompt += settings.data[1]
    return system_prompt

async def does_response_fit_request(user_request: str = "", assistant_response: str = "", iteration_count: int = 5) -> dict:
    data = {
        "agent_name": "does_response_fit_request",
        "user_input": f"Request: {user_request} \n\nResponse: {assistant_response}"
    }

    response: dict = await aggregation(iteration_count, data)
    return response

async def does_content_fit_task(content: str = "", task: str = "", iteration_count: int = 5) -> dict:
    data_export = {
        "agent_name": "does_content_fit_task",
        "user_input": f"CONTENT:\n{content}\n\nTASK:\n{task}"
    }

    response: dict = await aggregation(iteration_count, data_export)
    return response

async def does_evaluation_fit_content(content: str = "", evaluation: str = "", iteration_count: int = 5) -> dict:
    data_export = {
        "agent_name": "does_evaluation_fit_content",
        "user_input": f"CONTENT:\n{content}\n\nEVALUATION:\n{evaluation}"
    }

    response: dict = await aggregation(iteration_count, data_export)
    return response

async def test_multiple_possibilities(content: str = "", concept: str = "", iteration_count: int = 5) -> dict:
    possibilities: list = []
    while True:
        i: int = 0
        if i > 5:
            return {
                "error": "Could not create possibilities from keyword."
            }
        try:
            possibilities_str: str = await main("create_possibilities_from_keyword", "'KEY': '" + concept + "'")
            possibilities_dict: dict = json.loads(possibilities_str)
            possibilities = possibilities_dict["possibilities"]
            break
        except Exception:
            print("Could not convert possibilities to a list. Retrying...")
            i += 1

    evaluations: dict = {}
    for possibility in possibilities:
        evaluations[possibility] = await does_evaluation_fit_content(content, possibility, iteration_count)

    evaluations["summary"] = {
        "content": content,
        "claims": []
    }

    i: int = 0
    for key in evaluations.keys():
        if "values" in evaluations[key] and "assessment" in evaluations[key]["values"] and "reasoning" in evaluations[key]["values"]:
            evaluations["summary"]["claims"].append({
                "claim": key,
                "fit": evaluations[key]["values"]["assessment"]["average"] if "average" in evaluations[key]["values"]["assessment"] else "",
                "analysis": evaluations[key]["values"]["reasoning"]["analysis"] if "analysis" in evaluations[key]["values"]["reasoning"] else ""
            })
        i += 1

    best_claim_obj = max(evaluations["summary"]["claims"], key=lambda x: x["fit"]) if evaluations["summary"]["claims"] else None
    evaluations["final"] = {
        "content": content,
        "claim": best_claim_obj["claim"] if best_claim_obj else None,
        "fit": best_claim_obj["fit"] if best_claim_obj else None,
        "analysis": best_claim_obj["analysis"] if best_claim_obj else None
    }
    
    return evaluations


if __name__ == "__main__":
    import asyncio

    # content: str = "I noticed this morning that I might have some odd rash on my arm. I think it might be a rash, but I'm not sure. I don't know if I should go to the doctor or not. Can you help me figure out what to do?"
    content: str = "I went to the city center. I talked to a few people. I took some pictures. I bought some souvenirs. I had a great time."
    concept: str = "a good news article"
    # print(json.loads(asyncio.run(main("create_possibilities_from_keyword", "'KEY': '" + keyword + "'"))))
    print(json.dumps(asyncio.run(test_multiple_possibilities(content, concept)), indent=4))

    # Example for does_response_fit_request
    # response: dict = asyncio.run(does_content_fit_task(data["content"], data["task"], data["iteration_count"]))
    # print(json.dumps(response, indent=4))