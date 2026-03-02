from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify
from flask_simplelogin import SimpleLogin, login_required
import riegosemanal

from config import Config

app = Flask(__name__)

app.config.from_object(Config)
SimpleLogin(app)

@app.route('/riegosemanal')
@login_required
def riego():
    litros_semanales = riegosemanal.obtener_datos()
    return render_template('riego.html', tabla=litros_semanales)

@app.route('/')
@login_required
def dashboard():
    # Métricas clave
    consumo_hoy = riegosemanal.obtener_consumo_dia(datetime.now())
    
    # Obtener datos de los últimos 7 días agrupados por parcela
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=7)
    consumo_semana = riegosemanal.obtener_consumo_periodo(fecha_inicio, fecha_fin)
    consumo_mes = riegosemanal.obtener_consumo_periodo(fecha_inicio=fecha_fin - timedelta(days=30), fecha_fin=fecha_fin)
    consumo_periodo = riegosemanal.obtener_consumo_periodo(fecha_inicio=fecha_fin - timedelta(days=15), fecha_fin=date.today())
    
    return render_template('dashboard.html',
                        consumo_hoy=consumo_hoy,
                        consumo_semana=consumo_semana,
                        consumo_mes=consumo_mes,
                        consumo_periodo=consumo_periodo
                    )

@app.route('/api/consumo-dia')
@login_required
def api_consumo_dia():

    fecha_str = request.args.get('fecha')
    
    if not fecha_str:
        fecha = datetime.now()
    else:
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Formato de fecha inválido'}), 400
    
    df = riegosemanal.obtener_consumo_dia(fecha)
    # Convertir a array de diccionarios con partida, fecha, valor
    datos = df[['partida', 'valor']].to_dict('records')
    
    return jsonify({
        'datos': datos
    })

@app.route('/api/consumo-semanal')
@login_required
def api_consumo_semanal():
    fecha_str = request.args.get('fecha') # espera 'YYYY-Www' (ej. '2026-W07') o 'YYYY-MM-DD'
    try:
        # Determinar rango inicio/fin (date objects)
        if not fecha_str:
            hoy = date.today()
            inicio = hoy - timedelta(days=hoy.weekday())  # lunes semana actual
            fin = inicio + timedelta(days=6)
        elif '-W' in fecha_str:
            # Formato week: 'YYYY-Www'
            year_str, week_str = fecha_str.split('-W')
            year = int(year_str)
            week = int(week_str)
            inicio = date.fromisocalendar(year, week, 1)  # lunes de la semana ISO
            fin = inicio + timedelta(days=6)
        else:
            # Fallback: tratar como fecha única 'YYYY-MM-DD' -> mismo inicio y fin
            dt = datetime.strptime(fecha_str, '%Y-%m-%d')
            inicio = dt.date()
            fin = inicio
    except Exception:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-Www o YYYY-MM-DD'}), 400

    print(fecha_str, inicio, fin)  # Debug: verificar fechas calculadas
    # Obtener datos de riego de la semana y sumar por parcela
    df = riegosemanal.obtener_consumo_periodo(fecha_inicio=inicio, fecha_fin=fin).to_dict('records')    
    
    print(df)  # Debug: verificar datos obtenidos antes de enviar respuesta

    return jsonify({
        'datos': df,
        'inicio': inicio.strftime('%Y-%m-%d'),
        'fin': fin.strftime('%Y-%m-%d')
    })

@app.route('/api/consumo-mensual')
@login_required
def api_consumo_mensual():
    fecha_str = request.args.get('fecha')  # espera 'YYYY-MM' (ej. '2026-02')
    try:
        if not fecha_str:
            hoy = date.today()
            year = hoy.year
            month = hoy.month
        else:
            year, month = map(int, fecha_str.split('-'))
        
        inicio = date(year, month, 1)
        primera_proximo_mes = (inicio.replace(day=1) + timedelta(days=32)).replace(day=1)
        fin = primera_proximo_mes - timedelta(days=1)# fecha segura para el siguiente mes
       
    except Exception:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM'}), 400

    df = riegosemanal.obtener_consumo_periodo(fecha_inicio=inicio, fecha_fin=fin).to_dict('records')
    
    return jsonify({
        'datos': df,
        'inicio': inicio.strftime('%Y-%m-%d'),
        'fin': fin.strftime('%Y-%m-%d')
    })

@app.route('/api/consumo-periodo')
@login_required
def api_consumo_periodo():
    fecha_inicio_str = request.args.get('fecha_inicio')  # espera 'YYYY-MM-DD'
    fecha_fin_str = request.args.get('fecha_fin')        # espera 'YYYY-MM-DD'
    try:
        if not fecha_inicio_str or not fecha_fin_str:
            return jsonify({'error': 'Debe proporcionar fecha_inicio y fecha_fin en formato YYYY-MM-DD'}), 400
        
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        
        if fecha_inicio > fecha_fin:
            return jsonify({'error': 'fecha_inicio no puede ser posterior a fecha_fin'}), 400
        
    except Exception:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM-DD'}), 400

    # Obtener datos de riego del periodo y sumar por parcela
    df = riegosemanal.obtener_consumo_periodo(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin).to_dict('records')
    
    return jsonify({
        'datos': df,
        'inicio': fecha_inicio.strftime('%Y-%m-%d'),
        'fin': fecha_fin.strftime('%Y-%m-%d')
    })

if __name__ == "__main__":
    app.run(debug=True)
