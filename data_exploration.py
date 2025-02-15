import pandas as pd
import plotly.express as px

# Constants
DATA_PATH = "cleaned_asthma_data.csv"


def load_data():
    """
    Load the cleaned dataset for exploration.
    Returns:
        pd.DataFrame: Cleaned dataset
    """
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Dataset loaded successfully. Shape: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return None


# ASTHMA OVERVIEW
def plot_diagnosis_distribution(df):
    """
    Visualize the distribution of asthma diagnosis.
    """
    diagnosis_counts = df["DIAGNOSIS"].value_counts().reset_index()
    diagnosis_counts.columns = ["Diagnosis", "Count"]

    fig = px.bar(diagnosis_counts,
                 x="Diagnosis",
                 y="Count",
                 text="Count",
                 title="Asthma Diagnosis Distribution",
                 labels={"Diagnosis": "Diagnosis (0 = No Asthma, 1 = Asthma)", "Count": "Number of Patients"},
                 color="Diagnosis",
                 color_discrete_map={0: "blue", 1: "red"})

    fig.update_layout(coloraxis_showscale=False)

    fig.show()


# DEMOGRAPHICS & ASTHMA
def explore_demographics(df):
    """
    Analyze demographic factors: Age, Gender, Ethnicity.
    """
    asthma_patients = df[df["DIAGNOSIS"] == 1]

    # Age Distribution
    fig = px.histogram(asthma_patients, x="AGE", nbins=20, title="Age Distribution Among Asthma Patients",
                       color_discrete_sequence=["blue"])
    fig.show()

    # Gender Distribution
    fig = px.box(asthma_patients, x="GENDER", y="AGE", title="Age Distribution by Gender (Asthma Patients)",
                 labels={"GENDER": "Gender (0 = Male, 1 = Female)", "AGE": "Age"},
                 color="GENDER")
    fig.show()

    # Ethnicity Distribution
    # Mapping des valeurs d'ethnicité
    ethnicity_labels = {
        0: "Caucasian",
        1: "African American",
        2: "Asian",
        3: "Other"
    }

    ethnicity_counts = asthma_patients["ETHNICITY"].value_counts().reset_index()
    ethnicity_counts.columns = ["Ethnicity", "Count"]

    ethnicity_counts["Ethnicity"] = ethnicity_counts["Ethnicity"].map(ethnicity_labels)

    fig = px.bar(ethnicity_counts,
                 x="Ethnicity",
                 y="Count",
                 text="Count",
                 title="Ethnicity Distribution Among Asthma Patients",
                 labels={"Ethnicity": "Ethnicity", "Count": "Number of Patients"},
                 color="Ethnicity",
                 color_discrete_sequence=px.colors.qualitative.Set2)

    fig.update_layout(coloraxis_showscale=False)

    fig.show()


#  RISK FACTORS & ASTHMA
def explore_risk_factors(df):
    """
    Investigate risk factors: Smoking, Pollution, Family History.
    Returns:
        tuple: (fig_smoking, fig_pollution, fig_family)
    """
    asthma_patients = df[df["DIAGNOSIS"] == 1]

    # Smoking & Asthma
    smoking_counts = asthma_patients["SMOKING"].value_counts().reset_index()
    smoking_counts.columns = ["Smoking", "Count"]
    fig_smoking = px.bar(
        smoking_counts,
        x="Smoking", y="Count", text="Count",
        title="Smoking Status Among Asthma Patients",
        labels={"Smoking": "Smoking (0=No, 1=Yes)", "Count": "Number of Patients"},
        color="Smoking"
    )
    fig_smoking.update_layout(coloraxis_showscale=False)

    # Pollution & Asthma
    fig_pollution = px.histogram(
        asthma_patients,
        x="POLLUTIONEXPOSURE",
        nbins=30,
        title="Pollution Exposure Among Asthma Patients",
        color_discrete_sequence=["purple"]
    )

    # Family History
    family_history_counts = asthma_patients["FAMILYHISTORYASTHMA"].value_counts().reset_index()
    family_history_counts.columns = ["Family History", "Count"]
    fig_family = px.bar(
        family_history_counts,
        x="Family History", y="Count", text="Count",
        title="Family History of Asthma",
        labels={"Family History": "Family History (0=No, 1=Yes)", "Count": "Number of Patients"},
        color="Family History"
    )
    fig_family.update_layout(coloraxis_showscale=False)

    return fig_smoking, fig_pollution, fig_family

# ALLERGEN EXPOSURE COMPARISON
def create_allergen_exposure_figure(df):
    """

    """
    allergens = ["PETALLERGY", "POLLENEXPOSURE", "DUSTEXPOSURE"]

    asthma_means = df[df["DIAGNOSIS"] == 1][allergens].mean()
    non_asthma_means = df[df["DIAGNOSIS"] == 0][allergens].mean()

    data = []
    for allergen in allergens:
        data.append({"Allergen": allergen, "Mean Exposure": asthma_means[allergen], "Group": "Asthma Patients"})
        data.append({"Allergen": allergen, "Mean Exposure": non_asthma_means[allergen], "Group": "Non-Asthma Patients"})

    df_plot = pd.DataFrame(data)

    fig_allergen = px.bar(df_plot,
                          x="Allergen",
                          y="Mean Exposure",
                          color="Group",
                          text="Mean Exposure",
                          barmode="group",
                          title="Comparison of Allergen Exposure (Asthma vs. Non-Asthma)",
                          labels={"Mean Exposure": "Mean Exposure Level", "Allergen": "Allergen Type"})
    return fig_allergen

# EXECUTION
if __name__ == "__main__":
    df = load_data()

    if df is not None:
        print("\n Running Data Exploration...\n")

       # plot_diagnosis_distribution(df)
       # explore_demographics(df)
       # explore_risk_factors(df)
       # compare_allergen_exposure(df)

        print("\n Data Exploration Completed.")
