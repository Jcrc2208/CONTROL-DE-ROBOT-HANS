import cv2
from ultralytics import YOLO

path_modelo = r"C:\Users\polic\OneDrive\Escritorio\Trabajo\CONTROL-DE-ROBOT-HANS\PiezaMetalica\best.pt"
model = YOLO(path_modelo)

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

    results = model(frame, stream=True)

    frame_dibujado = frame

    for r in results:
        frame_dibujado = r.plot()

    cv2.imshow('Deteccion de Pieza Metalica - Cobot HANS', frame_dibujado)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Ventana cerrada y recursos liberados con éxito.")