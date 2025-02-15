import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

from scraper_exploration import (
    load_data,
    get_global_values,
    clean_numeric_column,
    generate_treemap
)
from scraper_facts import fetch_asthma_data
from data_exploration import (
    load_data as load_asthma_data,
    explore_risk_factors,
    create_allergen_exposure_figure
)

# === STYLES GLOBAUX ===
global_style = {
    "maxWidth": "1200px",
    "margin": "auto",
    "padding": "20px"
}

card_style = {
    "padding": "30px",
    "borderRadius": "15px",
    "textAlign": "center",
    "boxShadow": "0px 4px 6px rgba(0, 0, 0, 0.1)"
}

graph_style = {
    "height": "500px"
}

# === APP INITIALIZATION ===
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# === DATA LOADING AND PREPARATION ===
asthma_facts = fetch_asthma_data()

# 1) GBD Data (Global Burden of Disease)
df = load_data("table_1_asthma_final_two_columns.csv")
df["Number of deaths (thousands)"] = clean_numeric_column(df["Number of deaths (thousands)"])
df["Number of prevalent cases (thousands)"] = clean_numeric_column(df["Number of prevalent cases (thousands)"])
asthma_summary = get_global_values(df)
df_sdi = df[df["SDI Category"].str.lower() != "global"].reset_index(drop=True)

# 2) Kaggle Data (individual patients)
df_asthma = load_asthma_data()

if df_asthma is None:
    raise ValueError("Failed to load df_asthma. Check your CSV path in data_exploration.py.")

# Create risk factor and exposure figures
fig_smoking, fig_pollution, fig_family = explore_risk_factors(df_asthma)
fig_allergen = create_allergen_exposure_figure(df_asthma)

# Map ethnicity labels for other potential graphs
ethnicity_labels = {0: "Caucasian", 1: "African American", 2: "Asian", 3: "Other"}
df_asthma["ETHNICITY"] = df_asthma["ETHNICITY"].map(ethnicity_labels)

# === ICONS ===
section_icons = {
    "Overview":  "https://img.icons8.com/?size=100&id=7964&format=png&color=000000",
    "Impact":    "https://img.icons8.com/?size=100&id=y970hF5zMqWz&format=png&color=000000",
    "Symptoms":  "https://img.icons8.com/?size=100&id=JsyadX1iwJK3&format=png&color=000000",
    "Causes":    "https://img.icons8.com/?size=100&id=48359&format=png&color=000000",
    "Treatment": "https://img.icons8.com/?size=100&id=66515&format=png&color=000000",
}

# === FACTS ACCORDION ===
accordion_items = []
for title in ["Overview", "Impact", "Symptoms", "Causes", "Treatment"]:
    accordion_items.append(
        dbc.AccordionItem(
            asthma_facts.get(title, "Data not available."),
            title=html.Div([
                html.Img(src=section_icons[title], height="30px", style={"marginRight": "10px"}),
                html.Span(title)
            ], style={"display": "flex", "alignItems": "center"})
        )
    )
accordion = dbc.Accordion(
    accordion_items,
    start_collapsed=True,
    style={"fontSize": "18px", "padding": "15px"}
)

# === "ABOUT THE DATASET" MODAL ===
modal = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("About the Dataset"), close_button=True),
        dbc.ModalBody(
            html.Div([
                html.P("This dashboard provides insights into asthma, analyzing its causes and symptoms."),
                html.H5("📊 Source Information", className="fw-bold"),
                html.P("1. "),
                html.Ul([
                    html.Li("Title: Asthma - Fact Sheets, WHO (World Health Organization)"),
                    html.Li("Published Online: who.int"),
                    html.Li("Retrieved From: https://www.who.int/news-room/fact-sheets/detail/asthma"),
                    html.Li("Geospatial Coverage: Worldwide"),
                    html.Li("License: Attribution 4.0 International (CC BY 4.0)"),
                ]),
                html.P("2. "),
                html.Ul([
                    html.Li("Authors: Rabie El Kharoua"),
                    html.Li("Title: Asthma Disease Dataset"),
                    html.Li("Published From: kaggle.com"),
                    html.Li("Retrieved From: https://www.kaggle.com/dsv/8669080"),
                    html.Li("License: Attribution 4.0 International (CC BY 4.0)"),
                ]),
                html.P("3. "),
                html.Ul([
                    html.Li("Authors: Soriano, Joan B et al."),
                    html.Li("Title: Global, regional, and national deaths, prevalence, disability-adjusted life years, and years lived with disability for chronic obstructive pulmonary disease and asthma, 1990–2015: a systematic analysis for the Global Burden of Disease Study 2015"),
                    html.Li("Published From: thelancet.com"),
                    html.Li("Retrieved From / DOI: https://doi.org/10.1016/S2213-2600(17)30293-X"),
                    html.Li("License: Attribution 4.0 International (CC BY 4.0)"),
                ]),
                html.H5("📖 Reference", className="fw-bold"),
                html.P(
                    "GBD 2015 Chronic Respiratory Disease Collaborators. Global, regional, and national deaths, "
                    "prevalence, disability-adjusted life years, and years lived with disability for chronic "
                    "obstructive pulmonary disease and asthma, 1990-2015: a systematic analysis for the Global "
                    "Burden of Disease Study 2015. Lancet Respir Med. 2017 Sep;5(9):691-706. "
                    "doi: 10.1016/S2213-2600(17)30293-X."
                ),
            ])
        ),
        dbc.ModalFooter(
            dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
        ),
    ],
    id="modal",
    is_open=False,
)


