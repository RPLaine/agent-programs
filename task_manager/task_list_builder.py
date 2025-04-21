"""
Task List Builder - Converts extracted tasks into structured JSON format.
A component of the task management system that builds on task_extractor results.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("task_manager.task_list_builder")

# Import from task_manager
from task_manager.task_extractor import TaskExtractor

# Import LLM API
try:
    import llm.api as api
except ImportError:
    # Fall back to relative import if we're running from within task_manager
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import llm.api as api


class TaskListBuilder:
    """Converts extracted task text into structured JSON format."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the TaskListBuilder.
        
        Args:
            output_dir: Directory to save task outputs. If None, defaults to 'output' in parent directory.
        """
        # Initialize the task extractor
        self.task_extractor = TaskExtractor(output_dir=output_dir)
        
        if not output_dir:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(script_dir, "output")
            
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        logger.info(f"TaskListBuilder initialized. Output directory: {output_dir}")
        
    def build_task_list(self, text: str) -> Dict[str, Any]:
        """Extract tasks from text and convert to structured JSON.
        
        Args:
            text: Natural language description containing potential tasks.
            
        Returns:
            Dictionary containing structured task list.
        """
        # First, use the task_extractor to get tasks as formatted text
        extracted_tasks = self.task_extractor.extract_tasks(text)
        logger.info("Tasks extracted, converting to structured JSON format")
        
        # Then, use LLM API to convert to JSON structure
        return self._convert_to_json(extracted_tasks)
        
    def _convert_to_json(self, tasks_text: str) -> Dict[str, Any]:
        """Convert extracted tasks text to structured JSON.
        
        Args:
            tasks_text: The extracted tasks as text.
            
        Returns:
            Dictionary containing structured task list.
        """
        system_prompt = """
You are a structured data conversion specialist. Convert the given task list into a valid JSON format with the following structure:

```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "description": "More detailed description if available",
      "priority": "high|medium|low", 
      "category": "Category if evident from context",
      "subtasks": [
        {
          "id": "1.1",
          "title": "Subtask title",
          "description": "Subtask description"
        }
      ]
    }
  ],
  "metadata": {
    "count": 5,
    "categories": ["category1", "category2"],
    "created_at": "2025-04-21T10:30:00Z"
  }
}
```

Rules:
1. Assign IDs sequentially (1, 2, 3, etc. for top-level tasks)
2. For subtasks, use hierarchical IDs (1.1, 1.2, etc.)
3. Infer priority and category from context if possible
4. Ensure the JSON is valid and well-structured
5. Preserve all task information from the input
"""

        prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Convert the following task list to the JSON structure specified:

{tasks_text}
<|im-end|>
<|im-assistant|>
"""
        data = {"prompt": prompt, "max_length": 4000}
        response = api.request(data)
        
        # Try to extract JSON from the response
        try:
            # Find JSON content between ```json and ``` if present
            if "```json" in response and "```" in response.split("```json", 1)[1]:
                json_str = response.split("```json", 1)[1].split("```", 1)[0].strip()
            else:
                # Otherwise use the whole response
                json_str = response.strip()
                
            # Parse the JSON string
            tasks_json = json.loads(json_str)
            logger.info(f"Successfully converted tasks to JSON with {len(tasks_json.get('tasks', []))} tasks")
            
            # Save the JSON to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"tasks_{timestamp}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_json, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved task list to {output_path}")
            
            return tasks_json
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.debug(f"Raw response: {response}")
            raise ValueError(f"Failed to convert tasks to valid JSON: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing response: {e}")
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract tasks and convert to JSON")
    parser.add_argument('--input', '-i', type=str, help='Input text or file path containing task descriptions')
    parser.add_argument('--output-dir', '-o', type=str, help='Output directory for JSON files')
    args = parser.parse_args()
    
    builder = TaskListBuilder(output_dir=args.output_dir)
    
    if args.input:
        # Check if input is a file path
        if os.path.isfile(args.input):
            with open(args.input, 'r', encoding='utf-8') as f:
                input_text = f.read()
        else:
            input_text = args.input
            
        # Process the input
        result = builder.build_task_list(input_text)
        print(f"Processed {len(result.get('tasks', []))} tasks")
    else:
        print("Please provide input text or file using the --input argument.")
