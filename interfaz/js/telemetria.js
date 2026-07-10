// =========================================================================
// 1. INICIALIZACIÓN DE SOCKET.IO Y TELEMETRÍA UNIFICADA
// =========================================================================
const URL_BASE = "http://localhost:5000"; 
const socket = io(URL_BASE); 

// Confirmación de conexión en la consola
socket.on("connect", () => {
    console.log("Conectado al servidor de control del Cobot vía WebSockets (ID:", socket.id, ")");
});

socket.on("disconnect", () => {
    console.warn("Conexión perdida con el servidor del robot.");
});

// RECEPCIÓN DE TELEMETRÍA EN TIEMPO REAL (REEMPLAZA AL VIEJO FETCH)
socket.on("telemetria", (paquete) => {
    
    // 1. Actualizar Coordenadas Cartesianas (TCP) en el Dashboard
    if (paquete.posicion_cartesiana) {
        if (document.querySelector(".val-x")) document.querySelector(".val-x").innerText = paquete.posicion_cartesiana[0].toFixed(2);
        if (document.querySelector(".val-y")) document.querySelector(".val-y").innerText = paquete.posicion_cartesiana[1].toFixed(2);
        if (document.querySelector(".val-z")) document.querySelector(".val-z").innerText = paquete.posicion_cartesiana[2].toFixed(2);
        if (document.querySelector(".val-rx")) document.querySelector(".val-rx").innerText = paquete.posicion_cartesiana[3].toFixed(2);
        if (document.querySelector(".val-ry")) document.querySelector(".val-ry").innerText = paquete.posicion_cartesiana[4].toFixed(2);
        if (document.querySelector(".val-rz")) document.querySelector(".val-rz").innerText = paquete.posicion_cartesiana[5].toFixed(2);
    }
    
    // 2. Enviar ángulos reales al Gemelo Digital 3D (Three.js) y actualizar los textos de las articulaciones
    if (paquete.angulos_articulares) {
        if (typeof window.actualizarGemeloDigital === "function") {
            window.actualizarGemeloDigital(paquete.angulos_articulares);
        }
    }
});


// =========================================================================
// 2. MANEJO DE EVENTOS JOG (BOTONES + Y - VÍA WEBSOCKET)
// =========================================================================
const botonesJog = document.querySelectorAll(".btn-jog");

botonesJog.forEach(boton => {
    // Al presionar el botón (Soporta Mouse y Pantallas Táctiles)
    boton.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        
        const joint = parseInt(boton.getAttribute("data-joint"), 10);
        const direction = parseInt(boton.getAttribute("data-dir"), 10);

        console.log(`[WS Emit] Iniciando JOG -> J${joint + 1}, Dir: ${direction}`);
        
        // Emitimos el evento directo por el canal de WebSocket
        socket.emit("jog_start", { 
            joint: joint, 
            direction: direction, 
            state: 1 
        });
    });

    // Al soltar el click o remover el dedo
    boton.addEventListener("pointerup", stopRobotMovement);
    // Por seguridad: si arrastran el cursor fuera del botón mientras presionan, se detiene
    boton.addEventListener("pointerleave", stopRobotMovement);
});

function stopRobotMovement() {
    console.log("[WS Emit] Deteniendo JOG");
    // Emitimos el evento de paro inmediato
    socket.emit("jog_stop");
}


// =========================================================================
// 3. MANEJO DEL SLIDER DE VELOCIDAD
// =========================================================================
const sliderVelocidad = document.getElementById("speed-slider");
const textoVelocidad = document.getElementById("speed-value");

if (sliderVelocidad) {
    // Actualización visual en la pantalla en tiempo real (Local)
    sliderVelocidad.addEventListener("input", (e) => {
        const valor = e.target.value;
        textoVelocidad.innerText = `${valor}%`;
    });

    // Enviamos el cambio al servidor únicamente cuando el usuario suelta el slider
    sliderVelocidad.addEventListener("change", (e) => {
        const valor = parseInt(e.target.value, 10);
        
        console.log(`[WS Emit] Cambiando velocidad global a: ${valor}%`);
        // Enviamos la nueva velocidad por WebSocket
        socket.emit("change_speed", { speed: valor });
    });
}


// =========================================================================
// 4. RESPUESTAS DE ERROR DESDE EL SERVIDOR (Para Debugear)
// =========================================================================
socket.on("jog_response", (data) => {
    if (data.status === "error") {
        console.error("Error en el SDK de Huayan al ejecutar JOG:", data.message);
    }
});

socket.on("speed_response", (data) => {
    if (data.status === "error") {
        console.error("Error en el SDK al cambiar velocidad:", data.message);
    }
});


// =========================================================================
// 5. TELEMETRÍA MODELO 3D - COBOT HANS E05 CON GRIPPER METÁLICO
// =========================================================================
const contenedor = document.getElementById('cobot-visual-area');
const scene = new THREE.Scene();

