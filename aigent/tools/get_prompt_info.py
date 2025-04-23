import os
import importlib

def get_prompt_filenames() -> list[str]:
    try:
        import aigent.prompts as prompts_package
        prompts_dir = os.path.dirname(prompts_package.__file__)
        filenames = []
        for filename in os.listdir(prompts_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                filename_without_ext = filename[:-3]
                filenames.append(filename_without_ext)
        return filenames
    except ImportError:
        print("Error: aigent.prompts package not found")
        return []

def get_prompt_data(filename: str) -> list[str]:
    module_path = f"aigent.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'data'):
            return module.data
        else:
            print(f"Warning: No 'data' list found in {filename}")
            return []
    except ImportError:
        print(f"Error: Could not import module {module_path}")
        return []
    except AttributeError:
        print(f"Error: Module {module_path} does not have a 'data' attribute")
        return []
    
def get_prompt_dict(filename: str) -> dict:
    module_path = f"aigent.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'prompt_dict'):
            return module.prompt_dict
        else:
            print(f"Warning: No 'prompt_dict' found in {filename}")
            return {}
    except ImportError:
        print(f"Error: Could not import module {module_path}")
        return {}
    except AttributeError:
        print(f"Error: Module {module_path} does not have a 'prompt_dict' attribute")
        return {}

if __name__ == "__main__":
    prompt_files = get_prompt_filenames()
    print(f"Available prompt files: {prompt_files}")
    if prompt_files:
        sample_file = prompt_files[0]
        data = get_prompt_data(sample_file)
        print(f"\nData from {sample_file}: {data}")
