objective: str = """
** Objective **
Is the assistant's response valid?
"""

expected_structure: str = """
** Expected structure **
{
  "response_is_valid": boolean,
  "reason": string,
  "response_can_be_improved": boolean
}
"""

data: list = [
    objective,
    expected_structure
]