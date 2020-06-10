from datetime import datetime as dt

import csv
import datetime
import logging
import os
import pandas as pd
import requests
import shutil
import sys
from bs4 import BeautifulSoup

LOGIN_URL = "http://tarragon.gootem.com/autentica.html"
LOGOUT_URL = "http://tarragon.gootem.com/logout.html"
BASE_URL = "http://tarragon.gootem.com/index.php?lang=en&page=historial_riego&idContador={0}&mes=F{1}"


def get_dataframe_filtered_by_user(dataframe, user):
    inicial = ""
    if user == "marcocerveraborja":
        inicial = "B"
    elif user == "marcozanonteofilo":
        inicial = "F"
    elif user == "isaac":
        inicial = "I"
    try:
        return dataframe.loc[dataframe['user'] == inicial].drop(['user'], axis=1)
    except:
        logging.error("error al leer usuario")
        sys.exit(1)


def main():
    logging.basicConfig(filename="{}.log".format(os.path.basename(__file__).split('.')[0]),
                        format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p', filemode="a")

    logging.info("Empezando")
    try:
        # Leemos los contadores
        contadores = pd.read_csv("contadores.tsv", sep="\t", header=None, names=['user', 'partida', 'contador', 'hanegadas'])

        # por cada usuario hac
        usuarios = pd.read_csv("userpass.tsv", sep="\t", header=None, names=['user', 'psswd', 'name'])
    except:
        logging.error("Error leyendo ficheros de configuración")
        sys.exit(1)

    month = dt.now().strftime('%m')
    year = dt.now().strftime('%Y')

    # anyo y dia del mes pasado para archivar documentos
    archive = (dt.utcnow().replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")

    # Preparando para archivar
    archive_folder_path = os.path.abspath(os.getcwd()) + os.path.sep + year
    if not os.path.isdir(archive_folder_path):
        os.mkdir(archive_folder_path)

    for usuario in usuarios.itertuples():

        # Crear Sesion
        session_requests = requests.session()

        # TODO Sacar las llamadas a request a una funcion
        try:
            # Get login csrf token
            result = session_requests.get(LOGIN_URL)
            result.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.exception("Error HTTP: {0}".format(errh.response.status_code))
        except requests.exceptions.ConnectionError as errc:
            logging.exception("Error de conexión")
        except requests.exceptions.Timeout as errt:
            logging.exception("Error de Timeout")  # en español Timeout queda feo
        except requests.exceptions.RequestException as err:
            logging.exception("Error")

        # Create payload
        payload = {
            "usuario": usuario.user,
            "password": usuario.psswd
        }
        try:
            # Perform login
            result = session_requests.post(LOGIN_URL, data=payload, headers=dict(referer=LOGIN_URL))
            result.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.exception("Error HTTP: {0}".format(errh.response.status_code))
        except requests.exceptions.ConnectionError as errc:
            logging.exception("Error de conexión")
        except requests.exceptions.Timeout as errt:
            logging.exception("Error de Timeout")  # en español Timeout queda feo
        except requests.exceptions.RequestException as err:
            logging.exception("Error")

        for campo in get_dataframe_filtered_by_user(contadores, usuario.user).itertuples():

            # Si es dia 1 se archiva el csv
            nombrecsv = campo.partida + ".csv"
            csv_working_file = '{0}{1}{2}'.format(os.path.abspath(os.getcwd()), os.path.sep, nombrecsv)
            if dt.now().day == 1:
                shutil.copy2(csv_working_file,
                             '{0}{1}{2}{3}'.format(archive_folder_path, os.path.sep, archive, nombrecsv))

            download_data_url = BASE_URL.format(campo.contador, month + year)

            result = session_requests.get(download_data_url, headers=dict(referer=download_data_url))

            # Como en la web solo hay una tabla la buscamos
            table = BeautifulSoup(result.content, 'lxml').find('table')

            # Headers para el csv
            table_headers = [header.text for header in table.find_all('th')]
            rows = []

            for row in table.find_all('tr'):
                rows.append([val.text for val in row.find_all('td')])

            with open(csv_working_file, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(table_headers)
                writer.writerows(row for row in rows if row)

        try:
            # Perform login
            result = requests.get(LOGOUT_URL, headers=dict(referer=download_data_url))
            result.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logging.exception("Error HTTP: {0}".format(errh.response.status_code))
        except requests.exceptions.ConnectionError:
            logging.exception("Error de conexión")
        except requests.exceptions.Timeout:
            logging.exception("Error de Timeout")  # en español Timeout queda feo
        except requests.exceptions.RequestException:
            logging.exception("Error")

    logging.info("Terminando")


if __name__ == '__main__':
    main()
