import time
from pymodbus.client import ModbusTcpClient

ROBOT_IP = "192.168.10.11"
PORT = 502
DEVICE_ID = 1

client = ModbusTcpClient(ROBOT_IP, port=PORT)

def proteger_registros():
    if not client.connect():
        print("No se pudo conectar")
        return

    valores_a_escribir = [100, 200, 300, 400, 500]
    
    print("Iniciando protección de registros (Watchdog activo)...")
    
    try:
        while True:
            # Escribimos el bloque de valores en los registros 0-3 para mantenerlos protegidos
            result = client.write_registers(
                address=0,
                values=valores_a_escribir,
                device_id=DEVICE_ID
            )
            
            if result.isError():
                print("Error al proteger registros:", result)
            else:
                print("Valores forzados exitosamente en 0-3")
            
            # Refresco cada segundo para mantener el control
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nProtección detenida por el usuario.")
        client.close()

if __name__ == "__main__":
    proteger_registros()