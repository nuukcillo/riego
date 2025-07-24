import argparse
import logging
import sqlite3
from datetime import datetime as dt

import requests
from bs4 import BeautifulSoup

from database.riego_repository import load_data, get_db_path
from telegramutils import enviar_avisos_riego_anormal, enviar_informe_riego_diario
from utils import load_config, setup_logging, make_request

def parse_and_save_to_db(html_content, partida, conn, parse_all=False):
    """Parsea tabla HTML e inserta los datos en SQLite"""
    table = BeautifulSoup(html_content, 'lxml').find('table')
    if not table:
        logging.warning("No se encontró la tabla en el HTML.")
        return

    rows = [[td.text.strip() for td in tr.find_all('td')] for tr in table.find_all('tr') if tr.find_all('td')]

    cursor = conn.cursor()
    if parse_all:
        rows_to_parse = rows
    else:
        rows_to_parse = [rows[-1]] if rows else []

    for row in rows_to_parse:
        try:            
            # Original date string
            date_string = row[0].strip()
            
            # Parse the string into a datetime object
            parsed_date = dt.strptime(date_string, "%b %d %Y %I:%M%p")
            
            # Convert to SQLite-compatible format (YYYY-MM-DD HH:MM:SS)
            sqlite_date = parsed_date.strftime("%Y-%m-%d %H:%M:%S")
            
            riego = row[4].strip()

            riego_int = int(riego.split()[0])  # Extrae el primer elemento y lo convierte a entero

            cursor.execute("""
                    INSERT INTO datos_riego (partida, fecha, valor)
                    VALUES (?, ?, ?)
                    ON CONFLICT(partida, fecha) DO UPDATE SET valor=excluded.valor
                """, (partida, sqlite_date, riego_int))
        except Exception as e:
            logging.error(f"Error insertando fila: {row} - {e}")

    conn.commit()

def main():
    """Main function to run the web scraping and data insertion"""
    parser = argparse.ArgumentParser(description="Web scraping script")
    parser.add_argument("--parse_all", action="store_true", help="Parse all rows instead of just the last one")
    parser.add_argument("--month_year", type=str, help="Month and year to scrape (MMYYYY)", default=dt.now().strftime('%m%Y'))
    args = parser.parse_args()

    month_year = args.month_year

    setup_logging()
    logging.info("Inicio del script")

    parse_all = args.parse_all  # Store the value of parse_all

    config = load_config()
    LOGIN_URL = config['LOGIN_URL']
    LOGIN_URL_REF = config['LOGIN_URL_REF']
    LOGOUT_URL = config['LOGOUT_URL']
    BASE_URL = config['BASE_URL']
    TELEGRAM_TOKEN = config['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = config['TELEGRAM_CHAT_ID']
    # Cargar datos
    counters, users = load_data()

    # Conexión a la base de datos SQLite
    conn = sqlite3.connect(get_db_path())

    for user in users.itertuples():
        session = requests.Session()
        login_payload = {"usuario": user.user, "password": user.psswd}

        response = make_request(session, 'POST', LOGIN_URL, data=login_payload, headers={'referer': LOGIN_URL_REF})
        if not response or response.status_code != 200:
            logging.error(f"Error al hacer login con {user.user}")
            continue

        user_counters = counters[counters['inicial'] == user.inicial]
        for counter in user_counters.itertuples():
            data_url = BASE_URL.format(counter.contador, month_year)
            response = make_request(session, 'GET', data_url, headers={'referer': data_url})
            if response and response.content:
                parse_and_save_to_db(response.content, counter.partida, conn, parse_all)  # Pass the stored value
        

        make_request(session, 'GET', LOGOUT_URL, headers={'referer': LOGIN_URL_REF})
    
    enviar_informe_riego_diario(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, conn)
    enviar_avisos_riego_anormal(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    conn.close()
    logging.info("Script terminado correctamente")

if __name__ == '__main__':
    main()