import os
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash 
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit  #Para el manejo de WebSockets en tiempo real
from datetime import datetime, timezone  
from robot_manager import RobotHuayanManager

app = Flask(__name__)
CORS(app)  

# Configuración de la base de datos
# Esto creará la base de datos en la carpeta de tu usuario de Windows, 100% fuera de tu proyecto
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.expanduser('~'), 'robot_monitoreo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# NUEVO: Inicialización de Flask-SocketIO. cors_allowed_origins="*" evita problemas de conexión desde tu interfaz
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
robot = RobotHuayanManager()

contador_lecturas = 0
FRECUENCIA_MUESTREO = 10  

# =========================================================================
# MODELOS DE LA BASE DE DATOS (SQLAlchemy)
# =========================================================================

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='User')  
    ultima_conexion = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class HistorialCinematico(db.Model):
    __tablename__ = 'historial_cinematico'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    j1 = db.Column(db.Float); j2 = db.Column(db.Float); j3 = db.Column(db.Float)
    j4 = db.Column(db.Float); j5 = db.Column(db.Float); j6 = db.Column(db.Float)
    pos_x = db.Column(db.Float); pos_y = db.Column(db.Float); pos_z = db.Column(db.Float)
    rot_rx = db.Column(db.Float); rot_ry = db.Column(db.Float); rot_rz = db.Column(db.Float)

class EstadoTermicoElectrico(db.Model):
    __tablename__ = 'estado_termico_electrico'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    temp_j1 = db.Column(db.Float); temp_j2 = db.Column(db.Float); temp_j3 = db.Column(db.Float)
    temp_j4 = db.Column(db.Float); temp_j5 = db.Column(db.Float); temp_j6 = db.Column(db.Float)
    corriente_j1 = db.Column(db.Float); corriente_j2 = db.Column(db.Float); corriente_j3 = db.Column(db.Float)
    corriente_j4 = db.Column(db.Float); corriente_j5 = db.Column(db.Float); corriente_j6 = db.Column(db.Float)

# =========================================================================
# TAREA EN SEGUNDO PLANO: EMISIÓN DE TELEMETRÍA Y ALMACENAMIENTO EN BD
# =========================================================================

def emitir_telemetria_continua():
    """ 
    Hilo asíncrono que corre en segundo plano. 
    Obtiene la telemetría del SDK y la escupe por WebSockets al cliente sin bloquear el servidor.
    """
    global contador_lecturas
    while True:
        try:
            # Obtener el paquete directamente desde el SDK
            paquete = robot.obtener_paquete_telemetria()
            
            if paquete:
                # Emitir a todos los clientes web conectados por el canal 'telemetria'
                socketio.emit('telemetria', paquete)
                
                # Manejo de la persistencia usando el contexto de la app para SQLAlchemy
                contador_lecturas += 1
                if contador_lecturas >= FRECUENCIA_MUESTREO:
                    contador_lecturas = 0
                    
                    with app.app_context():
                        try:
                            timestamp_actual = datetime.now(timezone.utc)
                            
                            if "angulos_articulares" in paquete and "posicion_cartesiana" in paquete:
                                angulos = paquete["angulos_articulares"]
                                cartesianas = paquete["posicion_cartesiana"]
                                nueva_cinematica = HistorialCinematico(
                                    timestamp=timestamp_actual,
                                    j1=angulos[0], j2=angulos[1], j3=angulos[2], j4=angulos[3], j5=angulos[4], j6=angulos[5],
                                    pos_x=cartesianas[0], pos_y=cartesianas[1], pos_z=cartesianas[2],
                                    rot_rx=cartesianas[3], rot_ry=cartesianas[4], rot_rz=cartesianas[5]
                                )
                                db.session.add(nueva_cinematica)
                                
                            if "temperatura_articulaciones" in paquete and "corriente_articulaciones" in paquete:
                                temps = paquete["temperatura_articulaciones"]
                                corrientes = paquete["corriente_articulaciones"]
                                nuevo_estado = EstadoTermicoElectrico(
                                    timestamp=timestamp_actual,
                                    temp_j1=temps[0], temp_j2=temps[1], temp_j3=temps[2], temp_j4=temps[3], temp_j5=temps[4], temp_j6=temps[5],
                                    corriente_j1=corrientes[0], corriente_j2=corrientes[1], corriente_j3=corrientes[2], corriente_j4=corrientes[3], corriente_j5=corrientes[4], corriente_j6=corrientes[5]
                                )
                                db.session.add(nuevo_estado)
                                
                            db.session.commit()
                        except Exception as ex:
                            db.session.rollback()
                            print(f"Error al escribir en la Base de Datos desde el hilo: {ex}")
                            
        except Exception as e:
            print(f"Error en el ciclo de telemetría: {e}")
            
        # Pausa del hilo: 100ms equivalen a 10 envíos por segundo (10Hz). 
        # Es ideal para fluidez visual en la interfaz sin saturar la red local.
        socketio.sleep(0.1) 

# =========================================================================
# ENDPOINTS HTTP TRADICIONALES (Para transacciones de datos)
# =========================================================================

