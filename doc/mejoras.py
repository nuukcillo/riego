"""
================================================================================
MEJORAS FUNCIONALES PARA EL PROYECTO RIEGO
================================================================================

Este archivo documenta todas las mejoras funcionales propuestas para el proyecto.
Cada mejora incluye descripción, módulos afectados, prioridad y ejemplo de código.

Fecha de creación: 29 de enero de 2026
================================================================================
"""

# ==============================================================================
# 1. DASHBOARD ANALÍTICO MEJORADO
# ==============================================================================
"""
MEJORA: Dashboard Analítico Mejorado
DESCRIPCIÓN: Panel de control principal con métricas clave, gráficos de 
             tendencias y alertas visuales.
PRIORIDAD: Alta (corto plazo)
MÓDULOS AFECTADOS: app.py, templates/dashboard.html, plotpygal.py

IMPLEMENTACIÓN SUGERIDA:

# En app.py - Nueva ruta para el dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Métricas clave
    consumo_hoy = obtener_consumo_dia(datetime.now())
    consumo_semana = obtener_consumo_semana()
    consumo_mes = obtener_consumo_mes()
    
    # Comparativa con recomendación
    recomendacion = leer_recomendacion_semanal()
    desviacion = ((consumo_semana - recomendacion) / recomendacion) * 100
    
    # Gráficos de tendencias (últimos 30 días, trimestre, año)
    tendencia_30d = generar_grafico_tendencia(30)
    tendencia_trimestre = generar_grafico_tendencia(90)
    
    # Alertas por desviación
    alertas = generar_alertas_desviacion(umbral=20)
    
    return render_template('dashboard.html',
                          consumo_hoy=consumo_hoy,
                          consumo_semana=consumo_semana,
                          consumo_mes=consumo_mes,
                          desviacion=desviacion,
                          tendencia_30d=tendencia_30d,
                          tendencia_trimestre=tendencia_trimestre,
                          alertas=alertas)

# Nueva función en riegosemanal.py
def obtener_consumo_dia(fecha):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    fecha_str = fecha.strftime('%Y-%m-%d')
    query = "SELECT SUM(valor) FROM datos_riego WHERE DATE(fecha) = ?"
    result = pd.read_sql_query(query, conn, params=[fecha_str])
    conn.close()
    return result.iloc[0, 0] or 0

def obtener_consumo_semana():
    hoy = datetime.now()
    inicio = hoy - timedelta(days=hoy.weekday())
    return obtener_consumo_periodo(inicio, hoy)

def obtener_consumo_mes():
    hoy = datetime.now()
    inicio = hoy.replace(day=1)
    return obtener_consumo_periodo(inicio, hoy)

def obtener_consumo_periodo(fecha_inicio, fecha_fin):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    inicio_str = fecha_inicio.strftime('%Y-%m-%d 00:00:00')
    fin_str = fecha_fin.strftime('%Y-%m-%d 23:59:59')
    query = "SELECT SUM(valor) FROM datos_riego WHERE fecha BETWEEN ? AND ?"
    result = pd.read_sql_query(query, conn, params=[inicio_str, fin_str])
    conn.close()
    return result.iloc[0, 0] or 0

def generar_alertas_desviacion(umbral=20):
    # Implementar lógica de alertas por desviación
    alertas = []
    # ... lógica
    return alertas
"""

# ==============================================================================
# 2. GESTIÓN DE UMBRALES INTELIGENTE
# ==============================================================================
"""
MEJORA: Umbrales Dinámicos por Parcela
DESCRIPCIÓN: Ajustar umbrales según estación/mes, cultivo y hanegadas.
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: avisosriego.py, database/models.py, config.json

IMPLEMENTACIÓN SUGERIDA:

# Nueva tabla en la base de datos
CREATE TABLE umbrales_dinamicos (
    id INTEGER PRIMARY KEY,
    partida TEXT NOT NULL,
    mes INTEGER NOT NULL,
    umbral_factor REAL DEFAULT 3.0,
    tipo_cultivo TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(partida, mes)
);

# Nueva tabla para histórico de anomalías
CREATE TABLE historico_anomalias (
    id INTEGER PRIMARY KEY,
    partida TEXT NOT NULL,
    fecha DATETIME NOT NULL,
    valor_riego REAL,
    media_semana REAL,
    umbral REAL,
    severidad TEXT,  -- 'bajo', 'medio', 'alto'
    accion_tomada TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# En avisosriego.py - Versión mejorada
def detectar_riegos_anormales_inteligentes(umbral_dinamico=True):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    hoy = datetime.now()
    hoy_str = hoy.strftime('%Y-%m-%d')
    mes_actual = hoy.month
    
    cursor.execute("SELECT DISTINCT partida FROM datos_riego")
    partidas = [row[0] for row in cursor.fetchall()]
    
    avisos = []
    
    for partida in partidas:
        # Obtener umbral dinámico si está habilitado
        if umbral_dinamico:
            cursor.execute("""
                SELECT umbral_factor FROM umbrales_dinamicos 
                WHERE partida = ? AND mes = ?
            """, (partida, mes_actual))
            resultado = cursor.fetchone()
            umbral_factor = resultado[0] if resultado else 3.0
        else:
            umbral_factor = 3.0
        
        # Obtener datos de la última semana
        inicio_semana = hoy - timedelta(days=7)
        inicio_str = inicio_semana.strftime('%Y-%m-%d 00:00:00')
        fin_str = hoy.strftime('%Y-%m-%d 0:00:00')
        
        cursor.execute("""
            SELECT valor FROM datos_riego
            WHERE partida = ? AND fecha >= ? AND fecha < ? AND valor > 0
        """, (partida, inicio_str, fin_str))
        valores_semana = [row[0] for row in cursor.fetchall()]
        
        if not valores_semana:
            continue
        
        media_semana = sum(valores_semana) / len(valores_semana)
        umbral = media_semana * umbral_factor
        
        # Datos de hoy
        cursor.execute("""
            SELECT valor, fecha FROM datos_riego
            WHERE partida = ? AND DATE(fecha) = ?
        """, (partida, hoy_str))
        datos_hoy = cursor.fetchall()
        
        for valor, fecha in datos_hoy:
            if valor > umbral:
                # Calcular severidad
                desviacion_pct = ((valor - media_semana) / media_semana) * 100
                if desviacion_pct > 150:
                    severidad = 'alto'
                elif desviacion_pct > 100:
                    severidad = 'medio'
                else:
                    severidad = 'bajo'
                
                aviso = {
                    'partida': partida,
                    'fecha': fecha,
                    'valor': valor,
                    'media': media_semana,
                    'severidad': severidad,
                    'desviacion_pct': desviacion_pct
                }
                avisos.append(aviso)
                
                # Guardar en histórico
                cursor.execute("""
                    INSERT INTO historico_anomalias 
                    (partida, fecha, valor_riego, media_semana, umbral, severidad)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (partida, fecha, valor, media_semana, umbral, severidad))
    
    conn.commit()
    conn.close()
    return avisos

