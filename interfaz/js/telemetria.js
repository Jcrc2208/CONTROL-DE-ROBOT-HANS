// TELEMETRÍA - CONTROL DE POSICIONES Y ÁNGULOS ARTICULARES (CORREGIDO)
const URL_BASE = "http://localhost:5000/api/robot";

document.addEventListener("DOMContentLoaded", () => {

    function obtenerTelemetriaEstandar() {
        fetch(`${URL_BASE}/telemetria`)
            .then(res => res.json())
            .then(data => {
                // 1. Actualizar Coordenadas Cartesianas (TCP) en el Dashboard (MODIFICADO CON LAS NUEVAS CLASES)
                if (data.posicion_cartesiana) {
                    if (document.querySelector(".val-x")) document.querySelector(".val-x").innerText = data.posicion_cartesiana[0].toFixed(2);
                    if (document.querySelector(".val-y")) document.querySelector(".val-y").innerText = data.posicion_cartesiana[1].toFixed(2);
                    if (document.querySelector(".val-z")) document.querySelector(".val-z").innerText = data.posicion_cartesiana[2].toFixed(2);
                    if (document.querySelector(".val-rx")) document.querySelector(".val-rx").innerText = data.posicion_cartesiana[3].toFixed(2);
                    if (document.querySelector(".val-ry")) document.querySelector(".val-ry").innerText = data.posicion_cartesiana[4].toFixed(2);
                    if (document.querySelector(".val-rz")) document.querySelector(".val-rz").innerText = data.posicion_cartesiana[5].toFixed(2);
                }

                // 2. CONEXIÓN CRÍTICA: Enviar ángulos reales al Gemelo Digital 3D y textos
                if (data.angulos_articulares) {
                    // Llamamos a la función global que mueve las piezas mecánicas en Three.js
                    if (typeof window.actualizarGemeloDigital === "function") {
                        window.actualizarGemeloDigital(data.angulos_articulares);
                    }
                }
            })
            .catch(err => console.log("Error en página de telemetría:", err));
    }

    // Sondeo cíclico cada 100ms
    setInterval(obtenerTelemetriaEstandar, 100);
});

// --- MANEJO DE EVENTOS JOG (BOTONES + Y -) ---
const botonesJog = document.querySelectorAll(".btn-jog");
botonesJog.forEach(boton => {
    // Al presionar el botón (Soporta Mouse y Pantallas Táctiles)
    boton.addEventListener("pointerdown", (e) => {
        e.preventDefault();
        
        // CORRECCIÓN: Convertimos a entero (int) para que el backend y el SDK de CPS no tengan problemas de tipos
        const joint = parseInt(boton.getAttribute("data-joint"), 10);
        const direction = parseInt(boton.getAttribute("data-dir"), 10);

        fetch(`${URL_BASE}/jog/start`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ joint: joint, direction: direction })
        }).catch(err => console.error("Error al iniciar LongJog:", err));
    });

    // Al soltar el click o remover el dedo
    boton.addEventListener("pointerup", stopRobotMovement);
    // Por seguridad: si arrastran el cursor fuera del botón mientras presionan, se detiene
    boton.addEventListener("pointerleave", stopRobotMovement);
});

// CORRECCIÓN: Esta función ahora puede leer perfectamente 'URL_BASE' al estar en el mismo nivel de ámbito
function stopRobotMovement() {
    fetch(`${URL_BASE}/jog/stop`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    }).catch(err => console.error("Error al detener LongJog:", err));
}

// --- MANEJO DEL SLIDER DE VELOCIDAD ---
const sliderVelocidad = document.getElementById("speed-slider");
const textoVelocidad = document.getElementById("speed-value");

if (sliderVelocidad) {
    sliderVelocidad.addEventListener("input", (e) => {
        const valor = e.target.value;
        textoVelocidad.innerText = `${valor}%`;
    });

    // Enviamos el cambio al servidor únicamente cuando el usuario suelta el slider (Evita saturar peticiones HTTP)
    sliderVelocidad.addEventListener("change", (e) => {
        // CORRECCIÓN: Convertimos el valor a un entero limpio antes de mandarlo por JSON
        const valor = parseInt(e.target.value, 10);
        
        fetch(`${URL_BASE}/speed`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ speed: valor })
        }).catch(err => console.error("Error al enviar velocidad al robot:", err));
    });
}

