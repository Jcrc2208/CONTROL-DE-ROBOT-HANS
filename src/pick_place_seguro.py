from CPS import CPSClient
import time

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()


# COORDENADAS DEFINIDAS
PICK = [417.884, 227.981, 161.745, 177.171, 3.110, -154.484]
PLACE = [400.792, -228.182, 159.280, 176.366, 0.552, 162.710]

# PUNTOS DE TRASLACIÓN SEGURA (EL "VUELO" DEL ROBOT)
TRASLACION_SEGURA_1 = [386.760, 213.830, 412.385, 176.867, 8.911,-154.484]
TRASLACION_SEGURA_2 = [384.299, -158.737, 333.606, -179.087, 1.793, 158.107]

# ORIENTACIÓN (Usamos la misma para mantener estabilidad)
ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 

def inicializar():
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


# --- SECUENCIA MAESTRA ---
inicializar()

try:
    # 1. PICK
    mover_y_esperar(PICK)
    ejecutar_gripper(0)  # CERRAR
    
    # --- TRAYECTORIA SEGURA (SUBIR Y TRASLADAR) ---
    mover_y_esperar(TRASLACION_SEGURA_1) # Sube tras el pick
    mover_y_esperar(TRASLACION_SEGURA_2) # Viaja por arriba
    
    # 2. PLACE
    mover_y_esperar(PLACE)
    ejecutar_gripper(1000) # ABRIR
    
finally:
    cps.HRIF_DisConnect(0)
    print("Secuencia finalizada.")


#definir taryectoria segura entre pick and place 
#en este apartado se espera realizar una trayectoria destinada a hacer una tlaskacion seguro es decir que cuando tome un objeto se pueda ir hacia ariba esto para evitar posible colisiones 