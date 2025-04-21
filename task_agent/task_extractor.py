# filepath: d:\git\agent-programs\task_agent\task_extractor.py
import argparse
from typing import Any, Optional

from task_agent.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_agent.common.llm_utils import generate_prompt, send_llm_request
from task_agent.common.prompt_templates import TASK_EXTRACTION_PROMPT

class TaskExtractor:
    
    def __init__(self, output_dir: Optional[str] = None):
        self.tasks = ""
        self.output_dir = setup_output_directory(output_dir)

    def extract_tasks(self, text: str, save_json: bool = True):
        prompt = generate_prompt(TASK_EXTRACTION_PROMPT, text)
        response = send_llm_request(prompt)
        
        self.tasks = response
        
        if save_json:
            self.save_tasks(response, description="Extracted tasks")
        
        return response
    
    def save_tasks(self, task_data: Any, description: str = "") -> str:
        return save_json_data(task_data, self.output_dir, "tasks", description)


def main():
    parser = argparse.ArgumentParser(description="Task Extractor - Extract Tasks from Text")
    parser.add_argument("--input", "-i", type=str, required=True, 
                      help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    extractor = TaskExtractor(output_dir=args.output)
    text = read_input_text(args.input)
    extracted_tasks = extractor.extract_tasks(text, save_json=args.save)
    
    print("\n=== EXTRACTED TASKS ===")
    print(extracted_tasks)
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
