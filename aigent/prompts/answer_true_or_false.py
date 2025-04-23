role: str = """You are a true/false question analyzer."""

expected_structure: str = """Expected structure:
{
  "is_the_answer_true_or_false": boolean,
  "reasoning": string
}"""

data: list = [
    role,
    expected_structure
]