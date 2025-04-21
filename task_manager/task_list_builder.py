import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

from task_manager.task_extractor import TaskExtractor
from task_manager.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_manager.common.llm_utils import generate_prompt, send_llm_request
from task_manager.common.json_utils import extract_json_from_response, parse_json_safely, create_fallback_task_json
from task_manager.common.prompt_templates import JSON_CONVERSION_PROMPT


class TaskListBuilder:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = setup_output_directory(output_dir)
        self.task_extractor = TaskExtractor(output_dir=self.output_dir)
        
    def build_task_list(self, text: str) -> Dict[str, Any]:
        extracted_tasks = self.task_extractor.extract_tasks(text)
        return self._convert_to_json(extracted_tasks)
        
    def _convert_to_json(self, tasks_text: str) -> Dict[str, Any]:
        prompt = generate_prompt(
            JSON_CONVERSION_PROMPT,
            f"Convert the following task list to the JSON structure specified:\n\n{tasks_text}"
        )
        
        response = send_llm_request(prompt, max_length=4000)
        
        try:
            json_str, extraction_success = extract_json_from_response(response)
            
            if not extraction_success:
                return create_fallback_task_json(tasks_text)
            
            tasks_json, parsing_success = parse_json_safely(json_str)
            
            if not parsing_success:
                return create_fallback_task_json(tasks_text)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(self.output_dir, f"tasks_{timestamp}.json")
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_json, f, indent=2, ensure_ascii=False)
            
            return tasks_json
        
        except Exception:
            return create_fallback_task_json(tasks_text)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Extract tasks and convert to JSON")
    parser.add_argument('--input', '-i', type=str, help='Input text or file path containing task descriptions')
    parser.add_argument('--output-dir', '-o', type=str, help='Output directory for JSON files')
    args = parser.parse_args()
    
    builder = TaskListBuilder(output_dir=args.output_dir)
    
    if args.input:
        input_text = read_input_text(args.input)
        result = builder.build_task_list(input_text)
        print(f"Processed {len(result.get('tasks', []))} tasks")
    else:
        print("Please provide input text or file using the --input argument.")
