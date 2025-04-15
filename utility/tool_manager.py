import os
import sys
import importlib
from typing import Dict, Any, List, Optional


class ToolManager:
    def __init__(self):
        self.available_tools = {}
        self.tool_modules = {}
        self.tools_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools")
    
    def discover_tools(self):
        tools_dir = self.tools_dir
        
        if not os.path.exists(tools_dir) or not os.path.isdir(tools_dir):
            print(f"Tools directory not found: {tools_dir}")
            return
        
        self._discover_tools_in_directory(tools_dir, "")
    
    def _discover_tools_in_directory(self, path: str, package_prefix: str):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            if os.path.isdir(item_path) and not item.startswith("__"):
                subpackage = f"{package_prefix}.{item}" if package_prefix else item
                self._discover_tools_in_directory(item_path, subpackage)
            
            elif item.endswith(".py") and not item.startswith("__"):
                module_name = item[:-3]  # Remove .py extension
                full_module_name = f"{package_prefix}.{module_name}" if package_prefix else module_name
                
                try:
                    module_path = f"tools.{full_module_name}" if package_prefix else f"tools.{module_name}"
                    module = importlib.import_module(module_path)
                    
                    # Add to available tools
                    self.available_tools[full_module_name] = {
                        "module_name": module_path,
                        "file_path": item_path,
                        "name": module_name
                    }
                    
                    self.tool_modules[full_module_name] = module
                    
                except Exception as e:
                    print(f"Error importing tool {full_module_name}: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[Any]:
        if tool_name in self.tool_modules:
            return self.tool_modules[tool_name]
        
        for name, module in self.tool_modules.items():
            if name.endswith(tool_name):
                return module
        
        return None
    
    def get_tool_function(self, tool_name: str, function_name: str) -> Optional[Any]:
        tool = self.get_tool(tool_name)
        if tool and hasattr(tool, function_name):
            return getattr(tool, function_name)
        return None
    
    def execute_tool(self, tool_name: str, function_name: str = "", **kwargs) -> Any:
        tool = self.get_tool(tool_name)
        if not tool:
            print(f"Tool not found: {tool_name}")
            return None
        
        if function_name is None:
            # Try to find a function with the same name as the module
            module_name = tool_name.split(".")[-1]
            if hasattr(tool, module_name):
                function = getattr(tool, module_name)
                return function(**kwargs)
            
            # Look for common function names
            for common_function in ["main", "execute", "run"]:
                if hasattr(tool, common_function):
                    function = getattr(tool, common_function)
                    return function(**kwargs)
        else:
            if hasattr(tool, function_name):
                function = getattr(tool, function_name)
                return function(**kwargs)
        
        print(f"Function not found in tool {tool_name}: {function_name}")
        return None
    
    def list_available_tools(self) -> Dict[str, Dict[str, str]]:
        return self.available_tools