def obtener_historico_anomalias(partida=None, dias=30):
    # Obtener histórico de anomalías pasadas
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    if partida:
        query = """
            SELECT * FROM historico_anomalias 
            WHERE partida = ? AND created_at >= ?
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=[partida, fecha_limite])
    else:
        query = """
            SELECT * FROM historico_anomalias 
            WHERE created_at >= ?
            ORDER BY created_at DESC
        """
        df = pd.read_sql_query(query, conn, params=[fecha_limite])
    
    conn.close()
    return df
"""

# ==============================================================================
# 3. REPORTES DETALLADOS
# ==============================================================================
"""
MEJORA: Reportes Comparativos y de Eficiencia
DESCRIPCIÓN: Reportes detallados con desviación %, eficiencia, predicciones
PRIORIDAD: Alta (corto plazo)
MÓDULOS AFECTADOS: riegosemanal.py, app.py, requirements.txt (agregar reportlab, openpyxl)

IMPLEMENTACIÓN SUGERIDA:

# En riegosemanal.py - Nuevas funciones
def generar_reporte_comparativo(fecha_inicio=None, fecha_fin=None):
    if not fecha_inicio:
        fecha_inicio = datetime.now().replace(day=1)
    if not fecha_fin:
        fecha_fin = datetime.now()
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    # Consumo real en el período
    query = """
        SELECT partida, SUM(valor) as consumo_total
        FROM datos_riego
        WHERE fecha BETWEEN ? AND ? AND valor > 0
        GROUP BY partida
    """
    consumo_real = pd.read_sql_query(query, conn, 
                                      params=[fecha_inicio.strftime('%Y-%m-%d 00:00:00'),
                                             fecha_fin.strftime('%Y-%m-%d 23:59:59')])
    
    # Obtener hanegadas de cada parcela
    counters = pd.read_sql_query("SELECT partida, hanegadas FROM counters", conn)
    
    # Unir datos
    reporte = consumo_real.merge(counters, on='partida')
    
    # Calcular recomendación (asumiendo 4 m³/hanegada/semana)
    dias_periodo = (fecha_fin - fecha_inicio).days + 1
    semanas = dias_periodo / 7
    recomendacion_semanal = 4  # leer de config
    reporte['recomendacion_total'] = reporte['hanegadas'] * recomendacion_semanal * semanas
    
    # Desviación
    reporte['desviacion_m3'] = reporte['consumo_total'] - reporte['recomendacion_total']
    reporte['desviacion_pct'] = (reporte['desviacion_m3'] / reporte['recomendacion_total']) * 100
    
    # Eficiencia (litros/hectárea/día)
    reporte['eficiencia_l_ha_dia'] = (reporte['consumo_total'] * 1000) / (reporte['hanegadas'] * 10000 * dias_periodo)
    
    conn.close()
    return reporte

def exportar_reporte_pdf(reporte, fecha_inicio, fecha_fin):
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib import colors
    from datetime import datetime
    
    filename = f"reporte_riego_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    elements = []
    
    # Título
    styles = getSampleStyleSheet()
    titulo = Paragraph(f"Reporte de Riego {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}", 
                      styles['Heading1'])
    elements.append(titulo)
    elements.append(Spacer(1, 0.3*inch))
    
    # Tabla de datos
    data = [['Parcela', 'Consumo (m³)', 'Recomendación (m³)', 'Desviación (%)', 'Eficiencia (L/ha/día)']]
    for _, row in reporte.iterrows():
        data.append([
            row['partida'],
            f"{row['consumo_total']:.2f}",
            f"{row['recomendacion_total']:.2f}",
            f"{row['desviacion_pct']:.2f}%",
            f"{row['eficiencia_l_ha_dia']:.2f}"
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    return filename

def exportar_reporte_excel(reporte, fecha_inicio, fecha_fin):
    filename = f"reporte_riego_{fecha_inicio.strftime('%Y%m%d')}_{fecha_fin.strftime('%Y%m%d')}.xlsx"
    reporte.to_excel(filename, sheet_name='Reporte', index=False)
    return filename

def predecir_consumo_semanal(partida, dias=7):
    # Obtener últimos 30 días de datos
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    fecha_fin = datetime.now()
    fecha_inicio = fecha_fin - timedelta(days=30)
    
    query = """
        SELECT DATE(fecha) as fecha, SUM(valor) as consumo
        FROM datos_riego
        WHERE partida = ? AND fecha BETWEEN ? AND ? AND valor > 0
        GROUP BY DATE(fecha)
        ORDER BY fecha DESC
    """
    datos = pd.read_sql_query(query, conn,
                             params=[partida, 
                                    fecha_inicio.strftime('%Y-%m-%d 00:00:00'),
                                    fecha_fin.strftime('%Y-%m-%d 23:59:59')])
    conn.close()
    
    if len(datos) < 7:
        return None
    
    # Calcular promedio móvil simple (SMA)
    media = datos['consumo'].rolling(window=7).mean()
    prediccion = media.iloc[-1] * dias if media.iloc[-1] else 0
    
    return prediccion

# En app.py - Nueva ruta para exportar reportes
@app.route('/reportes')
@login_required
def reportes():
    fecha_inicio = request.args.get('fecha_inicio', 
                                    datetime.now().replace(day=1).strftime('%Y-%m-%d'))
    fecha_fin = request.args.get('fecha_fin', datetime.now().strftime('%Y-%m-%d'))
    
    reporte = generar_reporte_comparativo(
        datetime.strptime(fecha_inicio, '%Y-%m-%d'),
        datetime.strptime(fecha_fin, '%Y-%m-%d')
    )
    
    return render_template('reportes.html', 
                          reporte=reporte.to_html(classes='table striped'),
                          fecha_inicio=fecha_inicio,
                          fecha_fin=fecha_fin)

@app.route('/reportes/descargar/pdf')
@login_required
def descargar_reporte_pdf():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    reporte = generar_reporte_comparativo(fecha_inicio, fecha_fin)
    filename = exportar_reporte_pdf(reporte, fecha_inicio, fecha_fin)
    
    return send_file(filename, as_attachment=True)

@app.route('/reportes/descargar/excel')
@login_required
def descargar_reporte_excel():
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    
    reporte = generar_reporte_comparativo(fecha_inicio, fecha_fin)
    filename = exportar_reporte_excel(reporte, fecha_inicio, fecha_fin)
    
    return send_file(filename, as_attachment=True)
"""

