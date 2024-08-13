import json

def load_json(file_path="/root/config.json"):
    with open(file_path, 'r') as f:
        return json.load(f)