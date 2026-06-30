// =========================================================================
// TELEMETRÍA - CONTROL DE POSICIONES Y ÁNGULOS ARTICULARES (CORREGIDO)
// =========================================================================
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

// Telemetria modelo 3D - REDISEÑO PARA COBOT HANS E05
const contenedor = document.getElementById('cobot-visual-area');

const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(40, contenedor.clientWidth / contenedor.clientHeight, 0.1, 1000);
// Ajustamos la cámara ligeramente de lado para apreciar el desfase tridimensional del E05
camera.position.set(1.4, 1.0, 1.4);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(contenedor.clientWidth, contenedor.clientHeight);
contenedor.appendChild(renderer.domElement);

const controls = new THREE.OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

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

// Eje 6: Brida final (Plato rotatorio plano de ensamble para la pinza)
agregarVolumenE05(J6, new THREE.CylinderGeometry(0.034, 0.034, 0.02, 24), matRobot, 0, 0, 0, Math.PI / 2); 

window.piezasRobot = { j1: J1, j2: J2, j3: J3, j4: J4, j5: J5, j6: J6 };
// FUNCIÓN GLOBAL QUE CONTROLARÁ LA ANIMACIÓN
window.actualizarGemeloDigital = function(angulos) {
    // Límites nativos del E05
    const limites = [360, 135, 153, 360, 180, 360];
    
    // Convertir y validar que sean números reales
    const validados = angulos.map((ang, i) => {
        const num = parseFloat(ang) || 0;
        return Math.max(-limites[i], Math.min(limites[i], num));
    });

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