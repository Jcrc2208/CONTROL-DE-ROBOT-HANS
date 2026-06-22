import time
from CPS import CPSClient  

class RobotHuayanManager:
    STATE_DISCONNECTED = "DESCONECTADO"
    STATE_CONNECTED    = "CONECTADO"

    def __init__(self):
        self.sdk = CPSClient() 
        self.box_id = 0
        self.rbt_id = 0
        self.ip = "192.168.10.11"  
        self.port = 10003
        
        self.current_state = self.STATE_DISCONNECTED
        
        self.conectar_con_robot()

    def conectar_con_robot(self):
        """Intenta abrir el socket de comunicación con el controlador del robot."""
        try:
            if hasattr(self.sdk, 'HRIF_Connect'):
                print(f"Intentando conectar al Cobot en {self.ip}:{self.port}...")
                # Se invoca la función de conexión del SDK de Hans/Huayan
                self.sdk.HRIF_Connect(self.box_id, self.ip, self.port)
                time.sleep(0.5) # Breve pausa para dejar que el socket se establezca
        except Exception as e:
            print(f"Error crítico al intentar invocar HRIF_Connect: {e}")

    def obtener_paquete_telemetria(self):
        # 1. VERIFICAR CONEXIÓN
        esta_conectado = False
        try:
            if hasattr(self.sdk, 'HRIF_IsConnected'):
                esta_conectado = self.sdk.HRIF_IsConnected(self.box_id)
                
                # Si el socket se cerró por alguna razón, intentamos reconectar en caliente
                if not esta_conectado:
                    self.conectar_con_robot()
                    esta_conectado = self.sdk.HRIF_IsConnected(self.box_id)

                self.current_state = self.STATE_CONNECTED if esta_conectado else self.STATE_DISCONNECTED
        except Exception as e:
            print(f"Error al verificar conexión: {e}")
            esta_conectado = False
            self.current_state = self.STATE_DISCONNECTED

        # Si el robot sigue desconectado, devolvemos respuestas en 0 de inmediato
        if not esta_conectado:
            return {
                "conectado": False,
                "estado_app": self.current_state,
                "posicion_cartesiana": [0.0] * 6,
                "angulos_articulares": [0.0] * 6
            }

        cartesianas = [0.0] * 6
        articulares = [0.0] * 6

        # 2. POSICIÓN CARTESIANA (HRIF_ReadActTcpPos)
        try:
            buffer_tcp = []
            if hasattr(self.sdk, 'HRIF_ReadActTcpPos'):
                self.sdk.HRIF_ReadActTcpPos(self.box_id, self.rbt_id, buffer_tcp)
                cartesianas = [float(x) for x in buffer_tcp] if buffer_tcp else [0.0] * 6
        except Exception as e:
            print(f"No se pudo leer Posición TCP: {e}")

        # 3. ÁNGULOS ARTICULARES (HRIF_ReadActJointPos)
        try:
            buffer_joints = []
            if hasattr(self.sdk, 'HRIF_ReadActJointPos'):
                self.sdk.HRIF_ReadActJointPos(self.box_id, self.rbt_id, buffer_joints)
                articulares = [float(x) for x in buffer_joints] if buffer_joints else [0.0] * 6
        except Exception as e:
            print(f"No se pudo leer Ángulos Articulares: {e}")

        return {
            "conectado": True,
            "estado_app": self.current_state,
            "posicion_cartesiana": cartesianas,
            "angulos_articulares": articulares
        }