# filepath: d:\git\agent-programs\task_manager\common\agent_config.py
from typing import Dict, Any, Optional
import json
import os

class AgentConfig:
    """
    Configuration manager for agent settings.
    Handles loading, storing, and retrieving configuration values.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config: Dict[str, Any] = {}
        self.config_path = config_path
        
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
    
    def load_config(self, config_path: str) -> None:
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading config from {config_path}: {e}")
            self.config = {}
    
    def save_config(self, config_path: Optional[str] = None) -> bool:
        """
        Save configuration to a file.
        
        Args:
            config_path: Path to save the configuration (uses self.config_path if not provided)
            
        Returns:
            True if saved successfully, False otherwise
        """
        save_path = config_path or self.config_path
        if not save_path:
            print("No config path specified")
            return False
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config to {save_path}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key is not found
            
        Returns:
            The configuration value or default
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
    
    def update(self, values: Dict[str, Any]) -> None:
        """
        Update multiple configuration values.
        
        Args:
            values: Dictionary of configuration key-value pairs
        """
        self.config.update(values)
