import pandas as pd
import plotly.express as px

# Load data
def load_data(file_path="table_1_asthma_final_two_columns.csv"):
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    if "Category" in df.columns:
        df = df.rename(columns={"Category": "SDI Category"})
    if "SDI Category" not in df.columns:
        raise Exception("Error: The column 'SDI Category' does not exist in the CSV file.")

    return df

# Clean numeric values
def clean_numeric_column(col):
    return pd.to_numeric(col.astype(str).str.replace(" ", ""), errors="coerce")

# Extract global values
def get_global_values(df):
    df_global = df[df["SDI Category"].str.lower() == "global"].reset_index(drop=True)
    number_of_deaths = df_global["Number of deaths (thousands)"].values[0]
    number_of_cases = df_global["Number of prevalent cases (thousands)"].values[0]
    return {"deaths": number_of_deaths, "cases": number_of_cases}

# Generate Treemap
def generate_treemap(df, value_col, color_scale, title):
    fig = px.treemap(
        df,
        path=["SDI Category"],
        values=value_col,
        color=value_col,
        color_continuous_scale=color_scale,
        title=title
    )
    return fig

# Main execution
if __name__ == "__main__":
    df = load_data()
    df["Number of deaths (thousands)"] = clean_numeric_column(df["Number of deaths (thousands)"])
    df["Number of prevalent cases (thousands)"] = clean_numeric_column(df["Number of prevalent cases (thousands)"])

    asthma_summary = get_global_values(df)
    print(f"Total deaths in 2015: {asthma_summary['deaths']} thousand")
    print(f"Total prevalent cases in 2015: {asthma_summary['cases']} thousand")
    print("Data ready for the Dashboard:", asthma_summary)

    df_sdi = df[df["SDI Category"].str.lower() != "global"].reset_index(drop=True)

    fig_deaths_treemap = generate_treemap(
        df_sdi, "Number of deaths (thousands)", "Reds",
        "Distribution of Asthma-related Deaths by SDI Category (Treemap)"
    )
    #fig_deaths_treemap.show()

    fig_cases_treemap = generate_treemap(
        df_sdi, "Number of prevalent cases (thousands)", "Blues",
        "Distribution of Asthma Prevalent Cases by SDI Category (Treemap)"
    )
    #fig_cases_treemap.show()

    print("Analysis of deaths and prevalent cases by SDI Category completed")