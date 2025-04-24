import os
import time
import uuid
import json
import aiohttp    

import aigent.settings as settings
from aigent.tools.get_prompt_info import get_prompt_dict

class Agent:
    def __init__(
            self,
            prompt_dict: dict = {},
            output_file_type: str = ".txt",
            output_dir_name: str = "",
            llm_url: str = "https://www.northbeach.fi/dolphin"
            ):

        self.prompt_dict: dict = prompt_dict
        self.output_file_type: str = output_file_type
        self.output_dir_name: str = output_dir_name
        self.llm_url: str = llm_url
        
        self.handle_output_dir()
    
    async def process(self, user_input: str = "", model_url: str = "") -> str:
        prompt: str = self.create_prompt(user_input)
        if model_url == "": model_url = self.llm_url
        data: dict = {
            "prompt": prompt,
            "user_input": user_input,
            "model_url": model_url
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

    def create_system_prompt(self) -> str:
        system_prompt: str = settings.data[0]
        system_prompt += self.prompt_dict['system'] if 'system' in self.prompt_dict else ""
        system_prompt += settings.data[1]
        return system_prompt

    def create_prompt(self, user_input: str = "") -> str:
        system_prompt: str = self.create_system_prompt()
        prompt: str = f"""<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{user_input}
{self.prompt_dict["user"] if "user" in self.prompt_dict else ""}
<|im-end|>
<|im-assistant|>
{self.prompt_dict["assistant"] if "assistant" in self.prompt_dict else ""}"""
        return prompt

    async def request(self, data: dict, max_length: int = 64000, timeout: int = 300, tries: int = 10) -> str:
        data["max_length"] = max_length
        
        try:
            async with aiohttp.ClientSession() as session:
                result: str = ""
                i: int = 0
                while i < tries:
                    async with session.post(data["model_url"], json=data, timeout=timeout) as response:
                        response.raise_for_status()
                        response_text = await response.text()
                        result = self.clean_response_text(response_text)
                        if result:
                            break
                    i += 1
                return result
        except Exception as e:
            print(f"Error: {e}")
            return str(e)
        
    def clean_response_text(self, response_text: str) -> str:
        if "<|im-assistant|>" in response_text:
            response_text = response_text.split("<|im-assistant|>")[-1]
        special_tokens: list[str] = ["<|im-assistant|>", "<|im-end|>", "<|im-user|>", "<|im-system|>"]
        for token in special_tokens:
            response_text = response_text.replace(token, "")
        return response_text.strip()


async def run_agent_process(agent_name: str, user_input: str = "") -> str:
    prompt_dict: dict = get_prompt_dict(agent_name)
    agent: Agent = Agent(prompt_dict)
    if user_input == "":
        user_input = input("Enter your input: ")
    response = await agent.process(user_input)
    
    parsed_response: dict = {}
    try:
        parsed_response = json.loads(response)
        return json.dumps(parsed_response, indent=4)
    except json.JSONDecodeError:
        print("-" * 20)
        print("Failed to parse the response as JSON.")
        print("Response:")
        print(response)
        print("-" * 20)
        return response