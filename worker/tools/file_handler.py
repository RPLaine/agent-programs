async def save_data(data: dict) -> None:
    print("Saving session data...")

    import json
    import os
    
    output_dir = "output/sessions/"
    os.makedirs(output_dir, exist_ok=True)

    filename: str = "session.json"

    if "session" in data and "time" in data["session"] and "id" in data["session"]:
        filename = data["session"]["time"] + "_" + data["session"]["id"] + ".json"
    else:
        import time
        filename = str(int(time.time())) + "_session" + ".json"
    
    filepath: str = output_dir + filename

    with open(filepath, "w+") as f:
        json.dump(data, f, indent=4)

    print(f"Data saved to {filepath}")