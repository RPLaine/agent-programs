import time
import uuid

content: str = "Local news from Pori" # Initial content for improvement

settings: dict = {
    "claim": "a complete news article", # Destination of the improvement
    "content": [content],
    "iterations": 3,
    "pass_value": 0.85,
    "session": {
        "id": str(uuid.uuid4()).split("-")[0],
        "time": str(time.time()).split(".")[0],
    },
    "agent": {
        "llm_url": "https://www.northbeach.fi/dolphin",
        "global_system_start_prompt": "",
        "global_system_end_prompt": ""
    },
    "tools": [
        "Let AI do a web search",
        "Let AI search RSS feeds",
        "Let a journalist take a photo",
        "Let a journalist interview a person"
    ]
}