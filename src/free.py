from CPS import CPSClient
import time

# --- CONFIGURACIÓN ---
IP = '192.168.10.11'
PORT = 10003
cps = CPSClient()

def inicializar():
    cps.HRIF_Connect(0, IP, PORT)
    cps.HRIF_Connect2Box(0)
    cps.HRIF_Electrify(0)
    cps.HRIF_Connect2Controller(0)
    cps.HRIF_GrpEnable(0, 0)
    print("Robot conectado y habilitado.")

def modo_manual_full(activar):
    if activar:
        print(">>> Intentando forzar modo LIBRE...")
        # 1. Simulamos que el botón de seguridad está cerrado (1 = presionado)
        cps.HRIF_HRAppCmd(0, 'hr_robot_core', 'SetSafetyButton', [1], [])
        time.sleep(0.1)
        # 2. Activamos Freedrive
        cps.HRIF_GrpOpenFreeDriver(0, 0)
    else:
        print(">>> Bloqueando a modo RÍGIDO...")
        cps.HRIF_GrpCloseFreeDriver(0, 0)
        # Reset para limpiar el estado forzado
        cps.HRIF_HRAppCmd(0, 'hr_robot_core', 'GrpReset', [], [])

# --- LÓGICA DE PRUEBA ---
inicializar()
estado = False # False = Rígido, True = Libre

print("\n--- PRUEBA DE CONTROL DE SEGURIDAD (Presiona ENTER) ---")
try:
    while True:
        input(f"Modo actual: {'LIBRE' if estado else 'RÍGIDO'}. Presiona ENTER para cambiar...")
        estado = not estado
        modo_manual_full(estado)
except KeyboardInterrupt:
    print("\nDesconectando...")
finally:
    cps.HRIF_DisConnect(0)
    cps.HRIF_DisConnect(0)