import json

TEMPLATES_FILE_PATH = 'Data/Prompt/prompt_templates.json'

def load_templates(file_path=TEMPLATES_FILE_PATH):
    """Load prompt templates from JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    
def find_prompt_by_title(title, templates = load_templates()):
    """Find prompt by title in loaded templates."""
    for prompts in templates.values():
        for prompt in prompts:
            if prompt.get('title') == title:
                return prompt.get('prompt', '')
    return None  # Return None if title is not found

def save_templates(templates, file_path=TEMPLATES_FILE_PATH):
    """Save templates to JSON file."""
    with open(file_path, 'w') as f:
        json.dump(templates, f, indent=4)

if __name__ == "__main__":
    # Example usage
    
    title_to_find = "Blog Posting Schedule"
    prompt_found = find_prompt_by_title(title_to_find, templates)
    if prompt_found:
        print(f"Prompt found:\n{prompt_found}")
    else:
        print(f"No prompt found with title '{title_to_find}'")
