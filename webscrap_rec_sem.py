import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import setup_logging

# Configura logging
setup_logging()

# URL principal
url = "http://riegos.ivia.es/resumenes"

try:
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'
except requests.RequestException as e:
    logging.error(f"Error al conectar con la web: {e}")
    exit(1)

# Parsear HTML
soup = BeautifulSoup(response.text, 'lxml')

# === 1. Extraer tabla de necesidades ===
tabla = soup.select_one('table#tabla_informe_necesidades')

if not tabla:
    logging.error("No se encontró la tabla con ID 'tabla_informe_necesidades'")
    exit(1)

# Buscar fila que contiene "LOS SERRANOS" (mayúsculas, sin tildes)
serranos_td = tabla.find('td', string=lambda t: t and 'LOS SERRANOS' in t.upper())

if not serranos_td:
    logging.warning("No se encontró la fila para 'LOS SERRANOS'")
else:
    # Extraer la 8ª columna (índice 7) que corresponde al 55%
    try:
        celdas = serranos_td.find_parent('tr').find_all('td')
        valor_55 = celdas[7].get_text(strip=True)
        print(f"💧 Valor para Los Serranos al 55% de sombreado: {valor_55} mm")
    except IndexError:
        logging.error("No se pudo acceder a la columna 55% en la fila de LOS SERRANOS")

# === 2. Extraer semana y fechas del encabezado ===
titular = soup.select_one('div#informe_citricos > h3.titular')

if not titular:
    logging.warning("No se encontró el encabezado de fechas")
else:
    texto = titular.get_text(strip=True)
    try:
        # Formato esperado: "NECESIDADES DE AGUA DE LOS CÍTRICOS DEL 21/07/2025 AL 27/07/2025"
        inicio_str = texto.split("DEL ")[1].split(" AL ")[0]
        fin_str = texto.split(" AL ")[1]
        
        fecha_inicio = datetime.strptime(inicio_str, '%d/%m/%Y')
        fecha_fin = datetime.strptime(fin_str, '%d/%m/%Y')
        semana = fecha_inicio.isocalendar()[1]

        print(f"📅 Semana {semana} | Fechas: {inicio_str} a {fin_str}")
    except (IndexError, ValueError) as e:
        logging.error(f"No se pudieron extraer las fechas: {e}")
