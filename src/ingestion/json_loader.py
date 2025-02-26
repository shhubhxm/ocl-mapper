# src/ingestion/json_loader.py
import json
import os

def load_json(json_path):
    """
    Loads the extracted JSON file and returns only the 'concepts' list.
    """
    try:
        # Ensure the file exists
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found at: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            full_data = json.load(f)

        # Extract only the 'concepts' key
        concepts = full_data.get("concepts", [])

        if not concepts:
            print("⚠ Warning: No concepts found in the JSON file!")

        return concepts

    except Exception as e:
        raise ValueError(f"Error loading JSON file: {e}")

if __name__ == "__main__":
    # Adjust the path to match your extracted JSON file location
    json_file_path = "data/raw/export.json"

    # Load and test the JSON extraction
    concepts_data = load_json(json_file_path)
    print(f"✅ Loaded {len(concepts_data)} concepts")
    print(concepts_data[:3])  # Print first 3 concepts for verification

