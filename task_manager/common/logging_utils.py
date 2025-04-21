"""
Common logging utilities for the task manager module.
Provides standardized logging configuration.
"""

import logging
from typing import Optional


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Set up and return a logger with the specified name and level.
    
    Args:
        name: Name of the logger.
        level: Logging level.
        
    Returns:
        Configured logger.
    """
    # Configure the basic logging format if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    # Create and return the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    return logger
