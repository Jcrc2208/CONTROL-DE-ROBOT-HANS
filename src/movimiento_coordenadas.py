import time
from CPS import CPSClient

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()
rbtID = 0

# --- CONEXIÓN Y PUESTA EN MARCHA ---
print("Conectando al robot...")
cps.HRIF_Connect(rbtID, IP, PORT)
cps.HRIF_Connect2Box(rbtID)
cps.HRIF_Electrify(rbtID)
cps.HRIF_Connect2Controller(rbtID)
cps.HRIF_GrpEnable(rbtID, 0)

# El manual indica StartMaster antes de mover nada
print("Iniciando estación maestra...")
cps.HRIF_SendRaw(rbtID, "StartMaster,;")
time.sleep(4) 

def modo_libre():
    print("--- ACTIVANDO MODO LIBRE (Teaching) ---")
    # Comando según protocolo: StartAssistiveMode,rbtID,;
    cps.HRIF_SendRaw(rbtID, f"StartAssistiveMode,{rbtID},;")
    
    input("Modo Libre activo. Mueve el robot y presiona ENTER para terminar...")
    
    cps.HRIF_SendRaw(rbtID, f"CloseAssistiveMode,{rbtID},;")
    print("Modo Libre desactivado.")

def ejecutar_pick():
    print("--- INICIANDO PICK AND PLACE ---")
    
    # 1. Mover a punto (aquí iría tu lógica de waypoint)
    print("Moviendo a pieza...")
    
    # 2. Gripper (Usando plugin según SDK)
    print("Cerrando gripper...")
    res = []
    # Usamos el plugin de gripper para la acción de agarre
    cps.HRIF_HRAppCmd(rbtID, 'hr_gri_plugins', 'GripperCatchMoveTo', [2, 0], res)
    
    print("Pieza capturada.")
    time.sleep(1)

# --- FLUJO PRINCIPAL ---
try:
    # Decisión de calibración
    calibrar = input("¿Deseas entrar al modo libre para calibrar? (s/n): ").lower()
    if calibrar == 's':
        modo_libre()
    
    # Decisión de ejecutar ciclo
    ejecutar = input("¿Deseas iniciar el ciclo de Pick and Place? (s/n): ").lower()
    if ejecutar == 's':
        ejecutar_pick()
    else:
        print("Ciclo cancelado.")

finally:
    cps.HRIF_DisConnect(rbtID)
    print("Desconectado.") 