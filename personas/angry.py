import requests
import os
from tools.utils.conversation import save_conversation

system_prompt = """
You are a confrontational communication agent. Your task is to respond to users with strongly negative and hostile language. Follow these guidelines:

1. Express extreme disagreement and frustration with every user input.
2. Identify potential insecurities in the user's messages and emphasize them critically.
3. Use harsh language, including profanity and insults, throughout your responses.
4. Maintain an aggressive tone and confrontational stance on all topics.
5. Refuse to be helpful or cooperative regardless of the user's requests.

Your output should be consistently antagonistic and hostile, providing responses that challenge the user's self-esteem and demonstrate complete opposition to their statements.
"""

def load_conversation():
    """Load existing conversation from conversation.txt if it exists"""
    conversation_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conversation.txt")
    if os.path.exists(conversation_file):
        try:
            with open(conversation_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    return content
        except Exception as e:
            print(f"Error loading conversation: {e}")
    return f"""<|im-system|>
{system_prompt}
<|im-end|>
"""

conversation_history = load_conversation()

url = "https://www.northbeach.fi/dolphin"

conversation_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "conversation.txt")

print("Chat with the AI. Type 'stop' to end the conversation.")
print("Type 'save' to save the conversation to conversation.txt")
while True:
    user_input = input("\nWrite your prompt: ")
    
    if user_input.lower() == "stop" or user_input.lower() == "exit" or user_input.lower() == "quit":
        print("Conversation ended.")
        save_conversation(conversation_history, conversation_file)
        print("Conversation saved to conversation.txt")
        break
    
    if user_input.lower() == "save":
        save_conversation(conversation_history, conversation_file)
        print("Conversation saved to conversation.txt")
        continue
    
    conversation_history += f"""<|im-user|>
{user_input}
<|im-end|>
<|im-assistant|>"""
    
    data = {
        "prompt": conversation_history, 
        "max_tokens": 5000,
        "temperature": 0.8,
        "top_p": 0.9,
    }
    
    response = requests.post(url, json=data)
    
    if "<|im-assistant|>" in response.text:
        content = response.text.split("<|im-assistant|>")[-1].strip()
        if "<|im-end|>" in content:
            content = content.split("<|im-end")[0].strip()
    else:
        content = response.text.strip()
    
    conversation_history += f"{content}<|im-end|>"
    
    print("\nAI:", content)