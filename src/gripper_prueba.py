import cv2
import numpy as np
import time
from CPS import CPSClient

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
result = []
# Inicialización
if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión al robot")
cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)


#atributo ret para almacenar el resultado de la función HRIF_HRAppCmd
#ret =
ret = cps.HRIF_HRAppCmd(0,'hr_gri_plugins','GripperCatchMoveTo',[2,0],result)

print("Gripper:", ret)
print("Result:", result)

cps.HRIF_DisConnect(0)
print("Robot disconnected.")


