import sqlite3
import pandas as pd
import json
from datetime import datetime, timedelta
from database.riego_repository import get_db_path, load_data
from flask import current_app

def obtener_valores_riego(inicial=None, todos=False):
    """
    Obtiene los valores de riego de la base de datos para la semana actual.
    Si 'inicial' se indica, filtra por ese usuario.
    Si 'todos' es True, devuelve todos los registros.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # Calcular inicio y fin de la semana actual
    hoy = datetime.now()
    inicio_semana = hoy - timedelta(days=hoy.weekday())
    fin_semana = inicio_semana + timedelta(days=6)
    inicio_str = inicio_semana.strftime('%Y-%m-%d 00:00:00')
    fin_str = fin_semana.strftime('%Y-%m-%d 23:59:59')

    query = "SELECT partida, fecha, valor FROM datos_riego"
    params = []

    if not todos:
        query += " WHERE fecha BETWEEN ? AND ?"
        params.extend([inicio_str, fin_str])

    if inicial:
        # Si ya hay un WHERE, añadimos AND
        if not todos:
            query += " AND partida IN (SELECT partida FROM counters WHERE inicial=?)"
        else:
            query += " WHERE partida IN (SELECT partida FROM counters WHERE inicial=?)"
        params.append(inicial)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def leer_recomendacion_semanal(app=None):
    """
    Lee el valor de 'recomendacion_semanal' de un archivo JSON.
    Si se pasa una app Flask, usa su logger.
    """
    archivo_config = "config.json"
    try:
        with open(archivo_config, 'r', encoding='utf-8') as archivo:
            config = json.load(archivo)
            return config.get("recomendacion_semanal", None)
    except FileNotFoundError:
        msg = f"El archivo {archivo_config} no se encontró."
        if app:
            app.logger.error(msg)
    except json.JSONDecodeError:
        msg = f"El archivo {archivo_config} no es un JSON válido."
        if app:
            app.logger.error(msg)
    return 0

def obtener_recomendacion_semanal(counters, riego_semanal):
    # Load recommendations and data
    recomendacion_semanal = leer_recomendacion_semanal(app=current_app)

    # Calculate weekly irrigation total
    riego_semanal['Riego Semanal'] = riego_semanal.sum(axis=1)

    # Initialize recommendation column
    riego_semanal['Recomendacion Semanal'] = 0.0

    # Vectorized assignment for 'Recomendacion Semanal'
    hanegadas = counters.set_index('nombre_completo')['hanegadas']

    for parcela in riego_semanal.index:
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
