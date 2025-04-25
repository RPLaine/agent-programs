import asyncio
import time
import uuid
import json

from aigent.test_claim import main as test_claim
from aigent.make_plan import main as make_plan
# from aigent.execute_plan import main as execute_plan

from input.get_input import intention, content

def get_session() -> dict:
    current_time: str = str(time.time()).split(".")[0]
    id_extension: str = str(uuid.uuid4()).split("-")[0]

    session: dict = {
        "id": current_time + "-" + id_extension,
        "start_time": current_time,
        "end_time": None,
        "intention": intention,
        "initial_content": content,
        "iteration_count": 5
    }

    return session

def initialize_data() -> dict:
    print("Initializing session...")
    data: dict = {
        "intention": intention,
        "content": content,
        "iteration_count": 5,
        "session": get_session()
    }
    print("Session initialized.")
    print(json.dumps(data, indent=2))
    return data

def finalize_data(data: dict) -> dict:
    print("Finalizing session...")
    data["session"]["end_time"] = str(time.time()).split(".")[0]
    save_data(data)
    print("Session finalized.")
    print(json.dumps(data["session"], indent=2))
    return data

def save_data(data: dict) -> None:
    print("Saving session data...")
    import os
    
    output_dir = "output/sessions/"
    os.makedirs(output_dir, exist_ok=True)
    
    filename: str = data["session"]["id"] + ".json"
    filepath: str = output_dir + filename

    with open(filepath, "w+") as f:
        json.dump(data, f, indent=4)

    print(f"Data saved to {filepath}")



async def main():
    data = initialize_data()

    print("Processing...")
    data["process"] = await test_claim(data["content"], data["intention"], data["iteration_count"])

    finalize_data(data)



if __name__ == "__main__":
    asyncio.run(main())