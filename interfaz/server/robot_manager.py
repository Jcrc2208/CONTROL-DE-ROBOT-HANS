import time
from CPS import CPSClient  

class RobotHuayanManager:
    STATE_DISCONNECTED = "DESCONECTADO"
    STATE_CONNECTED    = "CONECTADO"

    def __init__(self):
        self.sdk = CPSClient() 
        # Parámetros por defecto apuntando al Cobot real
        self.box_id = 0
        self.rbt_id = 0
        self.ip = "192.168.10.11"  
        self.port = 10003
        self.sampling_ms = 100  
        
        self.current_state = self.STATE_DISCONNECTED
        
    def obtener_paquete_telemetria(self):
        # Verificar activamente mediante el SDK si el socket/hardware responde
        esta_conectado = False
        try:
            if hasattr(self.sdk, 'HRIF_IsConnected'):
                esta_conectado = self.sdk.HRIF_IsConnected(self.box_id)
                self.current_state = self.STATE_CONNECTED if esta_conectado else self.STATE_DISCONNECTED
        except Exception as e:
            print(f"Error al verificar conexión: {e}")
            esta_conectado = False
            self.current_state = self.STATE_DISCONNECTED

        # Si el robot está desconectado físicamente, devolvemos ceros sin interrogar los registros
        if not esta_conectado:
            return {
                "conectado": False,
                "estado_app": self.current_state,
                "posicion_cartesiana": [0.0] * 6,
                "angulos_articulares": [0.0] * 6,
            }

        # Inicializar contenedores para las lecturas exitosas
        cartesianas = [0.0] * 6
        articulares = [0.0] * 6

        # Leer Posición Cartesiana Real (TCP)
        try:
            buffer_tcp = []
            if hasattr(self.sdk, 'HRIF_ReadActTcpPos'):
                self.sdk.HRIF_ReadActTcpPos(self.box_id, self.rbt_id, buffer_tcp)
                cartesianas = [float(x) for x in buffer_tcp] if buffer_tcp else [0.0] * 6
        except Exception as e:
            print(f"No se pudo leer Posición TCP: {e}")

        # Leer Ángulos Articulares Reales (J1-J6)
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
            "angulos_articulares": articulares,
        }