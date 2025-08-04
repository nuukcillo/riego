import requests
from datetime import datetime as dt, timedelta
from avisosriego import detectar_riegos_anormales


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
    cursor.execute("SELECT mes, riegos_por_semana FROM recomendacion_semanal")
    recomendaciones = cursor.fetchall()

    
  
