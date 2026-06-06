import socket
import threading
import json
import math
import tkinter as tk

# --- PARÁMETROS TÉCNICOS ---
LIMITS = [(-360, 360), (-135, 135), (-150, 150), (-360, 360), (-147, 147), (-360, 360)]
LINKS = [50, 90, 80, 40, 30, 20] # Longitudes en píxeles para el dibujo en pantalla

class ServidorRobot:
    def __init__(self, root):
        self.root = root
        self.root.title("Hans Robot E05 - Monitor Mínimo")
        self.angles = [0.0] * 6
        self.scales = []

        # 1. PANEL IZQUIERDO: CONTROLES (Solo lectura)
        self.panel_izq = tk.Frame(root, padx=15, pady=15)
        self.panel_izq.pack(side="left", fill="y")
        
        tk.Label(self.panel_izq, text="TELEMETRÍA J1-J6", font=("Arial", 12, "bold")).pack(pady=5)
        for i, (mn, mx) in enumerate(LIMITS):
            tk.Label(self.panel_izq, text=f"Articulación J{i+1}").pack(anchor="w")
            sc = tk.Scale(self.panel_izq, from_=mx, to=mn, orient="horizontal", length=180, state="disabled")
            sc.pack(pady=2)
            self.scales.append(sc)

        # 2. PANEL DERECHO: CANVAS DE DIBUJO (Estructura pura)
        self.canvas = tk.Canvas(root, width=500, height=500, bg="white")
        self.canvas.pack(side="right", fill="both", expand=True)

        self.dibujar_estructura()

        # 3. RED: HILO RECEPTOR UDP
        self.udp_running = True
        threading.Thread(target=self.receptor_udp, daemon=True).start()

    def dibujar_estructura(self):
        """Calcula la cinemática directa básica y dibuja las líneas del brazo"""
        self.canvas.delete("all")
        
        # Origen del dibujo (Centro inferior del Canvas)
        x, y = 250, 400 
        angulo_acumulado = 0.0
        puntos = [(x, y)]

        # Calcular posiciones de cada articulación consecutiva
        # Omitimos J1 para la vista lateral (J1 es rotación de base), graficamos el resto de la cadena angular
        for angle, longitud in zip(self.angles, LINKS):
            angulo_acumulado += math.radians(angle)
            x += longitud * math.sin(angulo_acumulado)
            y -= longitud * math.cos(angulo_acumulado) # Restamos porque en Canvas el eje Y baja
            puntos.append((x, y))

        # Dibujar las líneas que unen los puntos (Estructura del brazo)
        for i in range(len(puntos) - 1):
            color = "#d62728" if i >= 3 else "#1f77b4" # Color diferente para identificar la muñeca
            self.canvas.create_line(puntos[i][0], puntos[i][1], puntos[i+1][0], puntos[i+1][1], width=6, fill=color)
            self.canvas.create_oval(puntos[i][0]-5, puntos[i][1]-5, puntos[i][0]+5, puntos[i][1]+5, fill="black")

    def actualizar_interfaz(self):
        """Actualiza barras y redibuja los eslabones"""
        for i, val in enumerate(self.angles):
            self.scales[i].configure(state="normal")
            self.scales[i].set(val)
            self.scales[i].configure(state="disabled")
        self.dibujar_estructura()

    def receptor_udp(self):
        """Escucha los datos enviados por el script del robot"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 5005))
        sock.settimeout(1.0)
        
        while self.udp_running:
            try:
                data, _ = sock.recvfrom(1024)
                self.angles = json.loads(data.decode('utf-8'))
                self.root.after(0, self.actualizar_interfaz)
            except socket.timeout:
                continue
        sock.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorRobot(root)
    def salir():
        app.udp_running = False
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", salir)
    root.mainloop()