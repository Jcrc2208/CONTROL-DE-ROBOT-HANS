import cv2
import numpy as np
import time
from CPS import CPSClient

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()

# Inicialización
if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión al robot")
cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

# Bandera para controlar el estado del gripper (evita saturar el puerto)
gripper_abierto = False

# --- PARÁMETROS DE FILTRADO Y CONTROL ---
GAIN = 0.05
GAIN_J6 = 0.08    # Ganancia para el sexto eje 
FACTOR_FLEX = 0.7 
DEAD_ZONE = 25  
AREA_SEGURIDAD = 25000

# Historial para suavizado
vel_history = []
HISTORY_SIZE = 8

def smooth_velocity(new_vel):
    vel_history.append(new_vel)
    if len(vel_history) > HISTORY_SIZE:
        vel_history.pop(0)
    return np.mean(vel_history, axis=0)

print(">>> SISTEMA BIOMIMÉTICO ESTABILIZADO Y GRIPPER ACTIVADOS.", flush=True)

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read() 
        if not ret: break
        
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        mask = cv2.inRange(hsv, np.array([40, 70, 70]), np.array([80, 255, 255]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        vel = [0.0] * 6
        status = "BUSCANDO..."

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)    
            if area > 800:
                if area > AREA_SEGURIDAD:
                    vel = [0.0] * 6
                    status = "ALERTA SEGURIDAD"
                else:
                    x, y, w, h = cv2.boundingRect(c)
                    cx, cy = x + w//2, y + h//2
                    
                    # Dibujo visual
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                    cv2.line(frame, (cx, 0), (cx, 240), (0, 255, 0), 1)
                    cv2.line(frame, (0, cy), (320, cy), (0, 255, 0), 1)
                    
                    err_x, err_y = cx - 160, cy - 120
                    
                    if abs(err_x) < DEAD_ZONE and abs(err_y) < DEAD_ZONE:
                        vel = [0.0] * 6
                        status = "CENTRADO - ABRIENDO..."
                        
                        # Acción Gripper: Solo abre si no ha sido abierto antes
                        if not gripper_abierto:
                            cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [2, 1000], [])
                            gripper_abierto = True
                    else:
                        # Reset de la bandera si sale del centro para permitir cierre posterior
                        gripper_abierto = False 
                        
                        # Cálculo de velocidades (Incluyendo  la libertad de los 6 ejes)
                        vel[0] = -err_x * (GAIN * 1.2)
                        vel[1] = -(err_y * GAIN)
                        vel[2] = -(vel[1] * FACTOR_FLEX)
                        vel[3] = -err_x * (GAIN * 0.8)
                        vel[4] = -(err_y * (GAIN * 0.8))
                        vel[5] = -err_x * GAIN_J6  # Ganancia para rotación muñeca

                        status = "TRACKING..."
        
        # --- FILTRO Y ENVÍO ---
        vel_smooth = smooth_velocity(vel).tolist()
        cps.HRIF_SpeedJ(0, 0, vel_smooth, 20.0, 0.1)
        # UI
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Tracking Pro", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break


finally:
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 20.0, 0.1)
    cps.HRIF_DisConnect(0)
    cap.release()
    cv2.destroyAllWindows()