from datetime import datetime, date, timedelta
from flask import Flask, render_template, request, jsonify
import time
from flask_simplelogin import SimpleLogin, login_required

from database.riego_repository import load_data, obtener_inicial
import plotpygal
import riegosemanal

from config import Config

app = Flask(__name__)

app.config.from_object(Config)
SimpleLogin(app)


@app.route("/")
@app.route("/index")
@login_required
def home():
    _, usuarios = load_data()

    nombre_usuarios = usuarios['name'].tolist()
    id_usuarios = usuarios['user'].tolist()
    return render_template('index.html', users_name=nombre_usuarios, users_len=len(nombre_usuarios),
                           users_id=id_usuarios)


@app.route('/gente/<people>')
@login_required
def gente(people):
    parcelas_ret = []  # Lista que guardará los nombres de los archivos SVG de cada parcela
   
    inicial = obtener_inicial(people)
    df = riegosemanal.obtener_valores_riego(inicial=inicial, todos=True).iloc[:, -7:]

    # Dibujar gráficos para cada parcela
    for parcela in df.index:
        # Filtrar los datos para cada parcela
        parcela_data = df.loc[parcela]
        
        # Generar el gráfico para la parcela
        plotpygal.plot_barchar_riego(parcela_data.index.tolist(), parcela_data.tolist(), parcela)

        # Añadir el nombre del archivo SVG generado a la lista
        parcelas_ret.append(f"{parcela}.svg")

    # Pasar los nombres de los archivos SVG y el número de parcelas a la plantilla
    return render_template('bar.html', parcelas=parcelas_ret, num_parcelas=len(parcelas_ret), cache=str(time.time()))



# @app.route("/bar")
# def bar():
#     plotpygal.main()
#     img_url = 'static/images/c_villar.svg?cache=' + str(time.time())
#     return render_template('bar.html', image_url=img_url)
#

@app.route('/riegosemanal')
@login_required
def riego():
    litros_semanales = riegosemanal.obtener_datos()
    return render_template('riego.html', tabla=litros_semanales.to_html(classes="responsible-table striped",
                                                                        index_names=False, index=True, justify='center'
                                                                        ))
@app.route('/dashboard')
@login_required
def dashboard():
    # Métricas clave
    consumo_hoy = riegosemanal.obtener_consumo_dia(datetime.now()).to_html(classes="responsible-table striped",
                                                                        index_names=False, index=True, justify='center'
                                                                        )
    
    # Obtener datos de los últimos 7 días agrupados por parcela
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=7)
    consumo_semana = riegosemanal.obtener_consumo_periodo(fecha_inicio, fecha_fin)
    consumo_semana_html = consumo_semana.to_html(classes="responsible-table striped",
                                                                        index_names=False, index=True, justify='center'
                                                                        )
    consumo_mes = riegosemanal.obtener_consumo_mes()
    
    # Comparativa con recomendación
    recomendacion = riegosemanal.leer_recomendacion_semanal()
    desviacion = ((consumo_semana - recomendacion) / recomendacion) * 100
    
    # Gráficos de tendencias (últimos 30 días, trimestre, año)
    tendencia_30d = riegosemanal.generar_grafico_tendencia(30)
    tendencia_trimestre = riegosemanal.generar_grafico_tendencia(90)

    # Alertas por desviación
    alertas = riegosemanal.generar_alertas_desviacion(umbral=20)
    
    return render_template('dashboard.html',
                          consumo_hoy=consumo_hoy,
                          consumo_semana=consumo_semana_html,
                          consumo_mes=consumo_mes,
                          desviacion=desviacion,
                          tendencia_30d=tendencia_30d,
                          tendencia_trimestre=tendencia_trimestre,
                          alertas=alertas)

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

    # Obtener datos de riego de la semana y sumar por parcela
    df = riegosemanal.obtener_consumo_periodo(fecha_inicio=inicio, fecha_fin=fin).to_dict('records')    
    
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
       
    except Exception:
        return jsonify({'error': 'Formato de fecha inválido. Use YYYY-MM'}), 400

    # Obtener datos de riego del mes y sumar por parcela
    df = riegosemanal.obtener_consumo_mes(fecha=inicio)
    consumo_mensual = df.groupby('partida')['valor'].sum().reset_index()
    consumo_mensual.columns = ['partida', 'valor']
    
    datos = consumo_mensual.to_dict('records')
    
    return jsonify({
        'datos': datos,
        'inicio': inicio.strftime('%Y-%m-%d'),
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
    app.run()
