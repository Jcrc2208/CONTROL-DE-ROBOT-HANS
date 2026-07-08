from CPS import CPSClient
import time
import cv2
from ultralytics import YOLO

#----- configutación -----
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()

#-----importacion ruta de modelo preetrenado yolo---
path_modelo = r"C:\Users\polic\OneDrive\Escritorio\Trabajo\CONTROL-DE-ROBOT-HANS\PiezaMetalica\best.pt"
model = YOLO(path_modelo)
cap = cv2.VideoCapture(0)

#definicon de algroitmo de deteccion de objetos



