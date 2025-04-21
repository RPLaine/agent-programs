# filepath: d:\git\agent-programs\task_manager\task_extractor.py
"""
Task Extractor - An AI-based system for extracting, prioritizing, and managing tasks from user input.
Built for the Dolphin AI system.
"""

import os
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

# Setup logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("task_manager.task_extractor")

# Import API utility similar to what's used in task_extraction.py
try:
    import llm.api as api
except ImportError:
    # Fall back to relative import if we're running from within task_manager
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import llm.api as api


class TaskExtractor:
    """Task Extractor that extracts and manages tasks from natural language input."""
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the TaskExtractor.
        
        Args:
            output_dir: Directory to save task outputs. If None, defaults to 'output' in parent directory.
        """
        self.tasks = ""  # Initialize as empty string since API returns strings
        
        if not output_dir:
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            output_dir = os.path.join(script_dir, "output")
            
        os.makedirs(output_dir, exist_ok=True)
        self.output_dir = output_dir
        logger.info(f"TaskExtractor initialized. Output directory: {output_dir}")

    def extract_tasks(self, text: str) -> str:
        """Extract tasks from natural language text.
        
        Args:
            text: Natural language description containing potential tasks.
            
        Returns:
            Extracted tasks as a formatted string.
        """
        logger.info("Extracting tasks from input text")
        
        system_prompt = """
You are a task extraction specialist. Your task is to analyze natural language descriptions and transform them into clear, actionable task lists. Follow these guidelines:

1. Identify distinct actions, steps, or activities in the provided text
2. Transform each identified element into a concise task statement
3. Preserve the hierarchical structure and logical flow of the original content
4. Format tasks with clear numbering or bullet points when appropriate
5. Group related tasks together under meaningful categories
6. Ensure each task is specific, actionable, and self-contained
7. Preserve any timing or sequence information from the original text

Your output should be a well-structured list of tasks that captures all the actions implied in the original description while making them explicit and actionable.
"""

        prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{text}
<|im-end|>
<|im-assistant|>
"""
        data = {"prompt": prompt, "max_length": 2048}
        response = api.request(data)
        
        # Store the raw string response for use in other methods
        self.tasks = response
        
        return response

    def prioritize_tasks(self, tasks: Optional[str] = None) -> Dict[str, Any]:
        """Prioritize a list of tasks based on dependencies and importance.
        
        Args:
            tasks: Task list to prioritize. If None, uses previously extracted tasks.
            
        Returns:
            Dictionary containing original and prioritized tasks.
        """
        if tasks is None:
            if not self.tasks:
                raise ValueError("No tasks available to prioritize. Extract tasks first or provide a task list.")
            tasks = self.tasks
        
        logger.info("Prioritizing tasks")
        
        system_prompt = """
You are a task prioritization specialist. Your task is to analyze a list of tasks and prioritize them based on logical sequence, dependencies, and importance. Follow these guidelines:

1. Identify dependencies between tasks (which tasks must be completed before others)
2. Assign priority levels (High, Medium, Low) to each task
3. Group tasks by category or project phase when appropriate
4. Highlight any critical path tasks that may become bottlenecks
5. Preserve the essential content and meaning of each task

Your output should be the same list of tasks, but reorganized and annotated with priority levels to create an optimal execution sequence.
"""

        prompt = f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
Task List:
{tasks}
<|im-end|>
<|im-assistant|>
"""
        data = {"prompt": prompt, "max_length": 2048}
        response = api.request(data)
        
        result = {
            "extracted_tasks": tasks,
            "prioritized_tasks": response
        }
        
        return result
    
    def save_tasks(self, task_data: Dict[str, Any], description: str = "") -> str:
        """Save task data to a file.
        
        Args:
            task_data: Dictionary containing task information.
            description: Brief description of the task set.
            
        Returns:
            Path to the saved file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tasks_{timestamp}.json"
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data for saving
        save_data = {
            "timestamp": timestamp,
            "description": description,
            "task_data": task_data
        }
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Tasks saved to {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving tasks to {filepath}: {e}")
            raise
    
    def process_input(self, text: str, prioritize: bool = True, save: bool = True) -> Dict[str, Any]:
        """Process user input to extract and optionally prioritize tasks.
        
        Args:
            text: Natural language input text.
            prioritize: Whether to prioritize the extracted tasks.
            save: Whether to save the results to a file.
            
        Returns:
            Dictionary containing the extracted and potentially prioritized tasks.
        """
        logger.info("Processing user input for task extraction")
        
        tasks = self.extract_tasks(text)
        
        result = {
            "original_text": text,
            "extracted_tasks": tasks
        }
        
        if prioritize:
            prioritized = self.prioritize_tasks(tasks)
            result["prioritized_tasks"] = prioritized["prioritized_tasks"]
        
        if save:
            output_path = self.save_tasks(result, description=text[:50] + "..." if len(text) > 50 else text)
            result["output_file"] = output_path
        
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
    
    # Get input text
    if args.input:
        if os.path.isfile(args.input):
            try:
                with open(args.input, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                print(f"Error reading file: {e}")
                text = input("Enter description text: ")
        else:
            text = args.input
    else:
        text = input("Enter description text: ")
    
    # Process the input
    result = extractor.process_input(text, prioritize=args.prioritize, save=args.save)
    
    # Display results
    print("\n=== EXTRACTED TASKS ===")
    print(result["extracted_tasks"])
    
    if args.prioritize:
        print("\n=== PRIORITIZED TASKS ===")
        print(result["prioritized_tasks"])
    
    if args.save:
        print(f"\nResults saved to: {result['output_file']}")


if __name__ == "__main__":
    main()
