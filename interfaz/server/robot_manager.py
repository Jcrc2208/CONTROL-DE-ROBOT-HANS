import time
from CPS import CPSClient  

class RobotHuayanManager:
    STATE_DISCONNECTED = "DESCONECTADO"
    STATE_INITIALIZING = "INICIALIZANDO"
    STATE_IDLE         = "LISTO_APAGADO"  
    STATE_READY        = "READY_SERVO_ON" 
    STATE_ERROR        = "ERROR_ALARMA"   

    def __init__(self):
        self.sdk = CPSClient() 
        
        # Parámetros por defecto apuntando al Cobot real
        self.box_id = 0
        self.rbt_id = 0
        self.ip = "192.168.10.11"  
        self.port = 10003
        self.sampling_ms = 100  
        
        self.current_state = self.STATE_DISCONNECTED


    def actualizar_configuracion(self, box_id, rbt_id, ip, port, sampling_ms):
        self.box_id = int(box_id)
        self.rbt_id = int(rbt_id)
        self.ip = str(ip)
        self.port = int(port)
        self.sampling_ms = int(sampling_ms)
        return True

    def conectar_hardware(self):
        if self.current_state != self.STATE_DISCONNECTED:
            return True
            
        self.current_state = self.STATE_INITIALIZING
        resultado = self.sdk.HRIF_Connect(self.box_id, self.ip, self.port)
        
        if resultado == 0:
            self.current_state = self.STATE_IDLE
            return True
        else:
            self.current_state = self.STATE_DISCONNECTED
            return False

    def establecer_velocidad_global(self, velocidad):
        if self.current_state == self.STATE_DISCONNECTED:
            return False
        resultado = self.sdk.HRIF_SetOverride(self.box_id, self.rbt_id, float(velocidad))
        return resultado == 0

    def establecer_modo_operacion(self, modo_simulacion):
        if self.current_state == self.STATE_DISCONNECTED:
            return False
        state = 1 if modo_simulacion else 0
        resultado = self.sdk.HRIF_SetSimulation(self.box_id, state)
        return resultado == 0

    def detener_robot(self):
        if self.current_state == self.STATE_DISCONNECTED:
            return False
        resultado = self.sdk.HRIF_GrpStop(self.box_id, self.rbt_id)
        return resultado == 0

    def cambiar_estado_servo(self, encender=True):
        if self.current_state == self.STATE_DISCONNECTED:
            return False
        nuevo_valor_servo = 1 if encender else 0
        resultado = self.sdk.HRIF_SetServoState(self.box_id, self.rbt_id, nuevo_valor_servo)
        
        if resultado == 0:
            self.current_state = self.STATE_READY if encender else self.STATE_IDLE
            return True
        return False

    def limpiar_alarmas(self):
        if self.current_state == self.STATE_DISCONNECTED:
            return False
        resultado = self.sdk.HRIF_ResetRobotError(self.box_id, self.rbt_id)
        if resultado == 0 and self.current_state == self.STATE_ERROR:
            self.current_state = self.STATE_IDLE
        return resultado == 0

    def leer_diagnostico_bajo_nivel(self):
        if self.current_state == self.STATE_DISCONNECTED:
            return {"voltaje_bus": "0 V", "simulacion": "Desconectado", "codigo_error": "N/A"}
            
        buffer_state = []
        self.sdk.HRIF_ReadRobotState(self.box_id, self.rbt_id, buffer_state)
        # El voltaje suele ubicarse en los índices eléctricos del buffer de respuesta
        voltaje = f"{buffer_state[9]} V" if len(buffer_state) > 9 else "Desconocido"
        
        # 2. HRIF_IsSimulateRobot (pág 5): Solo requiere boxID y un buffer de salida
        buffer_sim = []
        self.sdk.HRIF_IsSimulateRobot(self.box_id, buffer_sim)
        es_simulado = "Activo" if (buffer_sim and buffer_sim[0] == '1') else "Inactivo"
        
        # 3. HRIF_GetErrorCode
        buffer_error = []
        self.sdk.HRIF_GetErrorCode(self.box_id, self.rbt_id, buffer_error)
        error_activo = buffer_error[0] if buffer_error else "0"
        
        return {
            "voltaje_bus": voltaje,
            "simulacion": es_simulado,
            "codigo_error": error_activo
        }

    def obtener_paquete_telemetria(self):
        esta_conectado = self.current_state != self.STATE_DISCONNECTED
        
        # Valores por defecto en caso de fallo o desconexión
        override_val = 0.50
        es_simulado = True
        estop_activo = False
        voltaje = "24"
        error_activo = "0"
        cartesianas = [0.0] * 6
        articulares = [0.0] * 6

        if not esta_conectado:
            return {
                "conectado": False,
                "estado_app": self.current_state,
                "override": override_val,
                "simulacion": es_simulado,
                "temperatura": 0,
                "estop": estop_activo,
                "posicion_cartesiana": cartesianas,
                "angulos_articulares": articulares,
                "voltaje_bus": voltaje,
                "codigo_error": error_activo
            }

        try:
            buffer_override = []
            if hasattr(self.sdk, 'HRIF_GetOverride'):
                self.sdk.HRIF_GetOverride(self.box_id, self.rbt_id, buffer_override)
                override_val = float(buffer_override[0]) if buffer_override else 0.50
            elif hasattr(self.sdk, 'get_override'):
                override_val = float(self.sdk.get_override(self.box_id, self.rbt_id))
        except Exception as e:
            print(f"No se pudo leer Override: {e}")

        try:
            buffer_sim = []
            if hasattr(self.sdk, 'HRIF_IsSimulateRobot'):
                self.sdk.HRIF_IsSimulateRobot(self.box_id, buffer_sim)
                es_simulado = True if (buffer_sim and buffer_sim[0] == '1') else False
            elif hasattr(self.sdk, 'is_simulation'):
                es_simulado = bool(self.sdk.is_simulation(self.box_id))
        except Exception as e:
            print(f"No se pudo leer Modo Simulación: {e}")

        try:
            buffer_state = []
            if hasattr(self.sdk, 'HRIF_ReadRobotState'):
                self.sdk.HRIF_ReadRobotState(self.box_id, self.rbt_id, buffer_state)
                if buffer_state and len(buffer_state) > 9:
                    if buffer_state[7] == '1':
                        estop_activo = True
                        self.current_state = self.STATE_ERROR
                    voltaje = buffer_state[9]
        except Exception as e:
            print(f"No se pudo leer Estado Robot: {e}")

        try:
            buffer_error = []
            if hasattr(self.sdk, 'HRIF_GetErrorCode'):
                self.sdk.HRIF_GetErrorCode(self.box_id, self.rbt_id, buffer_error)
                error_activo = buffer_error[0] if buffer_error else "0"
        except Exception as e:
            print(f"No se pudo leer Código de Error: {e}")

        try:
            buffer_tcp = []
            if hasattr(self.sdk, 'HRIF_GetActualTCPPos'):
                self.sdk.HRIF_GetActualTCPPos(self.box_id, self.rbt_id, buffer_tcp)
                cartesianas = [float(x) for x in buffer_tcp] if buffer_tcp else [0.0]*6
        except Exception as e:
            print(f"No se pudo leer Posición TCP: {e}")

        try:
            buffer_joints = []
            if hasattr(self.sdk, 'HRIF_GetActualJointPos'):
                self.sdk.HRIF_GetActualJointPos(self.box_id, self.rbt_id, buffer_joints)
                articulares = [float(x) for x in buffer_joints] if buffer_joints else [0.0]*6
        except Exception as e:
            print(f"No se pudo leer Ángulos Articulares: {e}")

        return {
            "conectado": esta_conectado,
            "estado_app": self.current_state,
            "override": override_val,
            "simulacion": es_simulado,
            "temperatura": 32,
            "estop": estop_activo,
            "posicion_cartesiana": cartesianas,
            "angulos_articulares": articulares,
            "voltaje_bus": voltaje,
            "codigo_error": error_activo
        }