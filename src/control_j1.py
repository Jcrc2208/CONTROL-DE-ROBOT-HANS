import cv2
import numpy as np
import time
from CPS import CPSClient

IP   = '192.168.10.11'  # Tu IP de red interna
PORT = 10003
cps = CPSClient()

# Inicialización del SDK
ret = cps.HRIF_Connect(0, IP, PORT)
if ret != 0: raise RuntimeError("Falla de conexión al SDK")
cps.HRIF_Connect2Box(0)
cps.HRIF_Electrify(0)
cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0)
cps.HRIF_SetOverride(0, 0, 15)  # Override al 15%

print(">>> TRACKING POR VELOCIDAD DIRECTA ACTIVADO. Usando HRIF_SpeedJ...", flush=True)

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
        
        omega = 0.0  # Velocidad por defecto: quieto

        if det is not None:
            x, y, w, h = det
            cx = x + w // 2
            error_centro = cx - 160
            
            # Zona muerta de 20 píxeles
            if abs(error_centro) > 20:
                # Kp para velocidad (un error de 100px dará 6 grados/segundo)
                Kp = -0.06
                omega = error_centro * Kp
                # Limitamos la velocidad máxima de giro por seguridad a 12 deg/s
                omega = max(-12.0, min(12.0, omega))
                
                print(f"[SPEED CONTROL] Velocidad J1 -> {omega:+.2f} deg/s | Error: {error_centro}", flush=True)

        # FUNCIÓN REAL DE VELOCIDAD DIRECTA SIN COORDENADAS:
        # HRIF_SpeedJ(boxID, rbtID, [J1, J2, J3, J4, J5, J6], aceleración, tiempo_de_ejecución)
        # Mandamos 'omega' a J1, y 0.0 a los demás motores.
        # Si omega es 0.0, el motor frena en seco inmediatamente.
        cps.HRIF_SpeedJ(0, 0, [float(omega), 0.0, 0.0, 0.0, 0.0, 0.0], 40.0, 0.04)
        
        # Sincronización estricta a 25Hz (cada 40ms) para encadenar las velocidades fluido
        elapsed = time.time() - start_time
        time.sleep(max(0.0, 0.04 - elapsed))

        # Dibujos rápidos en pantalla
        if det is not None:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.imshow("Tracking por Velocidad", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Al salir, mandamos velocidad 0 para asegurar que se detenga
    try: cps.HRIF_SpeedJ(0, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 40.0, 0.1)
    except: pass
    cap.release()
    cps.HRIF_DisConnect(0)
    cv2.destroyAllWindows()
    print(">>> Sistema cerrado de forma segura.", flush=True)