import sqlite3
import os
import pandas as pd

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'riego.db')

def load_data():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)

    # Load data into DataFrames
    counters = pd.read_sql_query("SELECT * FROM counters", conn)
    users = pd.read_sql_query("SELECT * FROM users", conn)

    conn.close()
    return counters, users

def obtener_inicial(usuario):
    # Conectar a la base de datos SQLite
    conn = sqlite3.connect(get_db_path())  # Reemplaza con el nombre de tu base de datos
    cursor = conn.cursor()

    # Consultar la inicial del usuario
    cursor.execute('''
        SELECT inicial FROM users WHERE user = ?
    ''', (usuario,))

    # Obtener el resultado
    resultado = cursor.fetchone()
    conn.close()

    # Si se encuentra el usuario, devolver la inicial
    if resultado:
        return resultado[0]
    else:
        return None  # Usuario no encontrado
