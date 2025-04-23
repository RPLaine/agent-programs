import aigent.tools.get_prompt_info as get_prompt_info
import json
import os

def get_current_file_name_without_extention() -> str:
    current_file = os.path.basename(__file__)
    current_file_name = os.path.splitext(current_file)[0]
    return current_file_name

objective: str = """
Choose an agent that would serve the user request.

Respond in JSON format:
{
    "helpful_agent_for_the_user_message": one agent name from the list of agents
}
"""

agents: list = get_prompt_info.get_prompt_filenames()

agents_data = {}
for agent in agents:
    if agent == get_current_file_name_without_extention():
        continue
    prompt_data = get_prompt_info.get_prompt_data(agent)
    agents_data[agent] = prompt_data[0] if prompt_data else ""

agents_list = """
agent_names: [""" + ", ".join(agents_data.keys()) + "]"

data: list = [
    agents_list,
    objective
]

assistant_start: str = """
{
    "chosen_agent": """

prompt_dict: dict = {
    "system": data,
    "user": "",
    "assistant": assistant_start
}

if __name__ == "__main__":
    print("Testing choose_agent.py")
    print("-" * 30)
    
    print(data[0])
    print()
    
    print(data[1])
    print()
    
    print(data[2])
    print()
    
    print("Test completed successfully.")