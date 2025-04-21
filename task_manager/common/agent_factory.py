from typing import Dict, Type, Any, Optional
import importlib
import os
import inspect

from task_manager.common.base_agent import BaseAgent

class AgentFactory:
    """
    Factory class for creating and managing agent instances.
    Handles agent registration, discovery, and instantiation.
    """
    
    def __init__(self):
        """Initialize the agent factory with an empty registry."""
        self.agent_registry: Dict[str, Type[BaseAgent]] = {}
    
    def register_agent(self, agent_name: str, agent_class: Type[BaseAgent]) -> None:
        """
        Register an agent class with the factory.
        
        Args:
            agent_name: Name to register the agent under
            agent_class: The agent class to register
        """
        if not issubclass(agent_class, BaseAgent):
            raise TypeError(f"Agent class must be a subclass of BaseAgent: {agent_class.__name__}")
        
        self.agent_registry[agent_name] = agent_class
    
    def create_agent(self, agent_name: str, **kwargs) -> BaseAgent:
        """
        Create an instance of a registered agent.
        
        Args:
            agent_name: Name of the agent to create
            **kwargs: Arguments to pass to the agent constructor
            
        Returns:
            An instance of the requested agent
            
        Raises:
            KeyError: If the agent name is not registered
        """
        if agent_name not in self.agent_registry:
            raise KeyError(f"Agent not registered: {agent_name}")
        
        agent_class = self.agent_registry[agent_name]
        return agent_class(**kwargs)
    
    def discover_agents(self, package_path: str = "task_manager") -> None:
        """
        Automatically discover and register agent classes from a package.
        
        Args:
            package_path: The package path to search for agents
        """
        # Get the absolute path to the package
        try:
            package = importlib.import_module(package_path)
            package_dir = os.path.dirname(inspect.getfile(package))
            
            # Recursively walk through the package directory
            for root, dirs, files in os.walk(package_dir):
                # Skip __pycache__ directories
                if "__pycache__" in root:
                    continue
                
                # Process Python files
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        # Get the relative module path
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, os.path.dirname(package_dir))
                        module_path = f"{package_path}.{os.path.splitext(rel_path.replace(os.sep, '.'))[0]}"
                        
                        try:
                            # Import the module
                            module = importlib.import_module(module_path)
                            
                            # Find and register agent classes
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    issubclass(obj, BaseAgent) and 
                                    obj != BaseAgent):
                                    # Register with the class name
                                    self.register_agent(name, obj)
                        except (ImportError, AttributeError) as e:
                            print(f"Error importing module {module_path}: {e}")
        except ImportError as e:
            print(f"Error importing package {package_path}: {e}")
    
    def list_available_agents(self) -> Dict[str, str]:
        """
        List all available agents and their descriptions.
        
        Returns:
            A dictionary mapping agent names to their descriptions
        """
        return {
            name: agent_class.__doc__ or "No description available" 
            for name, agent_class in self.agent_registry.items()
        }
