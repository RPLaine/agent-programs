"""
Task Extractor - An AI-based system for extracting, prioritizing, and managing tasks from user input.
Built for the Dolphin AI system.
"""

import argparse
from typing import Dict, Any, Optional

# Import common utilities
from task_manager.common.logging_utils import setup_logger
from task_manager.common.file_utils import setup_output_directory, save_json_data, read_input_text
from task_manager.common.llm_utils import generate_prompt, send_llm_request
from task_manager.common.prompt_templates import TASK_EXTRACTION_PROMPT, TASK_PRIORITIZATION_PROMPT


# Setup logging
logger = setup_logger("task_manager.task_extractor")


class TaskExtractor:
    """Task Extractor that extracts and manages tasks from natural language input."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the TaskExtractor.
        
        Args:
            output_dir: Directory to save task outputs. If None, defaults to 'output' in parent directory.
        """
        self.tasks = ""  # Initialize as empty string since API returns strings
        self.output_dir = setup_output_directory(output_dir)
        logger.info(f"TaskExtractor initialized. Output directory: {self.output_dir}")

    def extract_tasks(self, text: str, save_json: bool = True) -> str:
        """Extract tasks from natural language text.
        
        Args:
            text: Natural language description containing potential tasks.
            save_json: Whether to automatically save the extracted tasks as JSON.
            
        Returns:
            Extracted tasks as a formatted string.
        """
        logger.info("Extracting tasks from input text")
        
        # Generate prompt using the template
        prompt = generate_prompt(TASK_EXTRACTION_PROMPT, text)
        
        # Send request to LLM API
        response = send_llm_request(prompt)
        
        # Store the raw string response for use in other methods
        self.tasks = response
        
        # Automatically save tasks to JSON if requested
        if save_json:
            self.save_tasks(response, description="Extracted tasks")
            logger.info("Automatically saved extracted tasks to JSON file")
        
        return response

    def prioritize_tasks(self, tasks: Optional[str] = None, save_json: bool = True) -> Dict[str, Any]:
        """Prioritize a list of tasks based on dependencies and importance.
        
        Args:
            tasks: Task list to prioritize. If None, uses previously extracted tasks.
            save_json: Whether to automatically save the prioritized tasks as JSON.
            
        Returns:
            Dictionary containing original and prioritized tasks.
        """
        if tasks is None:
            if not self.tasks:
                raise ValueError("No tasks available to prioritize. Extract tasks first or provide a task list.")
            tasks = self.tasks
        
        logger.info("Prioritizing tasks")
        
        # Generate prompt using the template
        prompt = generate_prompt(TASK_PRIORITIZATION_PROMPT, f"Task List:\n{tasks}")
        
        # Send request to LLM API
        response = send_llm_request(prompt)
        
        result = {
            "extracted_tasks": tasks,
            "prioritized_tasks": response
        }
        
        # Automatically save prioritized tasks to JSON if requested
        if save_json:
            self.save_tasks(result, description="Prioritized tasks")
            logger.info("Automatically saved prioritized tasks to JSON file")
        
        return result
    
    def save_tasks(self, task_data: Any, description: str = "") -> str:
        """Save task data to a file.
        
        Args:
            task_data: Task data to save (string or dictionary).
            description: Brief description of the task set.
            
        Returns:
            Path to the saved file.
        """
        return save_json_data(task_data, self.output_dir, "tasks", description)
    
    def process_input(self, text: str, prioritize: bool = True, save: bool = True) -> Dict[str, Any]:
        """Process user input to extract and optionally prioritize tasks.
        
        Args:
            text: Natural language input text.
            prioritize: Whether to prioritize the extracted tasks.
            save: Whether to save the results to a file.
            
        Returns:
            Dictionary containing the extracted and potentially prioritized tasks.
        """
        # Extract tasks (saving is handled by the extract_tasks method if save=True)
        extracted_tasks = self.extract_tasks(text, save_json=save)
        
        result = {"extracted_tasks": extracted_tasks}
        
        # Prioritize tasks if requested
        if prioritize:
            prioritized = self.prioritize_tasks(extracted_tasks, save_json=save)
            result["prioritized_tasks"] = prioritized["prioritized_tasks"]
        
        return result


def main():
    """CLI entry point for task extractor."""
    parser = argparse.ArgumentParser(description="Task Extractor - Extract and Manage Tasks")
    parser.add_argument("--input", "-i", type=str, help="Input text or file path containing text to process")
    parser.add_argument("--output", "-o", type=str, help="Directory to save output files")
    parser.add_argument("--no-prioritize", dest="prioritize", action="store_false", 
                      help="Skip task prioritization")
    parser.add_argument("--no-save", dest="save", action="store_false",
                      help="Don't save results to file")
    
    args = parser.parse_args()
    
    # Initialize the task extractor
    extractor = TaskExtractor(output_dir=args.output)
    
    # Get input text using the common utility
    text = read_input_text(args.input)
    
    # Process the input
    result = extractor.process_input(text, prioritize=args.prioritize, save=args.save)
    
    # Display results
    print("\n=== EXTRACTED TASKS ===")
    print(result["extracted_tasks"])
    
    if args.prioritize:
        print("\n=== PRIORITIZED TASKS ===")
        print(result["prioritized_tasks"])
    
    if args.save:
        print("\nResults saved to the output directory.")


if __name__ == "__main__":
    main()
