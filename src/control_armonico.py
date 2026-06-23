import cv2
import numpy as np
import time
from CPS import CPSClient

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()

# --- PARÁMETROS ---
GAIN = 0.05
FACTOR_FLEX = 0.7 
DEAD_ZONE = 25
AREA_SEGURIDAD = 25000
AREA_AGARRE = 15000
ALPHA = 0.3 # Filtro EMA: 0.1 (muy suave/lento) a 0.9 (rápido/ruidoso)

# Inicialización Robot
if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)
cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [2, 100], [])

# Variables de estado
vel_filtrada = np.array([0.0] * 6)

def aplicar_filtro_ema(vel_actual, vel_anterior):
    return (ALPHA * np.array(vel_actual)) + ((1 - ALPHA) * vel_anterior)

def controlar_gripper(accion):
    cmd = 1 if accion == "cerrar" else 2
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperControl', [cmd], [])

# --- LOOP PRINCIPAL ---
cap = cv2.VideoCapture(0)
estado = "BUSCANDO"

try:
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        # 1. VISIÓN Y TRACKING
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([40, 70, 70]), np.array([80, 255, 255]))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        vel_objetivo = [0.0] * 6
        
        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            cx, cy = x + w//2, y + h//2
            
            # --- Lógica de visualización (Manteniendo tu estilo) ---
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
            cv2.line(frame, (cx, 0), (cx, 240), (0, 255, 0), 1)
            cv2.line(frame, (0, cy), (320, cy), (0, 255, 0), 1)
            
            if area > AREA_SEGURIDAD:
                estado = "ALERTA SEGURIDAD"
            elif area > AREA_AGARRE:
                estado = "AGARRANDO"
                controlar_gripper("cerrar")
            else:
                err_x, err_y = cx - 160, cy - 120
                if abs(err_x) < DEAD_ZONE and abs(err_y) < DEAD_ZONE:
                    estado = "CENTRADO - STOP"
                else:
                    estado = "TRACKING..."
                    vel_objetivo[0] = -err_x * (GAIN * 1.2)
                    vel_objetivo[1] = -(err_y * GAIN)
                    vel_objetivo[2] = -(vel_objetivo[1] * FACTOR_FLEX)
                    vel_objetivo[3] = -err_x * (GAIN * 0.8)
                    vel_objetivo[4] = -(err_y * (GAIN * 0.8))
                    vel_objetivo[5] = -(vel_objetivo[4] * FACTOR_FLEX)
        else:
            estado = "BUSCANDO..."

        # 2. FILTRADO Y ACTUACIÓN
        vel_filtrada = aplicar_filtro_ema(vel_objetivo, vel_filtrada)
        
        if estado == "AGARRANDO":
            cps.HRIF_SpeedJ(0, 0, [0.0]*6, 20.0, 0.1)
        else:
            cps.HRIF_SpeedJ(0, 0, vel_filtrada.tolist(), 20.0, 0.1)
        
        cv2.putText(frame, estado, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        cv2.imshow("Tracking Pro", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 20.0, 0.1)
    cps.HRIF_DisConnect(0)
    cap.release()
    cv2.destroyAllWindows() 