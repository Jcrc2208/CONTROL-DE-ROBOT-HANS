// TELEMETRÍA - CONTROL DE POSICIONES Y ÁNGULOS ARTICULARES
document.addEventListener("DOMContentLoaded", () => {
    const URL_BASE = "http://localhost:5000/api/robot";

    function obtenerTelemetriaEstandar() {
        fetch(`${URL_BASE}/telemetria`)
            .then(res => res.json())
            .then(data => {
                // 1. Actualizar Coordenadas Cartesianas (TCP)
                if (data.posicion_cartesiana && document.getElementById("pos-x")) {
                    document.querySelector("#pos-x span").innerText = data.posicion_cartesiana[0].toFixed(2);
                    document.querySelector("#pos-y span").innerText = data.posicion_cartesiana[1].toFixed(2);
                    document.querySelector("#pos-z span").innerText = data.posicion_cartesiana[2].toFixed(2);
                    document.querySelector("#rot-rx span").innerText = data.posicion_cartesiana[3].toFixed(2);
                    document.querySelector("#rot-ry span").innerText = data.posicion_cartesiana[4].toFixed(2);
                    document.querySelector("#rot-rz span").innerText = data.posicion_cartesiana[5].toFixed(2);
                }

                // 2. Actualizar Grados de cada Eje (Ángulos)
                if (data.angulos_articulares && document.getElementById("joint-j1")) {
                    document.querySelector("#joint-j1 span").innerText = `${data.angulos_articulares[0].toFixed(1)}`;
                    document.querySelector("#joint-j2 span").innerText = `${data.angulos_articulares[1].toFixed(1)}`;
                    document.querySelector("#joint-j3 span").innerText = `${data.angulos_articulares[2].toFixed(1)}`;
                    document.querySelector("#joint-j4 span").innerText = `${data.angulos_articulares[3].toFixed(1)}`;
                    document.querySelector("#joint-j5 span").innerText = `${data.angulos_articulares[4].toFixed(1)}`;
                    document.querySelector("#joint-j6 span").innerText = `${data.angulos_articulares[5].toFixed(1)}`;
                }
            })
            .catch(err => console.log("Error en página de telemetría:", err));
    }

    // Sondeo cíclico cada 100ms
    setInterval(obtenerTelemetriaEstandar, 100);
});