# ==============================================================================
# 4. API REST
# ==============================================================================
"""
MEJORA: API REST con Swagger
DESCRIPCIÓN: Endpoints REST para integración con sistemas externos
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: app.py, requirements.txt (agregar flask-restx, flask-cors)

IMPLEMENTACIÓN SUGERIDA:

# Instalar dependencias
pip install flask-restx flask-cors

# En app.py - Crear API
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS

CORS(app)
api = Api(app, version='1.0', title='API Riego',
          description='API para acceso a datos de riego')

ns = api.namespace('api/v1', description='Operaciones de riego')

# Modelos para Swagger
datos_riego_model = api.model('DatosRiego', {
    'partida': fields.String(required=True),
    'fecha': fields.DateTime(required=True),
    'valor': fields.Float(required=True)
})

@ns.route('/datos/<string:partida>')
class DatosRiegoAPI(Resource):
    @ns.doc('get_datos_riego')
    @ns.param('dias', 'Número de días a recuperar', type=int, default=7)
    def get(self, partida, dias=7):
        '''Obtener datos de riego de una parcela'''
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        
        fecha_inicio = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d 00:00:00')
        fecha_fin = datetime.now().strftime('%Y-%m-%d 23:59:59')
        
        query = """
            SELECT partida, fecha, valor 
            FROM datos_riego
            WHERE partida = ? AND fecha BETWEEN ? AND ?
            ORDER BY fecha DESC
        """
        datos = pd.read_sql_query(query, conn, params=[partida, fecha_inicio, fecha_fin])
        conn.close()
        
        return {'datos': datos.to_dict('records'), 'total': len(datos)}, 200

@ns.route('/consumo/periodo')
class ConsumoPeriodoAPI(Resource):
    @ns.doc('get_consumo_periodo')
    @ns.param('fecha_inicio', 'Fecha inicio (YYYY-MM-DD)', type=str)
    @ns.param('fecha_fin', 'Fecha fin (YYYY-MM-DD)', type=str)
    def get(self):
        '''Obtener consumo total en un período'''
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        
        consumo = obtener_consumo_periodo(
            datetime.strptime(fecha_inicio, '%Y-%m-%d'),
            datetime.strptime(fecha_fin, '%Y-%m-%d')
        )
        
        return {'consumo_total': consumo, 'unidad': 'm³'}, 200

@ns.route('/avisos')
class AvisosAPI(Resource):
    @ns.doc('get_avisos')
    def get(self):
        '''Obtener avisos de riego anormal'''
        avisos = detectar_riegos_anormales_inteligentes()
        return {'avisos': avisos, 'total': len(avisos)}, 200

@ns.route('/prediccion/<string:partida>')
class PrediccionAPI(Resource):
    @ns.doc('get_prediccion')
    @ns.param('dias', 'Días a predecir', type=int, default=7)
    def get(self, partida, dias=7):
        '''Predecir consumo de riego'''
        prediccion = predecir_consumo_semanal(partida, dias)
        
        return {
            'partida': partida,
            'prediccion_m3': prediccion,
            'dias': dias,
            'confiabilidad': 'media' if prediccion else 'baja'
        }, 200
"""