@app.route('/api/usuarios', methods=['POST'])
def registrar_usuario():
    try:
        data = request.get_json()
        if not data or not data.get('nombre') or not data.get('correo') or not data.get('password'):
            return jsonify({"status": "error", "message": "Faltan datos obligatorios."}), 400
            
        correo_existe = Usuario.query.filter_by(correo=data['correo']).first()
        if correo_existe:
            return jsonify({"status": "error", "message": "El correo ya está registrado."}), 400

        hash_password = generate_password_hash(data['password'])
        nuevo_usuario = Usuario(
            nombre=data['nombre'], correo=data['correo'], password_hash=hash_password, rol=data['rol'] 
        )
        db.session.add(nuevo_usuario)
        db.session.commit() 
        return jsonify({"status": "success", "message": "Usuario creado correctamente"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        usuarios_bd = Usuario.query.all()
        lista_usuarios = [{
            "id": u.id, "nombre": u.nombre, "correo": u.correo, "rol": u.rol,
            "ultima_conexion": u.ultima_conexion.strftime('%d/%m/%Y %H:%M') if u.ultima_conexion else "Sin conexión"
        } for u in usuarios_bd]
        return jsonify({"status": "success", "usuarios": lista_usuarios}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def dar_de_baja_usuario(id):
    try:
        # Buscar el usuario por su ID único en SQLite
        usuario = Usuario.query.get(id)
        
        if not usuario:
            return jsonify({"status": "error", "message": "El usuario no existe."}), 404
            
        # Eliminar el registro de la base de datos
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({"status": "success", "message": "Usuario dado de baja correctamente."}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
    try:
        data = request.get_json()
        usuario = Usuario.query.filter_by(correo=data.get('correo')).first()
        
        # Validación de login exacta con minúsculas del rol para tu frontend
        if usuario and check_password_hash(usuario.password_hash, data.get('password')):
            usuario.ultima_conexion = datetime.now(timezone.utc)
            db.session.commit()
            return jsonify({"status": "success", "nombre": usuario.nombre, "rol": usuario.rol.lower()}), 200
        return jsonify({"status": "error", "message": "Credenciales inválidas."}), 401
    except Exception as e:
        db.session.rollback()  
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================================================================
# EVENTOS WEBSOCKET (Control en tiempo real del Cobot)
# =========================================================================
@socketio.on('jog_start')
def handle_jog_start(data):
    """ Escucha el evento para iniciar el movimiento del robot por WebSocket """
    try:
        joint = int(data.get('joint', 0))
        direction_input = int(data.get('direction', 1)) 
        state = int(data.get('state', 1))  
        
        direction = 0 if direction_input == -1 else 1 
        print(f"[WS] Moviendo -> J{joint+1} | Dirección: {direction} | Estado: {state}")

        resultado = robot.iniciar_long_jog(joint, direction, state)
        emit('jog_response', {"status": "success", "result": resultado})
    except Exception as e:
        print(f"Error WS jog_start: {e}")
        emit('jog_response', {"status": "error", "message": str(e)})

@socketio.on('jog_stop')
def handle_jog_stop():
    """ Escucha el evento para detener inmediatamente el robot por WebSocket """
    try:
        print("[WS] Deteniendo movimiento del cobot.")
        resultado = robot.detener_movimiento()
        emit('jog_response', {"status": "success", "result": resultado})
    except Exception as e:
        print(f"Error WS jog_stop: {e}")
        emit('jog_response', {"status": "error", "message": str(e)})

@socketio.on('change_speed')
def handle_change_speed(data):
    """ Escucha el evento para ajustar el Override global de velocidad por WebSocket """
    try:
        valor_velocidad = int(data.get('speed', 20))
        print(f"[WS] Configurando velocidad general a: {valor_velocidad}%")
        resultado = robot.configurar_velocidad(valor_velocidad)
        emit('speed_response', {"status": "success", "result": resultado})
    except Exception as e:
        print(f"Error WS change_speed: {e}")
        emit('speed_response', {"status": "error", "message": str(e)})


# =========================================================================
# ARRANQUE DE LA APLICACIÓN
# =========================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas inicializadas correctamente.")
        
        # PRECARGA DE USUARIOS POR DEFECTO (Admin y User)
        usuarios_defecto = [
            {"nombre": "Administrador", "correo": "admin@gmail.com", "password": "admin", "rol": "admin"},
            {"nombre": "Operador Común", "correo": "user@gmail.com", "password": "user", "rol": "user"}
        ]
        
        for u_data in usuarios_defecto:
            existe = Usuario.query.filter_by(correo=u_data["correo"]).first()
            if not existe:
                hash_pw = generate_password_hash(u_data["password"])
                nuevo_u = Usuario(
                    nombre=u_data["nombre"],
                    correo=u_data["correo"],
                    password_hash=hash_pw,
                    rol=u_data["rol"]
                )
                db.session.add(nuevo_u)
                print(f"Usuario por defecto creado: {u_data['correo']}")
        
        db.session.commit()
    
    # Iniciar la tarea de telemetría asíncrona en el fondo
    socketio.start_background_task(emitir_telemetria_continua)
        
    print("Servidor híbrido (HTTP + WebSockets) corriendo en http://0.0.0.0:5000")
    # IMPORTANTE: Cambiamos app.run() por socketio.run() para dar soporte al motor asíncrono
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)