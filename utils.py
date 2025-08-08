import json
import sys
import os
import logging
import requests
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

def last_sunday():
    """
    Obtiene la fecha del último domingo.

    Returns:
        datetime.date: Fecha del último domingo.
    """
    today = date.today()
    last_sunday = today - timedelta(days=(today.weekday() + 1) % 7)  # Domingo de la semana pasada
    return last_sunday

def first_day_of_week():
    """
    Obtiene el primer día de la semana actual (lunes).

    Returns:
        datetime.date: Fecha del primer día de la semana actual.
    """
    today = date.today()
    first_day = today - timedelta(days=today.weekday())  # Lunes de esta semana
    return first_day

def load_config(config_filename='config.json'):
    """Load the configuration file."""
    config_path = os.path.join(os.path.dirname(__file__), config_filename)
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
    except json.JSONDecodeError:
        logging.error(f"El archivo {config_filename} no es un JSON válido.")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logging.error(f"Error loading config file: {e}")
        sys.exit(1)

def setup_logging():
    """Setup logging configuration."""
    log_filename = f"{os.path.basename(__file__).split('.')[0]}.log"
    logging.basicConfig(
        filename=log_filename,
        format='%(asctime)s %(message)s',
        datefmt='%d/%m/%Y %I:%M:%S %p',
        filemode="w+",
        level=logging.DEBUG
    )
    logging.info("Logging initialized")

def make_request(session, method, url, **kwargs):
    try:
        if method == 'GET':
            return session.get(url, **kwargs)
        elif method == 'POST':
            return session.post(url, **kwargs)
    except requests.RequestException as e:
        logging.error(f"Request error: {e}")
    return None