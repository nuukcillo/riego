import sqlite3
from datetime import datetime, timedelta
from database.riego_repository import get_db_path


def detectar_riegos_anormales(umbral_factor=3):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    hoy = datetime.now()
    hoy_str = hoy.strftime('%Y-%m-%d')
    inicio_semana = hoy - timedelta(days=7)
    inicio_str = inicio_semana.strftime('%Y-%m-%d 00:00:00')
    fin_str = hoy.strftime('%Y-%m-%d 0:00:00')

    # Obtener todas las partidas
    cursor.execute("SELECT DISTINCT partida FROM datos_riego")
    partidas = [row[0] for row in cursor.fetchall()]

    avisos = []

    for partida in partidas:
        # Valores de la última semana (excluyendo hoy)
        cursor.execute("""
            SELECT valor FROM datos_riego
            WHERE partida = ? AND fecha >= ? AND fecha < ? AND valor > 0 
        """, (partida, inicio_str, fin_str))
        valores_semana = [row[0] for row in cursor.fetchall()]
        if not valores_semana:
            continue

        media_semana = sum(valores_semana) / len(valores_semana)
        umbral = media_semana * umbral_factor

        # Valor de hoy
        cursor.execute("""
            SELECT valor, fecha FROM datos_riego
            WHERE partida = ? AND DATE(fecha) = ?
        """, (partida, hoy_str))
        datos_hoy = cursor.fetchall()
        for valor, fecha in datos_hoy:
            if valor > umbral:
                avisos.append(
                    f"Riego anormalmente alto en '{partida}' el {fecha}: {valor} m³ (media últ semana: {media_semana:.2f} m³)"
                )

    conn.close()
    return avisos

if __name__ == "__main__":
    avisos = detectar_riegos_anormales()
    if avisos:
        print("AVISOS DE RIEGO ANORMAL HOY:")
        for aviso in avisos:
            print(aviso)
    else:
        print("No se detectaron riegos anormales en el último mes.")