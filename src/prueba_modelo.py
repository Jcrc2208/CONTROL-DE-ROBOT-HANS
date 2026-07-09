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
ALTURA_SEGURIDAD = 20 # <--- ESTE ES TU PARÁMETRO DE AJUSTE (20 unidades = 1cm aprox)
ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 

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
    
    while True:
        for coords in PUNTOS_SCANEO:
            cps.HRIF_WayPoint(0, 0, 0, coords, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
            cps.waitBlendingDone(0, 0)
            
            for _ in range(15): # Observación en el punto
                ret, frame = cap.read()
                if not ret: continue
                
                hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                mask = cv2.inRange(hsv, np.array([35, 50, 50]), np.array([85, 255, 255]))
                M = cv2.moments(mask)
                
                if M["m00"] > 5000:
                    # DIBUJOS: Rectángulo y Centroide
                    x, y, w, h = cv2.boundingRect(mask)
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
                    cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)
                    
                    cv2.imshow("Vision - Deteccion", frame)
                    cv2.waitKey(500)
                    
                    # CÁLCULO Y MOVIMIENTO
                    offset_x = (cx - 320) * PIXEL_TO_MM
                    offset_y = (cy - 240) * PIXEL_TO_MM
                    
                    target = [coords[0] + offset_x, coords[1] + offset_y, coords[2], 178.7, -0.06, 171.8]
                    cps.HRIF_WayPoint(0, 0, 0, target, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
                    cps.waitBlendingDone(0, 0)
                    
                    # BAJADA CON PARÁMETRO DE SEGURIDAD
                    target[2] -= ALTURA_SEGURIDAD 
                    cps.HRIF_WayPoint(0, 0, 0, target, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
                    
                    ejecutar_gripper(0)
                    cap.release()
                    cv2.destroyAllWindows()
                    return True
                
                cv2.imshow("Vision - Deteccion", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'): break
    
    cap.release()
    cv2.destroyAllWindows()
    return False

# --- SECUENCIA MAESTRA ---
inicializar()
escaneo_y_pick()
cps.HRIF_DisConnect(0)