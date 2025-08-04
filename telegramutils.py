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

          
    cursor.execute("SELECT riegos_por_semana FROM recomendacion_semanal WHERE mes = ?", (fecha_inicio.month,))
    numero_riegos_rec_query = cursor.fetchone()

    numero_riegos_rec = 0
    
    if numero_riegos_rec_query is not None:
        numero_riegos_rec = int(numero_riegos_rec_query[0])
    
    if numero_riegos_rec == 0:
        print("No se encontró la recomendación de riego para este mes.")
        exit(1)
    
    # Obtener los riegos de la última semana por partida
    cursor.execute("""
        SELECT partida, COUNT(*) as num_riegos, SUM(valor) as total_riego
        FROM datos_riego
        WHERE fecha BETWEEN ? AND ?
        GROUP BY partida
    """, (fecha_inicio.strftime("%Y-%m-%d"), fecha_fin.strftime("%Y-%m-%d")))

    riegos_semanales = cursor.fetchall()

    fecha_inicio_str = fecha_inicio.strftime("%d/%m/%Y")
    fecha_fin_str = fecha_fin.strftime("%d/%m/%Y")
    
    mensaje = f"🍃 *Informe semanal riego* 🍊\n\n📅 Semana: *{fecha_inicio_str}* → *{fecha_fin_str}*\n\n"
    mensaje += f"Nº riegos recomendados: {numero_riegos_rec}\n"


    for partida, num_riegos, total_riego in riegos_semanales:
        cursor.execute("SELECT hanegadas FROM counters WHERE partida = ?", (partida,))
        resultado = cursor.fetchone()
        
        mensaje += f" `{partida}` | Número: *{num_riegos}* | Riego (m³): *{total_riego}* | "
        if resultado:
            hanegadas = resultado[0]
            recomendacion = 2.5 * hanegadas * num_riegos

            margen = recomendacion * 0.10
            if total_riego < recomendacion - margen:
                estado = "🔻 *Por debajo*"
            elif total_riego > recomendacion + margen:
                estado = "🔺 *Por encima*"
            else:
                estado = "✅ *Similar*"

            mensaje += f"📊 Recomendado: *{recomendacion:.2f}* → {estado}\n"
        
        if num_riegos < numero_riegos_rec:
            mensaje += f" | ⚠️: Nº Reg : {num_riegos}\n"
       

    # Enviar el mensaje por Telegram
    enviar_mensaje_telegram(telegram_token, telegram_chat_id, mensaje, parse_mode='Markdown')



  
