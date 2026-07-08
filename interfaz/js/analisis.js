// =========================================================================
// ANÁLISIS PREDICTIVO - MONITOREO DE SALUD DE COMPONENTES (WEBSOCKETS)
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
    // 1. Conexión al servidor WebSocket (Reutiliza la misma URL base de tu backend)
    const URL_BASE = "http://localhost:5000"; 
    const socket = io(URL_BASE); 

    console.log("Módulo de Análisis Predictivo inicializado. Esperando flujo de telemetría...");

    // 2. Escuchar el canal 'telemetria' en tiempo real (Elimina los HTTP Fetch cíclicos)
    socket.on("telemetria", (data) => {
        if (!data) return;

        // --- 1. Actualizar Panel de Errores Activos del Cobot ---
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

        // --- 2. Actualizar Corrientes Eléctricas Reales de los Ejes ---
        if (data.corriente_articulaciones && document.getElementById("current-j1")) {
            document.getElementById("current-j1").innerText = data.corriente_articulaciones[0].toFixed(2);
            document.getElementById("current-j2").innerText = data.corriente_articulaciones[1].toFixed(2);
            document.getElementById("current-j3").innerText = data.corriente_articulaciones[2].toFixed(2);
            document.getElementById("current-j4").innerText = data.corriente_articulaciones[3].toFixed(2);
            document.getElementById("current-j5").innerText = data.corriente_articulaciones[4].toFixed(2);
            document.getElementById("current-j6").innerText = data.corriente_articulaciones[5].toFixed(2);
        }

        // --- 3. Actualizar Temperaturas de los Motores ---
        if (data.temperatura_articulaciones && document.getElementById("temp-j1")) {
            document.getElementById("temp-j1").innerText = data.temperatura_articulaciones[0].toFixed(1);
            document.getElementById("temp-j2").innerText = data.temperatura_articulaciones[1].toFixed(1);
            document.getElementById("temp-j3").innerText = data.temperatura_articulaciones[2].toFixed(1);
            document.getElementById("temp-j4").innerText = data.temperatura_articulaciones[3].toFixed(1);
            document.getElementById("temp-j5").innerText = data.temperatura_articulaciones[4].toFixed(1);
            document.getElementById("temp-j6").innerText = data.temperatura_articulaciones[5].toFixed(1);
        }
    });

    // Manejadores de estado de la conexión para depuración
    socket.on("connect", () => {
        console.log("Canal de telemetría térmica/eléctrica conectado con éxito.");
    });

    socket.on("disconnect", () => {
        console.warn("Se interrumpió el flujo de datos de salud de componentes.");
    });
});