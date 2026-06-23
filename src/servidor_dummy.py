import socket
import json
import threading

HOST = "0.0.0.0"
PORT = 5000
# Este servidor dummy simula la recepción de coordenadas desde la IA y las imprime en consola.| No se conecta a ningún robot real, solo muestra lo que recibiría el cobot.

# --- Variables globales para trackear los sockets ---
robot_socket = None
lock = threading.Lock()  # Para manejar hilos de forma segura sin colisiones

def handle_client(conn, addr):
    global robot_socket
    print(f"\n[+] Nueva conexión establecida desde: {addr}")
    
    # METACONEXIÓN
    if addr[0] == "192.168.10.11":
        with lock:
            robot_socket = conn
        print(" HANS ROBOT registrado en el servidor central. Listo para recibir comandos.")
    else:
        print(" [PIPELINE DE IA] registrado. Iniciando transmisión de tracking.")

    with conn:
        while True:
            try:
                data = conn.recv(1024)
                if not data:
                    print(f"[-] Cliente desconectado: {addr}")
                    break
                
                # Distinguir entre IA y Robot por IP
                if addr[0] != "192.168.10.11":
                    coords = json.loads(data.decode('utf-8'))
                    x, y = coords["x"], coords["y"]

                    # --- AJUSTE MATEMÁTICO: Escala + Offset de Seguridad ---
                    # frames son de 320x240. Multiplicar por 0.1 da mm muy chicos 
                    x_mm = 350.0 + (x * 0.5)  
                    y_mm = -100.0 + (y * 0.5) 
                    z_mm = 200.0              # Altura segura sobre la mesa
                    
                    # Formatear comando industrial obligando el salto de línea \n
                    cmd = f"MOVEJ X={x_mm:.1f} Y={y_mm:.1f} Z={z_mm:.1f}\n"
                    print(f"[RUTEO] IA píxeles: ({x}, {y}) ➡️ Comando Cobot: {cmd.strip()}")

                    # GUARDAR EN LOG
                    with open("coords_log.csv", "a") as f:
                        f.write(f"{x},{y},{x_mm:.1f},{y_mm:.1f}\n")

                    # REENVIAR AL ROBOT (Si está conectado)
                    with lock:
                        if robot_socket is not None:
                            try:
                                robot_socket.sendall(cmd.encode('utf-8'))
                            except Exception as re_err:
                                print("[-] Error al inyectar comando al robot (Socket roto):", re_err)
                                robot_socket = None
                        else:
                            print(" Recibiendo IA, pero el Hans Robot no está conectado en el puerto.")

            except json.JSONDecodeError:
                pass  # Ignorar ráfagas incompletas de red
            except Exception as e:
                print(f"[-] Error en el hilo {addr}: {e}")
                break

    # Limpieza si el robot se cae
    if addr[0] == "192.168.10.11":
        with lock:
            robot_socket = None
        print(" Hans Robot desconectado del servidor.")
# --- SERVIDOR CENTRAL PARA IA Y ROBOT INDUSTRIAL ---
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Servidor industrial escuchando en {HOST}:{PORT}...")
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    start_server()
