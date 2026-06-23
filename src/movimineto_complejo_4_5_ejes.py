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

print(">>> SISTEMA BIOMIMÉTICO 5-EJES ARMONIZADO ACTIVADO.", flush=True)

# Parámetros de control
GAIN = 0.05
FACTOR_FLEX = 0.7 
DEAD_ZONE = 10
AREA_SEGURIDAD = 25000

cap = cv2.VideoCapture(0)

try:
    while True:
        ret, frame = cap.read() 
        if not ret: break
        
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower_green = np.array([40, 70, 70])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5)))
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        vel = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if contours:
            c = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(c)
            
            if area > 800:
                if area > AREA_SEGURIDAD:
                    vel = [0.0] * 6
                    print("!!! ALERTA DE SEGURIDAD !!!", flush=True)
                else:
                    x, y, w, h = cv2.boundingRect(c)
                    cx, cy = x + w//2, y + h//2
                    err_x, err_y = cx - 160, cy - 120
                    
                    if abs(err_x) < DEAD_ZONE: err_x = 0
                    if abs(err_y) < DEAD_ZONE: err_y = 0
                    
                    # --- LÓGICA DE ARMONÍA (Sincronización Total) ---
                    vel[0] = -err_x * (GAIN * 1.2)
                    vel[1] = -(err_y * GAIN)
                    vel[2] = -(vel[1] * FACTOR_FLEX)
                    vel[3] = -err_x * (GAIN * 0.8)
                    vel[4] = -(err_y * (GAIN * 0.8))
                    
                    # Normalización para evitar saturación de ejes
                    max_v = np.max(np.abs(vel[:5]))
                    if max_v > 5.0:
                        vel = [v * (5.0 / max_v) for v in vel]
                    
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
                    cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

        cps.HRIF_SpeedJ(0, 0, vel, 40.0, 0.04)
        
        info = f"J1:{vel[0]:.1f} J2:{vel[1]:.1f} J3:{vel[2]:.1f} J4:{vel[3]:.1f} J5:{vel[4]:.1f}"
        cv2.putText(frame, info, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        cv2.imshow("Tracking", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 40.0, 0.1)
    cps.HRIF_DisConnect(0)
    cap.release()
    cv2.destroyAllWindows()