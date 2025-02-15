import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO
import re

# URL of the table page
TABLE_URL = "https://pmc.ncbi.nlm.nih.gov/articles/PMC5573769/table/tbl1/"

# Define a user-agent to mimic a browser request
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}


def fetch_html(url: str, headers: dict) -> str:
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error accessing page (Status Code: {response.status_code})")
    return response.text


def extract_table(html: str) -> pd.DataFrame:
    """Extract the HTML table from the page using Pandas."""
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table")
    if not table:
        raise Exception("No table found on the page.")

    # Wrap the table HTML in a StringIO object to avoid deprecation warnings with pd.read_html
    html_table = StringIO(str(table))
    tables = pd.read_html(html_table)
    if not tables:
        raise Exception("No tables were found using pd.read_html.")

    return tables[0]


def extract_asthma_section(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the portion of the DataFrame corresponding to the Asthma section.
    Assumes that the row where the first column equals "Asthma" marks the beginning of that section.
    """
    # Identify the row where the first column is "asthma"
    mask = df.iloc[:, 0].astype(str).str.strip().str.lower() == "asthma"
    if not mask.any():
        raise Exception("No row with 'Asthma' found in the first column.")

    asthma_marker_index = df[mask].index[0]

    # All rows after the marker are part of the Asthma section
    df_asthma = df.loc[asthma_marker_index + 1:].reset_index(drop=True)

    first_row = df_asthma.iloc[0].astype(str).str.strip()
    if first_row.nunique() == 1 and first_row.iloc[0].lower() == "asthma":
        df_asthma = df_asthma.iloc[1:].reset_index(drop=True)

    # Rename the first column if it has a default name like "Unnamed: 0"
    if df_asthma.columns[0].startswith("Unnamed"):
        df_asthma = df_asthma.rename(columns={df_asthma.columns[0]: "Category"})

    return df_asthma


def extract_final_value(cell: str) -> str:
    """
    Extract the final numeric value from a cell (the value for 2015).
    For example, from "397 (363 to 439)" it returns "439".
    If the cell contains parentheses but does not match the expected format,
    it returns the part before the parenthesis.
    Otherwise, returns the stripped cell.
    """
    if not isinstance(cell, str):
        return cell
    # Replace any non-breaking spaces with a regular space.
    cell = cell.replace(" ", " ")
    pattern = re.compile(r'\(.*?to\s+([-−]?[0-9]+(?:[.,·][0-9]+)?)\)')
    match = pattern.search(cell)
    if match:
        return match.group(1).strip()
    else:
        # If a parenthesis exists but no match for "to" is found, return the text before the parenthesis.
        if '(' in cell:
            return cell.split('(')[0].strip()
        return cell.strip()


def process_asthma_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process the Asthma DataFrame by extracting only the final numeric value for each data cell.
    """
    df_processed = df.copy()
    for col in df_processed.columns[1:]:
        df_processed[col] = df_processed[col].apply(extract_final_value)
    return df_processed


def main():
    try:
        # Fetch the HTML content from the URL
        html_content = fetch_html(TABLE_URL, HEADERS)

        # Extract the first table from the HTML
        df_full = extract_table(html_content)
        print("Preview of the full extracted table:")
        print(df_full.head(10))

        # Extract the Asthma section from the full table
        df_asthma = extract_asthma_section(df_full)
        print("\nPreview of the extracted Asthma section:")
        print(df_asthma.head())

        # Process the Asthma data to extract the final numeric value from each cell
        df_asthma_processed = process_asthma_data(df_asthma)
        print("\nPreview of the processed Asthma data:")
        print(df_asthma_processed.head())

        # Retain only the desired columns
        columns_to_keep = ["Category", "Number of deaths (thousands)", "Number of prevalent cases (thousands)"]
        missing_cols = [col for col in columns_to_keep if col not in df_asthma_processed.columns]
        if missing_cols:
            raise Exception(f"Expected columns not found in the DataFrame: {missing_cols}")

        df_final = df_asthma_processed[columns_to_keep].copy()

        # Save the final DataFrame to a CSV file
        output_file = "table_1_asthma_final_two_columns.csv"
        df_final.to_csv(output_file, index=False)
        print(f"\n✅ Final CSV (with 2 columns) saved as '{output_file}'")
        print(df_final.head())

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
