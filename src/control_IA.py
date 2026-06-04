import cv2
import numpy as np
import socket
import json

# --- Configuración de comunicación ---
HOST =  "192.168.10.18"  # IP del cobot o servidor
PORT = 5000          # Puerto de conexión

# Crear socket UNA sola vez y mantenerlo abierto
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST,PORT))

def send_coords(x, y):
    """Enviar coordenadas al cobot/servidor vía TCP/IP"""
    try:
        data = json.dumps({"x": x, "y": y})
        sock.sendall(data.encode())
    except Exception as e:
        print("Error al enviar coordenadas:", e)

def detect_object(frame):
    """Detectar SOLO la pieza verde"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Rango de verde ---
    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    # Limpieza morfológica
    #s25pro 
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
    mask_green = cv2.morphologyEx(mask_green, cv2.MORPH_OPEN, kernel)

    # Buscar contornos
    contours, _ = cv2.findContours(mask_green, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        if cv2.contourArea(c) > 800:  # filtrar ruido
            x, y, w, h = cv2.boundingRect(c)
            return x, y, w, h, mask_green
    return None, None, None, None, mask_green

def pixels_to_cm(w_px, h_px, scale=0.05):
    """Convertir pixeles a cm (escala aproximada)"""
    return w_px * scale, h_px * scale

# --- Flag para elegir modo ---
USE_IMAGE = False  # True = imagen fija, False = video

if USE_IMAGE:
    frame = cv2.imread("modelos/modelo_pieza_prueba.jpeg")
    if frame is None:
        print("Error: no se pudo cargar la imagen")
        exit()

    x, y, w, h, mask = detect_object(frame)
    if x is not None:
        cx, cy = x + w//2, y + h//2
        ancho_cm, alto_cm = pixels_to_cm(w, h)
        send_coords(cx, cy)

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
        cv2.putText(frame, f"Centro: ({cx},{cy}) {ancho_cm:.1f}x{alto_cm:.1f}cm",
                    (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

    cv2.imshow("Imagen", frame)
    cv2.imshow("Mask", mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: no se pudo abrir la cámara.")
        exit()

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: no se pudo leer el frame.")
            break

        frame = cv2.resize(frame, (320,240))

        if frame_count % 2 == 0:
            x, y, w, h, mask = detect_object(frame)
            if x is not None:
                cx, cy = x + w//2, y + h//2
                ancho_cm, alto_cm = pixels_to_cm(w, h)
                send_coords(cx, cy)

                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
                cv2.putText(frame, f"Centro: ({cx},{cy}) {ancho_cm:.1f}x{alto_cm:.1f}cm",
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        frame_count += 1
        cv2.imshow("Tracking pieza verde", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    sock.close()
    cv2.destroyAllWindows()