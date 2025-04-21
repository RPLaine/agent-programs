"""
Task List Builder - Converts extracted tasks into structured JSON format.
A component of the task management system that builds on task_extractor results.
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from task_manager.task_extractor import TaskExtractor
from task_manager.common.logging_utils import setup_logger
from task_manager.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_manager.common.llm_utils import generate_prompt, send_llm_request
from task_manager.common.json_utils import extract_json_from_response, parse_json_safely, create_fallback_task_json
from task_manager.common.prompt_templates import JSON_CONVERSION_PROMPT

# Setup logging
logger = setup_logger("task_manager.task_list_builder")


class TaskListBuilder:
    """Converts extracted task text into structured JSON format."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the TaskListBuilder.
        
        Args:
            output_dir: Directory to save task outputs. If None, defaults to 'output' in parent directory.
        """
        # Initialize the task extractor
        self.output_dir = setup_output_directory(output_dir)
        self.task_extractor = TaskExtractor(output_dir=self.output_dir)
        logger.info(f"TaskListBuilder initialized. Output directory: {self.output_dir}")
        
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
        # Generate prompt using the template
        prompt = generate_prompt(
            JSON_CONVERSION_PROMPT,
            f"Convert the following task list to the JSON structure specified:\n\n{tasks_text}"
        )
        
        # Send request to LLM API
        response = send_llm_request(prompt, max_length=4000)
        
        # Try to extract JSON from the response
        try:
            # Extract JSON from the response
            json_str, extraction_success = extract_json_from_response(response)
            
            if not extraction_success:
                logger.error("Failed to extract JSON content from response")
                return create_fallback_task_json(tasks_text)
            
            # Parse the JSON string
            tasks_json, parsing_success = parse_json_safely(json_str)
            
            if not parsing_success:
                logger.error("Failed to parse JSON string")
                return create_fallback_task_json(tasks_text)
            
            logger.info(f"Successfully converted tasks to JSON with {len(tasks_json.get('tasks', []))} tasks")
            
            # Save the JSON to a file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"tasks_{timestamp}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_json, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Saved task list to {output_path}")
            
            return tasks_json
        
        except Exception as e:
            logger.error(f"Unexpected error processing response: {e}")
            return create_fallback_task_json(tasks_text)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract tasks and convert to JSON")
    parser.add_argument('--input', '-i', type=str, help='Input text or file path containing task descriptions')
    parser.add_argument('--output-dir', '-o', type=str, help='Output directory for JSON files')
    args = parser.parse_args()
    
    builder = TaskListBuilder(output_dir=args.output_dir)
    
    if args.input:
        # Get input text using the common utility
        input_text = read_input_text(args.input)
            
        # Process the input
        result = builder.build_task_list(input_text)
        print(f"Processed {len(result.get('tasks', []))} tasks")
    else:
        print("Please provide input text or file using the --input argument.")
