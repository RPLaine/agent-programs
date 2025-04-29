import os
import json
import aiohttp    

from worker.settings import settings

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
        print(f"  ├─ Creating prompt for agent...")
        prompt: str = self.create_prompt(user_input)
        if model_url == "": model_url = self.llm_url
        
        print(f"  ├─ Sending request to LLM at {model_url.split('/')[-1]}")
        data: dict = {
            "prompt": prompt,
            "user_input": user_input,
            "model_url": model_url
        }
        response: str = await self.request(data)

        return response
    
    def handle_output_dir(self):
        if self.output_dir_name is None or self.output_dir_name == "":
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.output_dir_name = os.path.join(project_root, "output")
        os.makedirs(self.output_dir_name, exist_ok=True)

    def create_system_prompt(self) -> str:
        system_prompt: str = settings["agent"]["global_system_start_prompt"]
        system_prompt += self.prompt_dict['system'] if 'system' in self.prompt_dict else ""
        system_prompt += settings["agent"]["global_system_end_prompt"]
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
                    try:
                        print(f"  ├─ Request attempt {i+1}/{tries} to LLM...")
                        async with session.post(data["model_url"], json=data) as response:
                            response.raise_for_status()
                            response_text = await response.text()
                            result = self.clean_response_text(response_text)
                            if result:
                                print(f"  ├─ Received response: {len(result)} characters")
                                break
                            else:
                                print(f"  ├─ ⚠️ Empty response received")
                    except Exception as e:
                        print(f"  ├─ ⚠️ Request attempt {i+1} failed: {str(e)[:100]}...")
                    i += 1
                    
                if not result:
                    print(f"  ├─ ❌ All {tries} request attempts failed")
                return result
        except Exception as e:
            error_msg = f"Error: {e}"
            print(f"  ├─ ❌ {error_msg}")
            return str(e)
        
    def clean_response_text(self, response_text: str) -> str:
        if "<|im-assistant|>" in response_text:
            response_text = response_text.split("<|im-assistant|>")[-1]
        special_tokens: list[str] = ["<|im-assistant|>", "<|im-end|>", "<|im-user|>", "<|im-system|>"]
        for token in special_tokens:
            response_text = response_text.replace(token, "")
        return response_text.strip()

async def get_prompt_dict(filename: str) -> dict:
    import importlib

    module_path = f"worker.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'prompt_dict'):
            return module.prompt_dict
        else:
            return {}
    except:
        return {}

async def run_agent(prompt_name: str, prompt_content: str = "") -> str:

    prompt_dict: dict = await get_prompt_dict(prompt_name)

    agent: Agent = Agent(prompt_dict)


    response = await agent.process(prompt_content)
    
    parsed_response: dict = {}

    try:
        parsed_response = json.loads(response)
        return json.dumps(parsed_response, indent=4)
    except:
        return response
    
if __name__ == "__main__":
    import asyncio

    prompt_name: str = "test"
    prompt_content: str = """
CLAIM:
The content is relevant to news.

CONTENT:
We have just found interesting fact about a new species of fish in the ocean.
"""

    response = asyncio.run(run_agent(prompt_name, prompt_content))
    print(response)