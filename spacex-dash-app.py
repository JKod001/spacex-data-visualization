#  Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout (IMPORTANT: one single html.Div wrapping everything)
app.layout = html.Div([
    html.H1(
        "SpaceX Launch Records Dashboard",
        style={"textAlign": "center", "color": "#503D36", "font-size": 40}
    ),

    # TASK 1: Launch Site Dropdown
    dcc.Dropdown(
        id="site-dropdown",
        options=[{"label": "All Sites", "value": "ALL"}] + [
            {"label": site, "value": site}
            for site in sorted(spacex_df["Launch Site"].unique())
        ],
        value="ALL",
        placeholder="Select a Launch Site here",
        searchable=True
    ),

    html.Br(),

    # TASK 2: Pie Chart (Success Counts)
    html.Div(dcc.Graph(id="success-pie-chart")),

    html.Br(),

    # TASK 3: Payload Range Slider
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id="payload-slider",
        min=0,
        max=10000,
        step=1000,
        marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
        value=[min_payload, max_payload]
    ),

    html.Br(),

    # TASK 4: Scatter Plot (Payload vs Class)
    html.Div(dcc.Graph(id="success-payload-scatter-chart")),
])

# TASK 2 CALLBACK: Update pie chart based on selected site
@app.callback(
    Output(component_id="success-pie-chart", component_property="figure"),
    Input(component_id="site-dropdown", component_property="value")
)
def update_pie_chart(selected_site):
    if selected_site == "ALL":
        # Total successful launches by site
        success_by_site = (
            spacex_df.groupby("Launch Site")["class"]
            .sum()
            .reset_index()
            .rename(columns={"class": "Successes"})
        )

        fig = px.pie(
            success_by_site,
            values="Successes",
            names="Launch Site",
            title="Total Success Launches By Site"
        )
        return fig
    else:
        # Success vs Failure for selected site
        site_df = spacex_df[spacex_df["Launch Site"] == selected_site]
        outcome_counts = site_df["class"].value_counts().reset_index()
        outcome_counts.columns = ["class", "count"]
        outcome_counts["Outcome"] = outcome_counts["class"].map({1: "Success", 0: "Failure"})

        fig = px.pie(
            outcome_counts,
            values="count",
            names="Outcome",
            title=f"Total Success Launches for site {selected_site}"
        )
        return fig

# TASK 4 CALLBACK: Update scatter chart based on selected site and payload range
@app.callback(
    Output(component_id="success-payload-scatter-chart", component_property="figure"),
    [
        Input(component_id="site-dropdown", component_property="value"),
        Input(component_id="payload-slider", component_property="value")
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range

    # Filter by payload range first
    df_filtered = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low) &
        (spacex_df["Payload Mass (kg)"] <= high)
    ]

    if selected_site == "ALL":
        fig = px.scatter(
            df_filtered,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title="Correlation between Payload and Success for all Sites"
        )
        return fig
    else:
        df_site = df_filtered[df_filtered["Launch Site"] == selected_site]
        fig = px.scatter(
            df_site,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            title=f"Correlation between Payload and Success for site {selected_site}"
        )
        return fig

# Run the app
if __name__ == "__main__":
    # Newer Dash uses app.run() (not run_server)
    app.run(host="0.0.0.0", port=8050, debug=False)