// Telemetria modelo 3D - REDISEÑO PARA COBOT HANS E05 CON GRIPPER METÁLICO
const contenedor = document.getElementById('cobot-visual-area');

const scene = new THREE.Scene();

// Ajustamos el FOV ligeramente para acomodar la longitud extra del gripper
const camera = new THREE.PerspectiveCamera(45, contenedor.clientWidth / contenedor.clientHeight, 0.1, 1000);
// Posición lateral para apreciar el desfase tridimensional del E05 y el nuevo gripper
camera.position.set(1.6, 1.2, 1.6);
// Apuntar ligeramente más arriba para centrar el robot con la herramienta
camera.lookAt(0, 0.3, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
contenedor.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
// Centrar el objetivo de la cámara un poco más arriba
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

// AxesHelper para verificar orientación espacial de los eslabones
const axesHelper = new THREE.AxesHelper(1.5);
axesHelper.position.y = -0.2; 
scene.add(axesHelper);

// Materiales de Grado Industrial (Estructura blanca/gris claro y juntas oscuras)
const matRobot = new THREE.MeshStandardMaterial({ color: 0xf5f5f7, roughness: 0.25, metalness: 0.05 }); 
const matArticulacion = new THREE.MeshStandardMaterial({ color: 0x1d2026, metalness: 0.6, roughness: 0.3 });

// --- MATERIAL CORREGIDO: Ajuste físico para simular metal/aluminio sin reflejos de entorno oscuros ---
const matGripperFinger = new THREE.MeshStandardMaterial({ 
    color: 0xdddddd,     // Gris claro industrial limpio (aluminio)
    metalness: 0.4,      // Balanceado para que la luz directa lo ilumine en vez de reflejar el "vacío"
    roughness: 0.4,      // Difusión moderada para captar mejor los brillos de la escena
});
// --------------------------------------------------------------------------------------------

// =========================================================================
// CONSTRUCCIÓN CON OFFSETS CINEMÁTICOS (Mapeo real Hans E05)
// =========================================================================
const baseGeo = new THREE.CylinderGeometry(0.065, 0.075, 0.08, 32);
const base = new THREE.Mesh(baseGeo, matRobot);
base.position.y = -0.16;
scene.add(base);

// Nodos Mecánicos (Posiciones jerárquicas con desfases reales)
const J1 = new THREE.Group(); 
J1.position.y = 0.04; 
base.add(J1);

// J2 (Hombro): Desfase lateral en Z para romper la alineación concéntrica
const J2 = new THREE.Group(); 
J2.position.set(0, 0.09, 0.055); 
J1.add(J2);

// J3 (Codo): Separado por la longitud del eslabón principal del hombro
const J3 = new THREE.Group(); 
J3.position.set(0, 0.33, 0); 
J2.add(J3); 

// J4 (Muñeca Pitch): Antebrazo + desfase frontal/lateral característico
const J4 = new THREE.Group(); 
J4.position.set(0, 0.29, -0.045); 
J3.add(J4); 

// J5 (Muñeca Yaw)
const J5 = new THREE.Group(); 
J5.position.set(0, 0.065, 0); 
J4.add(J5); 

// J6 (Brida portaherramientas / Efector final)
const J6 = new THREE.Group(); 
J6.position.set(0, 0.04, 0.035); 
J5.add(J6); 

// Función auxiliar para renderizar los volúmenes relativos
function agregarVolumenE05(padre, geo, mat, x = 0, y = 0, z = 0, rotX = 0, rotZ = 0) {
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(x, y, z);
    mesh.rotation.x = rotX;
    mesh.rotation.z = rotZ;
    padre.add(mesh); // Corregido: referencia directa al parámetro padre
    return mesh;
}

// =========================================================================
// VOLÚMENES GEOMÉTRICOS DEL DISEÑO DEL HANS ROBOT
// =========================================================================

// Eje 1: Base de rotación troncal
agregarVolumenE05(J1, new THREE.CylinderGeometry(0.05, 0.05, 0.1, 24), matArticulacion, 0, 0.05, 0);

// Eje 2: Hombro (Cilindro transversal + brazo estructural desfasado)
agregarVolumenE05(J2, new THREE.CylinderGeometry(0.048, 0.048, 0.11, 24), matArticulacion, 0, 0, -0.02, Math.PI / 2); 
agregarVolumenE05(J2, new THREE.BoxGeometry(0.052, 0.33, 0.052), matRobot, 0, 0.165, 0); 

// Eje 3: Codo (Cilindro transversal + antebrazo industrial)
agregarVolumenE05(J3, new THREE.CylinderGeometry(0.042, 0.042, 0.1, 24), matArticulacion, 0, 0, 0.02, Math.PI / 2);
agregarVolumenE05(J3, new THREE.BoxGeometry(0.046, 0.29, 0.046), matRobot, 0, 0.145, 0); 

// Eje 4: Primera Muñeca (Cilindro vertical de acoplamiento)
agregarVolumenE05(J4, new THREE.CylinderGeometry(0.035, 0.035, 0.07, 24), matArticulacion, 0, 0.02, 0);

// Eje 5: Segunda Muñeca (Cilindro transversal corto de cabeceo)
agregarVolumenE05(J5, new THREE.CylinderGeometry(0.032, 0.032, 0.06, 24), matArticulacion, 0, 0, 0, Math.PI / 2);

// =========================================================================
// EJE 6 Y AGREGADO DEL GRIPPER PRO (Estilo DH Robotics Bitono)
// =========================================================================

// Eje 6: Brida final (Plato rotatorio plano de ensamble)
const bridaFinal = agregarVolumenE05(J6, new THREE.CylinderGeometry(0.034, 0.034, 0.02, 24), matRobot, 0, 0, 0, Math.PI / 2); 

// --- NUEVOS MATERIALES DETALLADOS PARA EL GRIPPER ---
const matGripperCuerpo = new THREE.MeshStandardMaterial({ 
    color: 0x222222,     // Negro mate/antracita para el chasis principal
    metalness: 0.5, 
    roughness: 0.5 
});

const matGripperMecanismo = new THREE.MeshStandardMaterial({ 
    color: 0x111111,     // Negro más oscuro para los eslabones móviles
    metalness: 0.7, 
    roughness: 0.3 
});

const matGripperMetalClaro = new THREE.MeshStandardMaterial({ 
    color: 0xdddddd,     // Aluminio pulido para las puntas y pasadores
    metalness: 0.8, 
    roughness: 0.2 
});

// Contenedor principal del Gripper (Anclado a J6)
const gripperBase = new THREE.Group();
gripperBase.position.set(0, 0, 0.01); // Pegado a la brida
J6.add(gripperBase);

// 1. CUERPO CENTRAL (Chasis estilizado)
const centroGeo = new THREE.BoxGeometry(0.04, 0.03, 0.07);
const cuerpoCentro = new THREE.Mesh(centroGeo, matGripperCuerpo);
cuerpoCentro.position.set(0, 0, 0.035);
gripperBase.add(cuerpoCentro);

// Placas laterales embellecedoras (Efecto biselado/ensanchado)
const placaLatGeo = new THREE.BoxGeometry(0.01, 0.04, 0.05);
const placaL = new THREE.Mesh(placaLatGeo, matGripperCuerpo);
placaL.position.set(0.022, 0, 0.03);
gripperBase.add(placaL);

const placaR = placaL.clone();
placaR.position.x = -0.022;
gripperBase.add(placaR);

// Acople cilíndrico superior (Donde se une al robot)
const acopleGeo = new THREE.CylinderGeometry(0.028, 0.032, 0.015, 24);
const acople = new THREE.Mesh(acopleGeo, matGripperMetalClaro);
acople.rotation.x = Math.PI / 2;
acople.position.set(0, 0, 0.002);
gripperBase.add(acople);


// 2. MECANISMO DE ESLABONES (Brazos negros del pantógrafo)
const eslabonGeo = new THREE.BoxGeometry(0.006, 0.008, 0.035);
const pasadorGeo = new THREE.CylinderGeometry(0.003, 0.003, 0.012, 16);

// --- LADO IZQUIERDO (Eslabones) ---
const brazoL1 = new THREE.Mesh(eslabonGeo, matGripperMecanismo);
brazoL1.position.set(0.022, 0.01, 0.055);
brazoL1.rotation.y = Math.PI / 6; // Inclinación hacia afuera
gripperBase.add(brazoL1);

const brazoL2 = brazoL1.clone();
brazoL2.position.y = -0.01; // Eslabón paralelo inferior
gripperBase.add(brazoL2);

// Detalles de pasadores brillantes (Pernos plateados en las uniones)
const pernoL = new THREE.Mesh(pasadorGeo, matGripperMetalClaro);
pernoL.rotation.x = Math.PI / 2;
pernoL.position.set(0.028, 0.01, 0.068);
gripperBase.add(pernoL);


// --- LADO DERECHO (Eslabones) ---
const brazoR1 = new THREE.Mesh(eslabonGeo, matGripperMecanismo);
brazoR1.position.set(-0.022, 0.01, 0.055);
brazoR1.rotation.y = -Math.PI / 6; // Inclinación simétrica
gripperBase.add(brazoR1);

const brazoR2 = brazoR1.clone();
brazoR2.position.y = -0.01;
gripperBase.add(brazoR2);

const pernoR = pernoL.clone();
pernoR.position.x = -0.028;
gripperBase.add(pernoR);


// 3. DEDOS / MORDAZAS FINALES (Puntas Metálicas de Sujeción)
// Base del dedo (Bloque de aluminio) + Almohadilla de agarre
const dedoBaseGeo = new THREE.BoxGeometry(0.012, 0.035, 0.025);
const almohadillaGeo = new THREE.BoxGeometry(0.003, 0.028, 0.022);

// --- Dedo Izquierdo ---
const fingerL = new THREE.Group();
fingerL.position.set(0.032, 0, 0.075); // Posición abierta

const metalDedoL = new THREE.Mesh(dedoBaseGeo, matGripperMetalClaro);
const gomaDedoL = new THREE.Mesh(almohadillaGeo, matGripperCuerpo); // Goma interna oscura
gomaDedoL.position.x = -0.007; 
fingerL.add(metalDedoL, gomaDedoL);
gripperBase.add(fingerL);

// --- Dedo Derecho ---
const fingerR = new THREE.Group();
fingerR.position.set(-0.032, 0, 0.075); // Posición abierta simétrica

const metalDedoR = new THREE.Mesh(dedoBaseGeo, matGripperMetalClaro);
const gomaDedoR = new THREE.Mesh(almohadillaGeo, matGripperCuerpo);
gomaDedoR.position.x = 0.007; 
fingerR.add(metalDedoR, gomaDedoR);
gripperBase.add(fingerR);


// Guardar referencias manteniendo los mismos nombres por si animas apertura/cierre
window.piezasGripper = { base: gripperBase, fingerL: fingerL, fingerR: fingerR };

// =========================================================================
// SISTEMA DE CONTROL Y ANIMACIÓN
// =========================================================================

window.piezasRobot = { j1: J1, j2: J2, j3: J3, j4: J4, j5: J5, j6: J6 };

// FUNCIÓN GLOBAL QUE CONTROLARÁ LA ANIMACIÓN (MODIFICADA PARA PRESERVAR BOTONES)
window.actualizarGemeloDigital = function(angulos) {
    const limites = [360, 135, 153, 360, 180, 360];
    
    const validados = angulos.map((ang, i) => {
        const num = parseFloat(ang) || 0;
        return Math.max(-limites[i], Math.min(limites[i], num));
    });

    window.piezasRobot.j1.rotation.y = validados[0] * (Math.PI / 180);
    window.piezasRobot.j2.rotation.z = -validados[1] * (Math.PI / 180);
    window.piezasRobot.j3.rotation.z = validados[2] * (Math.PI / 180);
    window.piezasRobot.j4.rotation.y = validados[3] * (Math.PI / 180);
    window.piezasRobot.j5.rotation.z = validados[4] * (Math.PI / 180);
    window.piezasRobot.j6.rotation.y = validados[5] * (Math.PI / 180);

    // MODIFICADO: Ahora apunta exclusivamente al ID del span dinámico interno val-jX
    for (let i = 0; i < 6; i++) {
        const element = document.getElementById(`val-j${i + 1}`);
        if (element) {
            element.innerText = `${validados[i].toFixed(1)}°`;
        }
    }
};

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}
animate();

window.addEventListener('resize', () => {
    camera.aspect = contenedor.clientWidth / contenedor.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
});