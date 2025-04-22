import os
import time
import uuid
import requests

class Agent:
    def __init__(
            self, 
            prompt_data: dict = {
                "global_start_prompt": "",
                "global_end_prompt": "",
                "agent_system_prompt": ""
            }, 
            output_file_type: str = ".txt", 
            output_dir_name: str = "", 
            llm_url: str = "https://www.northbeach.fi/dolphin"
            ):
        
        self.prompt_data: dict = prompt_data
        self.system_prompt: str = self.create_system_prompt(prompt_data["global_start_prompt"], prompt_data["global_end_prompt"], prompt_data["agent_system_prompt"])
        self.output_file_type: str = output_file_type
        self.output_dir_name: str = output_dir_name
        self.llm_url: str = llm_url
        
        self.handle_output_dir()
    
    async def process(self, user_input: str):
        prompt: str = self.create_prompt(user_input)
        data: dict = {
            "prompt": prompt
            }
        response: str = await self.request(data)

        self.save_response(response)
        return response
    
    def handle_output_dir(self):
        if self.output_dir_name is None or self.output_dir_name == "":
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.output_dir_name = os.path.join(project_root, "output")
        os.makedirs(self.output_dir_name, exist_ok=True)

    def save_response(self, response: str):
        time_now: str = str(time.time()).split(".")[0]
        uuid_now: str = str(uuid.uuid4()).split("-")[0]
        file_name: str = time_now + "_" + uuid_now + self.output_file_type
        file_path: str = os.path.join(self.output_dir_name, file_name)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(response)

    def create_system_prompt(self, global_start_prompt: str = "", global_end_prompt: str = "", agent_system_prompt: str = "") -> str:
        system_prompt: str = f"""{global_start_prompt}
{agent_system_prompt}
{global_end_prompt}"""
        return system_prompt

    def create_prompt(self, user_input: str = "") -> str:
        system_prompt: str = self.system_prompt
        prompt: str = f"""<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{user_input}
<|im-end|>
<|im-assistant|>"""
        return prompt

    async def request(self, data: dict, max_length: int = 64000, timeout: int = 300) -> str:
        data["max_length"] = max_length
        
        try:
            response = requests.post(self.llm_url, json=data, timeout=timeout)
            response.raise_for_status()
            response.encoding = 'utf-8'
            result = self.clean_response(response.text)
            return result
        except Exception as e:
            print(f"Error: {e}")
            return str(e)
        
    def clean_response(self, response) -> str:
        if "<|im-assistant|>" in response:
            response = response.split("<|im-assistant|>")[-1]
        special_tokens = ["<|im-assistant|>", "<|im-end|>", "<|im-user|>", "<|im-system|>"]
        for token in special_tokens:
            response = response.replace(token, "")
        return response.strip()


if __name__ == "__main__":
    import asyncio

    prompt_data = {
        "global_start_prompt": "",
        "global_end_prompt": "Respond with only one message.",
        "agent_system_prompt": "You are the helpful assistant."
    }

    agent = Agent(prompt_data)
    user_input = "Who are you?"
    response = asyncio.run(agent.process(input("Enter your input: ")))
    print("Response:", response)