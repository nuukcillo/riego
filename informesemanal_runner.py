import os
import sqlite3
from telegramutils import enviar_informe_recomendacion_semanal
from database.riego_repository import get_db_path

def main():
    conn = sqlite3.connect(get_db_path())
    TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    enviar_informe_recomendacion_semanal(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, conn)
    conn.close()

if __name__ == "__main__":
    main()