//Telemetria modelo 3D
 // 1. Obtener el contenedor real del HTML
    const contenedor = document.getElementById('cobot-visual-area');

    // 2. Escena, Cámara y Renderizador acoplados al tamaño de la caja
    const scene = new THREE.Scene();
    //scene.background = new THREE.Color(0x1a1c23); // Fondo gris oscuro para hacer match con tu Dashboard

    const camera = new THREE.PerspectiveCamera(40, contenedor.clientWidth / contenedor.clientHeight, 0.1, 1000);
    camera.position.set(1.2, 1.2, 1.2);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
    contenedor.appendChild(renderer.domElement);

    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;

    // Luces
    const light = new THREE.DirectionalLight(0xffffff, 1.2);
    light.position.set(3, 5, 3);
    scene.add(light);
    scene.add(new THREE.AmbientLight(0x404040, 1.5));

    // Cuadrícula base (Piso)
    const gridHelper = new THREE.GridHelper(1.5, 15, 0x444444, 0x2d303e);
    gridHelper.position.y = -0.2;
    scene.add(gridHelper);

    // 3. Materiales cinemáticos
    const matRobot = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.3 }); // Cuerpo Blanco
    const matArticulacion = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.8, roughness: 0.2 });
    // Construcción del esqueleto anatómico
    const baseGeo = new THREE.CylinderGeometry(0.06, 0.07, 0.08, 32);
    const base = new THREE.Mesh(baseGeo, matRobot);
    base.position.y = -0.16;
    scene.add(base);

    const J1 = new THREE.Group(); J1.position.y = 0.04; base.add(J1);
    const J2 = new THREE.Group(); J2.position.y = 0.12; J1.add(J2);
    const J3 = new THREE.Group(); J3.position.y = 0.28; J2.add(J3); 
    const J4 = new THREE.Group(); J4.position.y = 0.22; J3.add(J4); 
    const J5 = new THREE.Group(); J5.position.y = 0.07; J4.add(J5); 
    const J6 = new THREE.Group(); J6.position.y = 0.04; J5.add(J6); 

    // Añadir volúmenes visuales a los nodos mecánicos
    function agregarVolumen(padre, geo, mat, yPos = 0, rotX = 0) {
        const mesh = new THREE.Mesh(geo, mat);
        mesh.position.y = yPos;
        mesh.rotation.x = rotX;
        padre.add(mesh);
    }

    agregarVolumen(J1, new THREE.CylinderGeometry(0.045, 0.045, 0.12, 16), matArticulacion, 0.06);
    agregarVolumen(J2, new THREE.CylinderGeometry(0.04, 0.04, 0.1, 16), matArticulacion, 0, Math.PI / 2);
    agregarVolumen(J2, new THREE.BoxGeometry(0.045, 0.28, 0.045), matRobot, 0.14); 
    agregarVolumen(J3, new THREE.CylinderGeometry(0.035, 0.035, 0.08, 16), matArticulacion, 0, Math.PI / 2);
    agregarVolumen(J3, new THREE.BoxGeometry(0.04, 0.22, 0.04), matRobot, 0.11); 
    agregarVolumen(J4, new THREE.CylinderGeometry(0.03, 0.03, 0.06, 16), matArticulacion, 0);
    agregarVolumen(J5, new THREE.CylinderGeometry(0.028, 0.028, 0.05, 16), matArticulacion, 0, Math.PI / 2);
    agregarVolumen(J6, new THREE.CylinderGeometry(0.03, 0.03, 0.015, 16), matRobot, 0.01); 

    window.piezasRobot = { j1: J1, j2: J2, j3: J3, j4: J4, j5: J5, j6: J6 };

    // FUNCIÓN GLOBAL QUE LLAMARÁS DESDE TU ARCHIVO JS AL RECIBIR DATOS
    window.actualizarGemeloDigital = function(angulos) {
        // Límites nativos del E05
        const limites = [360, 135, 153, 360, 180, 360];
        
        const validados = angulos.map((ang, i) => Math.max(-limites[i], Math.min(limites[i], ang)));

        // Mapeo anatómico directo a la animación 3D
        window.piezasRobot.j1.rotation.y = validados[0] * (Math.PI / 180);
        window.piezasRobot.j2.rotation.z = validados[1] * (Math.PI / 180);
        window.piezasRobot.j3.rotation.z = validados[2] * (Math.PI / 180);
        window.piezasRobot.j4.rotation.y = validados[3] * (Math.PI / 180);
        window.piezasRobot.j5.rotation.z = validados[4] * (Math.PI / 180);
        window.piezasRobot.j6.rotation.y = validados[5] * (Math.PI / 180);

        // Actualizar textos de los bloques en tu Dashboard automáticamente
        document.querySelector("#joint-j1 span").innerText = `${validados[0].toFixed(1)}°`;
        document.querySelector("#joint-j2 span").innerText = `${validados[1].toFixed(1)}°`;
        document.querySelector("#joint-j3 span").innerText = `${validados[2].toFixed(1)}°`;
        document.querySelector("#joint-j4 span").innerText = `${validados[3].toFixed(1)}°`;
        document.querySelector("#joint-j5 span").innerText = `${validados[4].toFixed(1)}°`;
        document.querySelector("#joint-j6 span").innerText = `${validados[5].toFixed(1)}°`;
    };

    // Bucle de rendering continuo
    function animate() {
        requestAnimationFrame(animate);
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // Evento de ajuste responsivo
    window.addEventListener('resize', () => {
        camera.aspect = contenedor.clientWidth / contenedor.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
    });

    // Simulador de prueba inicial (remover al meter la telemetría real)
    //setTimeout(() => { window.actualizarGemeloDigital([12.89, 11.38, 92.51, -3.83, 70.12, -25.80]); }, 1200);