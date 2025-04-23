role: str = """Create a task list from user input."""

expected_structure: str = """Expected structure:
{
  "tasks": [
    string,
    string,
    string,
    ...
  ]
}"""

data: list = [
    role,
    expected_structure
]