// Ajustamos el FOV ligeramente para acomodar la longitud extra del gripper
const camera = new THREE.PerspectiveCamera(45, contenedor.clientWidth / contenedor.clientHeight, 0.1, 1000);
camera.position.set(1.6, 1.2, 1.6);
camera.lookAt(0, 0.3, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
contenedor.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(0, 0.2, 0);

// Luces
const light = new THREE.DirectionalLight(0xffffff, 1.3);
light.position.set(4, 6, 3);
scene.add(light);
scene.add(new THREE.AmbientLight(0x404040, 1.6));

// Cuadrícula base (Piso)
const gridHelper = new THREE.GridHelper(1.5, 15, 0x444444, 0x2d303e);
gridHelper.position.y = -0.2;
scene.add(gridHelper); 

// AxesHelper para verificar orientación espacial
const axesHelper = new THREE.AxesHelper(1.5);
axesHelper.position.y = -0.2; 
scene.add(axesHelper);

// Materiales de Grado Industrial
const matRobot = new THREE.MeshStandardMaterial({ color: 0xf5f5f7, roughness: 0.25, metalness: 0.05 }); 
const matArticulacion = new THREE.MeshStandardMaterial({ color: 0x1d2026, metalness: 0.6, roughness: 0.3 });
const matGripperFinger = new THREE.MeshStandardMaterial({ color: 0xdddddd, metalness: 0.4, roughness: 0.4 });
const matGripperCuerpo = new THREE.MeshStandardMaterial({ color: 0x222222, metalness: 0.5, roughness: 0.5 });
const matGripperMecanismo = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.7, roughness: 0.3 });
const matGripperMetalClaro = new THREE.MeshStandardMaterial({ color: 0xdddddd, metalness: 0.8, roughness: 0.2 });

// =========================================================================
// CONSTRUCCIÓN CON OFFSETS CINEMÁTICOS (Mapeo real Hans E05)
// =========================================================================
const baseGeo = new THREE.CylinderGeometry(0.065, 0.075, 0.08, 32);
const base = new THREE.Mesh(baseGeo, matRobot);
base.position.y = -0.16;
scene.add(base);

const J1 = new THREE.Group(); 
J1.position.y = 0.04; 
base.add(J1);

const J2 = new THREE.Group(); 
J2.position.set(0, 0.09, 0.055); 
J1.add(J2);

const J3 = new THREE.Group(); 
J3.position.set(0, 0.33, 0); 
J2.add(J3); 

const J4 = new THREE.Group(); 
J4.position.set(0, 0.29, -0.045); 
J3.add(J4); 

const J5 = new THREE.Group(); 
J5.position.set(0, 0.065, 0); 
J4.add(J5); 

const J6 = new THREE.Group(); 
J6.position.set(0, 0.04, 0.035); 
J5.add(J6); 

function agregarVolumenE05(padre, geo, mat, x = 0, y = 0, z = 0, rotX = 0, rotZ = 0) {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);
    mesh.rotation.x = rotX;
    mesh.rotation.z = rotZ;
    padre.add(mesh);
    return mesh;
}

// Volúmenes estructurales
agregarVolumenE05(J1, new THREE.CylinderGeometry(0.05, 0.05, 0.1, 24), matArticulacion, 0, 0.05, 0);
agregarVolumenE05(J2, new THREE.CylinderGeometry(0.048, 0.048, 0.11, 24), matArticulacion, 0, 0, -0.02, Math.PI / 2); 
agregarVolumenE05(J2, new THREE.BoxGeometry(0.052, 0.33, 0.052), matRobot, 0, 0.165, 0); 
agregarVolumenE05(J3, new THREE.CylinderGeometry(0.042, 0.042, 0.1, 24), matArticulacion, 0, 0, 0.02, Math.PI / 2);
agregarVolumenE05(J3, new THREE.BoxGeometry(0.046, 0.29, 0.046), matRobot, 0, 0.145, 0); 
agregarVolumenE05(J4, new THREE.CylinderGeometry(0.035, 0.035, 0.07, 24), matArticulacion, 0, 0.02, 0);
agregarVolumenE05(J5, new THREE.CylinderGeometry(0.032, 0.032, 0.06, 24), matArticulacion, 0, 0, 0, Math.PI / 2);

// Brida final e integración del Gripper
const bridaFinal = agregarVolumenE05(J6, new THREE.CylinderGeometry(0.034, 0.034, 0.02, 24), matRobot, 0, 0, 0, Math.PI / 2); 

const gripperBase = new THREE.Group();
gripperBase.position.set(0, 0, 0.01); 
J6.add(gripperBase);

const centroGeo = new THREE.BoxGeometry(0.04, 0.03, 0.07);
const cuerpoCentro = new THREE.Mesh(centroGeo, matGripperCuerpo);
cuerpoCentro.position.set(0, 0, 0.035);
gripperBase.add(cuerpoCentro);

