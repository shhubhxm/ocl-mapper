import pandas as pd

# Load the dataset (update the filename if needed)
file_path = "data/raw/MSF_MentalHealth_Concepts_Benchmarking_Dataset.csv"
df = pd.read_csv(file_path)

# Take a 10% random sample
test_df = df.sample(frac=0.1, random_state=42)

# Save the test dataset to a new CSV file
test_df.to_csv("data/processed/datatest_MSF_MentalHealth.csv", index=False)

print("Test dataset created successfully with 10% of the original data.")
