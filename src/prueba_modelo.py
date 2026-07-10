from CPS import CPSClient
import time
import cv2
import numpy as np

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
GID = 2
PIXEL_TO_MM = 0.15 
ALTURA_SEGURIDAD = 25 # Ajuste fino para el Z (distancia de seguridad)
ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 

# Puntos de la ruta (el robot se moverá entre ellos mediante pasos)
PUNTOS_SCANEO = [
    [416.541, -253.515, 211.407, 178.774, -0.060, 171.814],
    [430.906, 172.157, 185.532, 178.596, 2.214, -139.280]
]

def inicializar():
    global cps
    if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
    cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
    cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

def ejecutar_gripper(valor):
    res = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [GID, valor], res)
    time.sleep(1.0)

def escaneo_y_pick():
    cap = cv2.VideoCapture(0)
    print("Iniciando escaneo inteligente...")
    
    # Bucle infinito de patrullaje
    while True:
        for i in range(len(PUNTOS_SCANEO)):
            inicio = PUNTOS_SCANEO[i]
            fin = PUNTOS_SCANEO[(i + 1) % len(PUNTOS_SCANEO)]
            
            # Dividimos la distancia en 5 micro-movimientos para reaccionar rápido
            pasos = 5
            for p in range(pasos):
                # Calculamos el punto intermedio
                intermedio = [inicio[j] + (fin[j] - inicio[j]) * (p / pasos) for j in range(6)]
                
                cps.HRIF_WayPoint(0, 0, 0, intermedio, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
                cps.waitBlendingDone(0, 0)
                
                # Análisis de Visión
                ret, frame = cap.read()
                if not ret: continue
                
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                # Filtro verde estricto
                mask = cv2.inRange(hsv, np.array([45, 100, 50]), np.array([75, 255, 255]))
                M = cv2.moments(mask)
                
                if M["m00"] > 5000:
                    # Dibujar Rectángulo y Centroide
                    x, y, w, h = cv2.boundingRect(mask)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cx, cy = int(M["m10"]/(M["m00"]+1e-5)), int(M["m01"]/(M["m00"]+1e-5))
                    cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)
                    
                    cv2.imshow("Vision - Deteccion", frame)
                    cv2.waitKey(500)
                    
                    # --- SECUENCIA DE PICK ---
                    offset_x = (cx - 320) * PIXEL_TO_MM
                    offset_y = (cy - 240) * PIXEL_TO_MM
                    
                    # Target de corrección
                    target = [intermedio[0] + offset_x, intermedio[1] + offset_y, intermedio[2], 178.7, -0.06, 171.8]
                    cps.HRIF_WayPoint(0, 0, 0, target, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
                    cps.waitBlendingDone(0, 0)
                    
                    # Bajada con parámetro de seguridad
                    target[2] -= ALTURA_SEGURIDAD
                    cps.HRIF_WayPoint(0, 0, 0, target, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
                    
                    ejecutar_gripper(0)
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                
                cv2.imshow("Vision - Deteccion", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break

# --- SECUENCIA MAESTRA ---
inicializar()
escaneo_y_pick()
cps.HRIF_DisConnect(0)