# ==============================================================================
# 5. AUTENTICACIÓN ROBUSTA
# ==============================================================================
"""
MEJORA: Sistema de Autenticación Mejorado
DESCRIPCIÓN: Reemplazar SimpleLogin por JWT + Flask-SQLAlchemy
PRIORIDAD: Media-Alta (mediano plazo)
MÓDULOS AFECTADOS: app.py, config.py, database/models.py, requirements.txt

IMPLEMENTACIÓN SUGERIDA:

# Instalar dependencias
pip install Flask-SQLAlchemy Flask-JWT-Extended PyJWT

# En database/models.py - Extender modelos
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    inicial = db.Column(db.String(10), nullable=False)
    rol = db.Column(db.String(20), default='usuario')  # 'admin', 'supervisor', 'usuario'
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'name': self.name,
            'rol': self.rol,
            'inicial': self.inicial
        }

class AuditoriaLog(db.Model):
    __tablename__ = 'auditoria_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    accion = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tabla_afectada = db.Column(db.String(50))
    registro_id = db.Column(db.Integer)
    cambios_previos = db.Column(db.JSON)
    cambios_nuevos = db.Column(db.JSON)
    ip_address = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# En app.py - Configurar JWT
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'tu-clave-secreta-muy-segura')
jwt = JWTManager(app)

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(user=data.get('username')).first()
    
    if not user or not user.check_password(data.get('password')):
        return {'error': 'Credenciales inválidas'}, 401
    
    if not user.activo:
        return {'error': 'Usuario desactivado'}, 403
    
    access_token = create_access_token(identity=user.id)
    
    # Registrar login en auditoría
    registrar_auditoria(user.id, 'LOGIN', 'Inicio de sesión exitoso')
    
    return {
        'access_token': access_token,
        'user': user.to_dict()
    }, 200

@app.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    registrar_auditoria(user_id, 'LOGOUT', 'Cierre de sesión')
    return {'mensaje': 'Sesión cerrada'}, 200

def registrar_auditoria(usuario_id, accion, descripcion, tabla=None, 
                       registro_id=None, cambios_previos=None, cambios_nuevos=None):
    log = AuditoriaLog(
        usuario_id=usuario_id,
        accion=accion,
        descripcion=descripcion,
        tabla_afectada=tabla,
        registro_id=registro_id,
        cambios_previos=cambios_previos,
        cambios_nuevos=cambios_nuevos,
        ip_address=request.remote_addr
    )
    db.session.add(log)
    db.session.commit()

# Roles y permisos
def requiere_rol(*roles):
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if user.rol not in roles:
                registrar_auditoria(user_id, 'ACCESO_DENEGADO', 
                                   f'Intento de acceso a {request.path}')
                return {'error': 'Acceso denegado'}, 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

@app.route('/admin/usuarios')
@requiere_rol('admin')
def listar_usuarios():
    usuarios = User.query.all()
    return render_template('admin/usuarios.html', usuarios=usuarios)
"""

# ==============================================================================
# 6. NOTIFICACIONES MEJORADAS
# ==============================================================================
"""
MEJORA: Sistema de Notificaciones Multicanal
DESCRIPCIÓN: Telegram, email, SMS con preferencias de usuario
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: telegramutils.py, requirements.txt (agregar python-telegram-bot, yagmail)

IMPLEMENTACIÓN SUGERIDA:

# Nueva tabla para canales de notificación
CREATE TABLE canales_notificacion (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER NOT NULL,
    tipo_canal TEXT NOT NULL,  -- 'telegram', 'email', 'sms'
    valor TEXT NOT NULL,  -- token, email, teléfono
    activo BOOLEAN DEFAULT 1,
    horario_silencio_inicio TIME,  -- ej: 22:00
    horario_silencio_fin TIME,     -- ej: 08:00
    frecuencia TEXT DEFAULT 'inmediato',  -- 'inmediato', 'diario', 'semanal'
    FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE plantillas_notificacion (
    id INTEGER PRIMARY KEY,
    tipo_evento TEXT NOT NULL,  -- 'riego_anormal', 'reporte_diario', 'reporte_semanal'
    canal TEXT NOT NULL,
    asunto TEXT,
    cuerpo TEXT,
    variables TEXT  -- JSON con variables disponibles
);

# En telegramutils.py - Sistema mejorado
class NotificadorMulticanal:
    def __init__(self):
        self.db_path = get_db_path()
    
    def enviar_notificacion(self, usuario_id, tipo_evento, datos):
        '''Enviar notificación por todos los canales configurados del usuario'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Obtener canales activos del usuario
        cursor.execute("""
            SELECT tipo_canal, valor FROM canales_notificacion
            WHERE usuario_id = ? AND activo = 1
        """, (usuario_id,))
        canales = cursor.fetchall()
        
        # Obtener plantilla del evento
        cursor.execute("""
            SELECT cuerpo, asunto FROM plantillas_notificacion
            WHERE tipo_evento = ?
        """, (tipo_evento,))
        plantilla_row = cursor.fetchone()
        
        conn.close()
        
        if not plantilla_row:
            return False
        
        asunto, cuerpo = plantilla_row
        
        # Enviar por cada canal
        resultados = []
        for tipo_canal, valor in canales:
            if tipo_canal == 'telegram':
                resultado = self.enviar_telegram(valor, cuerpo)
            elif tipo_canal == 'email':
                resultado = self.enviar_email(valor, asunto, cuerpo)
            elif tipo_canal == 'sms':
                resultado = self.enviar_sms(valor, cuerpo)
            
            resultados.append(resultado)
        
        return all(resultados)
    
    def enviar_telegram(self, chat_id, mensaje):
        token = os.environ.get('TELEGRAM_TOKEN')
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        try:
            response = requests.post(url, data={
                'chat_id': chat_id,
                'text': mensaje,
                'parse_mode': 'Markdown'
            }, timeout=10)
            return response.ok
        except Exception as e:
            print(f"Error enviando Telegram: {e}")
            return False
    
    def enviar_email(self, email, asunto, cuerpo):
        try:
            yag = yagmail.SMTP(
                os.environ.get('EMAIL_USER'),
                os.environ.get('EMAIL_PASSWORD')
            )
            yag.send(to=email, subject=asunto, contents=cuerpo)
            return True
        except Exception as e:
            print(f"Error enviando email: {e}")
            return False
    
    def enviar_sms(self, telefono, mensaje):
        # Integrar con Twilio o similar
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(to=telefono, from_='+...', body=mensaje)
        # return message.sid is not None
        pass

# Uso
notificador = NotificadorMulticanal()
notificador.enviar_notificacion(usuario_id=1, tipo_evento='riego_anormal', 
                               datos={'partida': 'P001', 'valor': 50})
"""

