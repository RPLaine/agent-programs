import json
import re
from datetime import datetime
from typing import Dict, Any, Tuple

def extract_json_from_response(response: str) -> Tuple[str, bool]:
    json_str = ""
    success = False
    
    # Strategy 1: Find JSON content between ```json and ```
    if "```json" in response and "```" in response.split("```json", 1)[1]:
        json_str = response.split("```json", 1)[1].split("```", 1)[0].strip()
        success = True
    
    # Strategy 2: Find content between { and the last }
    elif response.strip().startswith("{") and "}" in response:
        # Find outermost JSON object
        start_idx = response.find("{")
        end_idx = response.rfind("}")
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_str = response[start_idx:end_idx+1].strip()
            success = True
    
    # Strategy 3: Just use the whole response if it might be JSON
    else:
        json_str = response.strip()
        success = json_str.startswith("{") and json_str.endswith("}")
    
    # Sanity check the extracted JSON string
    if not json_str:
        success = False
    
    if not (json_str.startswith("{") and json_str.endswith("}")):
        success = False
    
    return json_str, success


def parse_json_safely(json_str: str) -> Tuple[Dict[str, Any], bool]:
    try:
        parsed_json = json.loads(json_str)
        return parsed_json, True
    except json.JSONDecodeError as e:
        return {}, False


def create_fallback_task_json(tasks_text: str) -> Dict[str, Any]:
    # Create a simple parsing of the tasks
    tasks = []
    
    # Clean and normalize the text
    clean_text = tasks_text.strip()
    
    # Extract tasks using regex to find numbered or bulleted items
    task_patterns = [
        r'\n\s*(\d+)[\.)\s]+([^\n]+)',  # Numbered items: 1. Task description
        r'\n\s*[-•*]\s+([^\n]+)',       # Bulleted items: - Task description
        r'\n\s*([A-Z][^\.]+)\.'         # Capitalized sentences ending with period
    ]
    
    task_id = 1
    for pattern in task_patterns:
        matches = re.findall(pattern, '\n' + clean_text)
        if matches:
            for match in matches:
                # If the match is a tuple (from capturing groups), use the last element as the task
                task_title = match[-1] if isinstance(match, tuple) else match
                task_title = task_title.strip()
                
                if task_title and len(task_title) > 2:  # Basic validation
                    tasks.append({
                        "id": task_id,
                        "title": task_title,
                        "description": task_title,
                        "priority": "medium",
                        "category": "Task",
                        "subtasks": []
                    })
                    task_id += 1
    
    # If no tasks were found with regex, try line-based parsing
    if not tasks:
        lines = clean_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and not line.startswith('#') and not line.startswith('```'):
                tasks.append({
                    "id": task_id,
                    "title": line,
                    "description": line,
                    "priority": "medium",
                    "category": "Task",
                    "subtasks": []
                })
                task_id += 1
    
    # Create the final structure
    tasks_json = {
        "tasks": tasks,
        "metadata": {
            "count": len(tasks),
            "categories": ["Task"],
            "created_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    }
        
    return tasks_json
