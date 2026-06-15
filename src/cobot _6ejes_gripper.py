import cv2
import numpy as np
import time
from CPS import CPSClient
from enum import Enum, auto

# --- ESTRUCTURA DE ESTADOS ---
class State(Enum):
    BUSCANDO = auto()
    TRACKING = auto()
    CENTRADO = auto()
    SEGURIDAD = auto()
    RETORNANDO = auto()

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()

# Coordenadas exactas para el regreso
POS_HOME = [0.0, 0.0, -90.0, 0.0, 90.0, 0.0]

if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

# --- PARÁMETROS ---
GAIN = 0.05
GAIN_J6 = 0.08
FACTOR_FLEX = 0.7 
DEAD_ZONE = 25  
AREA_SEGURIDAD = 25000

vel_history = []
HISTORY_SIZE = 8
gripper_abierto = False
current_state = State.BUSCANDO
tiempo_ultima_deteccion = time.time()
TIEMPO_ESPERA_HOME = 5.0 

def smooth_velocity(new_vel):
    vel_history.append(new_vel)
    if len(vel_history) > HISTORY_SIZE: vel_history.pop(0)
    return np.mean(vel_history, axis=0)

def mover_a_home():
    print("-> Limpiando buffer y regresando a HOME...", flush=True)
    # 1. Parada de emergencia suave: enviamos cero velocidad para liberar el stream
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 20.0, 0.1)
    time.sleep(0.5) # Damos tiempo al controlador para procesar la parada
    
    # 2. Ejecutar movimiento absoluto
    cps.HRIF_WayPoint(0, 0, 0, POS_HOME, [45, 0, 45, 0, 45, 0], "TCP", "Base", 20, 50, 0, 1, 0, 0, 0, "0")
    cps.waitBlendingDone(0, 0)
    print("   Robot en posición de reposo exacta.", flush=True)

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([40, 70, 70]), np.array([80, 255, 255]))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        vel = [0.0] * 6
        
        # --- LÓGICA DE ESTADOS ---
        if not contours:
            if current_state != State.RETORNANDO and (time.time() - tiempo_ultima_deteccion > TIEMPO_ESPERA_HOME):
                current_state = State.RETORNANDO
                mover_a_home()
                current_state = State.BUSCANDO
            else:
                current_state = State.BUSCANDO
        else:
            tiempo_ultima_deteccion = time.time()
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            
            if area > AREA_SEGURIDAD:
                current_state = State.SEGURIDAD
            else:
                x, y, w, h = cv2.boundingRect(c)
                cx, cy = x + w//2, y + h//2
                
                # Dibujo visual
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                
                err_x, err_y = cx - 160, cy - 120
                
                if abs(err_x) < DEAD_ZONE and abs(err_y) < DEAD_ZONE:
                    current_state = State.CENTRADO
                else:
                    current_state = State.TRACKING
                    vel[0] = -err_x * (GAIN * 1.2)
                    vel[1] = -(err_y * GAIN)
                    vel[2] = -(vel[1] * FACTOR_FLEX)
                    vel[3] = -err_x * (GAIN * 0.8)
                    vel[4] = -(err_y * (GAIN * 0.8))
                    vel[5] = -err_x * GAIN_J6

        # --- EJECUCIÓN Y ENVÍO ---
        if current_state == State.RETORNANDO:
            # Aquí el robot está ocupado con el WayPoint, el bucle no envía nada
            pass
        else:
            if current_state == State.CENTRADO:
                vel = [0.0] * 6
                if not gripper_abierto:
                    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [2, 1000], [])
                    gripper_abierto = True
            elif current_state != State.CENTRADO:
                gripper_abierto = False
                
            # Envío de velocidades para tracking
            vel_smooth = smooth_velocity(vel).tolist()
            cps.HRIF_SpeedJ(0, 0, vel_smooth, 20.0, 0.1)
        
        cv2.putText(frame, str(current_state.name), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Tracking Pro", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 20.0, 0.1)
    cps.HRIF_DisConnect(0)
    cap.release()
    cv2.destroyAllWindows()


    #eliminar filtros para elimiar latencia 
    #es posible que el filtro de suavizado esté introduciendo latencia, especialmente si el robot responde rápidamente a los comandos. Para eliminar esta latencia, puedes comentar o eliminar la función `smooth_velocity` y enviar las velocidades directamente sin promediarlas. Aquí te muestro cómo hacerlo:
    #tener en cuenta el factor de flexion.
    #por ultimo realizar pruebas en conjunto y ajustar codigo 


    """
    añadir maquina de estados y crear un algortimo de procesamiento multihilos 
    para mejorar la eficiencia del procesamiento de imagen y el control del robot. Esto permitirá que el robot responda más rápidamente a los cambios en la posición del objeto sin que el procesamiento de imagen bloquee el envío de comandos al robot.
    """ 