# ==============================================================================
# 7. BASE DE DATOS OPTIMIZADA
# ==============================================================================
"""
MEJORA: Optimización de Base de Datos
DESCRIPCIÓN: Índices, particionamiento, caché, archivado de datos
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: database/models.py, database/create_db.py

IMPLEMENTACIÓN SUGERIDA:

# Crear índices para mejorar rendimiento
CREATE INDEX idx_datos_riego_partida ON datos_riego(partida);
CREATE INDEX idx_datos_riego_fecha ON datos_riego(fecha);
CREATE INDEX idx_datos_riego_partida_fecha ON datos_riego(partida, fecha);
CREATE INDEX idx_auditoria_usuario ON auditoria_logs(usuario_id);
CREATE INDEX idx_auditoria_timestamp ON auditoria_logs(timestamp);

# Particionamiento por mes (en databases más avanzadas)
# Para SQLite, implementar archivado manual de datos antiguos

def archivar_datos_antiguos(dias=365):
    '''Archivar datos más antiguos que dias'''
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    fecha_limite = (datetime.now() - timedelta(days=dias)).strftime('%Y-%m-%d')
    
    # Crear tabla de archivo si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS datos_riego_archivo (
            LIKE datos_riego
        )
    """)
    
    # Mover datos antiguos a archivo
    cursor.execute("""
        INSERT INTO datos_riego_archivo
        SELECT * FROM datos_riego
        WHERE fecha < ?
    """, (fecha_limite,))
    
    cursor.execute("DELETE FROM datos_riego WHERE fecha < ?", (fecha_limite,))
    conn.commit()
    conn.close()

# Implementar caché con Redis (opcional pero recomendado)
# pip install redis

from redis import Redis
import json

class CacheDatos:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = Redis(host=host, port=port, db=db, decode_responses=True)
        self.ttl = 3600  # 1 hora
    
    def get_consumo_semana(self, partida):
        key = f"consumo_semana:{partida}"
        cached = self.redis.get(key)
        if cached:
            return json.loads(cached)
        
        consumo = obtener_consumo_semana(partida)
        self.redis.setex(key, self.ttl, json.dumps(consumo))
        return consumo
    
    def invalidar_consumo(self, partida):
        key = f"consumo_semana:{partida}"
        self.redis.delete(key)

cache = CacheDatos()
"""

# ==============================================================================
# 8. MANTENIMIENTO DE INFRAESTRUCTURA
# ==============================================================================
"""
MEJORA: Logging, Health Checks, Backups Automáticos
DESCRIPCIÓN: Sistema robusto de mantenimiento e monitoreo
PRIORIDAD: Alta (mediano plazo)
MÓDULOS AFECTADOS: app.py, requirements.txt, utils.py

IMPLEMENTACIÓN SUGERIDA:

# Instalar dependencias
pip install python-logging-loki schedule

# En config.py - Configurar logging
import logging
from logging.handlers import RotatingFileHandler
import os

def configurar_logging(app):
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/riego.log', maxBytes=10240000, backupCount=10)
    file_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Aplicación de riego iniciada')

# En utils.py - Funciones de salud
def health_check():
    '''Verificar estado del sistema'''
    checks = {
        'database': check_database(),
        'telegram_api': check_telegram_api(),
        'scraping_api': check_scraping_api(),
        'disk_space': check_disk_space(),
        'memory': check_memory()
    }
    
    all_healthy = all(checks.values())
    return {
        'status': 'healthy' if all_healthy else 'warning',
        'checks': checks
    }

def check_database():
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return True
    except:
        return False

def check_telegram_api():
    token = os.environ.get('TELEGRAM_TOKEN')
    try:
        response = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=5)
        return response.ok
    except:
        return False

def check_scraping_api():
    try:
        response = requests.get("https://tarragon.gootem.com", timeout=10)
        return response.status_code == 200
    except:
        return False

def check_disk_space():
    import shutil
    total, used, free = shutil.disk_usage("/")
    percent_used = (used / total) * 100
    return percent_used < 90

def check_memory():
    import psutil
    memory = psutil.virtual_memory()
    return memory.percent < 85

# En app.py - Rutas de health check
@app.route('/health')
def health():
    health_status = health_check()
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return health_status, status_code

# Backups automáticos
import shutil
import schedule

def hacer_backup():
    '''Crear backup de la base de datos'''
    db_path = get_db_path()
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'riego_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_path)
        app.logger.info(f"Backup realizado: {backup_path}")
        
        # Eliminar backups antiguos (> 30 días)
        for filename in os.listdir(backup_dir):
            filepath = os.path.join(backup_dir, filename)
            if os.path.getmtime(filepath) < time.time() - 30 * 86400:
                os.remove(filepath)
    except Exception as e:
        app.logger.error(f"Error en backup: {e}")

# Programar backups diarios
schedule.every().day.at("03:00").do(hacer_backup)

# En un thread separado en app.py
import threading

def ejecutar_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

scheduler_thread = threading.Thread(target=ejecutar_scheduler, daemon=True)
scheduler_thread.start()
"""

# ==============================================================================
# 9. INTERFAZ MEJORADA
# ==============================================================================
"""
MEJORA: UI/UX Moderna e Interactiva
DESCRIPCIÓN: Gráficos interactivos, tabla mejorada, responsive design, modo oscuro
PRIORIDAD: Alta (corto plazo)
MÓDULOS AFECTADOS: templates/, static/, requirements.txt (agregar flask-cors, jsonify)

IMPLEMENTACIÓN SUGERIDA:

# Instalar dependencias para gráficos interactivos
pip install plotly kaleido

# Reemplazar gráficos SVG estáticos con Plotly

