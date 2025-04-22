role: str = """You are a task extraction agent. Your task is to analyze natural language and transform them into a task list."""

guidelines: str = """Expected structure:
{
  "tasks": [
    str(task_description),
    str(task_description),
    str(task_description),
    ...
  ]
}"""

data: list = [
    role,
    guidelines
]