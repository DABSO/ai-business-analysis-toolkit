import os

def load_prompt(file_name: str) -> str:
    """Load prompt text from a file."""
    prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', file_name)
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()