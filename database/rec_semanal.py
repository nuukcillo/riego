import sqlite3

from riego_repository import get_db_path


def recomendacion_semanal_migration():
    """Crea la tabla recomendacion_semanal y la llena con datos iniciales"""
    try:
        
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        
        # Crear la tabla
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS recomendacion_semanal (
            mes INTEGER PRIMARY KEY,  -- 1 = enero, 12 = diciembre
            riegos_por_semana INTEGER
        )
        ''')

        # Datos de riegos por semana según el mes
        datos_riego = [
            (1, 2),   # Enero
            (2, 2),   # Febrero
            (3, 3),   # Marzo
            (4, 3),   # Abril
            (5, 4),   # Mayo
            (6, 5),   # Junio
            (7, 6),   # Julio
            (8, 6),   # Agosto
            (9, 5),   # Septiembre
            (10, 4),  # Octubre
            (11, 3),  # Noviembre
            (12, 2)   # Diciembre
        ]

        # Insertar los datos
        cursor.executemany('''
        INSERT OR REPLACE INTO recomendacion_semanal (mes, riegos_por_semana)
        VALUES (?, ?)
        ''', datos_riego)

        cursor.execute('''
            INSERT OR REPLACE INTO config (key, value) 
            VALUES ("FACTOR_HGA_RIEGO", "2.5")
        ''')

        # Confirmar cambios y cerrar conexión
        conn.commit()
        conn.close()

        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    if recomendacion_semanal_migration():
        print("Migración completada exitosamente.")
    else:
        print("Hubo un error durante la migración.")