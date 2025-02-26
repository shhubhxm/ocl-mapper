# src/ingestion/json_loader.py
import json

def load_json(file_path):
    """
    Loads a JSON file and returns the parsed data.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise ValueError(f"Error loading JSON file: {e}")

if __name__ == "__main__":
    # Example usage (update file path as needed)
    data = load_json("data/raw/export.json")
    print(data)
