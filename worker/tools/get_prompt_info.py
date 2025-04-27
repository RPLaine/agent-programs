import os
import importlib

def get_prompt_filenames() -> list[str]:
    import worker.prompts as prompts_package

    try:
        prompts_dir = os.path.dirname(prompts_package.__file__)
        filenames = []
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                filename_without_ext = filename[:-3]
                filenames.append(filename_without_ext)
        return filenames
    except:
        return []

def get_prompt_data(filename: str) -> list[str]:
    module_path = f"worker.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'data'):
            return module.data
        else:
            return []
    except:
        return []
    
def get_prompt_dict(filename: str) -> dict:
    module_path = f"worker.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'prompt_dict'):
            return module.prompt_dict
        else:
            return {}
    except:
        return {}

if __name__ == "__main__":
    import json 

    print(json.dumps(get_prompt_dict("test"), indent=2))
    print(json.dumps(get_prompt_dict("plan"), indent=2))
    print(json.dumps(get_prompt_dict("work"), indent=2))
