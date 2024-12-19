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