# En plotpygal.py - Versión con Plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_interactive_riego(fechas, valores, parcela):
    '''Crear gráfico interactivo con Plotly'''
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=fechas,
        y=valores,
        name='Consumo de Riego',
        marker_color='rgba(55, 150, 200, 0.8)',
        hovertemplate='<b>%{x}</b><br>Consumo: %{y} m³<extra></extra>'
    ))
    
    # Añadir línea de tendencia
    z = np.polyfit(range(len(valores)), valores, 1)
    p = np.poly1d(z)
    tendencia = p(range(len(valores)))
    
    fig.add_trace(go.Scatter(
        x=fechas,
        y=tendencia,
        mode='lines',
        name='Tendencia',
        line=dict(color='red', dash='dash')
    ))
    
    fig.update_layout(
        title=f'Consumo de Riego - {parcela}',
        xaxis_title='Fecha',
        yaxis_title='m³',
        hovermode='x unified',
        template='plotly_white',
        height=400
    )
    
    return fig.to_html(div_id=f"chart_{parcela}")

def plot_comparativa_recomendacion(reporte):
    '''Comparativa real vs recomendado'''
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "bar"}, {"type": "pie"}]]
    )
    
    parcelas = reporte['partida'].tolist()
    
    fig.add_trace(
        go.Bar(x=parcelas, y=reporte['consumo_total'], name='Consumo Real',
               marker_color='lightblue'),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=parcelas, y=reporte['recomendacion_total'], name='Recomendación',
               marker_color='lightgreen'),
        row=1, col=1
    )
    
    desviaciones = reporte['desviacion_pct'].tolist()
    fig.add_trace(
        go.Pie(labels=parcelas, values=[abs(d) for d in desviaciones],
               name='Desviación %'),
        row=1, col=2
    )
    
    fig.update_layout(height=500, title_text="Análisis Consumo vs Recomendación")
    return fig.to_html()

# En templates/base.html - Estructura mejorada con Bootstrap 5
'''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Riego{% endblock %}</title>
    
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Plotly -->
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    
    <link rel="stylesheet" href="{{ url_for('static', filename='css/main.css') }}">
    {% block extra_css %}{% endblock %}
</head>
<body>
    {% include 'header.html' %}
    
    <main class="container-fluid py-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else 'success' }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
    
    {% include 'footer.html' %}
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
'''

# En templates/dashboard.html - Nuevo dashboard
'''
{% extends "base.html" %}

{% block title %}Dashboard - Riego{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-3">
        <div class="card bg-primary text-white">
            <div class="card-body">
                <h5 class="card-title">Consumo Hoy</h5>
                <p class="card-text display-6">{{ consumo_hoy }} m³</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card bg-info text-white">
            <div class="card-body">
                <h5 class="card-title">Consumo Semana</h5>
                <p class="card-text display-6">{{ consumo_semana }} m³</p>
                <span class="badge bg-{{ 'success' if desviacion >= 0 else 'warning' }}">
                    {{ desviacion|round(2) }}%
                </span>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card bg-success text-white">
            <div class="card-body">
                <h5 class="card-title">Consumo Mes</h5>
                <p class="card-text display-6">{{ consumo_mes }} m³</p>
            </div>
        </div>
    </div>
    
    <div class="col-md-3">
        <div class="card {% if alertas %}bg-danger{% else %}bg-secondary{% endif %} text-white">
            <div class="card-body">
                <h5 class="card-title">Alertas</h5>
                <p class="card-text display-6">{{ alertas|length }}</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5>Tendencia Últimos 30 Días</h5>
            </div>
            <div class="card-body">
                {{ tendencia_30d|safe }}
            </div>
        </div>
    </div>
    
    <div class="col-lg-6">
        <div class="card">
            <div class="card-header">
                <h5>Alertas Activas</h5>
            </div>
            <div class="card-body">
                {% if alertas %}
                    <div class="list-group">
                        {% for alerta in alertas %}
                            <div class="list-group-item {% if alerta.severidad == 'alto' %}list-group-item-danger{% elif alerta.severidad == 'medio' %}list-group-item-warning{% else %}list-group-item-info{% endif %}">
                                <h6 class="mb-1">{{ alerta.partida }}</h6>
                                <p class="mb-1">{{ alerta.fecha }}: {{ alerta.valor }} m³ (Desviación: {{ alerta.desviacion_pct|round(2) }}%)</p>
                                <small>Severidad: <span class="badge bg-secondary">{{ alerta.severidad }}</span></small>
                            </div>
                        {% endfor %}
                    </div>
                {% else %}
                    <p class="text-muted">No hay alertas activas</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Modo oscuro -->
<script>
    // Detectar preferencia del usuario
    if (localStorage.getItem('theme') === 'dark' || 
        window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }
    
    // Botón para cambiar tema
    document.getElementById('toggle-theme')?.addEventListener('click', function() {
        const theme = document.documentElement.getAttribute('data-bs-theme');
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
    });
</script>

{% endblock %}
'''

