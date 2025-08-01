import sqlite3
import os

def reset_database():
    db_path = get_db_path()
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Base de datos eliminada: {db_path}")
    else:
        print("No se encontró ninguna base de datos existente para eliminar.")
def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'riego.db')

def execute_sql_commands(commands):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for command in commands:
        cursor.execute(command)
    conn.commit()
    conn.close()

def create_database():
    commands = [
        '''
        CREATE TABLE IF NOT EXISTS counters (
            inicial TEXT,
            partida TEXT,
            contador TEXT,
            hanegadas REAL,
            nombre_completo TEXT,
            PRIMARY KEY (partida),
            FOREIGN KEY (inicial) REFERENCES users(inicial)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS users (
            user TEXT,
            psswd TEXT,
            name TEXT,
            inicial TEXT,
            PRIMARY KEY (user, inicial)
        )
        ''',
        '''
        CREATE TABLE IF NOT EXISTS datos_riego (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida TEXT,
            fecha TEXT,
            valor INTEGER,
            UNIQUE(partida, fecha)
            FOREIGN KEY (partida) REFERENCES counters(partida)
        )
        ''',
          # Índices recomendados
        'CREATE INDEX IF NOT EXISTS idx_datos_partida ON datos_riego(partida, fecha)',
        'CREATE INDEX IF NOT EXISTS idx_counters_inicial ON counters(inicial)',
        'CREATE INDEX IF NOT EXISTS idx_users_user ON users(user)'
    ]
    execute_sql_commands(commands)

def insert_data():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Insert data into counters table
    cursor.executemany('''
    INSERT INTO counters (inicial, partida, contador, hanegadas, nombre_completo) VALUES (?, ?, ?, ?, ?)
    ''', [
        ('B', 'carretera', 'C000453', 3, 'Carretera'),
        ('B', 'c_villar', 'C000233', 20, 'Camino el Villar'),
        ('F', 'higuerica', 'C000141', 6, 'Higuerica'),
        ('F', 'tarrosa', 'C000171', 7.7, 'Tarrosa'),
        ('F', 'panderon', 'C000329', 120, 'Panderón'),
        ('F', 'mojon', 'C000340', 29, 'Mojón'),
        ('F', 'lalosa', 'C000356', 5, 'La Losa'),
        ('F', 'corralquemao', 'C000606', 6, 'Corral Quemao'),
        ('F', 'villaricos', 'C000621', 6, 'Villaricos'),
        ('I', 'clochas', 'C000670', 29, 'Clochas')
    ])

    # Insert data into users table
    cursor.executemany('''
    INSERT INTO users (user, psswd, name, inicial) VALUES (?, ?, ?, ?)
    ''', [
        ('marcocerveraborja', '44883358', 'Borja', 'B'),
        ('marcozanonteofilo', '22601346', 'Filo', 'F'),
        # Add more rows as needed
    ])

    conn.commit()
    conn.close()

reset_database()
# Create database and insert data
create_database()
insert_data()
