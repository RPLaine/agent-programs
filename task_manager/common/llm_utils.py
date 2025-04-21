"""
Common LLM API utilities for the task manager module.
Provides standardized interaction with the LLM API.
"""

import logging
from typing import Dict, Any, Optional

import llm.api as api
from task_manager.common.logging_utils import setup_logger

# Set up logger
logger = setup_logger("task_manager.common.llm_utils")


def generate_prompt(system_prompt: str, user_prompt: str) -> str:
    """Generate a formatted prompt for the LLM API.
    
    Args:
        system_prompt: System instructions.
        user_prompt: User input.
        
    Returns:
        Formatted prompt string.
    """
    return f"""
<|im-system|>
{system_prompt}
<|im-end|>
<|im-user|>
{user_prompt}
<|im-end|>
<|im-assistant|>
"""


def send_llm_request(prompt: str, max_length: int = 2048) -> str:
    """Send a request to the LLM API and return the response.
    
    Args:
        prompt: The formatted prompt to send.
        max_length: Maximum token length for the response.
        
    Returns:
        The LLM API response.
    """
    data = {"prompt": prompt, "max_length": max_length}
    logger.info(f"Sending request to LLM API with max_length={max_length}")
    
    try:
        response = api.request(data)
        logger.info(f"Received response of length: {len(response)} characters")
        return response
    except Exception as e:
        logger.error(f"Error calling LLM API: {e}")
        raise
