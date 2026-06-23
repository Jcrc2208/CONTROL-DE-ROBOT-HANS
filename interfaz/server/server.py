from flask import Flask, jsonify
from flask_cors import CORS
from robot_manager import RobotHuayanManager

app = Flask(__name__)
CORS(app)  # Permite peticiones desde tu frontend (HTML/JS)

robot = RobotHuayanManager()

# 1. Obtener Telemetría (Para el sondeo cíclico de la interfaz)
@app.route('/api/robot/telemetria', methods=['GET'])
def get_telemetria():
    paquete = robot.obtener_paquete_telemetria()
    return jsonify(paquete), 200

if __name__ == '__main__':
    print("Servidor de Telemetría HTTP corriendo en http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)