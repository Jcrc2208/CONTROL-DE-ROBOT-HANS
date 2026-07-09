from CPS import CPSClient
import time
import cv2

#from ultralytics import YOLO

#----- configutación -----
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
GID = 2


#cordendas definidas
SCANEO = [416.541, -253.515, 211.407,178.774,-0.060,171.814]
SCANEO_1 = [430.906, 172.157, 185.532, 178.596,2.214,-139.280]


ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 


#-----importacion ruta de modelo preetrenado yolo---
#path_modelo = r"C:\Users\polic\OneDrive\Escritorio\Trabajo\CONTROL-DE-ROBOT-HANS\PiezaMetalica\best.pt"
#model = YOLO(path_modelo)
#cap = cv2.VideoCapture(0)


#lo siguiente seria integran los algoritmos de inteligencia artificial para la detección de objetos y la planificación de trayectorias, pero por ahora se mantiene la secuencia básica de pick and place con el gripper.
def inicializar():
    if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
    cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
    cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

def escaneo(coords):
     cps.HRIF_WayPoint(0, 0, 0, coords, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
     cps.waitBlendingDone(0, 0)
     print(f"inicio: {coords}")
    

def ejecutar_gripper(valor):
    res = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [GID, valor], res)
    time.sleep(1.0) 

# --- SECUENCIA MAESTRA ---
inicializar()


try:
    #inicio de escaneo
    escaneo(SCANEO)
    ejecutar_gripper(1000)  # CERRAR
    escaneo(SCANEO_1)

   
finally:
    cps.HRIF_DisConnect(0)
    print("Secuencia finalizada.")