import cv2
from ultralytics import YOLO

# 1. Ajustamos la ruta exacta basada en tu nueva organización de carpetas
# Usamos 'best.pt' apuntando directamente a la subcarpeta PiezaMetalica
path_modelo = r"C:\Users\polic\OneDrive\Escritorio\Trabajo\CONTROL-DE-ROBOT-HANS\PiezaMetalica\best.pt"
model = YOLO(path_modelo)

# 2. Inicializar la cámara web (Usa el Python 3.13 de tu entorno de trabajo)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara de la laptop.")
    exit()

print("¡Cámara activada con éxito con tu modelo de 50 epochs!")
print("Presiona la tecla 'q' enfocando la ventana del video para salir.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: No se pudo leer el cuadro de la cámara.")
        break

    # 3. Inferencia de YOLOv8 optimizada
    results = model(frame, stream=True)

    # Inicializamos frame_dibujado con el cuadro original por si no detecta nada
    frame_dibujado = frame

    # 4. Dibujar las cajas sobre el frame
    for r in results:
        frame_dibujado = r.plot()

    # 5. Mostrar la ventana con el video local
    cv2.imshow('Deteccion de Pieza Metalica - Cobot HANS', frame_dibujado)

    # 6. Salida limpia con la tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Ventana cerrada y recursos liberados con éxito.")