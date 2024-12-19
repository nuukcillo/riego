import pandas as pd
import os
from database.riego_repository import load_data
from utils import is_current_week, leer_recomendacion_semanal


def obtener_valores_riego(counters):
    # Load data from database 
    # Obtain the list of unique parcels
    lista_parcelas = counters['partida'].tolist()

    # List to hold DataFrames for merging later
    litros_totales = []

    # Process each parcel
    for parcela in lista_parcelas:
        csv_file = os.path.join('csv_files', f"{parcela}.csv")
        
        # Skip if file doesn't exist
        if not os.path.exists(csv_file):
            continue
        
        # Load CSV data
        litros = pd.read_csv(csv_file)

        # Drop unnecessary columns and clean up data
        litros = litros.drop(['L. inicial', 'L. final'], axis=1)
        litros['Total'] = pd.to_numeric(litros['Total'].str.split(' ').str[0], errors='coerce').fillna(0)
        litros['Fin'] = pd.to_datetime(litros['Fin'], format='%b %d %Y %I:%M%p').dt.date
        litros['Inicio'] = pd.to_datetime(litros['Inicio'], format='%b %d %Y %I:%M%p').dt.date

        # Filter by current week
        litros['Semana'] = litros['Inicio'].apply(is_current_week)
        
        # Add parcel name to the dataframe
        nombre_parcela = counters.loc[counters['partida'] == parcela, 'nombre_completo']
        if not nombre_parcela.empty:
            litros['NombreParcela'] = nombre_parcela.iloc[0]

        # Filter the data by current week and add it to the list
        litros_filtrados = litros[litros['Semana']]
        litros_totales.append(litros_filtrados[['Fin', 'Total', 'NombreParcela']])

    # If there is no data to process, return an empty DataFrame
    if not litros_totales:
        return pd.DataFrame()

    # Merge all data frames into one
    riego_semanal = pd.concat(litros_totales, axis=0, ignore_index=True)

    # Pivot the table to make 'Fin' as columns
    riego_semanal = riego_semanal.pivot_table(index='NombreParcela', columns='Fin', values='Total', aggfunc='sum')
    
    # Format the columns to be in the desired date format
    #riego_semanal.columns = riego_semanal.columns.strftime('%d/%b')
    return riego_semanal

def obtener_recomendacion_semanal(counters, riego_semanal):
    # Load recommendations and data
    recomendacion_semanal = leer_recomendacion_semanal()

    # Calculate weekly irrigation total
    riego_semanal['Riego Semanal'] = riego_semanal.sum(axis=1)

    # Initialize recommendation column
    riego_semanal['Recomendacion Semanal'] = 0.0

    # Vectorized assignment for 'Recomendacion Semanal'
    valid_parcelas = riego_semanal.index
    hanegadas = counters.set_index('nombre_completo')['hanegadas']

    for parcela in valid_parcelas:
        if parcela in hanegadas.index:
            riego_semanal.at[parcela, 'Recomendacion Semanal'] = hanegadas.loc[parcela] * recomendacion_semanal

    # Calculate the remaining weekly irrigation
    riego_semanal['Restante Semanal'] = riego_semanal['Recomendacion Semanal'] - riego_semanal['Riego Semanal']

    return riego_semanal

def obtener_datos():
    counters, _ = load_data()
    df = obtener_valores_riego(counters)
    return obtener_recomendacion_semanal(counters, df)

if __name__ == "__main__":
    # Obtain the final weekly irrigation data
    riego_semanal = obtener_datos()
    print(riego_semanal)
