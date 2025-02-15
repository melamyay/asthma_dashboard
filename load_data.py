import os
import pandas as pd

# Define dataset path
DATA_PATH = "data/asthma_disease_data.csv"

def load_dataset(file_path=DATA_PATH):
    """
    Load and display basic information about the dataset.

    Args:
        file_path (str): Path to the dataset CSV file.

    Returns:
        pd.DataFrame: Loaded dataset as a pandas DataFrame, or None if an error occurs.
    """
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f" Error: The file '{file_path}' was not found. Make sure the path is correct.")
        return None

    try:
        # Load the dataset
        df = pd.read_csv(file_path)

        # Display dataset shape and first rows
        print(f" Dataset successfully loaded! Shape: {df.shape}")
        print("\n First 5 rows of the dataset:")
        print(df.head())

        # Display dataset info
        print("\n Dataset Information:")
        df.info()

        return df

    except Exception as e:
        print(f" Error loading dataset: {e}")
        return None

# Run this script independently to test the dataset loading
if __name__ == "__main__":
    df = load_dataset()
