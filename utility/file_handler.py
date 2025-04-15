import os
import shutil
from typing import List, Dict, Any, Optional


class FileHandler:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
    
    def read_file(self, filename: str) -> Optional[str]:
        filepath = os.path.join(self.base_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            return None
        except Exception as e:
            print(f"Error reading file {filename}: {e}")
            return None
    
    def write_file(self, filename: str, content: str) -> bool:
        filepath = os.path.join(self.base_dir, filename)
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file {filename}: {e}")
            return False
    
    def list_files(self, subdir: str = "") -> List[str]:
        dir_path = os.path.join(self.base_dir, subdir)
        try:
            if os.path.exists(dir_path):
                files = []
                for item in os.listdir(dir_path):
                    item_path = os.path.join(dir_path, item)
                    if os.path.isfile(item_path):
                        files.append(os.path.join(subdir, item) if subdir else item)
                return files
            return []
        except Exception as e:
            print(f"Error listing files in {subdir}: {e}")
            return []
    
    def file_exists(self, filename: str) -> bool:
        filepath = os.path.join(self.base_dir, filename)
        return os.path.exists(filepath) and os.path.isfile(filepath)
    
    def copy_file(self, source: str, destination: str) -> bool:
        source_path = os.path.join(self.base_dir, source)
        dest_path = os.path.join(self.base_dir, destination)
        try:
            if os.path.exists(source_path):
                os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                shutil.copy2(source_path, dest_path)
                return True
            return False
        except Exception as e:
            print(f"Error copying file from {source} to {destination}: {e}")
            return False
    
    def delete_file(self, filename: str) -> bool:
        filepath = os.path.join(self.base_dir, filename)
        try:
            if os.path.exists(filepath) and os.path.isfile(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filename}: {e}")
            return False
