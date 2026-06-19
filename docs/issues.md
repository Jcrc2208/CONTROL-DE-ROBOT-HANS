"""
-errores en protocoolos de comunicacion modbus , ethercaat, IP

estos errores se producen principalmente porque no existe comuncacion viable entre doferente protcolos basicmante para establecer comunicacion entre el cobot S05 , controlador y la laptop se establecio un protocoolo de funcionamiento  por direccion IP es decir se establlece un scaneo de direcciones, este escaneo se habilita por la terminal (cmd)el comando para establecer ese scaneo de redes es [arp -a] este comando realiza un scaneo de las direcciones ip disponibles que se conocen en tu pc ahora es importance mencionar los prefijos que tienen la direccion IP normalmente los prefijos establecidos son (192.168.) estas driecciones son predeterminas entre dispositos los que relamente importan los ultimos prefios que son los nobrados prefijos de canal y numero de dispositivo que son esos (192.168.10.18) los ultimos dos los que importan para establecer comunicacion el prefijo numero 10 es el canal le puedes asignaar cualquier pero debe de estar en el mismo canal que el dispositivo con el que deseas establecer comunicacion y el ultimo digito solo es numero de dispositivo pedes asignar desde el 1 al 200 pero no debe de tener el mismo numero que el otro dispositivo.

-una vez asegurandose esa interpretacion entre los canales y prefijos correctos establecimos comunicacion es decir escribimos el comando ping y la direccion del dispositivo en este caso es ping(192.168.10.18)


C:\Users\magad>ping 192.168.10.11

Haciendo ping a 192.168.10.11 con 32 bytes de datos:
Respuesta desde 192.168.10.11: bytes=32 tiempo=1ms TTL=64
Respuesta desde 192.168.10.11: bytes=32 tiempo=1ms TTL=64
Respuesta desde 192.168.10.11: bytes=32 tiempo=1ms TTL=64
Respuesta desde 192.168.10.11: bytes=32 tiempo=1ms TTL=64

Estadísticas de ping para 192.168.10.11:
    Paquetes: enviados = 4, recibidos = 4, perdidos = 0
    (0% perdidos),
Tiempos aproximados de ida y vuelta en milisegundos:
    Mínimo = 1ms, Máximo = 1ms, Media = 1ms

----------se muestran  estos comandos de confirmacion que se establecio la corecta comunicacion entre dispostivos.....

"""

"""
reduccion de latencia en el algoritmo base para el control de movimiento armonico entre los 6 ejes del brazo robtico (HANS ROBOTS) y el gripper DH ROBOTICS

