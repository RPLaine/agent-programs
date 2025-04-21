import argparse
from typing import Any, Optional

from task_manager.common.base_agent import BaseAgent
from task_manager.common.file_utils import read_input_text
from task_manager.common.prompt_templates import TASK_EXTRACTION_PROMPT

class TaskExtractor(BaseAgent):
    def __init__(self, output_dir: Optional[str] = None):
        super().__init__(output_dir)
        self.tasks = ""
    
    def process(self, input_data: str, save_output: bool = True):
        prompt = self.generate_llm_prompt(TASK_EXTRACTION_PROMPT, input_data)
        response = self.execute_llm_request(prompt)
        
        self.tasks = response
        
        if save_output:
            self.save_tasks(response, description="Extracted tasks")
        
        return response
    
    def save_tasks(self, task_data: Any, description: str = "") -> str:
        return self.save_results(task_data, "tasks", description)


def main():
    """Command-line entry point for task extraction."""
    parser = argparse.ArgumentParser(description="Task Extractor - Extract Tasks from Text")
    parser.add_argument("--input", "-i", type=str, required=True, 
                      help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    extractor = TaskExtractor(output_dir=args.output)
    text = read_input_text(args.input)
    extracted_tasks = extractor.process(text, save_output=args.save)
    
    print("\n=== EXTRACTED TASKS ===")
    print(extracted_tasks)
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