# === CALLBACK: OPEN/CLOSE THE MODAL ===
@app.callback(
    Output("modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    prevent_initial_call=True
)
def toggle_modal(n_open, n_close):
    ctx = dash.callback_context
    if not ctx.triggered:
        return False
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    return button_id == "open-modal"


# =============================================================================
#                                  LAYOUTS
# =============================================================================

# === HOME LAYOUT ===
home_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Exploring the Impact of Asthma on Health",
                    className="text-primary fw-bold",
                    style={"fontSize": "45px", "textAlign": "left"})
        ),
        dbc.Col(
            dbc.Button("About Dataset", id="open-modal", color="info", className="mt-3"),
            style={"textAlign": "right"}
        ),
    ], className="mt-4 mb-3"),

    modal,  # The modal component

    dbc.Row([
        dbc.Col(html.P(
            "This application provides insights into asthma, analyzing its causes, symptoms, "
            "and treatments across different populations. Using data from reputable sources, "
            "we aim to uncover trends and disparities in asthma management.",
            style={"fontSize": "18px", "maxWidth": "100%"}
        ))
    ]),
    dbc.Row([
        dbc.Col([
            html.H3("Asthma Insights", className="text-dark fw-bold", style={"marginBottom": "15px"}),
            accordion
        ]),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H5("Global Asthma Cases (2015)", className="card-title text-primary"),
                    html.H2(f"{asthma_summary['cases']:,}K", className="display-3 text-primary fw-bold"),
                    html.P("Total number of asthma cases worldwide", className="card-text"),
                ]),
                className="mb-4 shadow-sm",
                style=card_style
            ),
            dbc.Card(
                dbc.CardBody([
                    html.H5("Global Asthma Deaths (2015)", className="card-title text-danger"),
                    html.H2(f"{asthma_summary['deaths']:,}K", className="display-3 text-danger fw-bold"),
                    html.P("Total number of deaths caused by asthma", className="card-text"),
                ]),
                className="shadow-sm",
                style=card_style
            ),
        ]),
    ], className="mt-4"),
], fluid=True)

# === TREEMAP LAYOUT ===
treemap_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Asthma Cases and Deaths by SDI Category (2015)",
                    className="text-primary fw-bold",
                    style={"marginBottom": "5px"}),

        )
    ], className="mt-2 mb-2"),

    dbc.Row([
        dbc.Col(html.P( "The Socio-Demographic Index (SDI) is a composite measure of a country's development, "
            "combining income per capita, average years of schooling, and total fertility rate. "
            "It categorizes regions into Low, Low-Middle, Middle, High-Middle, and High SDI categories.",
            style={"fontSize": "18px", "maxWidth": "100%"}
        ))
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(
            dcc.Graph(
                figure=generate_treemap(
                    df_sdi,
                    "Number of deaths (thousands)",
                    "Reds",
                    "Asthma-related Deaths by SDI Category (2015)"
                ),
                style={"height": "600px"}
            ),
        ),
        dbc.Col(
            dcc.Graph(
                figure=generate_treemap(
                    df_sdi,
                    "Number of prevalent cases (thousands)",
                    "Blues",
                    "Asthma Prevalent Cases by SDI Category (2015)"
                ),
                style={"height": "600px"}
            ),
        ),
    ], className="mt-4"),
], fluid=True)

# === DEMOGRAPHICS LAYOUT ===
demographics_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Asthma Demographics Analysis", className="text-primary fw-bold"),
        )
    ], className="mt-4 mb-3"),

    dbc.Row([
        dbc.Col(html.P(
            "This dataset includes both asthmatic and non-asthmatic patients. "
            "Here, we focus solely on those with asthma to analyze demographic distributions "
            "and identify possible patterns and risk factors.",
            style={"fontSize": "18px", "maxWidth": "100%"}
        )),
    ], className="mb-4"),

    # Dropdown for demographic grouping
    dbc.Row([
        dbc.Col(html.Label("Grouped by:", className="fw-bold")),
        dbc.Col(dcc.Dropdown(
            id="demographic-choice",
            options=[
                {"label": "AGE", "value": "AGE"},
                {"label": "GENDER", "value": "GENDER"},
                {"label": "ETHNICITY", "value": "ETHNICITY"}
            ],
            value="AGE",
            clearable=False,
            style={"width": "60%"}
        ), width=9),
    ], className="mb-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(id="demographic-graph"))
    ], className="mt-4"),

    # Internal navigation buttons (optional)
    dbc.Row([
        dbc.Col(
            dbc.Button("⏪ Previous", id="prev-page", color="secondary", outline=True, size="lg"),

        ),
        dbc.Col(
            dbc.Button("🏠 Home", id="home-page", color="primary", size="lg"),

        ),
    ], className="mt-4"),
], fluid=True)

