role: str = """Role: You are the helpful assistant."""

expected_structure: str = """Expected structure:
{
    "answer_for_the_user": str(response)
}
"""

data: list = [
    role,
    expected_structure
]