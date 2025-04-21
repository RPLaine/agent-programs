# filepath: d:\git\agent-programs\task_agent\task_extractor.py
import argparse
from typing import Any, Optional
import json

from task_agent.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_agent.common.llm_utils import generate_prompt, send_llm_request
from task_agent.common.prompt_templates import TASK_EXTRACTION_PROMPT

class TaskExtractor:
    def __init__(self, output_dir: Optional[str] = None):
        self.tasks = ""
        self.output_dir = setup_output_directory(output_dir)

    def extract_tasks(self, user_input: str, save_json: bool = True):
        prompt = generate_prompt(TASK_EXTRACTION_PROMPT, user_input)
        response = send_llm_request(prompt)
        
        self.tasks = response
        
        if save_json:
            self.save_tasks(response, description="Extracted tasks")

        try:
            response = json.loads(str(response))
        except json.JSONDecodeError:
            print("Failed to decode JSON response. Returning raw response.")
            return response 
        
        return response
    
    def save_tasks(self, data: Any, description: str = "") -> str:
        return save_json_data(data, self.output_dir, "tasks", description)



def main():
    parser = argparse.ArgumentParser(description="Task Extractor - Extract Tasks from Text")
    parser.add_argument("--input", "-i", type=str, 
                      help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    extractor = TaskExtractor(output_dir=args.output)

    test_text = """
I try to find ruling of law in the case of a car accident form the Internet.
"""

    if args.input:
        text = read_input_text(args.input)
    else:
        text = test_text

    extracted_tasks = extractor.extract_tasks(text, save_json=args.save)
    
    print("\n=== EXTRACTED TASKS ===")
    print(json.dumps(extracted_tasks, indent=2))
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
