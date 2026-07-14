Huayan Control Industrial

Roadmap Funcional V2

Arquitectura de Módulos y Evolución de la Plataforma

Objetivo General

La evolución de Huayan Control Industrial tiene como propósito convertirse en una plataforma integral para la supervisión, operación, configuración y administración de robots colaborativos Hans Robotics, permitiendo centralizar en una única interfaz todas las herramientas necesarias para la puesta en marcha, monitoreo y análisis del robot.

La plataforma no busca limitarse a una aplicación específica, sino establecer una arquitectura escalable capaz de adaptarse a diferentes aplicaciones industriales como Pick & Place, Machine Tending, inspección, manipulación de materiales, automatización de procesos y futuras integraciones con Inteligencia Artificial y Gemelo Digital.

---


Módulo Dashboard

Objetivo

Proporcionar al usuario una vista general del estado operativo del robot colaborativo y de la plataforma.

Funcionalidades

- Estado actual del robot.
- Estado de conexión.
- Tiempo de operación.
- Producción del día.
- Alarmas activas.
- Últimos eventos registrados.
- Resumen general de la operación.
- Accesos rápidos hacia los módulos principales.

Este módulo funcionará como el centro de operación de la plataforma.



---

Módulo Robot

Objetivo

Centralizar toda la información técnica del robot colaborativo.

Funcionalidades

- Estado del controlador.
- Estado del robot.
- Posición actual.
- Coordenadas cartesianas.
- Posición articular.
- Herramienta activa.
- Payload configurado.
- Variables de operación.
- Entradas y salidas digitales.
- Información de conexión.

Este módulo permitirá visualizar en tiempo real la información necesaria para la supervisión del cobot.

---



Módulo Control Manual

Objetivo

Permitir al operador controlar el robot manualmente durante tareas de configuración, pruebas y mantenimiento.

Funcionalidades

Movimiento Cartesiano

- Movimiento en eje X.
- Movimiento en eje Y.
- Movimiento en eje Z.
- Rotación RX.
- Rotación RY.
- Rotación RZ.

Movimiento Articular

- Movimiento individual de cada articulación.
- Configuración de velocidad.
- Configuración de paso incremental.
- Regreso automático a Home.
- Paro inmediato del movimiento.

Este módulo reproducirá una experiencia similar a la pestaña Jog disponible en el controlador del robot.

---



Módulo Free Drive

Objetivo

Facilitar la enseñanza de posiciones directamente desde la plataforma.

Funcionalidades

- Activar modo Free Drive.
- Desactivar modo Free Drive.
- Capturar posición actual.
- Guardar automáticamente las coordenadas.
- Asignar nombre al punto.
- Editar puntos existentes.
- Eliminar puntos.

El operador podrá mover manualmente el robot y registrar posiciones sin introducir coordenadas manualmente.

---




Módulo Supervisión Remota

Objetivo

Permitir la supervisión del robot desde cualquier ubicación mediante acceso remoto seguro.

Funcionalidades

- Visualización del estado del robot.
- Variables en tiempo real.
- Alarmas.
- Colisiones.
- Eventos.
- Registro histórico.
- Diagnóstico remoto.

La plataforma diferenciará claramente entre supervisión remota y control remoto.

Las operaciones que comprometan la seguridad del sistema, como la recuperación después de una parada de emergencia o una colisión, deberán requerir intervención presencial cuando las condiciones de seguridad así lo exijan.

---



Módulo Telemetría

Objetivo

Capturar información operacional para generar indicadores de desempeño.

Variables

- Horas de operación.
- Tiempo de ciclo.
- Producción.
- Frecuencia de errores.
- Colisiones.
- Estado de los ejes.
- Alarmas.
- Eventos.
- Tendencias operativas.

La información recopilada permitirá desarrollar herramientas avanzadas de análisis.

---



Módulo Alarmas

Objetivo

Centralizar todos los eventos críticos registrados durante la operación.

Funcionalidades

- Historial de alarmas.
- Clasificación por prioridad.
- Código de error.
- Descripción.
- Hora de ocurrencia.
- Estado de resolución.
- Búsqueda por fecha.
- Filtros.

---



Módulo Historial

Objetivo

Registrar todas las actividades realizadas dentro del sistema.

Funcionalidades

- Historial de movimientos.
- Historial de aplicaciones ejecutadas.
- Historial de usuarios.
- Historial de cambios.
- Historial de eventos.
- Exportación de registros.

---



Módulo Inteligencia Artificial

Objetivo

Asistir al operador mediante análisis inteligente de la información generada por la plataforma.

Funcionalidades

- Detección de tendencias.
- Análisis de comportamiento.
- Recomendaciones de mantenimiento.
- Alertas inteligentes.
- Diagnóstico preliminar.
- Evaluación de productividad.
- Predicción de fallas.

Este módulo evolucionará conforme aumente la cantidad de información disponible mediante la telemetría.

---



Módulo Configuración

Objetivo

Administrar todos los parámetros generales de la plataforma.

Funcionalidades

- Configuración de usuarios.
- Roles y permisos.
- Robots registrados.
- Parámetros de comunicación.
- Configuración del Offset.
- Configuración del Safe Point.
- Configuración de velocidades.
- Preferencias generales.
- Integraciones futuras.

---



Arquitectura de Comunicación

La plataforma evolucionará hacia una arquitectura basada en un Gateway Industrial que elimine la dependencia de introducir manualmente la dirección IP del controlador.

El Gateway será responsable de establecer la comunicación con el robot y exponer los servicios necesarios hacia Huayan Control Industrial mediante una interfaz segura.

Se contempla la integración futura con tecnologías como VPN, túneles seguros y soluciones de acceso remoto administrado para facilitar el despliegue en diferentes instalaciones industriales sin modificar la experiencia del usuario final.



---

Visión a Largo Plazo

Huayan Control Industrial evolucionará desde una plataforma de supervisión hacia un ecosistema inteligente de automatización industrial, integrando telemetría avanzada, inteligencia artificial, mantenimiento predictivo, visión artificial y gemelo digital, convirtiéndose en una solución escalable para la administración de robots colaborativos Hans Robotics en múltiples aplicaciones industriales.