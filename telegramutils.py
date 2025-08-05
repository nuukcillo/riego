import requests
from datetime import datetime as dt, timedelta
from avisosriego import detectar_riegos_anormales
from utils import last_sunday


def enviar_mensaje_telegram(token, chat_id, mensaje, parse_mode=None):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode

    response = requests.post(url, data=payload)
    return response.ok

def enviar_informe_riego_diario(telegram_token, telegram_chat_id, conn):
    cursor = conn.cursor()
    if telegram_token and telegram_chat_id:
        # Fecha de ayer
        fecha_obj = dt.now() - timedelta(days=1)
        fecha_str = fecha_obj.strftime('%Y-%m-%d')

        # Obtener todas las partidas con riego en esa fecha
        cursor.execute("""
            SELECT partida, valor 
            FROM datos_riego 
            WHERE fecha LIKE ?
        """, (f"{fecha_str}%",))
        resultados = cursor.fetchall()

        if not resultados:
            mensaje = f"📅 {fecha_str}\n💧 No se registró riego en ninguna partida."
        else:
            # Encabezado del mensaje
            mensaje = f"📅 *Reporte de Riego - {fecha_str}*\n\n"
            mensaje += "🌾 *Resumen por Partida:*\n\n"
            mensaje += "```\n"
            mensaje += f"{'Partida':<15}{'Riego (m³)':>12}\n"
            mensaje += f"{'-'*27}\n"
            for partida, valor in resultados:
                mensaje += f"{partida:<15}{valor:>12}\n"
            mensaje += "```\n"

        enviar_mensaje_telegram(telegram_token, telegram_chat_id, mensaje, parse_mode='Markdown')

def enviar_avisos_riego_anormal(telegram_token, telegram_chat_id):
    avisos = detectar_riegos_anormales()
    if avisos:
        mensaje = "⚠️ *Avisos* ⚠️\n\n"
        mensaje += "\n".join(avisos)
        enviar_mensaje_telegram(telegram_token, telegram_chat_id, mensaje, parse_mode='Markdown')
 
def enviar_informe_recomendacion_semanal(telegram_token, telegram_chat_id, conn):
    cursor = conn.cursor()

    fecha_fin = last_sunday()
    fecha_inicio = fecha_fin - timedelta(days=6)

    # Obtener número de riegos recomendados por semana
    cursor.execute("SELECT riegos_por_semana FROM recomendacion_semanal WHERE mes = ?", (fecha_inicio.month,))
    numero_riegos_rec_row = cursor.fetchone()
    numero_riegos_rec = int(numero_riegos_rec_row[0]) if numero_riegos_rec_row else 0

    if numero_riegos_rec == 0:
        print("No se encontró la recomendación de riego para este mes.")
        return

    # Obtener riegos de la semana con hanegadas en una sola consulta
    cursor.execute("""
        SELECT d.partida, COUNT(*) as num_riegos, SUM(d.valor) as total_riego, c.hanegadas
        FROM datos_riego d
        JOIN counters c ON d.partida = c.partida
        WHERE d.fecha BETWEEN ? AND ?
        GROUP BY d.partida
    """, (fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")))

    riegos = cursor.fetchall()

    # Encabezado del mensaje
    fecha_inicio_str = fecha_inicio.strftime("%d/%m/%Y")
    fecha_fin_str = fecha_fin.strftime("%d/%m/%Y")
    
    mensaje_md = (
    "🍃 *Informe semanal riego* 🍊\n\n"
    f"📅 Semana: *{fecha_inicio.strftime('%d/%m/%Y')}* → *{fecha_fin.strftime('%d/%m/%Y')}*\n"
    f"Nº riegos recomendados: *{numero_riegos_rec}*\n\n"
    "```\n"
    "Partida   | #Riegos | Real (m³) | Recom.  | Estado \n"
    "----------|---------|-----------|---------|--------\n"
    )

    for partida, num_riegos, total_riego, hanegadas in riegos:
        recomendado = 2.5 * hanegadas * num_riegos
        margen = recomendado * 0.10

        if total_riego < recomendado - margen:
            estado = "🔻Bajo"
        elif total_riego > recomendado + margen:
            estado = "🔺Alto"
        else:
            estado = "✅OK"

        mensaje_md += f"{partida:<10}|{num_riegos:^9}|{total_riego:^11.1f}|{recomendado:^9.1f}|{estado:^8}\n"

    mensaje_md += "```"

    # Enviar con parse_mode Markdown
    enviar_mensaje_telegram(telegram_token, telegram_chat_id, mensaje_md, parse_mode='Markdown')

    mensaje_html = (
    "🍃 <b>Informe semanal riego</b> 🍊<br><br>"
    f"📅 Semana: <b>{fecha_inicio.strftime('%d/%m/%Y')}</b> → <b>{fecha_fin.strftime('%d/%m/%Y')}</b><br>"
    f"Nº riegos recomendados: <b>{numero_riegos_rec}</b><br><br>"
    "<pre>\n"
    "Partida   | #Riegos | Real (m³) | Recom.  | Estado \n"
    "----------|---------|-----------|---------|--------\n"
    )

    for partida, num_riegos, total_riego, hanegadas in riegos:
        recomendado = 2.5 * hanegadas * num_riegos
        margen = recomendado * 0.10

        if total_riego < recomendado - margen:
            estado = "🔻Bajo"
        elif total_riego > recomendado + margen:
            estado = "🔺Alto"
        else:
            estado = "✅OK"

        mensaje_html += f"{partida:<10}|{num_riegos:^9}|{total_riego:^11.1f}|{recomendado:^9.1f}|{estado:^8}\n"

    mensaje_html += "</pre>"

    # Enviar con parse_mode HTML
    enviar_mensaje_telegram(telegram_token, telegram_chat_id, mensaje_html, parse_mode='HTML')


  
