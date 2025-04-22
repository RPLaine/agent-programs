import os
import importlib
from typing import List, Any, Optional

def get_prompt_filenames() -> List[str]:
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

def get_prompt_data(filename: str) -> Optional[List[Any]]:
    module_path = f"aigent.prompts.{filename}"
    try:
        module = importlib.import_module(module_path)
        if hasattr(module, 'data'):
            return module.data
        else:
            print(f"Warning: No 'data' list found in {filename}")
            return None
    except ImportError:
        print(f"Error: Could not import module {module_path}")
        return None
    except AttributeError:
        print(f"Error: Module {module_path} does not have a 'data' attribute")
        return None

if __name__ == "__main__":
    prompt_files = get_prompt_filenames()
    print(f"Available prompt files: {prompt_files}")
    if prompt_files:
        sample_file = prompt_files[0]
        data = get_prompt_data(sample_file)
        print(f"\nData from {sample_file}: {data}")