# En templates/riego.html - Tabla mejorada
'''
{% extends "base.html" %}

{% block title %}Riego Semanal - Riego{% endblock %}

{% block content %}
<div class="card">
    <div class="card-header d-flex justify-content-between">
        <h5>Datos de Riego Semanal</h5>
        <div>
            <a href="/reportes/descargar/pdf" class="btn btn-sm btn-danger">
                <i class="fas fa-file-pdf"></i> PDF
            </a>
            <a href="/reportes/descargar/excel" class="btn btn-sm btn-success">
                <i class="fas fa-file-excel"></i> Excel
            </a>
        </div>
    </div>
    <div class="card-body">
        <div class="table-responsive">
            <table class="table table-striped table-hover" id="tabla-riego">
                <thead class="table-dark">
                    <tr>
                        <th>Parcela</th>
                        <th>Lunes</th>
                        <th>Martes</th>
                        <th>Miércoles</th>
                        <th>Jueves</th>
                        <th>Viernes</th>
                        <th>Sábado</th>
                        <th>Domingo</th>
                        <th>Total Semana</th>
                    </tr>
                </thead>
                <tbody>
                    <!-- Datos se cargan dinámicamente -->
                </tbody>
            </table>
        </div>
    </div>
</div>

<script src="https://cdn.datatables.net/1.13.0/js/jquery.dataTables.min.js"></script>
<script>
    $(document).ready(function() {
        $('#tabla-riego').DataTable({
            "language": {
                "url": "//cdn.datatables.net/plug-ins/1.13.0/i18n/es-ES.json"
            },
            "columnDefs": [
                {
                    "render": function(data, type, row) {
                        return parseFloat(data).toFixed(2) + ' m³';
                    },
                    "targets": [1, 2, 3, 4, 5, 6, 7, 8]
                }
            ]
        });
    });
</script>
{% endblock %}
'''
"""

# ==============================================================================
# 10. VALIDACIÓN Y CALIDAD DE DATOS
# ==============================================================================
"""
MEJORA: Validación y Detección de Anomalías de Datos
DESCRIPCIÓN: Detectar datos inconsistentes, duplicados, saltos anormales
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: webscrapBD.py, avisosriego.py, utils.py

IMPLEMENTACIÓN SUGERIDA:

# En utils.py - Validadores de datos
class ValidadorDatos:
    @staticmethod
    def validar_valor_riego(valor, partida, fecha_anterior=None, valor_anterior=None):
        '''Validar que el valor de riego sea coherente'''
        
        errores = []
        
        # Validación 1: Valor positivo
        if valor < 0:
            errores.append(f"Valor negativo: {valor}")
        
        # Validación 2: No excedeR 1000 m³ en un día (valor máximo razonable)
        if valor > 1000:
            errores.append(f"Valor excepcional: {valor} m³")
        
        # Validación 3: Detectar saltos anormales (> 500% del valor anterior)
        if valor_anterior and valor_anterior > 0:
            variacion_pct = ((valor - valor_anterior) / valor_anterior) * 100
            if variacion_pct > 500:
                errores.append(f"Salto anormal: +{variacion_pct:.0f}%")
        
        return {
            'valido': len(errores) == 0,
            'errores': errores,
            'valor': valor,
            'partida': partida,
            'fecha': fecha_anterior
        }
    
    @staticmethod
    def detectar_duplicados(datos):
        '''Detectar registros duplicados'''
        duplicados = datos[datos.duplicated(subset=['partida', 'fecha'], keep=False)]
        return duplicados

    @staticmethod
    def detectar_datos_faltantes(datos, partida, fecha_inicio, fecha_fin):
        '''Detectar saltos en fechas (datos faltantes)'''
        fecha_rango = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
        datos_partida = datos[datos['partida'] == partida]
        fechas_existentes = pd.to_datetime(datos_partida['fecha'])
        
        fechas_faltantes = fecha_rango[~fecha_rango.isin(fechas_existentes)]
        return fechas_faltantes

# En webscrapBD.py - Usar validadores antes de insertar
def guardar_datos_validados(partida, fecha, valor):
    validacion = ValidadorDatos.validar_valor_riego(valor, partida)
    
    if not validacion['valido']:
        logging.warning(f"Datos inválidos: {validacion['errores']}")
        # Opción 1: No guardar
        # Opción 2: Guardar con marca de 'revisar'
        # Opción 3: Guardar pero registrar en tabla de anomalías
        
        return {
            'guardado': False,
            'razon': validacion['errores']
        }
    
    # Guardar normalmente
    guardar_en_bd(partida, fecha, valor)
    return {'guardado': True}

# Implementar reintento automático con exponential backoff
import time

def scraping_con_reintentos(url, max_reintentos=3, delay_base=2):
    '''Realizar scraping con reintentos automáticos'''
    for intento in range(max_reintentos):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            if intento < max_reintentos - 1:
                delay = delay_base * (2 ** intento)  # Exponential backoff
                logging.warning(f"Reintentando en {delay}s (intento {intento + 1}/{max_reintentos}): {e}")
                time.sleep(delay)
            else:
                logging.error(f"Scraping fallido después de {max_reintentos} intentos: {e}")
                raise
"""

# ==============================================================================
# 11. PROGRAMACIÓN FLEXIBLE
# ==============================================================================
"""
MEJORA: Programación Flexible con APScheduler o Celery
DESCRIPCIÓN: Ejecutar tareas en background según horario configurable
PRIORIDAD: Media (mediano plazo)
MÓDULOS AFECTADOS: app.py, requirements.txt

IMPLEMENTACIÓN SUGERIDA:

# Instalar APScheduler
pip install APScheduler

# En app.py - Configurar scheduler
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# Tareas programadas
def tarea_scraping_diario():
    '''Ejecutar scraping cada día a las 6:00 AM'''
    import webscrapBD
    try:
        webscrapBD.scraping_principal()
        app.logger.info("Scraping diario completado")
    except Exception as e:
        app.logger.error(f"Error en scraping diario: {e}")

def tarea_revisar_avisos():
    '''Revisar avisos cada hora'''
    from avisosriego import detectar_riegos_anormales_inteligentes
    try:
        avisos = detectar_riegos_anormales_inteligentes()
        if avisos:
            notificador.enviar_notificacion(tipo_evento='riego_anormal', datos={'avisos': avisos})
    except Exception as e:
        app.logger.error(f"Error revisando avisos: {e}")

def tarea_reporte_semanal():
    '''Enviar reporte semanal los domingos a las 20:00'''
    try:
        # Generar y enviar reporte
        pass
    except Exception as e:
        app.logger.error(f"Error en reporte semanal: {e}")

