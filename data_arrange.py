import pandas as pd
# from functools import reduce (used in case of merging multiple files)


# Vis 2
def arrange_data_temp_precip():
    # Open the Excel files
    df_temp_change = pd.read_excel('Datos/1_climate-change.xlsx')
    df_precip = pd.read_excel('Datos/2_average-monthly-precipitation.xlsx')

    # Group the dates by year and calculate the mean of temperature anomaly
    prom_cambio_temp_mundial = df_temp_change.groupby(df_temp_change['Day'].dt.year)['temperature_anomaly'].agg(
        ['mean']).reset_index()

    # Rename cols Day to Year (because it just keeps year), and agg mean to 'Avg Year Temp Change'
    prom_cambio_temp_mundial.rename(columns={'Day': 'Year', 'mean': 'Avg Year Temp Change'}, inplace=True)

    # Inner Join dataframe, get the files merge by corresponding year.
    df_temp_change_precip = pd.merge(df_precip, prom_cambio_temp_mundial, on=['Year'], how='inner')

    # Return Dataframe ready
    return df_temp_change_precip


# Vis 3
def arrange_data_pob_gases():
    # Open the Excel files
    df_pob = pd.read_excel('Datos/5_future-population-projections-by-country.xlsx')
    df_gases_co2 = pd.read_excel('Datos/3_co-emissions-per-capita.xlsx')
    df_gases_ghg = pd.read_excel('Datos/4_total-ghg-emissions-excluding-lufc.xlsx')

    # Inner Join dataframe, get the files merge by corresponding year (other attributes guarantee just one match).
    df_pob_co2 = pd.merge(df_pob, df_gases_co2, on=['Entity', 'Code', 'Year'], how='inner')

    # Create new col of 'Total CO2 emissions' and calculate it's value.
    df_pob_co2['Total CO2 emissions'] = (
            df_pob_co2['Total population estimates, 1970-2100 (IIASA (2015))'] * df_pob_co2[
        'Annual CO2 emissions (per capita)'])

    # Inner Join dataframe, get the files merge by corresponding year.
    df_pob_ghg = pd.merge(df_pob, df_gases_ghg, on=['Entity', 'Code', 'Year'], how='inner')
    # Create new col of 'Annual GHG emission per capita' and calcute it's value.
    df_pob_ghg['Annual GHG emissions (per capita)'] = (
            df_pob_ghg['Total GHG emissions excluding LUCF (CAIT)'] / df_pob_ghg[
        'Total population estimates, 1970-2100 (IIASA (2015))'])

    # Return both Dataframes (CO2 and GHG) ready
    return df_pob_co2, df_pob_ghg


# Vis 1
def arrange_data_gases_temp():
    # Open the Excel files
    df_temp_change = pd.read_excel('Datos/1_climate-change.xlsx')

    # Get gases dataframes ready
    df_co2, df_ghg = arrange_data_pob_gases()

    # Group the dates by year and calculate the mean of temperature anomaly
    prom_cambio_temp_mundial = df_temp_change.groupby(df_temp_change['Day'].dt.year)['temperature_anomaly'].agg(
        ['mean']).reset_index()
    # Rename cols Day to Year (because it just keeps year), and agg mean to 'Avg Year Temp Change'
    prom_cambio_temp_mundial.rename(columns={'Day': 'Year', 'mean': 'Avg Year Temp Change'}, inplace=True)

    # Merge multiple data frames, optional (not used because CO2 and GHG don't need to be merged)
    # data_frames = [df_co2, df_ghg]
    # df_merged_temp_gases = reduce(lambda left, right: pd.merge(left, right, on=['Entity', 'Code', 'Year'],
    #                                                           how='inner'), data_frames)

    # Get the total emissions of CO2 worldwide by year
    df_prom_anual_co2 = df_co2.groupby(df_co2['Year'])['Total CO2 emissions'].agg(['sum']).reset_index()
    df_prom_anual_co2.rename(columns={'sum': 'Total Tons CO2 per Year'}, inplace=True)

    # Get the total emissions of GHG worldwide by year
    df_prom_anual_ghg = df_ghg.groupby(df_ghg['Year'])['Total GHG emissions excluding LUCF (CAIT)'].agg(
        ['sum']).reset_index()
    df_prom_anual_ghg.rename(columns={'sum': 'Total Tons GHG per Year'}, inplace=True)

    # Merge the temp changes with gases emissions yearly
    df_merged_temp_co2 = pd.merge(df_prom_anual_co2, prom_cambio_temp_mundial, on=['Year'], how='inner')
    df_merged_temp_ghg = pd.merge(df_prom_anual_ghg, prom_cambio_temp_mundial, on=['Year'], how='inner')

    return df_merged_temp_co2, df_merged_temp_ghg
