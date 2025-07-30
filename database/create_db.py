import argparse
import sqlite3
import os
import json
from dataclasses import dataclass

@dataclass
class User:
    user: str
    psswd: str
    name: str
    inicial: str

@dataclass
class Counter:
    inicial: str
    partida: str
    contador: str
    hanegadas: float
    nombre_completo: str

@dataclass
class WebScrapConfig:
    key: str
    value: str


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
        '''
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY NOT NULL,
            value TEXT NOT NULL
        )
        ''',
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
    users = [
        User('marcocerveraborja', '44883358', 'Borja', 'B'),
        User('marcozanonteofilo', '22601346', 'Filo', 'F'),
    ]

    counters = [
        Counter('B', 'carretera', 'C000453', 3, 'Carretera'),
        Counter('B', 'c_villar', 'C000233', 20, 'Camino el Villar'),
        Counter('F', 'higuerica', 'C000141', 6, 'Higuerica'),
        Counter('F', 'tarrosa', 'C000171', 7.7, 'Tarrosa'),
        Counter('F', 'panderon', 'C000329', 120, 'Panderón'),
        Counter('F', 'mojon', 'C000340', 29, 'Mojón'),
        Counter('F', 'lalosa', 'C000356', 5, 'La Losa'),
        Counter('F', 'corralquemao', 'C000606', 6, 'Corral Quemao'),
        Counter('F', 'villaricos', 'C000621', 6, 'Villaricos'),
        Counter('I', 'clochas', 'C000670', 29, 'Clochas'),
    ]

    configs = [
        WebScrapConfig('LOGIN_URL', 'https://riego.example.com/login'),
        WebScrapConfig('LOGIN_URL_REF', 'https://riego.example.com/login_ref'),
        WebScrapConfig('LOGOUT_URL', 'https://riego.example.com/logout'),
        WebScrapConfig('BASE_URL', 'https://riego.example.com/'),
        WebScrapConfig('recomendacion_semanal', '4'),
    ]

    cursor.executemany('''
        INSERT INTO users (user, psswd, name, inicial) VALUES (?, ?, ?, ?)
    ''', [(u.user, u.psswd, u.name, u.inicial) for u in users])

    cursor.executemany('''
        INSERT INTO counters (inicial, partida, contador, hanegadas, nombre_completo) VALUES (?, ?, ?, ?, ?)
    ''', [(c.inicial, c.partida, c.contador, c.hanegadas, c.nombre_completo) for c in counters])

    cursor.executemany('''
        INSERT INTO config (key, value) VALUES (?, ?)
    ''', [(c.key, c.value) for c in configs])

    conn.commit()
    conn.close()

def migrate_configjson(json_file='config.json'):
    """Migración directa sin dividir URLs"""
    try:
        with open(json_file, 'r') as f:
            config = json.load(f)
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY NOT NULL,
                value TEXT NOT NULL
            );
        """)
        
        # Insertamos todas las URLs completas directamente
        data = [
            ('LOGIN_URL', config['LOGIN_URL']),
            ('LOGIN_URL_REF', config['LOGIN_URL_REF']),
            ('LOGOUT_URL', config['LOGOUT_URL']),
            ('BASE_URL', config['BASE_URL']),  # La mantenemos por si acaso
            ('recomendacion_semanal', str(config.get('recomendacion_semanal', 4)))  # Valor por defecto
        ]
        
        cursor.executemany("""
            INSERT OR REPLACE INTO config (key, value) 
            VALUES (?, ?)
        """, data)
        
        conn.commit()
        
        print(f"Migración exitosa! Backup")

        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Gestión de la base de datos de riego.")
    parser.add_argument(
        "accion",
        choices=["init", "reset_init", "migrate_config"],
        help="Acción a realizar: init (crear/insertar), reset_init (resetear y crear), migrate_config (migrar config.json)"
    )
    parser.add_argument(
        "--config", 
        default="config.json",
        help="Ruta del archivo config.json (solo para migrate_config)"
    )

    args = parser.parse_args()

    if args.accion == "init":
        create_database()
        insert_data()
        print("Base de datos inicializada.")
    elif args.accion == "reset_init":
        reset_database()
        create_database()
        insert_data()
        print("Base de datos reseteada e inicializada.")
    elif args.accion == "migrate_config":
        success = migrate_configjson(args.config)
        if success:
            print("Configuración migrada correctamente.")
        else:
            print("Fallo al migrar configuración.")