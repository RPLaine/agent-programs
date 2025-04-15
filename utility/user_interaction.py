import time
from typing import List, Dict, Any


class UserInteraction:
    def __init__(self):
        self.interaction_history = []
    
    def request_information(self, questions: List[str]) -> Dict[str, str]:
        print("\n--- Additional Information Needed ---")
        
        responses = {}
        for question in questions:
            response = input(f"{question} ")
            responses[question] = response
            
            self.log_interaction("question", question, response)
        
        return responses
    
    def provide_update(self, update_text: str):
        print(f"\n--- Status Update ---\n{update_text}\n")
        self.log_interaction("update", update_text, None)
    
    def confirm_action(self, action_description: str) -> bool:
        response = input(f"\nConfirm: {action_description} (y/n): ")
        confirmed = response.lower() in ["y", "yes"]
        
        self.log_interaction("confirmation", action_description, "yes" if confirmed else "no")
        return confirmed
    
    def log_interaction(self, interaction_type: str, content: str, response: Any = None):
        self.interaction_history.append({
            "type": interaction_type,
            "content": content,
            "response": response,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def get_interaction_history(self) -> List[Dict[str, Any]]:
        return self.interaction_history
    
    def choose_option(self, prompt: str, options: List[str]) -> str:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        while True:
            try:
                choice = int(input("Enter your choice (number): "))
                if 1 <= choice <= len(options):
                    selected = options[choice-1]
                    self.log_interaction("option_choice", prompt, selected)
                    return selected
                else:
                    print(f"Please enter a number between 1 and {len(options)}")
            except ValueError:
                print("Please enter a valid number")
    
    def provide_feedback(self, result: Any) -> str:
        print("\n--- Job Results ---")
        print(result)
        
        feedback = input("\nPlease provide any feedback on these results: ")
        self.log_interaction("feedback", str(result), feedback)
        
        return feedback
