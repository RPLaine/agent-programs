import os
import time
import uuid
import requests
import json

import aigent.settings as settings

class Agent:
    def __init__(
            self,
            prompt_list: list = [],
            output_file_type: str = ".txt",
            output_dir_name: str = "",
            llm_url: str = "https://www.northbeach.fi/dolphin"
            ):

        self.prompt_list: list = prompt_list
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

        self.save_response(user_input, response)
        return response
    
    def handle_output_dir(self):
        if self.output_dir_name is None or self.output_dir_name == "":
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.output_dir_name = os.path.join(project_root, "output")
        os.makedirs(self.output_dir_name, exist_ok=True)

    def save_response(self, user_input: str, response: str):
        time_now: str = str(time.time()).split(".")[0]
        uuid_now: str = str(uuid.uuid4()).split("-")[0]
        file_name: str = time_now + "_" + uuid_now + self.output_file_type
        file_path: str = os.path.join(self.output_dir_name, file_name)

        file_dict: dict = {
            "user_input": user_input,
            "response": response
        }

        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(file_dict, indent=2))

    def create_system_prompt(self, prompt_list:list = []) -> str:
        system_prompt: str = settings.data[0] # global guidelines
        for prompt in prompt_list:
            if prompt == "":
                continue
            system_prompt += f"{prompt}\n"
        system_prompt += settings.data[1] # global reminder
        return system_prompt.strip()

    def create_prompt(self, user_input: str = "") -> str:
        system_prompt: str = self.create_system_prompt(self.prompt_list)
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

    prompt_list: list = [
        """Role: You are the helpful assistant.""",
        """Expected structure:
{
    "answer_for_the_user": str(response)
}""",
    ]

    agent = Agent(prompt_list)
    user_input = "Who are you?"
    response = asyncio.run(agent.process(input("Enter your input: ")))
    if json.loads(response):
        response = json.loads(response)
        response = json.dumps(response, indent=2)
    print(response)