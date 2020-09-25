from functools import reduce

import pandas as pd
import datetime


# Funcion para saber si la fecha actual esta es una semana concreta
def check_if_current_week(date):
    start_week = datetime.date.today() - datetime.timedelta(datetime.date.today().weekday())
    end_week = start_week + datetime.timedelta(7)
    return (date >= start_week) and (date < end_week)


def obtener_valores_riego():
    # leer parcelas
    parcelas = pd.read_csv("contadores.tsv", sep="\t", header=None, names=['user', 'partida', 'contador', 'hanegadas'])
    datos_parcelas = pd.read_csv("datos_parcelas.tsv", delimiter="\t")

    lista_parcelas = parcelas['partida'].tolist()

    # obtener los litros de todas las parcelas en una lista de dataframes
    litros_totales = []
    for parcela in lista_parcelas:
        nombrecsv = "{}.csv".format(parcela)
        litros = pd.read_csv(nombrecsv)
        litros = litros.drop(['L. inicial', 'L. final'], axis=1)

        litros['Total'] = litros['Total'].apply(lambda x: x.split(' ')[0])
        litros['Total'] = pd.to_numeric(litros['Total'], errors='coerce').fillna(0)
        litros['Fin'] = pd.to_datetime(litros.Fin).dt.date
        litros['Inicio'] = pd.to_datetime(litros.Fin).dt.date
        litros['Semana'] = litros['Inicio'].apply(check_if_current_week)
        nombre_parcela = datos_parcelas[datos_parcelas['filename'].str.contains(nombrecsv.split('.')[0])]

        litros = litros.assign(NombreParcela=nombre_parcela.iloc[0, 1])
        litros_filtrados = litros.loc[litros.Semana]
        litros_totales.append(litros_filtrados[['Fin', 'Total', 'NombreParcela']])

    # juntar todos los dataframes en uno
    riego_semanal = reduce(lambda df1, df2: pd.merge(df1, df2, on='Fin'), litros_totales).T

    riego_semanal.columns = riego_semanal.loc['Fin']
    riego_semanal.drop(['Fin'], inplace=True)
    riego_semanal.reset_index(inplace=True)

    riego_semanal['Nombre Parcela'] = None

    for i, row in riego_semanal.iterrows():
        if i % 2 == 0:
            riego_semanal['Nombre Parcela'][i] = riego_semanal.iloc[i + 1, 1]

    riego_semanal = riego_semanal.iloc[::2]
    riego_semanal_columnas = [col for col in riego_semanal.columns if
                              type(col) == datetime.date or col == 'Nombre Parcela']
    riego_semanal_columnas = riego_semanal_columnas[-1:] + riego_semanal_columnas[:-1]
    riego_semanal = riego_semanal[riego_semanal_columnas]

    for i, n in enumerate(riego_semanal_columnas):
        if type(n) == datetime.date:
            riego_semanal_columnas[i] = n.strftime('%d/%b')

    riego_semanal.columns = riego_semanal_columnas

    return riego_semanal


def obtener_recomendacion_semanal(riego_semanal):
    recomendacion_semanal = 8

    parcelas = pd.read_csv("contadores.tsv", sep="\t", header=None, names=['user', 'partida', 'contador', 'hanegadas'])
    datos_parcelas = pd.read_csv("datos_parcelas.tsv", delimiter="\t")
    join_datos = parcelas.merge(datos_parcelas, left_on='partida', right_on='filename')
    riego_semanal['Recomendacion Semanal'] = 0.0
    riego_semanal['Riego Semanal'] = riego_semanal.iloc[:, 1:5].sum(axis=1)

    riego_semanal.reset_index(inplace=True)

    for i, row in riego_semanal.iterrows():
        hanegadas = join_datos.loc[join_datos['Nombre Completo'] == riego_semanal['Nombre Parcela'][i]]['hanegadas'][i]
        riego_semanal.at[i, 'Recomendacion Semanal'] = hanegadas * recomendacion_semanal

    riego_semanal['Restante Semanal'] = riego_semanal['Riego Semanal'] - riego_semanal['Recomendacion Semanal']

    return riego_semanal.iloc[:, 1:]


def obtener_datos():
    df = obtener_valores_riego()
    return obtener_recomendacion_semanal(df)
