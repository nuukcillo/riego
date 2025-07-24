import sqlite3
from datetime import datetime, timedelta
from database.create_db import get_db_path


def detectar_riegos_anormales(umbral_factor=3):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fechas para el último mes
    hoy = datetime.now()
    hace_un_mes = hoy - timedelta(days=30)
    fecha_inicio = hace_un_mes.strftime('%Y-%m-%d 00:00:00')
    fecha_fin = hoy.strftime('%Y-%m-%d 23:59:59')

    # Obtener todas las partidas
    cursor.execute("SELECT DISTINCT partida FROM datos_riego")
    partidas = [row[0] for row in cursor.fetchall()]

    avisos = []

    for partida in partidas:
        cursor.execute("""
            SELECT valor, fecha FROM datos_riego
            WHERE partida = ? AND fecha BETWEEN ? AND ? AND valor > 0
            ORDER BY fecha
        """, (partida, fecha_inicio, fecha_fin))
        datos = cursor.fetchall()
        if not datos:
            continue

        valores = [row[0] for row in datos]
        media = sum(valores) / len(valores)
        umbral = media * umbral_factor

        for valor, fecha in datos:
            if valor > umbral:
                avisos.append(
                    f"Riego anormalmente alto en '{partida}' el {fecha}: {valor} m³ (media últ 30d: {media:.2f} m³)"
                )

    conn.close()
    return avisos

if __name__ == "__main__":
    avisos = detectar_riegos_anormales()
    if avisos:
        print("AVISOS DE RIEGO ANORMAL:")
        for aviso in avisos:
            print(aviso)
    else:
        print("No se detectaron riegos anormales en el último mes.")