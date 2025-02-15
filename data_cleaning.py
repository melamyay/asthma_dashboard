from load_data import load_dataset


def clean_data(df):
    """
    Cleans the dataset by removing duplicates and converting column names to uppercase.
    Missing values are kept as they are.

    """

    print("Starting data cleaning...")

    # Remove duplicate
    initial_shape = df.shape
    df = df.drop_duplicates()
    print(f" Removed {initial_shape[0] - df.shape[0]} duplicate rows.")

    # Keep missing values as they are
    missing_values = df.isnull().sum()
    print(f"\n🔍 Missing values before cleaning:\n{missing_values[missing_values > 0]}")

    # Convert column names to uppercase
    df.columns = df.columns.str.upper()

    # Final check
    print("\n Data cleaning completed!")
    print(f"Final dataset shape: {df.shape}")

    return df


# Execute cleaning process
if __name__ == "__main__":
    df = load_dataset()
    df_cleaned = clean_data(df)

    # Save cleaned dataset
    df_cleaned.to_csv("cleaned_asthma_data.csv", index=False)
    print("\n Cleaned data saved as 'cleaned_asthma_data.csv'.")

