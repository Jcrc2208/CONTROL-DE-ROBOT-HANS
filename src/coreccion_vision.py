import cv2
import numpy as np
import socket
import json

# --- Configuración de comunicación ---
HOST = "127.0.0.1"   # IP del cobot o servidor
PORT = 5000          # Puerto de conexión

# Crear socket UNA sola vez y mantenerlo abierto
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

def send_coords(x, y):
    """Enviar coordenadas al cobot/servidor vía TCP/IP"""
    try:
        data = json.dumps({"x": x, "y": y})
        sock.sendall(data.encode())
    except Exception as e:
        print("Error al enviar coordenadas:", e)

def detect_object(frame):
    """Detectar la pieza filtrando por color"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # --- Rangos de color ---
    lower_blue = np.array([100, 150, 0])
    upper_blue = np.array([140, 255, 255])
    mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

    lower_red1 = np.array([0, 50, 50])
    upper_red1 = np.array([15, 255, 255])
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)

    lower_red2 = np.array([160, 50, 50])
    upper_red2 = np.array([180, 255, 255])
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)

    mask_red = mask_red1 | mask_red2

    lower_green = np.array([40, 70, 70])
    upper_green = np.array([80, 255, 255])
    mask_green = cv2.inRange(hsv, lower_green, upper_green)

    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([30, 255, 255])
    mask_yellow = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Gris metálico
    lower_gray = np.array([0, 0, 50])
    upper_gray = np.array([180, 50, 200])
    mask_gray = cv2.inRange(hsv, lower_gray, upper_gray)

    masks = {
        "azul": mask_blue,
        "rojo": mask_red,
        "verde": mask_green,
        "amarillo": mask_yellow,
        "gris metálico": mask_gray
    }

    areas = {color: cv2.countNonZero(mask) for color, mask in masks.items()}
    detected_color = max(areas, key=areas.get)
    chosen_mask = masks[detected_color]

    contours, _ = cv2.findContours(chosen_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        return x, y, w, h, chosen_mask, detected_color
    return None, None, None, None, chosen_mask, "ninguno"

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

    x, y, w, h, mask, color = detect_object(frame)
    if x is not None:
        cx, cy = x + w//2, y + h//2
        ancho_cm, alto_cm = pixels_to_cm(w, h)
        send_coords(cx, cy)

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
        cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
        cv2.putText(frame, f"Centro: ({cx},{cy}) {ancho_cm:.1f}x{alto_cm:.1f}cm Color: {color}",
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
            x, y, w, h, mask, color = detect_object(frame)
            if x is not None:
                cx, cy = x + w//2, y + h//2
                ancho_cm, alto_cm = pixels_to_cm(w, h)
                send_coords(cx, cy)

                cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)
                cv2.circle(frame, (cx,cy), 5, (0,0,255), -1)
                cv2.putText(frame, f"Centro: ({cx},{cy}) {ancho_cm:.1f}x{alto_cm:.1f}cm Color: {color}",
                            (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        frame_count += 1
        cv2.imshow("Tracking pieza", frame)
        cv2.imshow("Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    sock.close()
    cv2.destroyAllWindows()