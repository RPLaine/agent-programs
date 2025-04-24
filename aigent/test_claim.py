import json
from aigent.agent import run_agent_process


async def aggregate_responses(count: int, data: dict) -> dict:
    response_dict = {}
    response_dict["responses"] = []
    i = 0
    while i < count:
        response = await run_agent_process(data["agent_name"], data["user_input"])
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
            summary_response = await run_agent_process("analyze_sentiments", json.dumps(response_dict["values"][key]))
            response_dict["values"][key] = {
                "values": response_dict["values"][key],
                "analysis": summary_response
            }

    return response_dict


async def does_evaluation_fit_content(content: str = "", claim: str = "", iteration_count: int = 5) -> dict:
    data_export = {
        "agent_name": "does_evaluation_fit_content",
        "user_input": f"CONTENT: '{content}'\nCLAIM: '{claim}'"
    }

    response: dict = await aggregate_responses(iteration_count, data_export)
    return response


async def main(content: str = "", claim: str = "", iteration_count: int = 5) -> dict:
    possibilities: list = []
    while True:
        i: int = 0
        if i > 5:
            return {
                "error": "Could not create possibilities from keyword."
            }
        try:
            possibilities_str: str = await run_agent_process("create_possibilities_from_keyword", "VALUE: '" + claim + "'")
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
        if "values" in evaluations[key] and "value" in evaluations[key]["values"] and "reasoning" in evaluations[key]["values"]:
            evaluations["summary"]["claims"].append({
                "claim": key,
                "value": evaluations[key]["values"]["value"]["average"] if "average" in evaluations[key]["values"]["value"] else "",
                "analysis": evaluations[key]["values"]["reasoning"]["analysis"] if "analysis" in evaluations[key]["values"]["reasoning"] else ""
            })
        i += 1

    best_claim_obj = max(evaluations["summary"]["claims"], key=lambda x: x["value"]) if evaluations["summary"]["claims"] else None
    evaluations["final"] = {
        "content": content,
        "evaluation": best_claim_obj["claim"] if best_claim_obj else None,
        "evaluation_truth_value": best_claim_obj["value"] if best_claim_obj else None,
        "analysis": best_claim_obj["analysis"] if best_claim_obj else None
    }
    
    return evaluations


if __name__ == "__main__":
    import asyncio # important for async functions

    content: str = "I went to the city center. I talked to a few people. I took some pictures. I bought some souvenirs. I had a great time."
    claim: str = "a good news article"
    iterations: int = 3

    print(json.dumps(asyncio.run(
        main(
            content, 
            claim, 
            iterations
            )), indent=4))