from CPS import CPSClient
import time

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
GID = 2
result = []

# Inicialización
if cps.HRIF_Connect(0, IP, PORT) != 0: raise RuntimeError("Error de conexión")
cps.HRIF_Connect2Box(0); cps.HRIF_Electrify(0); cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0); cps.HRIF_SetOverride(0, 0, 15)

def detectar_objeto():
    # 1. Comando de cierre
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GripperCatchMoveTo', [GID, 0], result)
    time.sleep(2) 
    
    # 2. Obtener posición
    res_pos = []
    cps.HRIF_HRAppCmd(0, 'hr_gri_plugins', 'GetCatchPosition', [GID], res_pos)
    posicion = int(res_pos[1]) if len(res_pos) > 1 else 0
    
    # 3. Lógica binaria: El umbral es 40
    # Si es >= 40, consideramos que hay objeto. Si es < 40, no hay nada.
    if posicion >= 40:
        return "TIENE OBJETO"
    else:
        return "NO TIENE OBJETO"

# --- EJECUCIÓN DIRECTA ---
estado_final = detectar_objeto()
print(f"ESTADO ACTUAL: {estado_final}")