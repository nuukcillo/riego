import os
import sys
import csv
import json
import shutil
import logging
import datetime
from datetime import datetime as dt
from bs4 import BeautifulSoup
import requests
from database.riego_repository import load_data

def load_config(config_filename='config.json'):
    """Load the configuration file."""
    config_path = os.path.join(os.path.dirname(__file__), config_filename)
    try:
        with open(config_path, 'r') as config_file:
            return json.load(config_file)
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

def archive_csv(file_path, archive_folder, archive_date):
    """Archive a CSV file if it exists."""
    if os.path.isfile(file_path):
        archive_path = os.path.join(archive_folder, f"{archive_date}_{os.path.basename(file_path)}")
        shutil.copy2(file_path, archive_path)
        logging.info(f"Archived {file_path} to {archive_path}")

def parse_table_to_csv(html_content, csv_path):
    """Parse an HTML table and save it to a CSV file."""
    table = BeautifulSoup(html_content, 'lxml').find('table')
    if not table:
        logging.error("No table found in the HTML content")
        return

    headers = [header.text for header in table.find_all('th')]
    rows = [[cell.text for cell in row.find_all('td')] for row in table.find_all('tr')]

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(row for row in rows if row)
    logging.info(f"Saved table to {csv_path}")

def make_request(session, method, url, **kwargs):
    """Make an HTTP request and handle exceptions."""
    try:
        if method == 'GET':
            return session.get(url, **kwargs)
        elif method == 'POST':
            return session.post(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    except requests.exceptions.RequestException as e:
        logging.exception(f"Request failed: {e}")
        return None

def main():
    setup_logging()
    logging.info("Starting script")

    # Load configuration
    config = load_config()
    LOGIN_URL = config['LOGIN_URL']
    LOGIN_URL_REF = config['LOGIN_URL_REF']
    LOGOUT_URL = config['LOGOUT_URL']
    BASE_URL = config['BASE_URL']

    # Load user and counters data from database
    counters, users = load_data()

    current_month_year = dt.now().strftime('%m%Y')
    archive_date = (dt.now() - datetime.timedelta(days=dt.now().day)).strftime("%Y%m")
    archive_folder = os.path.join(os.getcwd(), 'csv_files', dt.now().strftime('%Y'))
    os.makedirs(archive_folder, exist_ok=True)

    # Ensure CSV directory exists
    csv_directory = os.path.join(os.getcwd(), 'csv_files')
    os.makedirs(csv_directory, exist_ok=True)

    # Process each user
    for user in users.itertuples():
        session = requests.Session()
        login_payload = {"usuario": user.user, "password": user.psswd}

        # Perform login
        response = make_request(session, 'POST', LOGIN_URL, data=login_payload, headers={'referer': LOGIN_URL_REF})
        if not response or response.status_code != 200:
            logging.error(f"Login failed for user {user.user}")
            continue

        # Process counters for the user
        user_counters = counters[counters['inicial'] == user.inicial]
        for counter in user_counters.itertuples():
            csv_file = os.path.join(csv_directory, f"{counter.partida}.csv")

            # Archive CSV if it's the first day of the month
            if dt.now().day == 1:
                archive_csv(csv_file, archive_folder, archive_date)

            # Download data
            data_url = BASE_URL.format(counter.contador, current_month_year)
            response = make_request(session, 'GET', data_url, headers={'referer': data_url})
            if response and response.content:
                parse_table_to_csv(response.content, csv_file)

        # Logout
        make_request(session, 'GET', LOGOUT_URL, headers={'referer': LOGIN_URL_REF})

    logging.info("Script finished")

if __name__ == '__main__':
    main()
