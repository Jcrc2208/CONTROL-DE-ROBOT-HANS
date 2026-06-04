import cv2
import numpy as np
import time
from CPS import CPSClient

IP   = '192.168.10.11'
PORT = 10003
cps = CPSClient()

# Inicialización
ret = cps.HRIF_Connect(0, IP, PORT)
if ret != 0: raise RuntimeError("Falla de conexión al SDK")
cps.HRIF_Connect2Box(0)
cps.HRIF_Electrify(0)
cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0)
cps.HRIF_SetOverride(0, 0, 15)

print(">>> TRACKING 3D BALANCEADO Y ACOPLADO ACTIVADO...", flush=True)

def detect_object(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 800:
            return cv2.boundingRect(c), mask_green
    return None, mask_green

cap = cv2.VideoCapture(0)

try:
    while True:
        start_time = time.time()
        ret_cam, frame = cap.read()
        if not ret_cam: break

        frame = cv2.resize(frame, (320, 240))
        det, mask = detect_object(frame)
        
        omega_j1, omega_j2, omega_j3 = 0.0, 0.0, 0.0

        if det is not None:
            x, y, w, h = det
            cx, cy = x + w // 2, y + h // 2
            
            # 1. J1: BASE (Horizontal)
            error_x = cx - 160
            if abs(error_x) > 15:
                omega_j1 = max(-10.0, min(10.0, error_x * -0.06))

            # 2. J2: HOMBRO (Vertical) - Ganancia reducida para mayor control
            error_y = cy - 120
            if abs(error_y) > 10:
                omega_j2 = max(-8.0, min(8.0, error_y * -0.045))

            # 3. J3: CODO (Profundidad + Acoplamiento)
            # El acoplamiento ayuda a que el J3 compense el arco del J2
            ancho_objetivo = 60
            error_w = w - ancho_objetivo
            acoplamiento_j2 = (cy - 120) * 0.015 
            
            if abs(error_w) > 10 or abs(cy - 120) > 10:
                omega_j3 = max(-7.0, min(7.0, (error_w * 0.08) + acoplamiento_j2))

            print(f"[TRACKING 3D] J1:{omega_j1:+.1f} | J2:{omega_j2:+.1f} | J3:{omega_j3:+.1f}", flush=True)

        # Mando al robot
        cps.HRIF_SpeedJ(0, 0, [float(omega_j1), float(omega_j2), float(omega_j3), 0.0, 0.0, 0.0], 40.0, 0.04)
        
        elapsed = time.time() - start_time
        time.sleep(max(0.0, 0.04 - elapsed))

        # Visuals
        if det is not None:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)

        cv2.imshow("Tracking 3D - Acoplado", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

finally:
    cps.HRIF_SpeedJ(0, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 40.0, 0.1)
    cap.release()
    cps.HRIF_DisConnect(0)
    cv2.destroyAllWindows()