// ANÁLISIS PREDICTIVO - MONITOREO DE SALUD DE COMPONENTES
document.addEventListener("DOMContentLoaded", () => {
    const URL_BASE = "http://localhost:5000/api/robot";

    function obtenerDatosSalud() {
        fetch(`${URL_BASE}/telemetria`)
            .then(res => res.json())
            .then(data => {
                
                // 1. Actualizar Panel de Errores Activos del Cobot
                if (data.error_robot !== undefined && document.getElementById("robot-error")) {
                    const errorSpan = document.getElementById("robot-error");
                    const errorPanel = document.getElementById("error-panel");
                    
                    errorSpan.innerText = data.error_robot;
                    
                    // Si el código del SDK es diferente de "0", encendemos alerta visual
                    if (data.error_robot !== 0 && data.error_robot !== "0") {
                        errorPanel.classList.add("danger-alert");
                    } else {
                        errorPanel.classList.remove("danger-alert");
                    }
                }

                // 2. Actualizar Corrientes Eléctricas Reales de los Ejes
                if (data.corriente_articulaciones && document.getElementById("current-j1")) {
                    document.getElementById("current-j1").innerText = data.corriente_articulaciones[0].toFixed(2);
                    document.getElementById("current-j2").innerText = data.corriente_articulaciones[1].toFixed(2);
                    document.getElementById("current-j3").innerText = data.corriente_articulaciones[2].toFixed(2);
                    document.getElementById("current-j4").innerText = data.corriente_articulaciones[3].toFixed(2);
                    document.getElementById("current-j5").innerText = data.corriente_articulaciones[4].toFixed(2);
                    document.getElementById("current-j6").innerText = data.corriente_articulaciones[5].toFixed(2);
                }

                // 3. Actualizar Temperaturas de los Motores
                if (data.temperatura_articulaciones && document.getElementById("temp-j1")) {
                    document.getElementById("temp-j1").innerText = data.temperatura_articulaciones[0].toFixed(1);
                    document.getElementById("temp-j2").innerText = data.temperatura_articulaciones[1].toFixed(1);
                    document.getElementById("temp-j3").innerText = data.temperatura_articulaciones[2].toFixed(1);
                    document.getElementById("temp-j4").innerText = data.temperatura_articulaciones[3].toFixed(1);
                    document.getElementById("temp-j5").innerText = data.temperatura_articulaciones[4].toFixed(1);
                    document.getElementById("temp-j6").innerText = data.temperatura_articulaciones[5].toFixed(1);
                }
            })
            .catch(err => console.log("Error en página de análisis predictivo:", err));
    }

    // Sondeo cíclico cada 100ms
    setInterval(obtenerDatosSalud, 100);
});