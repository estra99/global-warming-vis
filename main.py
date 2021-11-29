from dash import dcc
from dash import html
from dash import dash
from dash.dependencies import Input, Output
from data_arrange import arrange_data_gases_temp, arrange_data_pob_gases, arrange_data_temp_precip
import plotly.express as px
import pandas as pd

# Data Stage (load the clean data from the Excel files)
# Vis 1
df_temp_co2, df_temp_ghg = arrange_data_gases_temp()

# Vis 2
df_temp_change_precip = arrange_data_temp_precip()

# Vis 3
df_pob_co2, df_pob_ghg = arrange_data_pob_gases()


# Visualizations Stage

animations = {
    'Scatter': px.scatter(
        df, x="gdpPercap", y="lifeExp", animation_frame="year",
        animation_group="country", size="pop", color="continent",
        hover_name="country", log_x=True, size_max=55,
        range_x=[100, 100000], range_y=[25, 90]),
    'Bar': px.bar(
        df, x="continent", y="pop", color="continent",
        animation_frame="year", animation_group="country",
        range_y=[0, 4000000000]),
}

app = dash.Dash(__name__)

app.layout = html.Div([
    html.P("Select an animation:"),
    dcc.RadioItems(
        id='selection',
        options=[{'label': x, 'value': x} for x in animations],
        value='Scatter'
    ),
    dcc.Graph(id="graph"),
])


@app.callback(
    Output("graph", "figure"),
    [Input("selection", "value")])
def display_animated_graph(s):
    return animations[s]


app.run_server(debug=True)
