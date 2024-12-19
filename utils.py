import json
from datetime import date, timedelta

def is_current_week(date_to_check):
    """
    Verifica si una fecha pertenece a la semana actual (lunes a domingo).

    Args:
        date_to_check (datetime.date): Fecha a comprobar.

    Returns:
        bool: True si la fecha está dentro de la semana actual, False en caso contrario.
    """
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Lunes de esta semana
    end_of_week = start_of_week + timedelta(days=7)         # Lunes de la próxima semana
    return start_of_week <= date_to_check < end_of_week

def leer_recomendacion_semanal():
    """
    Lee el valor de 'recomendacion_semanal' de un archivo JSON.

    Returns:
        int: Valor de la recomendación semanal, o None si no se encuentra.
    """
    archivo_config = "config.json"
    try:
        with open(archivo_config, 'r', encoding='utf-8') as archivo:
            config = json.load(archivo)
            return config.get("recomendacion_semanal", None)
    except FileNotFoundError:
        print(f"El archivo {archivo_config} no se encontró.")
    except json.JSONDecodeError:
        print(f"El archivo {archivo_config} no es un JSON válido.")
    return None
