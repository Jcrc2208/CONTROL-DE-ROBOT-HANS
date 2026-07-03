// TELEMETRÍA - CONTROL DE POSICIONES Y ÁNGULOS ARTICULARES (CORREGIDO)
document.addEventListener("DOMContentLoaded", () => {
    const URL_BASE = "http://localhost:5000/api/robot";

    function obtenerTelemetriaEstandar() {
        fetch(`${URL_BASE}/telemetria`)
            .then(res => res.json())
            .then(data => {
                // 1. Actualizar Coordenadas Cartesianas (TCP) en el Dashboard
                if (data.posicion_cartesiana && document.getElementById("pos-x")) {
                    document.querySelector("#pos-x span").innerText = data.posicion_cartesiana[0].toFixed(2);
                    document.querySelector("#pos-y span").innerText = data.posicion_cartesiana[1].toFixed(2);
                    document.querySelector("#pos-z span").innerText = data.posicion_cartesiana[2].toFixed(2);
                    document.querySelector("#rot-rx span").innerText = data.posicion_cartesiana[3].toFixed(2);
                    document.querySelector("#rot-ry span").innerText = data.posicion_cartesiana[4].toFixed(2);
                    document.querySelector("#rot-rz span").innerText = data.posicion_cartesiana[5].toFixed(2);
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

// El resto de tu código de Three.js (scene, camera, meshes, window.actualizarGemeloDigital...) se queda EXACTAMENTE IGUAL.
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

// --- ACTUALIZACIÓN: Material específico para las mordazas del gripper con acabado metálico ---
const matGripperFinger = new THREE.MeshStandardMaterial({ 
    color: 0xaaaaaa, // Color base gris claro para metal
    metalness: 1.0,  // Totalmente metálico
    roughness: 0.1,  // Muy pulido/brillante
    envMapIntensity: 1.0 // Intensidad de reflexión (si añades un mapa de entorno luego)
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
    padre.add(mesh);
    return mesh; // Devolvemos el mesh por si necesitamos manipularlo individualmente
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
// EJE 6 Y AGREGADO DEL GRIPPER (Pinza Paralela Metálica)
// =========================================================================

// Eje 6: Brida final (Plato rotatorio plano de ensamble)
const bridaFinal = agregarVolumenE05(J6, new THREE.CylinderGeometry(0.034, 0.034, 0.02, 24), matRobot, 0, 0, 0, Math.PI / 2); 

// --- DISEÑO DEL GRIPPER (Acoplado a J6 para que rote con él) ---

// Base del Gripper (Cuerpo principal)
const gripperBaseGeo = new THREE.BoxGeometry(0.06, 0.04, 0.06); 
// Usamos el material metálico también para el cuerpo principal del gripper para consistencia
const gripperBase = new THREE.Mesh(gripperBaseGeo, matGripperFinger); 
gripperBase.position.set(0, 0, 0.04); // Desfase en Z para salir de la brida
J6.add(gripperBase);

// Guías de deslizamiento (Detalle estético)
const guiaGeo = new THREE.CylinderGeometry(0.005, 0.005, 0.06, 16);
const guiaL = new THREE.Mesh(guiaGeo, matArticulacion); // Guías oscuras para contraste
guiaL.rotation.z = Math.PI / 2;
guiaL.position.set(0, 0.012, 0.01);
gripperBase.add(guiaL);

const guiaR = guiaL.clone();
guiaR.position.y = -0.012;
gripperBase.add(guiaR);

// Dedos del Gripper (Mordazas) - Usando el material metálico
const fingerGeo = new THREE.BoxGeometry(0.015, 0.06, 0.01); // Largos y finos

// Dedo Izquierdo
const fingerL = new THREE.Mesh(fingerGeo, matGripperFinger);
fingerL.position.set(0.02, 0, 0.035); // Posición abierta (X+), sobresaliendo (Z+)
gripperBase.add(fingerL);

// Dedo Derecho
const fingerR = new THREE.Mesh(fingerGeo, matGripperFinger);
fingerR.position.set(-0.02, 0, 0.035); // Posición abierta (X-), sobresaliendo (Z+)
gripperBase.add(fingerR);

// Guardar referencias por si se quiere animar la apertura/cierre después
window.piezasGripper = { base: gripperBase, fingerL: fingerL, fingerR: fingerR };

// =========================================================================
// SISTEMA DE CONTROL Y ANIMACIÓN
// =========================================================================

window.piezasRobot = { j1: J1, j2: J2, j3: J3, j4: J4, j5: J5, j6: J6 };

// FUNCIÓN GLOBAL QUE CONTROLARÁ LA ANIMACIÓN
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

    const joints = ["j1", "j2", "j3", "j4", "j5", "j6"];
    joints.forEach((j, i) => {
        const element = document.querySelector(`#joint-${j} span`);
        if (element) {
            element.innerText = `${validados[i].toFixed(1)}°`;
        }
    });
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