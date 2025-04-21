from typing import Any, Optional

from task_manager.common.file_utils import setup_output_directory, save_json_data
from task_manager.common.llm_utils import generate_prompt, send_llm_request

class BaseAgent:    
    def __init__(self, output_dir: Optional[str] = None):
        self.results = None
        self.output_dir = setup_output_directory(output_dir)

    def process(self, input_data: Any, save_output: bool = True) -> Any:
        raise NotImplementedError("Subclasses must implement the process method")
    
    def generate_llm_prompt(self, template: str, input_data: Any) -> str:
        return generate_prompt(template, input_data)
    
    def execute_llm_request(self, prompt: str):
        return send_llm_request(prompt)
    
    def save_results(self, data: Any, prefix: str = "results", description: str = "") -> str:
        return save_json_data(data, self.output_dir, prefix, description)
