import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from database.riego_repository import get_db_path, load_data, obtener_factor_recomendacion_semanal_hanegada, obtener_riegos_mes_recomendados
from utils import first_day_of_week

def obtener_valores_riego(fecha=None,inicial=None, todos=False):
    """
    Obtiene los valores de riego de la base de datos para la semana actual.
    Si 'inicial' se indica, filtra por ese usuario.
    Si 'todos' es True, devuelve todos los registros.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # Calcular inicio y fin de la semana actual
    inicio_semana = first_day_of_week(fecha)
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

def obtener_recomendacion_semanal(counters, riego_semanal):
    # Load recommendations and data
    recomendacion_semanal = obtener_factor_recomendacion_semanal_hanegada() * obtener_riegos_mes_recomendados(first_day_of_week())

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
    df = obtener_valores_riego()
    return obtener_recomendacion_semanal(counters, df)

def obtener_consumo_dia(fecha):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    fecha_str = fecha.strftime('%Y-%m-%d')
    query = "SELECT partida, valor FROM datos_riego WHERE DATE(fecha) = ?"
    result = pd.read_sql_query(query, conn, params=[fecha_str])
    conn.close()
    return result

def obtener_consumo_mes():
    hoy = datetime.now()
    inicio = hoy.replace(day=1)
    return obtener_consumo_periodo(inicio, hoy)

def obtener_consumo_periodo(fecha_inicio, fecha_fin):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    inicio_str = fecha_inicio.strftime('%Y-%m-%d 00:00:00')
    fin_str = fecha_fin.strftime('%Y-%m-%d 23:59:59')
    query = "SELECT SUM(valor), partida FROM datos_riego WHERE fecha BETWEEN ? AND ? GROUP BY partida"
    result = pd.read_sql_query(query, conn, params=[inicio_str, fin_str])
    conn.close()
    return result.iloc[0, 0] or 0

def generar_alertas_desviacion(umbral=20):
    # Implementar lógica de alertas por desviación
    alertas = []
    # ... lógica
    return alertas

if __name__ == "__main__":
    # Obtain the final weekly irrigation data
    riego_semanal = obtener_datos()
