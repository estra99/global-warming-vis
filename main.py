from dash import dcc
from dash import html
from dash import dash
from dash.dependencies import Input, Output
from data_arrange import arrange_data_gases_temp, arrange_data_pob_gases, arrange_data_temp_precip
import plotly.express as px
import pandas as pd

# Data Stage (load the clean data from the Excel files)
# Vis 1
df_pob_co2, df_pob_ghg = arrange_data_pob_gases()
# Vis 2
df_temp_change_precip = arrange_data_temp_precip()
# Vis 3
df_temp_co2, df_temp_ghg = arrange_data_gases_temp()

# Visualizations Stage
# Visualization #1
emissions = {
    'CO2': px.scatter(
        df_pob_co2, x='Total CO2 emissions', y='Annual CO2 emissions (per capita)', animation_frame='Year',
        animation_group='Entity', size='Total population estimates, 1970-2100 (IIASA (2015))',
        color='Total CO2 emissions',
        hover_name='Entity', log_x=True, size_max=80, color_continuous_scale='Jet',
        range_x=[100000, 15000000000], range_y=[-20, 80]),

    'GHG': px.scatter(
        df_pob_ghg, x='Total GHG emissions excluding LUCF (CAIT)', y='Annual GHG emissions (per capita)',
        animation_frame='Year',
        animation_group='Entity', size='Total population estimates, 1970-2100 (IIASA (2015))',
        color='Total GHG emissions excluding LUCF (CAIT)',
        hover_name='Entity', log_x=True, size_max=80, color_continuous_scale='Jet',
        range_x=[500000, 15000000000], range_y=[-20, 80]),
}

# Visualization #2
years_precip_temp = df_temp_change_precip['Year'].unique()

# App
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('El inicio del fin: Cambiemos nuestro destino.'),
    html.H4(children='''El cambio climático amenaza nuestra existencia y toda la vida del planeta Tierra, 
    a continuación le presentamos una serie de visualizaciones para que se informe y tome acciones para eliminarlo, 
    ¡debemos actuar YA! '''),
    html.Br(),
    html.H3('1. Vínculo entre la población y los gases de efecto invernadero'),
    html.P("Seleccione un tipo de emisión:"),
    dcc.RadioItems(
        id='selection_emission',
        options=[{'label': x, 'value': x} for x in emissions],
        value='CO2'
    ),
    dcc.Graph(id="vis1"),
    html.Br(),
    html.H3('2. Relación entre las temperaturas y los cambios de precipitaciones'),
    html.P("Seleccione un año: "),
    dcc.Dropdown(id="selection_year_temp_precip",
                 options=[
                     {'label': i, 'value': i} for i in years_precip_temp
                 ],
                 multi=False,
                 value=1957,
                 style={'width': "40%"}
                 ),
    html.Div(id='avg_temp_change', children=[]),
    dcc.Graph(id="vis2"),
    html.Br(),
    html.H3('3. Gases de efecto invernadero y su efecto en la temperatura global'),
    dcc.Dropdown(id="gas_emision",
                 options=[
                     {"label": "Emisiones de CO2", "value": "CO2"},
                     {"label": "Emisiones de GHG", "value": "GHG"}],
                 multi=False,
                 value="CO2",
                 style={'width': "40%"}),
    dcc.Graph(id='vis3'),
    dcc.Slider(
        id='year_slider_gases_temp',
        min=1970,
        max=2015,
        value=2000,
        step=5,
        tooltip={"placement": "bottom", "always_visible": True}
    )
])


@app.callback(
    Output("vis1", "figure"),
    [Input("selection_emission", "value")])
def display_animated_graph(s):
    return emissions[s]


@app.callback(
    [Output("vis2", "figure"),
     Output("avg_temp_change", "children")],
    Input("selection_year_temp_precip", "value"))
def display_precip_temp(year_temp_precip):
    df_filter_by_year = df_temp_change_precip[df_temp_change_precip['Year'] == year_temp_precip]
    avg_temp_change_year = df_filter_by_year['Avg Year Temp Change'].unique()[0]
    container_temp_change_year = "Promedio de cambio en temperatura global: {}".format(avg_temp_change_year)

    map_precip_temp = px.choropleth(df_filter_by_year, locations='Code', color='Average monthly precipitation',
                                    hover_name='Entity', color_continuous_scale=px.colors.sequential.Plasma)

    return map_precip_temp, container_temp_change_year


@app.callback(
    Output("vis3", "figure"),
    [Input("gas_emision", "value"),
     Input("year_slider_gases_temp", "value")])
def display_gases_temp(gas_type_emision, year_max):
    if gas_type_emision == 'CO2':
        min_year = df_temp_co2['Year'].min()
        if year_max <= min_year:
            year_max = min_year + 5
        mask = (df_temp_co2['Year'] > min_year) & (df_temp_co2['Year'] <= year_max)
        df_filtered = df_temp_co2.loc[mask]
        fig = px.line(df_filtered, x='Year', y='Avg Year Temp Change', title='Cambio de temperatura del planetea en '
                                                                             'el tiempo en relación a emisiones CO2',
                      text='Total Tons CO2 per Year')
        return fig
    elif gas_type_emision == 'GHG':
        min_year = df_temp_ghg['Year'].min()
        if year_max <= min_year:
            year_max = min_year + 5
        mask = (df_temp_ghg['Year'] > min_year) & (df_temp_ghg['Year'] <= year_max)
        df_filtered = df_temp_ghg.loc[mask]
        fig = px.line(df_filtered, x='Year', y='Avg Year Temp Change', title='Cambio de temperatura del planetea en '
                                                                             'el tiempo en relación a emisiones de GHG',
                      text='Total Tons GHG per Year')
        return fig


app.run_server(debug=True)
