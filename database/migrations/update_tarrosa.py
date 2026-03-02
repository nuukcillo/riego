import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import sqlite3
from database.create_db import get_db_path

def update_tarrosa_counter():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE counters
        SET contador = ?
        WHERE partida = ?
    """, ('C000169', 'tarrosa'))
    conn.commit()
    conn.close()
    print("Counter de 'tarrosa' actualizado correctamente.")

if __name__ == "__main__":
    update_tarrosa_counter()
