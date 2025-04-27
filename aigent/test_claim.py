import json
import time
from aigent.agent import run_agent_process


async def aggregate_responses(count: int, data: dict) -> dict:
    response_dict: dict = {}
    response_dict["responses"] = []

    i: int = 0
    while i < count:
        try:
            response: float = float(await run_agent_process(data["agent_name"], data["user_input"]))
            response_dict["responses"].append(response)
            i += 1  # Only increment if successful
        except Exception as e:
            print(f"Error processing response: {e}")
            continue

    # Since we're working with floats, not dictionaries, simplify the processing
    values_list = response_dict["responses"]
    
    # Cap maximum value at 1.0 if needed
    values_list = [min(value, 1.0) for value in values_list]
    
    # Add a single "value" key for statistics
    response_dict["values"] = {
        "value": {
            "values": values_list,
            "average": round(sum(values_list) / len(values_list), 2) if values_list else 0,
            "median": sorted(values_list)[len(values_list) // 2] if values_list else 0,
            "mode": max(set(values_list), key=values_list.count) if values_list else 0,
            "min": min(values_list) if values_list else 0,
            "max": max(values_list) if values_list else 0
        }
    }

    return response_dict


async def does_evaluation_fit_content(content: str = "", claim: str = "", iteration_count: int = 5) -> dict:
    data_export = {
        "agent_name": "does_evaluation_fit_content",
        "user_input": f"\nCONTENT: '{content}'\n\nCLAIM: '{claim}'"
    }

    response: dict = await aggregate_responses(iteration_count, data_export)
    return response


async def main(content: str = "", intention: str = "", iteration_count: int = 5) -> dict:
    """
    Main function to test a claim against content.
    Args:
        content (str): The content to be evaluated.
        intention (str): The claim or intention to be tested.
        iteration_count (int): The number of iterations for evaluation.
    Returns:
        dict: A dictionary containing the evaluation results.
    """
    start_time = time.time()
    
    print("\nTesting claim:\nCONTENT: " + content + "\nCLAIM: " + intention)
    print("\nCreating possibilities...")

    possibilities: list = []
    while True:
        i: int = 0
        if i > 5:
            return {
                "error": "Could not create possibilities intention."
            }
        try:
            possibilities_str: str = await run_agent_process("create_possibilities_from_keyword", "VALUE: '" + intention + "'")
            possibilities_dict: dict = json.loads(possibilities_str)
            possibilities = possibilities_dict["possibilities"]
            break
        except Exception:
            print("Could not convert possibilities to a list. Retrying...")
            i += 1

    print("Possibilities created.")
    print(possibilities)
    print("\nEvaluating possibilities...")

    evaluations: dict = {}
    for possibility in possibilities:
        evaluations[possibility] = await does_evaluation_fit_content(content, possibility, iteration_count)

    evaluations["summary"] = {
        "content": content,
        "claims": [],
        "statistics": {
            "average": 0,
            "median": 0,
            "mode": 0,
            "min": 0,
            "max": 0
        }
    }

    print("Evaluations completed.")
    print(evaluations)
    print("\nCreating summary...")

    i: int = 0
    for key in evaluations.keys():
        if "values" in evaluations[key] and "value" in evaluations[key]["values"]: # and "reasoning" in evaluations[key]["values"]:
            evaluations["summary"]["claims"].append({
                "rank": i,
                "intention": intention,
                "claim": key,
                "value": evaluations[key]["values"]["value"]["average"] if "average" in evaluations[key]["values"]["value"] else ""
                # "analysis": evaluations[key]["values"]["reasoning"]["analysis"] if "analysis" in evaluations[key]["values"]["reasoning"] else ""
            })
        i += 1

    if evaluations["summary"]["claims"]:
        values = [claim["value"] for claim in evaluations["summary"]["claims"] if isinstance(claim["value"], (int, float))]
        
        if values:
            value_counts = {}
            for value in values:
                if value in value_counts:
                    value_counts[value] += 1
                else:
                    value_counts[value] = 1
            
            max_frequency = max(value_counts.values())
            modes = [value for value, count in value_counts.items() if count == max_frequency]
            
            evaluations["summary"]["statistics"] = {
                "average": round(sum(values) / len(values), 2),
                "median": sorted(values)[len(values) // 2],
                "mode": modes[0] if modes else None,
                "min": min(values),
                "max": max(values)
            }

    best_claim_obj = max(evaluations["summary"]["claims"], key=lambda x: x["value"]) if evaluations["summary"]["claims"] else None
    execution_time = time.time() - start_time
    evaluations["final"] = {
        "intention": intention,
        "content": content,
        "evaluation": best_claim_obj["claim"] if best_claim_obj else None,
        "evaluation_truth_value": best_claim_obj["value"] if best_claim_obj else None,

        "rank": best_claim_obj["rank"] if best_claim_obj else None,
        "execution_time": execution_time
    }

    print("Summary created.")
    
    return evaluations


if __name__ == "__main__":
    import asyncio 

    content: str = "I went to the city center. I talked to a few people. I took some pictures. I bought some souvenirs. I had a great time."
    intention: str = "a good news article"
    iterations: int = 5

    print(json.dumps(asyncio.run(
        main(
            content, 
            intention, 
            iterations
            )), indent=4))