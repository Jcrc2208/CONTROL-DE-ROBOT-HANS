Este módulo contiene la arquitectura de software desarrollada en Python (Flask) y JavaScript para la adquisición y visualización de datos en tiempo real (telemetría) del brazo robótico colaborativo **Huayan/Hans Robot**.

La aplicación consulta de manera cíclica las coordenadas espaciales y los ángulos articulares directamente desde el controlador físico del robot a través de su SDK nativo.


El flujo de datos está estructurado en tres capas independientes siguiendo principios de Clean Code:

1. **Frontend (UI):** Una interfaz web construida con HTML5, CSS3 avanzados (Grid/Flexbox) y JavaScript Vanilla (`main.js`) que realiza sondeos asíncronos (`fetch`) cada 100ms.
2. **Servidor HTTP (Backend):** Una API REST construida con **Flask** que expone un endpoint seguro (`/api/robot/telemetria`) y gestiona las solicitudes de manera síncrona sin duplicar hilos de comunicación.
3. **Capa de Hardware (Manager):** La clase `RobotHuayanManager` que encapsula el cliente SDK (`CPSClient`), controla la apertura y reconexión automática del socket TCP/IP en el puerto `10003`, e inyecta buffers mutables a las funciones nativas de lectura.


### Pre-requisitos
* Python 3.10 o superior instalado.
* Tarjeta de red configurada en el mismo segmento que el controlador del robot:
  * **IP del Robot:** `192.168.10.11`
  * **Puerto:** `10003`

### Dependencias de Python
Instala los paquetes necesarios utilizando `pip`:

bash
pip install Flask flask-cors