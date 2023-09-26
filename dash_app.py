# dash_app.py
import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
import psycopg2
def retrieve_data_and_generate_plot():
    conn = psycopg2.connect(database="postgres", user="postgres", password="postgres", host="db", port="5432")
    statement = "SELECT country, AVG(points) AS avg_points, AVG(price) AS avg_price FROM Wines GROUP BY country"
    df_variety_analysis = pd.read_sql_query(statement, con=conn)
    conn.close()

    px.defaults.template = "plotly_white"  # Set the plotly template to white background
    px.defaults.color_continuous_scale = px.colors.sequential.Viridis

    # Variety Analysis Plot
    fig_variety = px.bar(df_variety_analysis, x="country", y="avg_points", color="avg_price",
                         title="Country Analysis: Average Points and Prices",
                         labels={"avg_points": "Average Points", "avg_price": "Average Price"},
                         color_continuous_scale=px.colors.sequential.Viridis)

    return fig_variety

def create_dashboard_layout():
    app = dash.Dash(__name__)

    app.layout = html.Div([
        html.H1('Wine Analysis'),
        dcc.Graph(id='wine-plot'),
        dcc.Interval(
            id='interval-component',
            interval=360,  # Refresh interval in milliseconds (1 hour in this case)
            n_intervals=0
        )
    ])

    @app.callback(
        dash.dependencies.Output('wine-plot', 'figure'),
        [dash.dependencies.Input('interval-component', 'n_intervals')]
    )
    def update_plot(n):
        fig_variety = retrieve_data_and_generate_plot()
        return fig_variety

    app.run_server(debug=False, host='0.0.0.0', port=8050)

