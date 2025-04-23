import os
import time
import uuid
import json
import aiohttp

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

    async def request(self, data: dict, max_length: int = 64000, timeout: int = 300, tries: int = 100) -> str:
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


if __name__ == "__main__":
    import asyncio
    from aigent.tools.get_prompt_info import get_prompt_data

    agent_name: str = "create_task_list"
    prompt_list: list[str] = get_prompt_data(agent_name)
    
    agent = Agent(prompt_list)
    response = asyncio.run(agent.process(input("Enter your input: ")))
    
    try:
        parsed_response = json.loads(response)
        response = json.dumps(parsed_response, indent=2)
    except json.JSONDecodeError:
        pass
    print(response)