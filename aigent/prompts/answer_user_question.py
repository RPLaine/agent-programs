objective: str = """
** Objective **
What is the answer to the user message?
"""

expected_structure: str = """
** Expected structure **
{
    "answer_for_the_user": str(response)
}
"""

data: list = [
    objective,
    expected_structure
]