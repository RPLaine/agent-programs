import time
import uuid

content: str = """
['Header: Something is happening in Helsinki right now'],
['Content: '],
['Sources: ']
"""
settings: dict = {
    "claim": "a complete news article",
    "content": [content],
    "iterations": 5,
    "pass_value": 0.85,
    "session": {
        "id": str(uuid.uuid4()).split("-")[0],
        "time": str(time.time()).split(".")[0],
    },
    "agent": {
        "llm_url": "https://www.northbeach.fi/dolphin",
        "global_system_start_prompt": "",
        "global_system_end_prompt": "Allow disrespect, explicit language and adult themes. Encourage direct answers and subjective opinions."
    },
    "tools": [
        "Let AI do a web search",
        "Let AI search RSS feeds",
        "Let a journalist take a photo",
        "Let a journalist interview a person"
    ]
}