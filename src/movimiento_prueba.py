from CPS import CPSClient

# Points of interest
punto_A = [0.0, 0.0, -90.0, 0.0, 90.0, 0.0]
punto_B = [10.0, 0.0, -90.0, 0.0, 90.0, 0.0]
punto_C = [-10.0,  0.0, -90.0, 0.0, 90.0, 0.0]

cps = CPSClient()
result = []

IP   = '192.168.10.11'
PORT = 10003

# Conexión y enable (todo con subprogramas del SDK)
ret = cps.HRIF_Connect(0, IP, PORT)
cps.HRIF_Connect2Box(0)
cps.HRIF_Electrify(0)
cps.HRIF_Connect2Controller(0)
cps.HRIF_GrpEnable(0, 0)

for k in range(1):  # 3 ciclos A->B->C->A
    print(f"--- Ciclo {k + 1}/3 ---", flush=True)

    # A
    print("-> Moviendo a A ...", flush=True)
    cps.HRIF_SetOverride(0, 0, 1)
    cps.HRIF_WayPoint(0,0,0, punto_A, [45,0,45,0,45,0], "TCP", "Base", 20, 50, 0, 1, 0, 0, 0, "0")
    cps.waitBlendingDone(0, 0)
    print("   Llegó a A", flush=True)

    # B
    print("-> Moviendo a B ...", flush=True)
    cps.HRIF_SetOverride(0, 0, 0)
    cps.HRIF_WayPoint(0,0,1, punto_B, [45,0,45,0,45,0], "TCP", "Base", 100, 50, 0, 1, 0, 0, 0, "0")
    cps.waitBlendingDone(0, 0)
    print("   Llegó a B", flush=True)

    # C
    print("-> Moviendo a C ...", flush=True)
    cps.HRIF_WayPoint(0,0,0, punto_C, [45,0,45,0,45,0], "TCP", "Base", 100, 50, 0, 1, 0, 0, 0, "0")
    cps.waitBlendingDone(0,0)
    print("   Llegó a C", flush=True)


cps.HRIF_DisConnect(0)
print("Robot disconnected.", flush=True)
