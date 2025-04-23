objective: str = """
** Objective **
Create a task list from user input.
"""

expected_structure: str = """
** Expected structure **
{
  "tasks_from_user_input": [
    string,
    string,
    string,
    ...
  ]
}"""

data: list = [
    objective,
    expected_structure
]