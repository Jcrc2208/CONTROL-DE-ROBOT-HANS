import cv2
import numpy as np
import time
from CPS import CPSClient   


#configuracion parametros 
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()








 #ORIENTACIÓN (Usamos la misma para mantener estabilidad)
ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 

def inicializar ():
 if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
 cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)


def ejecutar_gripper(valor):
    result = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [2, valor], result)
    time.sleep(1.0) 


def mover_y_esperar(coords):
    # Nota: usamos la coordenada de destino como orientación para evitar giros extraños
    cps.HRIF_WayPoint(0, 0, 0, coords, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
    cps.waitBlendingDone(0, 0)
    print(f"Llegó a destino: {coords}")

#secuencia pick and place inteligente 
inicializar()


#try:
   




#finally:
  #  cps.HRIF_DisConnect(0)
  #  print("Secuencia finalizada.")