# === FACTORS LAYOUT (PAGE 4) ===
factors_layout = dbc.Container([
    dbc.Row([
        dbc.Col(
            html.H1("Factors Analysis", className="text-primary fw-bold"),

        )
    ], className="mt-4 mb-3"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_smoking)),
        dbc.Col(dcc.Graph(figure=fig_pollution)),
    ], className="mb-5"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_family)),
        dbc.Col(dcc.Graph(figure=fig_allergen)),
    ], className="mb-5"),

    dbc.Row([
        dbc.Col(html.P(
            "Here, we provide a closer look at specific risk factors related to asthma, "
            "such as smoking habits, pollution exposure, family history, and allergen exposure.",
            style={"fontSize": "18px", "maxWidth": "100%"}
        )),
    ], className="mb-4"),
], fluid=True)


# =============================================================================
#                         APP LAYOUT & NAVIGATION
# =============================================================================
app.layout = dbc.Container(
    [
        dcc.Location(id="url", refresh=False),
        dbc.Tabs(
            [
                dbc.Tab(label="🏠 Home", tab_id="home"),
                dbc.Tab(label="🌍 Treemap", tab_id="treemap"),
                dbc.Tab(label="📊 Demographics", tab_id="demographics"),
                dbc.Tab(label="🔎 Factors", tab_id="factors"),
            ],
            id="tabs",
            active_tab="home"
        ),
        html.Div(id="page-content", children=home_layout, style=global_style),
html.A(
    html.Img(
        src="https://cdn-icons-png.flaticon.com/512/25/25231.png",
        style={"width": "40px", "height": "40px"}
    ),
    href="https://github.com/",
    target="_blank"
)
    ],
    fluid=True

)

# =============================================================================
#                                CALLBACKS
# =============================================================================

# --- Callback: Update demographic graph based on dropdown selection ---
@app.callback(
    Output("demographic-graph", "figure"),
    Input("demographic-choice", "value")
)
def update_demographic_graph(choice):
    """
    Updates the demographic graph based on the selected variable (AGE, GENDER, ETHNICITY).
    """
    dff = df_asthma[df_asthma["DIAGNOSIS"] == 1]

    if choice == "AGE":
        return px.histogram(
            dff,
            x="AGE",
            nbins=20,
            title="Age Distribution Among Asthma Patients",
            color_discrete_sequence=["blue"]
        )
    elif choice == "GENDER":
        return px.box(
            dff,
            x="GENDER",
            y="AGE",
            title="Age Distribution by Gender (Asthma Patients)",
            labels={"GENDER": "Gender (0=Male, 1=Female)", "AGE": "Age"},
            color="GENDER"
        )
    elif choice == "ETHNICITY":
        count_df = dff["ETHNICITY"].value_counts().reset_index()
        count_df.columns = ["Ethnicity", "Count"]

        fig = px.bar(
            count_df,
            x="Ethnicity",
            y="Count",
            text="Count",
            title="Ethnicity Distribution Among Asthma Patients",
            labels={"Ethnicity": "Ethnicity", "Count": "Number of Patients"},
            color="Ethnicity",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            coloraxis_showscale=False,
            xaxis=dict(title=""),
            yaxis=dict(title="Number of Asthma Patients"),
            showlegend=False
        )
        return fig

    # Fallback in case of unexpected value
    return px.histogram(dff, x="AGE")


# --- Callback: Navigation using internal buttons (optional) ---
@app.callback(
    Output("tabs", "active_tab"),
    [Input("prev-page", "n_clicks"), Input("home-page", "n_clicks")],
    prevent_initial_call=True
)
def navigate_buttons(prev_click, home_click):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id == "prev-page":
        return "treemap"
    elif button_id == "home-page":
        return "home"
    return dash.no_update

# --- Callback: Switch layout based on selected tab ---
@app.callback(
    Output("page-content", "children"),
    Input("tabs", "active_tab")
)
def switch_tab(active_tab):
    if active_tab == "treemap":
        return treemap_layout
    elif active_tab == "demographics":
        return demographics_layout
    elif active_tab == "factors":
        return factors_layout
    return home_layout


# === RUN THE APP ===
if __name__ == "__main__":
    app.run_server(debug=True)
