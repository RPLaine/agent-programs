import argparse
from typing import Dict, Any, Optional

from task_manager.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_manager.common.llm_utils import generate_prompt, send_llm_request
from task_manager.common.prompt_templates import TASK_PRIORITIZATION_PROMPT


class TaskPrioritizer:
    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = setup_output_directory(output_dir)
    
    def prioritize_tasks(self, tasks: str, save_json: bool = True) -> Dict[str, Any]:
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


def main():
    parser = argparse.ArgumentParser(description="Task Prioritizer - Prioritize Extracted Tasks")
    parser.add_argument("--input", "-i", type=str, required=True, 
                      help="Input text or file path containing extracted tasks to prioritize")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    prioritizer = TaskPrioritizer(output_dir=args.output)
    tasks = read_input_text(args.input)
    result = prioritizer.prioritize_tasks(tasks)
    
    print("\n=== PRIORITIZED TASKS ===")
    print(result["prioritized_tasks"])
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
