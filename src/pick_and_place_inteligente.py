from CPS import CPSClient
import time

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
GID = 2
result = []

# COORDENADAS DEFINIDAS
PICK = [417.884, 227.981, 161.745, 177.171, 3.110, -154.484]
PLACE = [400.792, -228.182, 159.280, 176.366, 0.552, 162.710]
TRASLACION_SEGURA_1 = [386.760, 213.830, 412.385, 176.867, 8.911,-154.484]
TRASLACION_SEGURA_2 = [384.299, -158.737, 333.606, -179.087, 1.793, 158.107]
ORIENTATION = [27.859, -7.479, 107.514, 1.919, 62.763, 0.412] 


#lo siguiente seria integran los algoritmos de inteligencia artificial para la detección de objetos y la planificación de trayectorias, pero por ahora se mantiene la secuencia básica de pick and place con el gripper.
def inicializar():
    if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
    cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
    cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

def ejecutar_gripper(valor):
    res = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [GID, valor], res)
    time.sleep(1.0) 

def detectar_objeto():
    res_pos = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GetCatchPosition', [GID], res_pos)
    posicion = int(res_pos[1]) if len(res_pos) > 1 else 0
    return "TIENE OBJETO" if posicion >= 40 else "NO TIENE OBJETO"

def mover_y_esperar(coords):
    cps.HRIF_WayPoint(0, 0, 0, coords, ORIENTATION, "TCP_1", "Base", 20, 50, 0, 0, 0, 0, 0, "0")
    cps.waitBlendingDone(0, 0)
    print(f"Llegó a destino: {coords}")

# --- SECUENCIA MAESTRA ---
inicializar()

try:
    # 1. PICK
    mover_y_esperar(PICK)
    ejecutar_gripper(0)  # CERRAR
    
    # --- LECTURA DE SEGURIDAD ---
    estado = detectar_objeto()
    print(f"Estado del agarre tras el PICK: {estado}")
    
    if estado == "TIENE OBJETO":
        print("Objeto confirmado, iniciando traslado...")
        # --- TRAYECTORIA SEGURA ---
        mover_y_esperar(TRASLACION_SEGURA_1)
        mover_y_esperar(TRASLACION_SEGURA_2)
        
        # 2. PLACE
        mover_y_esperar(PLACE)
        ejecutar_gripper(1000) # ABRIR
    else:
        print("ERROR: No se detectó objeto. Abortando movimiento de traslado por seguridad.")
    
finally:
    cps.HRIF_DisConnect(0)
    print("Secuencia finalizada.")