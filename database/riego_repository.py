import sqlite3
import os

from models import Counter, User, WebScrapConfig

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'riego.db')

def load_data():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Acceso por nombre de columna
    
    counters_rows = conn.execute("SELECT * FROM counters").fetchall()
    users_rows = conn.execute("SELECT * FROM users").fetchall()
    config_rows = conn.execute("SELECT * FROM config").fetchall()
    
    conn.close()

    counters = [Counter(
        inicial=row['inicial'],
        partida=row['partida'],
        contador=row['contador'],
        hanegadas=row['hanegadas'],
        nombre_completo=row['nombre_completo']
    ) for row in counters_rows]

    users = [User(
        user=row['user'],
        psswd=row['psswd'],
        name=row['name'],
        inicial=row['inicial']
    ) for row in users_rows]

    wsconfigs = [WebScrapConfig(
        key=row['key'],
        value=row['value']
    ) for row in config_rows]
    
    print(counters, users, wsconfigs)

    return counters, users, wsconfigs

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


if __name__ == '__main__':
    load_data()