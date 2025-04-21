import argparse
from typing import Any, Optional
import json

from task_agent.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_agent.common.llm_utils import generate_prompt, send_llm_request
from task_agent.common.prompt_templates import TRUE_FALSE_PROMPT

class TrueFalseAnalyzer:
    def __init__(self, output_dir: Optional[str] = None):
        self.verdict = ""
        self.output_dir = setup_output_directory(output_dir)

    def analyze(self, user_input: str, save_json: bool = True):
        prompt = generate_prompt(TRUE_FALSE_PROMPT, user_input)
        response = send_llm_request(prompt)
        
        self.verdict = response
        
        if save_json:
            self.save_verdict(self.output_dir, description="TrueFalse Analysis")

        try:
            response = json.loads(str(response))
        except json.JSONDecodeError:
            print("Failed to decode JSON response. Returning raw response.")
            return response 
        
        return response
    
    def save_verdict(self, data: Any, description: str = "") -> str:
        return save_json_data(data, self.output_dir, "verdict", description)

def main():
    parser = argparse.ArgumentParser(description="Task Extractor - Extract Tasks from Text")
    parser.add_argument("--input", "-i", type=str, 
                      help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()

    program = TrueFalseAnalyzer(output_dir=args.output)

    test_text = """
Are there fireflies?
"""
    
    if args.input:
        text = read_input_text(args.input)
    else:
        text = test_text
    
    result = program.analyze(text, save_json=args.save)
    
    print("\n=== TRUE/FALSE ANALYSIS ===")
    print(json.dumps(result, indent=2))
    
    if args.save:
        print("\nResults saved to the output directory.")

if __name__ == "__main__":
    main()
