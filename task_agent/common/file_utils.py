# filepath: d:\git\agent-programs\task_agent\common\file_utils.py
import os
import json
from datetime import datetime
from typing import Any, Optional


def setup_output_directory(output_dir: Optional[str] = None) -> str:
    if not output_dir:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(script_dir, "output")
        
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_json_data(data: Any, output_dir: str, filename_prefix: str = "tasks", description: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    if isinstance(data, str):
        data = {
            "tasks": data,
            "metadata": {
                "description": description,
                "created_at": datetime.now().isoformat(),
                "format": "text"
            }
        }
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return filepath


def read_input_text(input_path: Optional[str] = None) -> str:
    if input_path:
        if os.path.exists(input_path):
            with open(input_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return input_path
    else:
        print("Please enter your text (Ctrl+D or Ctrl+Z on a new line to finish):")
        lines = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        return '\n'.join(lines)
