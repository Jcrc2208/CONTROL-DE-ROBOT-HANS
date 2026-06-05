import math
import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

LIMITS = [
    (-360, 360),   # J1
    (-135, 135),   # J2
    (-150, 150),   # J3
    (-360, 360),   # J4
    (-147, 147),   # J5
    (-360, 360),   # J6
]

LINKS = [1.1, 1.0, 0.85, 0.55, 0.35, 0.25]

class Robot:

    def __init__(self, root):

        self.joints = []
        self.scales = []

        controls = tk.Frame(root)
        controls.pack(side="left", padx=10, pady=10)

        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.get_tk_widget().pack(
            side="right",
            fill="both",
            expand=True
        )

        # CREAR CONTROLES J1-J6
        for i, (mn, mx) in enumerate(LIMITS):

            tk.Label(
                controls,
                text=f"J{i+1}",
                font=("Arial", 12, "bold")
            ).pack()

            joint = tk.DoubleVar(value=0)
            self.joints.append(joint)

            scale = tk.Scale(
                controls,
                from_=mx,
                to=mn,
                orient="horizontal",
                length=250,
                resolution=1,
                variable=joint,
                command=lambda e, idx=i: self.limit_joint(idx)
            )

            scale.pack(pady=5)

            self.scales.append(scale)

        self.draw()

    # BLOQUEAR LIMITES
    def limit_joint(self, idx):

        mn, mx = LIMITS[idx]

        value = self.joints[idx].get()

        # SI PASA DEL LIMITE SE REGRESA
        if value < mn:
            self.joints[idx].set(mn)

        elif value > mx:
            self.joints[idx].set(mx)

        self.draw()

    # CINEMATICA
    def fk(self):

        x = y = a = 0

        points = [(0, 0)]

        for j, l in zip(self.joints, LINKS):

            a += math.radians(j.get())

            x += l * math.cos(a)
            y += l * math.sin(a)

            points.append((x, y))

        return np.array(points)

    # DIBUJAR ROBOT
    def draw(self):

        p = self.fk()

        self.ax.clear()

        self.ax.plot(
            p[:, 0],
            p[:, 1],
            "-o",
            linewidth=3,
            markersize=8
        )

        self.ax.set_xlim(-4, 4)
        self.ax.set_ylim(-4, 4)

        self.ax.set_aspect("equal")

        # QUITAR EJES
        self.ax.axis("off")

        self.canvas.draw()


root = tk.Tk()

root.title("Robot 6DOF")

Robot(root)

root.mainloop()