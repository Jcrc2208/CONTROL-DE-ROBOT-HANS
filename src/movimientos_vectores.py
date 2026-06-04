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

print(">>> SISTEMA BIOMIMÉTICO 3-EJES ACTIVADO.", flush=True)


# Parámetros de control
K_Y = 0.05
K_Z = 0.05
FACTOR_FLEX = 0.7 

cap = cv2.VideoCapture(0)


# El bloque try-finally asegura que el robot se detenga y se desconecte correctamente al salir del programa, incluso si ocurre un error o se interrumpe la ejecución. Esto es crucial para
try:
    while True:
        ret, frame = cap.read() 
        if not ret: break
        
        frame = cv2.resize(frame, (320, 240))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        

        # MÁSCARA: AJUSTA ESTOS VALORES SI NO DETECTA TU PIEZA
        lower_green = np.array([40, 70, 70])
        upper_green = np.array([80, 255, 255])
        mask = cv2.inRange(hsv, lower_green, upper_green)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
      # Velocidades de articulaciones (J1 a J6)
        vel = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        if contours:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 800:
                x, y, w, h = cv2.boundingRect(c)
                cx, cy = x + w//2, y + h//2
                
                # Errores
                err_x = cx - 160
                err_y = cy - 120
                
                # --- LÓGICA DE MOVIMIENTO ---
                # J1: Base
                vel[0] = -err_x * 0.06
                
                # J2: Hombro (Sube/Baja)
                # Si err_y es negativo (sube), v2 es positivo (sube).
                vel[1] = -(err_y * K_Y)
            

                # J3: Codo (Compensación estilo Flex)
                # J3 hace lo contrario a J2 para mantener el estiramiento
                vel[2] = -(vel[1] * FACTOR_FLEX)
                

                # Visualización
                cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                print(f"[BIOMIMÉTICO] Velocidades -> J1:{vel[0]:.2f} deg/s | J2:{vel[1]:.2f} deg/s | J3:{vel[2]:.2f} deg/s", flush=True)
                 


        # Envío al robot
        cps.HRIF_SpeedJ(0, 0, vel, 40.0, 0.04)

        # Info en pantalla
        info = f"J1:{vel[0]:.2f} J2:{vel[1]:.2f} J3:{vel[2]:.2f}"
        cv2.putText(frame, info, (10, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        if vel[0] != 0.0 or vel[1] != 0.0 or vel[2] != 0.0: 
        #imprime la info de velocidades en la consola para debug y seguimiento, con flush=True para asegurar que se muestre inmediatamente
          print(f"[INFO] {info}", flush=True)

        cv2.imshow("Tracking", frame)
        cv2.imshow("Mascara", mask)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): break

# Al salir, el bloque finally se asegura de que el robot se detenga y se desconecte correctamente, incluso si ocurre un error o se interrumpe la ejecución
finally:
    cps.HRIF_SpeedJ(0, 0, [0.0]*6, 40.0, 0.1)
    cps.HRIF_DisConnect(0)
    cap.release()
    cv2.destroyAllWindows()