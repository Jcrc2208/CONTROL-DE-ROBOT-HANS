from pymodbus.client import ModbusTcpClient

host = "192.168.0.50"
port = 502  

client = ModbusTcpClient(host, port=port   )
client.connect()

# Escribir un valor en el registro 0
x_mm = 100.0
y_mm = 150.0

client.write_register(0, int(x_mm * 10))
client.write_register(1, int(y_mm * 10))
print(f"Enviado al cobot: X={x_mm:.1f}mm, Y={y_mm:.1f}mm")
client.close()

