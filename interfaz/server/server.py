from flask import Flask, jsonify
from flask_cors import CORS
from robot_manager import RobotHuayanManager

app = Flask(__name__)
CORS(app)  # Permite peticiones desde tu frontend (HTML/JS)

# Inicializa el manejador del Cobot (los parámetros de red ahora son internos y fijos)
robot = RobotHuayanManager()

# 1. Obtener Telemetría (Para el sondeo cíclico de la interfaz)
@app.route('/api/robot/telemetria', methods=['GET'])
def get_telemetria():
    """
    Ruta que el frontend consulta periódicamente. 
    Devuelve el estado de conexión, estado actual de la app, 
    posiciones cartesianas y ángulos articulares en tiempo real.
    """
    paquete = robot.obtener_paquete_telemetria()
    return jsonify(paquete), 200

if __name__ == '__main__':
    print("Servidor de Telemetría HTTP corriendo en http://localhost:5000")
    # Ponemos debug=False para evitar hilos duplicados consultando el SDK al mismo tiempo
    app.run(host='0.0.0.0', port=5000, debug=False)