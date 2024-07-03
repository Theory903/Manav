import yaml
def load_configuration(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)