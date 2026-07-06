import time
from CPS import CPSClient

class RobotHuayanManager:
    STATE_DISCONNECTED = "DESCONECTADO"
    STATE_CONNECTED = "CONECTADO"

    def __init__(self):
        self.sdk = CPSClient()
        self.box_id = 0
        self.rbt_id = 0
        self.ip = "192.168.10.11"
        self.port = 10003

        self.current_state = self.STATE_DISCONNECTED

        self.conectar_con_robot()

    def conectar_con_robot(self):
        try:
            if hasattr(self.sdk, 'HRIF_Connect'):
                print(f"Intentando conectar al Cobot en {self.ip}:{self.port}...")
                self.sdk.HRIF_Connect(self.box_id, self.ip, self.port)
                time.sleep(0.5)
        except Exception as e:
            print(f"Error crítico al intentar invocar HRIF_Connect: {e}")

    def obtener_paquete_telemetria(self):
        # 1. VERIFICAR CONEXIÓN
        esta_conectado = False
        try:
            if hasattr(self.sdk, 'HRIF_IsConnected'):
                esta_conectado = self.sdk.HRIF_IsConnected(self.box_id)

            if not esta_conectado:
                self.conectar_con_robot()
                esta_conectado = self.sdk.HRIF_IsConnected(self.box_id)

            self.current_state = (
                self.STATE_CONNECTED if esta_conectado else self.STATE_DISCONNECTED
            )
        except Exception as e:
            print(f"Error al verificar conexión: {e}")
            esta_conectado = False
            self.current_state = self.STATE_DISCONNECTED

        if not esta_conectado:
            return {
                "conectado": False,
                "estado_app": self.current_state,
                "posicion_cartesiana": [0.0] * 6,
                "angulos_articulares": [0.0] * 6,
                "error_robot": "0",
                "corriente_articulaciones": [0.0] * 6,
                "temperatura_articulaciones": [0.0] * 6,
            }

        cartesianas = [0.0] * 6
        articulares = [0.0] * 6

        # 2. POSICIÓN CARTESIANA (HRIF_ReadActTcpPos)
        try:
            buffer_tcp = []
            if hasattr(self.sdk, 'HRIF_ReadActTcpPos'):
                self.sdk.HRIF_ReadActTcpPos(self.box_id, self.rbt_id, buffer_tcp)
                cartesianas = (
                    [float(x) for x in buffer_tcp] if buffer_tcp else [0.0] * 6
                )
        except Exception as e:
            print(f"No se pudo leer Posición TCP: {e}")

        # 3. ÁNGULOS ARTICULARES REALES (HRIF_ReadActJointPos)
        try:
            buffer_joints = []
            if hasattr(self.sdk, 'HRIF_ReadActJointPos'):
                self.sdk.HRIF_ReadActJointPos(self.box_id, self.rbt_id, buffer_joints)
                articulares = (
                    [float(x) for x in buffer_joints] if buffer_joints else [0.0] * 6
                )
        except Exception as e:
            print(f"No se pudo leer Ángulos Articulares: {e}")

        # 4. CORRECCIÓN PARA EL ERROR GENERAL DEL ROBOT
        error_robot = "0"
        try:
            if hasattr(self.sdk, 'HRIF_ReadRobotErrorCode'):
                # Esta función solo pide box_id y rbt_id, y retorna el entero
                resultado = self.sdk.HRIF_ReadRobotErrorCode(
                    self.box_id, self.rbt_id
                )
                error_robot = str(resultado)
        except Exception as e:
            print(f"No se pudo leer Error del Robot: {e}")

        # 5. CORRECCIÓN PARA LAS CORRIENTES REALES (HRIF_ReadActJointCur_nJ)
        corrientes = [0.0] * 6
        try:
            lista_corrientes = []
            if hasattr(self.sdk, 'HRIF_ReadActJointCur_nJ'):
                self.sdk.HRIF_ReadActJointCur_nJ(
                    self.box_id, self.rbt_id, lista_corrientes
                )
                corrientes = (
                    [float(i) for i in lista_corrientes]
                    if lista_corrientes
                    else [0.0] * 6
                )
        except Exception as e:
            print(f"No se pudo leer Corrientes: {e}")

        # 6. MANEJO DE TEMPERATURAS (Estimación basada en corriente)
        temperaturas = []
        for c in corrientes:
            # Simulación de inercia térmica base (temperatura ambiente + delta por corriente)
            temp_estimada = 35.0 + (abs(c) * 4.5)
            temperaturas.append(round(temp_estimada, 2))

        return {
            "conectado": True,
            "estado_app": self.current_state,
            "posicion_cartesiana": cartesianas,
            "angulos_articulares": articulares,
            "error_robot": error_robot,
            "corriente_articulaciones": corrientes,
            "temperatura_articulaciones": temperaturas,
        }

    # METODOS DE CONTROL PARA COMANDOS DEL ROBOT
    def iniciar_long_jog(self, joint_index, direction, state=1):
        """
        Inicia un movimiento continuo (Long Jog) en una articulación específica.
        joint_index: 0 (J1) a 5 (J6)
        direction: 1 (positivo) o -1 (negativo)
        state: 1 (iniciar movimiento) o 0 (detener movimiento)
        """
        try:
            if hasattr(self.sdk, 'HRIF_LongJogJ'):
                # Estructura del SDK de Huayan corregida agregando el parámetro 'state'
                ret = self.sdk.HRIF_LongJogJ(
                    self.box_id, self.rbt_id, joint_index, direction, state
                )
                print(
                    f"HRIF_LongJogJ enviado -> J{joint_index+1}, Dir: {direction}, Estado: {state}. Ret: {ret}"
                )
                return ret
            else:
                print("Error: El SDK no contiene la función HRIF_LongJogJ.")
                return -1
        except Exception as e:
            print(f"Error al ejecutar HRIF_LongJogJ: {e}")
            raise e # Elevamos el error para que el server.py en el bloque except capte el mensaje real

    def detener_movimiento(self):
        """
        Detiene inmediatamente cualquier movimiento manual o por trayectoria.
        """
        try:
            if hasattr(self.sdk, 'HRIF_GrpStop'):
                # HRIF_GrpStop requiere boxID y rbtID
                ret = self.sdk.HRIF_GrpStop(self.box_id, self.rbt_id)
                print(f"HRIF_GrpStop enviado. Ret: {ret}")
                return ret
            elif hasattr(self.sdk, 'HRIF_LongMoveEvent'):
                # Si prefieres mantener LongMoveEvent, asegúrate de que el tercer parámetro
                # coincida con el código de interrupción de tu panel de control.
                ret = self.sdk.HRIF_LongMoveEvent(self.box_id, self.rbt_id, 0)
                return ret
        except Exception as e:
            print(f"Error al detener movimiento: {e}")
            return -1

    def configurar_velocidad(self, porcentaje_velocidad):
        """
        Cambia la velocidad global (Override) de 0 a 100.
        """
        try:
            if hasattr(self.sdk, 'HRIF_SetOverride'):
                # Aseguramos límites por seguridad física
                porcentaje_velocidad = max(
                    0, min(100, int(porcentaje_velocidad))
                )

                ret = self.sdk.HRIF_SetOverride(
                    self.box_id, self.rbt_id, porcentaje_velocidad
                )
                print(
                    f"HRIF_SetOverride cambiado a: {porcentaje_velocidad}%. Ret: {ret}"
                )
                return ret
        except Exception as e:
            print(f"Error al configurar velocidad general: {e}")
            return -1