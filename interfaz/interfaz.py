import socket
import threading
import json
import math
import tkinter as tk

# --- PARÁMETROS TÉCNICOS ---
# Límites reales del Hans Robot E05
LIMITS = [(-360, 360), (-135, 135), (-150, 150), (-360, 360), (-147, 147), (-360, 360)]
# Longitudes visuales en píxeles de los eslabones (Base, Brazo, Antebrazo, Muñeca)
LINKS = [40, 100, 90, 40] 

class ServidorRobot:
    def __init__(self, root):
        self.root = root
        self.root.title("Hans Robot E05 - Monitor de Telemetría")
        self.angles = [0.0] * 6
        self.scales = []
        self.labels_val = []

        # 1. PANEL IZQUIERDO: CONTROLES Y LECTURAS
        self.panel_izq = tk.Frame(root, padx=15, pady=15, bg="#2e2e2e")
        self.panel_izq.pack(side="left", fill="y")
        
        tk.Label(self.panel_izq, text="TELEMETRÍA REAL (Grados)", font=("Arial", 12, "bold"), fg="white", bg="#2e2e2e").pack(pady=10)
        
        # Crear indicadores visuales para los 6 ejes
        for i, (mn, mx) in enumerate(LIMITS):
            frame_joint = tk.Frame(self.panel_izq, bg="#2e2e2e")
            frame_joint.pack(fill="x", pady=4)
            
            lbl = tk.Label(frame_joint, text=f"J{i+1}: 0.0°", font=("Courier", 10), fg="#00ff00", bg="#2e2e2e", width=12, anchor="w")
            lbl.pack(side="left")
            self.labels_val.append(lbl)
            
            sc = tk.Scale(frame_joint, from_=mn, to=mx, orient="horizontal", length=140, state="disabled", bg="#2e2e2e", fg="white")
            sc.pack(side="right")
            self.scales.append(sc)

        # 2. PANEL DERECHO: CANVAS DE DIBUJO
        self.canvas = tk.Canvas(root, width=600, height=500, bg="#1e1e1e")
        self.canvas.pack(side="right", fill="both", expand=True)

        self.dibujar_estructura()

        # 3. RED: HILO RECEPTOR UDP
        self.udp_running = True
        threading.Thread(target=self.receptor_udp, daemon=True).start()

    def dibujar_estructura(self):
        """Calcula la cinemática directa simplificada para vista lateral"""
        self.canvas.delete("all")
        
        # Grid de fondo para estética industrial/ingeniería
        for i in range(0, 600, 40):
            self.canvas.create_line(i, 0, i, 500, fill="#2b2b2b", width=1)
        for j in range(0, 500, 40):
            self.canvas.create_line(0, j, 600, j, fill="#2b2b2b", width=1)

        # Origen del robot en el Canvas (Base fija en el suelo)
        x, y = 300, 420 
        puntos = [(x, y)]

        # --- CINEMÁTICA DIRECTA SIMPLIFICADA (Vista Lateral) ---
        # Eslabón 1: Base (va recto hacia arriba basado en LINKS[0])
        y -= LINKS[0]
        puntos.append((x, y))

        # Ángulo J2 afecta al hombro (0 grados suele ser vertical o desfasado, ajustamos con math.pi/2)
        rad_j2 = math.radians(self.angles[1])
        x += LINKS[1] * math.sin(rad_j2)
        y -= LINKS[1] * math.cos(rad_j2)
        puntos.append((x, y))

        # Ángulo J3 afecta al codo (acumula el ángulo de J2)
        rad_j3 = rad_j2 + math.radians(self.angles[2])
        x += LINKS[2] * math.sin(rad_j3)
        y -= LINKS[2] * math.cos(rad_j3)
        puntos.append((x, y))

        # Ángulo J5 afecta a la muñeca (interviene en la inclinación final)
        rad_j5 = rad_j3 + math.radians(self.angles[4])
        x += LINKS[3] * math.sin(rad_j5)
        y -= LINKS[3] * math.cos(rad_j5)
        puntos.append((x, y))

        # Dibujar eslabones y articulaciones
        for i in range(len(puntos) - 1):
            # Cambia de color según la sección del brazo
            color = "#00adb5" if i >= 2 else "#ff2e63" 
            self.canvas.create_line(puntos[i][0], puntos[i][1], puntos[i+1][0], puntos[i+1][1], width=8, fill=color, capstyle="round")
            self.canvas.create_oval(puntos[i][0]-6, puntos[i][1]-6, puntos[i][0]+6, puntos[i][1]+6, fill="#eeeeee", outline="black")

        # Dibujar la carga o herramienta final (TCP)
        self.canvas.create_target(puntos[-1][0], puntos[-1][1])

    def actualizar_interfaz(self):
        """Actualiza barras, textos de telemetría y redibuja"""
        for i, val in enumerate(self.angles):
            self.labels_val[i].config(text=f"J{i+1}: {val:.1f}°")
            self.scales[i].configure(state="normal")
            self.scales[i].set(val)
            self.scales[i].configure(state="disabled")
        self.dibujar_estructura()

    def receptor_udp(self):
        """Escucha de forma segura los datos JSON entrantes"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 5005))
        sock.settimeout(0.5)
        
        while self.udp_running:
            try:
                data, _ = sock.recvfrom(1024)
                self.angles = json.loads(data.decode('utf-8'))
                # Invocar la actualización en el hilo principal de Tkinter
                self.root.after(0, self.actualizar_interfaz)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error en recepción UDP: {e}")
        sock.close()

# Extensión rápida para dibujar un pequeño efector final en el Canvas
def _create_target(self, x, y):
    self.create_oval(x-4, y-4, x+4, y+4, fill="yellow")
tk.Canvas.create_target = _create_target

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorRobot(root)
    def salir():
        app.udp_running = False
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", salir)
    root.mainloop()