# Añadir tareas al scheduler
scheduler.add_job(
    tarea_scraping_diario,
    CronTrigger(hour=6, minute=0),
    id='scraping_diario',
    name='Scraping diario',
    replace_existing=True
)

scheduler.add_job(
    tarea_revisar_avisos,
    CronTrigger(minute='*/60'),  # Cada hora
    id='revisar_avisos',
    name='Revisar avisos',
    replace_existing=True
)

scheduler.add_job(
    tarea_reporte_semanal,
    CronTrigger(day_of_week=6, hour=20, minute=0),  # Domingo 20:00
    id='reporte_semanal',
    name='Reporte semanal',
    replace_existing=True
)

# Panel de administración para gestionar horarios
@app.route('/admin/tareas')
@requiere_rol('admin')
def gestionar_tareas():
    tareas = []
    for job in scheduler.get_jobs():
        tareas.append({
            'id': job.id,
            'nombre': job.name,
            'proxima_ejecucion': job.next_run_time,
            'disparador': str(job.trigger)
        })
    
    return render_template('admin/tareas.html', tareas=tareas)

@app.route('/admin/tareas/<tarea_id>/ejecutar')
@requiere_rol('admin')
def ejecutar_tarea(tarea_id):
    job = scheduler.get_job(tarea_id)
    if job:
        job.func()
        return {'status': 'ok', 'mensaje': f'Tarea {tarea_id} ejecutada'}
    return {'error': 'Tarea no encontrada'}, 404

# Iniciar scheduler
if not scheduler.running:
    scheduler.start()
"""

# ==============================================================================
# 12. EXPORTACIÓN DE DATOS
# ==============================================================================
"""
MEJORA: Exportación a Múltiples Formatos e Integración Externa
DESCRIPCIÓN: CSV, JSON, Excel, Google Sheets, Webhooks
PRIORIDAD: Baja (largo plazo)
MÓDULOS AFECTADOS: app.py, riegosemanal.py, requirements.txt

IMPLEMENTACIÓN SUGERIDA:

# Instalar dependencias
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client openpyxl

# Funciones de exportación básica (CSV, JSON, Excel ya en reportes)

# Integración con Google Sheets
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class IntegradorGoogleSheets:
    def __init__(self, token_path='token.pickle', credentials_path='credentials.json'):
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.service = self.autenticar()
    
    def autenticar(self):
        creds = None
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token_file:
                creds = pickle.load(token_file)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    ['https://www.googleapis.com/auth/spreadsheets']
                )
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token_file:
                pickle.dump(creds, token_file)
        
        return build('sheets', 'v4', credentials=creds)
    
    def actualizar_spreadsheet(self, spreadsheet_id, datos, rango='Sheet1!A1'):
        '''Actualizar un Google Sheet con datos'''
        values = [datos.columns.tolist()] + datos.values.tolist()
        
        body = {'values': values}
        self.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=rango,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()

# Webhooks para sistemas externos
class GestorWebhooks:
    def __init__(self):
        self.db_path = get_db_path()
    
    def registrar_webhook(self, evento, url, activo=True):
        '''Registrar un webhook para un evento'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO webhooks (evento, url, activo)
            VALUES (?, ?, ?)
        """, (evento, url, activo))
        
        conn.commit()
        conn.close()
    
    def disparar_webhooks(self, evento, datos):
        '''Enviar datos a todos los webhooks registrados'''
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT url FROM webhooks
            WHERE evento = ? AND activo = 1
        """, (evento,))
        
        urls = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        payload = {
            'evento': evento,
            'timestamp': datetime.now().isoformat(),
            'datos': datos
        }
        
        for url in urls:
            try:
                requests.post(url, json=payload, timeout=10)
            except Exception as e:
                app.logger.error(f"Error disparando webhook {url}: {e}")

# Uso en eventos importantes
gestor_webhooks = GestorWebhooks()

def guardar_riego_con_webhook(partida, fecha, valor):
    guardar_en_bd(partida, fecha, valor)
    
    # Disparar webhook
    gestor_webhooks.disparar_webhooks('riego_registrado', {
        'partida': partida,
        'fecha': fecha,
        'valor': valor
    })
"""

# ==============================================================================
# RESUMEN DE IMPLEMENTACIÓN
# ==============================================================================
"""
PRIORIDADES Y ESTIMACIÓN DE TIEMPO:

FASE 1 - CORTO PLAZO (1-2 meses) - IMPACTO RÁPIDO:
1. Dashboard mejorado con gráficos interactivos Plotly
2. Tabla interactiva con DataTables (ordenar, filtrar)
3. Reportes comparativos (real vs recomendación)
4. Logging centralizado
5. Health checks básicos

Tiempo estimado: 40-50 horas

FASE 2 - MEDIANO PLAZO (2-4 meses) - ROBUSTEZ:
1. Autenticación robusta con JWT
2. API REST con Swagger
3. Umbrales dinámicos
4. Notificaciones multicanal
5. Backups y archivado de datos
6. APScheduler para tareas programadas
7. Validación y detección de anomalías

Tiempo estimado: 60-80 horas

FASE 3 - LARGO PLAZO (4-6 meses) - ESCALA:
1. Optimización de BD (índices, caché Redis)
2. Particionamiento de datos
3. Integración Google Sheets
4. Webhooks para sistemas externos
5. Modo oscuro
6. Estadísticas avanzadas y ML básico

Tiempo estimado: 50-70 horas

TOTAL: Aproximadamente 150-200 horas de desarrollo

DEPENDENCIAS CLAVE:
- Bootstrap 5 (UI)
- Plotly (gráficos interactivos)
- APScheduler (tareas programadas)
- Flask-JWT-Extended (autenticación)
- pandas, numpy (análisis de datos)
- Redis (caché opcional pero recomendado)
"""

if __name__ == "__main__":
    print(__doc__)