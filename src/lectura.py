
from pymodbus.client import ModbusTcpClient

ROBOT_IP = "192.168.10.11"
PORT = 502
DEVICE_ID = 1

client = ModbusTcpClient(ROBOT_IP, port=PORT)

if not client.connect():
    print("No se pudo conectar al cobot")
    exit()

print("Conectado al cobot")

result = client.read_holding_registers(
    address=0,
    count=10,
    device_id=DEVICE_ID
)

if result.isError():
    print("Error leyendo registros:", result)
else:
    print("Holding registers 0-9:", result.registers)

client.close()
