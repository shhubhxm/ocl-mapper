import pandas as pd
import json

# Load the JSON dataset (update filename if needed)
input_file = "data/raw/export.json"
output_file = "data/processed/export.json"

# Read the JSON file into a DataFrame
with open(input_file, "r") as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Take a 10% random sample
test_df = df.sample(frac=0.1, random_state=42)

# Convert back to JSON
test_data = test_df.to_dict(orient="records")

# Save the smaller JSON dataset
with open(output_file, "w") as f:
    json.dump(test_data, f, indent=4)

print(f"Test JSON file '{output_file}' created successfully with 10% of the original data.")
