description: str = """
** Question **
What is the boolean answer to the user message?
"""

expected_structure: str = """
** Expected structure **
{
  "is_the_answer_true_or_false": boolean,
  "reasoning": string
}
"""

data: list = [
    description,
    expected_structure
]