import sqlite3
import os

from database.models import Counter, User, WebScrapConfig
import os
import sqlite3

def get_db_path():
    """
    Devuelve la ruta absoluta de la base de datos.
    """
    return os.path.join(os.path.dirname(__file__), 'riego.db')


def load_data():
    """
    Carga los datos de counters, users y config desde la base de datos.
    Devuelve tres listas con objetos Counter, User y WebScrapConfig.
    """
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna

        counters_rows = conn.execute("SELECT * FROM counters").fetchall()
        users_rows = conn.execute("SELECT * FROM users").fetchall()
        config_rows = conn.execute("SELECT * FROM config").fetchall()

    counters = [
        Counter(
            inicial=row['inicial'],
            partida=row['partida'],
            contador=row['contador'],
            hanegadas=row['hanegadas'],
            nombre_completo=row['nombre_completo']
        )
        for row in counters_rows
    ]

    users = [
        User(
            user=row['user'],
            psswd=row['psswd'],
            name=row['name'],
            inicial=row['inicial']
        )
        for row in users_rows
    ]

    wsconfigs = [
        WebScrapConfig(
            key=row['key'],
            value=row['value']
        )
        for row in config_rows
    ]

    return counters, users, wsconfigs

def obtener_inicial(usuario):
    """
    Devuelve la inicial asociada a un usuario, o None si no existe.
    """
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT inicial FROM users WHERE user = ?",
            (usuario,)
        ).fetchone()
    return row[0] if row else None

def obtener_riegos_mes_recomendados(fecha):
    """
    Obtiene el número de riegos recomendados por mes.
    Retorna 0 si no se encuentra la recomendación.
    """
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT riegos_por_mes FROM recomendacion_semanal WHERE mes = ?",
            (fecha.month,)
        ).fetchone()
    return int(row[0]) if row else 0

def obtener_factor_recomendacion_semanal_hanegada():
    """
    Obtiene el factor de recomendación semanal por hanegada.
    Retorna 2.5 si no se encuentra el factor.
    """
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT value FROM config WHERE key = 'FACTOR_HGA_RIEGO'"
        ).fetchone()
    return float(row[0]) if row else 2.5

if __name__ == '__main__':
    load_data()