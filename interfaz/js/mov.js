//Lógica Controladora de la Interfaz - Archivo: mov.js
function cambiarConfiguracion(opcion) {
    const placeholder = document.getElementById('msg-placeholder');
    const formPickPlace = document.getElementById('form-pick-place');
    const formDeteccion = document.getElementById('form-deteccion');

    // Ocultamos todos los bloques primero para limpiar la pantalla
    placeholder.style.display = 'none';
    formPickPlace.style.display = 'none';
    formDeteccion.style.display = 'none';

    // Mostramos únicamente el seleccionado
    if (opcion === 'pick_and_place') {
        formPickPlace.style.display = 'block';
    } else if (opcion === 'deteccion') {
        formDeteccion.style.display = 'flex'; 
    }
}

// Actualiza el texto del porcentaje del slider de velocidad
function actualizarVelocidad(valor) {
    document.getElementById('speed-value').innerText = valor + '%';
}