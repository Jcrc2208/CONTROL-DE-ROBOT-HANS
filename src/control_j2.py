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
cps.HRIF_SetOverride(0, 0, 15)  # Override al 15% por pura seguridad

print(">>> TRACKING BIDIMENSIONAL POR VELOCIDAD ACTIVADO. Controlando J1 + J2...", flush=True)

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
        
        # Velocidades por defecto: quieto en ambos ejes
        omega_j1 = 0.0  
        omega_j2 = 0.0  

        if det is not None:
            x, y, w, h = det
            cx = x + w // 2
            cy = y + h // 2
            
            # --- 1. CONTROL DE LA BASE (J1 - Horizontal) ---
            error_x = cx - 160
            if abs(error_x) > 20:  # Zona muerta horizontal
                Kp_x = -0.06       # Tu ganancia fina que ya jala chulo
                omega_j1 = error_x * Kp_x
                omega_j1 = max(-12.0, min(12.0, omega_j1)) # Límite de velocidad J1

            # --- 2. CONTROL DEL HOMBRO (J2 - Vertical) ---
            error_y = cy - 120     # Centro vertical en 120 (240 / 2)
            if abs(error_y) > 20:  # Zona muerta vertical
                # NOTA: El J2 carga peso, ponle una ganancia un poco más baja para empezar
                # OJO CON EL SIGNO: Si al bajar el objeto el robot sube, cambia este -0.04 a positivo (+0.04)
                Kp_y = -0.04       
                omega_j2 = error_y * Kp_y
                omega_j2 = max(-8.0, min(8.0, omega_j2)) # Límite de velocidad J2 más castigado por seguridad

            if abs(error_x) > 20 or abs(error_y) > 20:
                print(f"[SPEED 2D] J1: {omega_j1:+.2f} deg/s (ErrX: {error_x}) | J2: {omega_j2:+.2f} deg/s (ErrY: {error_y})", flush=True)

        # MANDAMOS LA MATRIZ DE VELOCIDAD CON LOS DOS EJES DINÁMICOS
        # Mandamos 'omega_j1' al motor 1, 'omega_j2' al motor 2, y ceros a los demás.
        cps.HRIF_SpeedJ(0, 0, [float(omega_j1), float(omega_j2), 0.0, 0.0, 0.0, 0.0], 40.0, 0.04)
        
        # Sincronización estricta a 25Hz (cada 40ms)
        elapsed = time.time() - start_time
        time.sleep(max(0.0, 0.04 - elapsed))

        # Dibujos rápidos en pantalla para monitoreo
        if det is not None:
            cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
            cv2.circle(frame, (cx, cy), 5, (0,0,255), -1)
            # Cruz de centro ideal en la pantalla
            cv2.line(frame, (160, 0), (160, 240), (255, 0, 0), 1)
            cv2.line(frame, (0, 120), (320, 120), (255, 0, 0), 1)

        cv2.imshow("Tracking 2D por Velocidad - J1 + J2", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # Al salir, mandamos velocidad cero a TODAS las juntas para frenar el monstruo en seco
    print("\n>>> Frenando robot de forma segura...", flush=True)
    try: cps.HRIF_SpeedJ(0, 0, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 40.0, 0.1)
    except: pass
    cap.release()
    cps.HRIF_DisConnect(0)
    cv2.destroyAllWindows()
    print(">>> Sistema cerrado de forma segura.", flush=True)