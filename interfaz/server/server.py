from flask import Flask, request, jsonify
from flask_cors import CORS
from robot_manager import RobotHuayanManager

app = Flask(__name__)
CORS(app)  #

robot = RobotHuayanManager()

@app.route('/api/robot/conectar', methods=['POST'])
def conectar():
    data = request.json or {}
    box_id = data.get('box_id', 0)
    rbt_id = data.get('rbt_id', 0)
    ip = data.get('ip', '192.168.10.11')  
    port = data.get('port', 10003)
    sampling_ms = data.get('sampling_ms', 100)
    
    robot.actualizar_configuracion(box_id, rbt_id, ip, port, sampling_ms)
    
    if robot.conectar_hardware():
        return jsonify({"status": "success", "message": "¡Conectado exitosamente al Cobot!"}), 200

# 2. Control de Servos (Servo ON / Servo OFF)
@app.route('/api/robot/servo', methods=['POST'])
def controlar_servo():
    data = request.json or {}
    encender = data.get('encender', True)  
    
    if robot.cambiar_estado_servo(encender):
        msg = "Servo ON ejecutado" if encender else "Servo OFF ejecutado"
        return jsonify({"status": "success", "message": msg}), 200
    return jsonify({"status": "error", "message": "El SDK rechazó el comando del servo"}), 500

# 3. Limpiar Alertas / Reset Error
@app.route('/api/robot/reset-error', methods=['POST'])
def reset_error():
    if robot.limpiar_alarmas():
        return jsonify({"status": "success", "message": "Alarmas limpiadas"}), 200
    return jsonify({"status": "error", "message": "No se pudieron limpiar las alarmas"}), 500

# 4. Detener Robot (HRIF_CancelMotion)
@app.route('/api/robot/detener', methods=['POST'])
def detener():
    if robot.detener_robot():
        return jsonify({"status": "success", "message": "Movimiento cancelado"}), 200
    return jsonify({"status": "error", "message": "No se pudo detener el robot"}), 500

# 5. Obtener Telemetría (Para el sondeo cíclico de la interfaz)
@app.route('/api/robot/telemetria', methods=['GET'])
def get_telemetria():
    paquete = robot.obtener_paquete_telemetria()
    return jsonify(paquete), 200

if __name__ == '__main__':
    print("Servidor de pruebas HTTP corriendo en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
    