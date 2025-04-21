"""
Common file utilities for the task manager module.
Provides standardized file handling operations.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, Optional


def setup_output_directory(output_dir: Optional[str] = None) -> str:
    """Set up and return the output directory path.
    
    Args:
        output_dir: Directory to save task outputs. If None, defaults to 'output' in parent directory.
        
    Returns:
        Path to the output directory.
    """
    if not output_dir:
        script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        output_dir = os.path.join(script_dir, "output")
        
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def save_json_data(data: Any, output_dir: str, filename_prefix: str = "tasks", 
                 description: str = "") -> str:
    """Save data to a JSON file.
    
    Args:
        data: Data to save (string or dictionary).
        output_dir: Directory to save the file.
        filename_prefix: Prefix for the output filename.
        description: Brief description of the data.
        
    Returns:
        Path to the saved file.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    # Create a JSON structure if data is a string
    if isinstance(data, str):
        data = {
            "tasks": data,
            "metadata": {
                "description": description,
                "created_at": datetime.now().isoformat(),
                "format": "text"
            }
        }
    
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Save to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    return filepath


def read_input_text(input_path: Optional[str] = None) -> str:
    """Read input text from a file or user input.
    
    Args:
        input_path: Path to an input file or None to read from stdin.
        
    Returns:
        The input text.
    """
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
