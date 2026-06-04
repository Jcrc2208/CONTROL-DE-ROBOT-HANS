#!/usr/bin/env python3
from __future__ import annotations

import time
import cv2
import numpy as np

from CPS import CPSClient


IP = "192.168.10.11"
PORT = 10003

BOX_ID = 0
RBT_ID = 0

JOINT_REF = [0.0, 0.0, -90.0, 0.0, 90.0, 0.0]

J1_MIN = -50.0
J1_MAX = 50.0

# VISIÓN
FRAME_W = 320
FRAME_H = 240

CENTER_X = FRAME_W // 2

DEAD_ZONE_PX = 25

KP = 0.015

MIN_CONTOUR = 800

MOVE_COOLDOWN_S = 0.35

CAMERA_INDEX = 0

# HSV VERDE
LOWER_GREEN = np.array([40, 70, 70])
UPPER_GREEN = np.array([80, 255, 255])


def detect_green(frame):

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(
        hsv,
        LOWER_GREEN,
        UPPER_GREEN
    )

    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (5, 5)
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_OPEN,
        kernel
    )

    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return None, mask

    c = max(contours, key=cv2.contourArea)

    if cv2.contourArea(c) < MIN_CONTOUR:
        return None, mask

    x, y, w, h = cv2.boundingRect(c)

    return (x, y, w, h), mask

# CONECTAR ROBOT
def connect_robot(cps):

    print("Conectando robot...")

    ret = cps.HRIF_Connect(
        BOX_ID,
        IP,
        PORT
    )

    print("HRIF_Connect =", ret)

    cps.HRIF_Connect2Box(BOX_ID)
    print("HRIF_Connect2Box OK")

    cps.HRIF_Electrify(BOX_ID)
    print("HRIF_Electrify OK")

    cps.HRIF_Connect2Controller(BOX_ID)
    print("HRIF_Connect2Controller OK")

    cps.HRIF_GrpEnable(
        BOX_ID,
        RBT_ID
    )

    print("HRIF_GrpEnable OK")

    # IMPORTANTE:
    # override es de 0.0 a 1.0
    cps.HRIF_SetOverride(
        BOX_ID,
        RBT_ID,
        0.15
    )

    print(">>> Robot listo.")


def print_robot_error(cps, error_code):

    msg = []

    try:

        cps.HRIF_GetErrorCodeStr(
            BOX_ID,
            error_code,
            msg
        )

        print(f"ERROR {error_code}: {msg}")

    except Exception as exc:

        print(f"No se pudo leer error: {exc}")

# MOVER J1
def move_j1(cps, j1_deg):

    joints = [
        float(j1_deg),
        JOINT_REF[1],
        JOINT_REF[2],
        JOINT_REF[3],
        JOINT_REF[4],
        JOINT_REF[5]
    ]

    print(f"[MOVE] J1 -> {j1_deg:.2f}")

    ret = cps.HRIF_WayPoint(

        BOX_ID,
        RBT_ID,

        0,              # type=0 -> MoveJ

        joints,         # points
        joints,         # RawACSpoints

        "TCP",
        "Base",

        40,             # speed °/s
        60,             # acc °/s²

        0,              # radius

        1,              # isJoint=1

        0,
        0,
        0,

        "0"
    )

    return ret


def main():

    cps = CPSClient()

    j1_actual = 0.0

    last_move_t = 0.0


    try:

        connect_robot(cps)

    except Exception as exc:

        print(f"ERROR conexión robot: {exc}")

        return


    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():

        print("ERROR cámara.")

        cps.HRIF_DisConnect(BOX_ID)

        return

    print(">>> Cámara OK.")
    print(">>> Tracking iniciado.")
    print(">>> Q para salir.")


    try:

        while True:

            # reducir lag
            for _ in range(4):
                cap.grab()

            ok, frame = cap.read()

            if not ok:
                continue

            frame = cv2.resize(
                frame,
                (FRAME_W, FRAME_H)
            )

            det, mask = detect_green(frame)

            if det is not None:

                x, y, w, h = det

                cx = x + w // 2
                cy = y + h // 2

                error_px = cx - CENTER_X

                # dibujar
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.circle(
                    frame,
                    (cx, cy),
                    5,
                    (0, 0, 255),
                    -1
                )

                cv2.line(
                    frame,
                    (CENTER_X, 0),
                    (CENTER_X, FRAME_H),
                    (255, 255, 0),
                    1
                )

                # CONTROL
                if abs(error_px) > DEAD_ZONE_PX:

                    now = time.monotonic()

                    if now - last_move_t >= MOVE_COOLDOWN_S:

                        delta_deg = error_px * KP

                        # limitar movimiento
                        delta_deg = max(
                            -5.0,
                            min(5.0, delta_deg)
                        )

                        nuevo_j1 = j1_actual + delta_deg

                        # límites
                        nuevo_j1 = max(
                            J1_MIN,
                            min(J1_MAX, nuevo_j1)
                        )

                        ret = move_j1(
                            cps,
                            nuevo_j1
                        )

                        print(
                            f"[TRACK] "
                            f"error={error_px:+4d}px | "
                            f"delta={delta_deg:+.2f}° | "
                            f"J1={nuevo_j1:.2f}° | "
                            f"ret={ret}"
                        )

                        if ret == 0:

                            j1_actual = nuevo_j1

                            cps.waitBlendingDone(
                                BOX_ID,
                                RBT_ID
                            )

                        else:

                            print_robot_error(
                                cps,
                                ret
                            )

                        last_move_t = now


            cv2.imshow(
                "Tracking COBOT",
                frame
            )

            cv2.imshow(
                "Mask",
                mask
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        cap.release()

        cv2.destroyAllWindows()

        try:
            cps.HRIF_DisConnect(BOX_ID)
        except:
            pass

        print(">>> Sistema cerrado.")
2

if __name__ == "__main__":
    main()