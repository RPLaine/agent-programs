import argparse
from typing import Dict, Any, Optional

from task_manager.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_manager.common.llm_utils import generate_prompt, send_llm_request
from task_manager.common.prompt_templates import TASK_EXTRACTION_PROMPT, TASK_PRIORITIZATION_PROMPT


class TaskExtractor:
    
    def __init__(self, output_dir: Optional[str] = None):
        self.tasks = ""
        self.output_dir = setup_output_directory(output_dir)

    def extract_tasks(self, text: str, save_json: bool = True) -> str:
        prompt = generate_prompt(TASK_EXTRACTION_PROMPT, text)
        response = send_llm_request(prompt)
        
        self.tasks = response
        
        if save_json:
            self.save_tasks(response, description="Extracted tasks")
        
        return response

    def prioritize_tasks(self, tasks: Optional[str] = None, save_json: bool = True) -> Dict[str, Any]:
        if tasks is None:
            if not self.tasks:
                raise ValueError("No tasks available to prioritize. Extract tasks first or provide a task list.")
            tasks = self.tasks
        
        prompt = generate_prompt(TASK_PRIORITIZATION_PROMPT, f"Task List:\n{tasks}")
        response = send_llm_request(prompt)
        
        result = {
            "extracted_tasks": tasks,
            "prioritized_tasks": response
        }
        
        if save_json:
            self.save_tasks(result, description="Prioritized tasks")
        
        return result
    
    def save_tasks(self, task_data: Any, description: str = "") -> str:
        return save_json_data(task_data, self.output_dir, "tasks", description)
    
    def process_input(self, text: str, prioritize: bool = True, save: bool = True) -> Dict[str, Any]:
        extracted_tasks = self.extract_tasks(text, save_json=save)
        
        result = {"extracted_tasks": extracted_tasks}
        
        if prioritize:
            prioritized = self.prioritize_tasks(extracted_tasks, save_json=save)
            result["prioritized_tasks"] = prioritized["prioritized_tasks"]
        
        return result


def main():
    parser = argparse.ArgumentParser(description="Task Extractor - Extract and Manage Tasks")
    parser.add_argument("--input", "-i", type=str, help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-prioritize", dest="prioritize", action="store_false", 
                      help="Skip task prioritization")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    extractor = TaskExtractor(output_dir=args.output)
    text = read_input_text(args.input)
    result = extractor.process_input(text, prioritize=args.prioritize, save=args.save)
    
    print("\n=== EXTRACTED TASKS ===")
    print(result["extracted_tasks"])
    
    if args.prioritize:
        print("\n=== PRIORITIZED TASKS ===")
        print(result["prioritized_tasks"])
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
