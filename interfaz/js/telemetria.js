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