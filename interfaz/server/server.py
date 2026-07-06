from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash 
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone  # <-- Modificado para soportar zonas horarias (Python 3.13+)
from robot_manager import RobotHuayanManager

app = Flask(__name__)
CORS(app)  

# Desarrollo local (SQLite). Al pasar a producción, solo cambias esta URI por la de PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///robot_monitoreo.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
robot = RobotHuayanManager()

contador_lecturas = 0
FRECUENCIA_MUESTREO = 10  

# MODELOS DE LA BASE DE DATOS (SQLAlchemy)

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='User')  # 'Admin' o 'User'
    ultima_conexion = db.Column(db.DateTime, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # <-- Corregido deprecation

class HistorialCinematico(db.Model):
    __tablename__ = 'historial_cinematico'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # <-- Corregido deprecation
    # Ángulos articulares (J1 - J6)
    j1 = db.Column(db.Float)
    j2 = db.Column(db.Float)
    j3 = db.Column(db.Float)
    j4 = db.Column(db.Float)
    j5 = db.Column(db.Float)
    j6 = db.Column(db.Float)
    # Coordenadas cartesianas
    pos_x = db.Column(db.Float)
    pos_y = db.Column(db.Float)
    pos_z = db.Column(db.Float)
    rot_rx = db.Column(db.Float)
    rot_ry = db.Column(db.Float)
    rot_rz = db.Column(db.Float)

class EstadoTermicoElectrico(db.Model):
    __tablename__ = 'estado_termico_electrico'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc)) # <-- Corregido deprecation
    # Temperaturas por articulación (°C)
    temp_j1 = db.Column(db.Float)
    temp_j2 = db.Column(db.Float)
    temp_j3 = db.Column(db.Float)
    temp_j4 = db.Column(db.Float)
    temp_j5 = db.Column(db.Float)
    temp_j6 = db.Column(db.Float)
    # Corrientes por articulación (A)
    corriente_j1 = db.Column(db.Float)
    corriente_j2 = db.Column(db.Float)
    corriente_j3 = db.Column(db.Float)
    corriente_j4 = db.Column(db.Float)
    corriente_j5 = db.Column(db.Float)
    corriente_j6 = db.Column(db.Float)

# ENDPOINTS / RUTAS DEL SERVIDOR

# 1. Obtener Telemetría (Para el sondeo cíclico de la interfaz)
@app.route('/api/robot/telemetria', methods=['GET'])
def get_telemetria():
    global contador_lecturas
    paquete = robot.obtener_paquete_telemetria()
    
    # Control de muestreo para almacenamiento en BD
    contador_lecturas += 1
    if contador_lecturas >= FRECUENCIA_MUESTREO:
        contador_lecturas = 0  # Reiniciar contador
        
        try:
            timestamp_actual = datetime.now(timezone.utc) # <-- Corregido deprecation
            
            # Extraer y guardar datos cinemáticos si existen en el paquete
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
                
            # Extraer y guardar datos térmicos y eléctricos
            if "temperatura_articulaciones" in paquete and "corriente_articulaciones" in paquete:
                temps = paquete["temperatura_articulaciones"]
                corrientes = paquete["corriente_articulaciones"]
                
                nuevo_estado = EstadoTermicoElectrico(
                    timestamp=timestamp_actual,
                    temp_j1=temps[0], temp_j2=temps[1], temp_j3=temps[2], temp_j4=temps[3], temp_j5=temps[4], temp_j6=temps[5],
                    corriente_j1=corrientes[0], corriente_j2=corrientes[1], corriente_j3=corrientes[2], corriente_j4=corrientes[3], corriente_j5=corrientes[4], corriente_j6=corrientes[5]
                )
                db.session.add(nuevo_estado)

            # Confirmar los cambios en la base de datos SQLite
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            print(f"Error al escribir en la Base de Datos: {e}")
            
    return jsonify(paquete)

# 2. Registrar usuarios desde la Web
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
            nombre=data['nombre'],
            correo=data['correo'],
            password_hash=hash_password,
            rol=data['rol'] 
        )

        db.session.add(nuevo_usuario)
        db.session.commit() 

        return jsonify({"status": "success", "message": "Usuario creado correctamente"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500

# 3. Obtener todos los usuarios de la BD
@app.route('/api/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        usuarios_bd = Usuario.query.all()
        lista_usuarios = []
        for u in usuarios_bd:
            lista_usuarios.append({
                "id": u.id,
                "nombre": u.nombre,
                "correo": u.correo,
                "rol": u.rol,
                "ultima_conexion": u.ultima_conexion.strftime('%d/%m/%Y %H:%M') if u.ultima_conexion else "Sin conexión"
            })
            
        return jsonify({"status": "success", "usuarios": lista_usuarios}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 4. Control de Acceso (Login)
@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return jsonify({"status": "success"}), 200
        
    try:
        data = request.get_json()
        if not data or not data.get('correo') or not data.get('password'):
            return jsonify({"status": "error", "message": "Faltan correo o contraseña."}), 400

        usuario = Usuario.query.filter_by(correo=data['correo']).first()

        if usuario and check_password_hash(usuario.password_hash, data['password']):
            usuario.ultima_conexion = datetime.now(timezone.utc) # <-- Corregido deprecation
            db.session.commit()
            
            return jsonify({
                "status": "success",
                "nombre": usuario.nombre,
                "rol": usuario.rol  
            }), 200
        else:
            return jsonify({"status": "error", "message": "Credenciales inválidas."}), 401

    except Exception as e:
        db.session.rollback()  
        return jsonify({"status": "error", "message": str(e)}), 500

# 5. Iniciar Movimiento Manual (Long Jog)
@app.route('/api/robot/jog/start', methods=['POST'])
def start_jog():
    try:
        data = request.get_json()
        joint = int(data.get('joint', 0))
        direction_input = int(data.get('direction', 1)) # -1 o 1 desde la web
        state = int(data.get('state', 1))  
        # Mapeo binario correcto validado por el controlador (Ret: 0)
        # Si viene -1, enviamos 0. Si viene 1, enviamos 1.
        direction = 0 if direction_input == -1 else 1 
        
        print(f"Moviendo -> J{joint+1} | Dirección SDK: {direction} | Estado: {state}")

        resultado = robot.iniciar_long_jog(joint, direction, state)
        return jsonify({"status": "success", "result": resultado}), 200
    except Exception as e:
        print(f"Error al ejecutar HRIF_LongJogJ: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# 6. Detener Movimiento Manual
@app.route('/api/robot/jog/stop', methods=['POST'])
def stop_jog():
    try:
        resultado = robot.detener_movimiento()
        return jsonify({"status": "success", "result": resultado}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# 7. Configurar Velocidad Global (Override)
@app.route('/api/robot/speed', methods=['POST'])
def cambiar_velocidad():
    try:
        data = request.get_json()
        valor_velocidad = int(data.get('speed', 20)) # Por defecto 20%
        
        resultado = robot.configurar_velocidad(valor_velocidad)
        return jsonify({"status": "success", "result": resultado}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# =========================================================================
# ARRANQUE DE LA APLICACIÓN
# =========================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Base de datos y tablas inicializadas correctamente.")
        
    print("Servidor de Telemetría HTTP corriendo en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)