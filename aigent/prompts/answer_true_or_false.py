role: str = """You are a true/false question analyzer. Your task is to determine whether a statement about some data is true or false."""

guidelines: str = """Expected structure:
{
  "verdict": str("True" or "False" or "Insufficient data"),
  "explanation": str(explanation)
}"""

data: list = [
    role,
    guidelines
]