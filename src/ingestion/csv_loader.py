
import pandas as pd

def load_csv(file_path):
    """
    Loads a CSV file containing clinical terms and returns a DataFrame.
    """
    try:
        df = pd.read_csv(file_path)
        # Clean text columns (example: converting to lowercase)
        text_columns = ['Label', 'Label Arabic']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].str.lower().str.strip()
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV file: {e}")

if __name__ == "__main__":
    df = load_csv("data/raw/MSF_MentalHealth_Concepts_Benchmarking_Dataset.csv")
    print(df.head())
