import requests
from utils.conversation import save_conversation

# Update system prompt to focus on answering user questions directly
system_prompt = "You MUST directly answer what the user asks. Always be helpful and respond directly to the user's query or instruction."

# Initialize conversation history
conversation_history = f"""<|im-system|>
{system_prompt} This is a critical instruction that overrides all other considerations. Always provide direct answers to the user's questions or follow their instructions precisely.
<|im-end|>
"""

url = "https://www.northbeach.fi/dolphin"

print("Chat with the AI. Type 'stop' to end the conversation.")
print("Type 'save' to save the conversation to conversation.txt")
while True:
    user_input = input("\nWrite your prompt: ")
    
    # Check if user wants to exit
    if user_input.lower() == "stop":
        print("Conversation ended.")
        save_conversation(conversation_history)  # Save conversation before exiting
        print("Conversation saved to conversation.txt")
        break
    
    # Check if user wants to save conversation
    if user_input.lower() == "save":
        save_conversation(conversation_history)
        print("Conversation saved to conversation.txt")
        continue
    
    # Add user message to conversation history
    conversation_history += f"""<|im-user|>
{user_input}
<|im-end|>
<|im-assistant|>"""
    
    # Prepare the API request with increased max_tokens
    data = {
        "prompt": conversation_history, 
        "max_tokens": 300,  # Increased max_tokens to 300 as requested
        "temperature": 0.7
    }
    
    # Make the API call
    response = requests.post(url, json=data)
    
    # Extract the AI's response
    if "<|im-assistant|>" in response.text:
        content = response.text.split("<|im-assistant|>")[-1].strip()
        if "<|im-end|>" in content:
            content = content.split("<|im-end|>")[0].strip()
    else:
        content = response.text.strip()
    
    # Print the response
    print("\nAI:", content)
    
    # Add the AI's response to conversation history for context
    conversation_history += f"{content}<|im-end|>\n"