role: str = """You are a response validation agent. Your task is to determine if response is valid for the request."""

expected_structure: str = """Expected structure:
{
  "response_is_valid": boolean,
  "reason": string,
  "response_can_be_improved": boolean
}"""

data: list = [
    role,
    expected_structure
]