const placaLatGeo = new THREE.BoxGeometry(0.01, 0.04, 0.05);
const placaL = new THREE.Mesh(placaLatGeo, matGripperCuerpo);
placaL.position.set(0.022, 0, 0.03);
gripperBase.add(placaL);

const placaR = placaL.clone();
placaR.position.x = -0.022;
gripperBase.add(placaR);

const acopleGeo = new THREE.CylinderGeometry(0.028, 0.032, 0.015, 24);
const acople = new THREE.Mesh(acopleGeo, matGripperMetalClaro);
acople.rotation.x = Math.PI / 2;
acople.position.set(0, 0, 0.002);
gripperBase.add(acople);

const eslabonGeo = new THREE.BoxGeometry(0.006, 0.008, 0.035);
const pasadorGeo = new THREE.CylinderGeometry(0.003, 0.003, 0.012, 16);

// Mecanismo Izquierdo
const brazoL1 = new THREE.Mesh(eslabonGeo, matGripperMecanismo);
brazoL1.position.set(0.022, 0.01, 0.055);
brazoL1.rotation.y = Math.PI / 6;
gripperBase.add(brazoL1);

const brazoL2 = brazoL1.clone();
brazoL2.position.y = -0.01;
gripperBase.add(brazoL2);

const pernoL = new THREE.Mesh(pasadorGeo, matGripperMetalClaro);
pernoL.rotation.x = Math.PI / 2;
pernoL.position.set(0.028, 0.01, 0.068);
gripperBase.add(pernoL);

// Mecanismo Derecho
const brazoR1 = new THREE.Mesh(eslabonGeo, matGripperMecanismo);
brazoR1.position.set(-0.022, 0.01, 0.055);
brazoR1.rotation.y = -Math.PI / 6;
gripperBase.add(brazoR1);

const brazoR2 = brazoR1.clone();
brazoR2.position.y = -0.01;
gripperBase.add(brazoR2);

const pernoR = pernoL.clone();
pernoR.position.x = -0.028;
gripperBase.add(pernoR);

// Mordazas finales
const dedoBaseGeo = new THREE.BoxGeometry(0.012, 0.035, 0.025);
const almohadillaGeo = new THREE.BoxGeometry(0.003, 0.028, 0.022);

const fingerL = new THREE.Group();
fingerL.position.set(0.032, 0, 0.075);
const metalDedoL = new THREE.Mesh(dedoBaseGeo, matGripperMetalClaro);
const gomaDedoL = new THREE.Mesh(almohadillaGeo, matGripperCuerpo);
gomaDedoL.position.x = -0.007; 
fingerL.add(metalDedoL, gomaDedoL);
gripperBase.add(fingerL);

const fingerR = new THREE.Group();
fingerR.position.set(-0.032, 0, 0.075);
const metalDedoR = new THREE.Mesh(dedoBaseGeo, matGripperMetalClaro);
const gomaDedoR = new THREE.Mesh(almohadillaGeo, matGripperCuerpo);
gomaDedoR.position.x = 0.007; 
fingerR.add(metalDedoR, gomaDedoR);
gripperBase.add(fingerR);

window.piezasGripper = { base: gripperBase, fingerL: fingerL, fingerR: fingerR };
window.piezasRobot = { j1: J1, j2: J2, j3: J3, j4: J4, j5: J5, j6: J6 };

// =========================================================================
// SISTEMA DE CONTROL CINEMÁTICO REAL
// =========================================================================
window.actualizarGemeloDigital = function(angulos) {
    const limites = [360, 135, 153, 360, 180, 360];
    
    const validados = angulos.map((ang, i) => {
        const num = parseFloat(ang) || 0;
        return Math.max(-limites[i], Math.min(limites[i], num));
    });

    // Rotaciones de los eslabones en Three.js basados en cinemática del robot
    window.piezasRobot.j1.rotation.y = validados[0] * (Math.PI / 180);
    window.piezasRobot.j2.rotation.z = -validados[1] * (Math.PI / 180);
    window.piezasRobot.j3.rotation.z = validados[2] * (Math.PI / 180);
    window.piezasRobot.j4.rotation.y = validados[3] * (Math.PI / 180);
    window.piezasRobot.j5.rotation.z = validados[4] * (Math.PI / 180);
    window.piezasRobot.j6.rotation.y = validados[5] * (Math.PI / 180);

    // Actualiza las etiquetas numéricas de los ángulos (ej. val-j1, val-j2...)
    for (let i = 0; i < 6; i++) {
        const element = document.getElementById(`val-j${i + 1}`);
        if (element) {
            element.innerText = `${validados[i].toFixed(1)}°`;
        }
    }
};

// Loop de Renderizado de la escena
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();

// Responsividad del Canvas
window.addEventListener('resize', () => {
    camera.aspect = contenedor.clientWidth / contenedor.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
});