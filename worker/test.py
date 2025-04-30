from worker.agent import run_agent


async def main(data: dict) -> None:

    """
    Keys needed in dictionary:
    - claim: str
    - content: str
    - iterations: int
    """

    print(f"\n==== STARTING TEST MODULE ====")
    print(f"Testing claim: '{data['claim']}'")
    print(f"Content length: {len(data['content'][-1])} characters")
    print(f"Iterations: {data['iterations']}")

    user_prompt: str = f"""
CONTENT:
{data["content"][-1]}

CLAIM:
This content is {data["claim"]}

How well does the claim describe the content?
    """

    responses = []

    i: int = 0
    while i < data["iterations"]:
        try:
            print(f"  ├─ Running test iteration {i+1}/{data['iterations']}...")
            response: float = float(await run_agent("test", user_prompt))
            responses.append(response)
            print(f"  ├─ Test iteration {i+1} result: {response:.2f}")
            i += 1
        except Exception as e:
            print(f"  ├─ ⚠️ Test iteration failed: {e}")
            continue

    stats: dict = {
        "mean": sum(responses) / len(responses),
        "min": min(responses),
        "max": max(responses),
        "std": (sum((x - (sum(responses) / len(responses))) ** 2 for x in responses) / len(responses)) ** 0.5
    }

    data["test"] = {
        "responses": responses,
        "stats": stats,
        "value": stats["mean"]
    }

    print(f"  ├─ Test complete. Results:")
    print(f"  ├─ Mean: {stats['mean']:.2f}")
    print(f"  ├─ Min: {stats['min']:.2f}")
    print(f"  ├─ Max: {stats['max']:.2f}")
    print(f"  └─ Std Dev: {stats['std']:.2f}")

    data["action"] = ""
    print(f"\n==== TEST MODULE COMPLETED ====")


if __name__ == "__main__":
    import asyncio
    import json


    claim: str = "a best temperature for coffee"

    content: str = "Coffee is cold."

    data: dict = {
        "claim": claim,
        "content": [content],
        "iterations": 5
    }

    asyncio.run(main(data))

    print(json.dumps(data, indent=4))