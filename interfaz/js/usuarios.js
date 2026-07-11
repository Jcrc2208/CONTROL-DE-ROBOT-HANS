document.addEventListener("DOMContentLoaded", () => {
    const URL_BASE = "/api/usuarios";
    // const URL_BASE = "http://localhost:5000/api/usuarios";

    const btnAddUser = document.getElementById("btn-add-user");
    const userModal = document.getElementById("user-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const addUserForm = document.getElementById("add-user-form");
    const tableBody = document.getElementById("users-table-body");

    // =========================================================
    // ACCIÓN 1: Control de apertura y cierre del Modal Emergente
    // =========================================================
    if(btnAddUser) btnAddUser.addEventListener("click", () => userModal.style.display = "flex");
    if(btnCloseModal) btnCloseModal.addEventListener("click", () => userModal.style.display = "none");

    // =========================================================
    // ACCIÓN 2: Cargar y renderizar usuarios reales de SQLite
    // =========================================================
    function cargarUsuarios() {
        fetch(URL_BASE)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    tableBody.innerHTML = ""; 

                    data.usuarios.forEach(usuario => {
                        const rolClass = usuario.rol.toLowerCase() === 'admin' ? 'admin' : 'operator';
                        const rolTexto = usuario.rol.toLowerCase() === 'admin' ? 'Administrador' : 'Operador';

                        const fila = document.createElement("tr");
                        fila.className = "user-row";
                        fila.id = `user-${usuario.id}`;

                        fila.innerHTML = `
                            <td>
                                <strong class="user-name">${usuario.nombre}</strong>
                                <span class="user-id">ID: #00${usuario.id}</span>
                            </td>
                            <td class="user-email">${usuario.correo}</td>
                            <td>
                                <span class="role-tag ${rolClass}">${rolTexto}</span>
                            </td>
                            <td class="user-timestamp">${usuario.ultima_conexion}</td>
                            <td class="text-right">
                                <button class="delete-user-btn" data-id="${usuario.id}">
                                    <i class="fa-solid fa-user-minus"></i> Dar de Baja
                                </button>
                            </td>
                        `;
                        tableBody.appendChild(fila);
                    });
                } else {
                    console.error("Error al obtener usuarios:", data.message);
                }
            })
            .catch(err => console.error("Error en la petición GET:", err));
    }

    // Ejecutar la carga automática al entrar
    cargarUsuarios();

    // =========================================================
    // ACCIÓN 3: Interceptación de formulario (POST)
    // =========================================================
    if(addUserForm) {
        addUserForm.addEventListener("submit", (e) => {
            e.preventDefault(); 
            const nuevoUsuario = {
                nombre: document.getElementById("modal-nombre").value,
                correo: document.getElementById("modal-correo").value,
                password: document.getElementById("modal-password").value,
                rol: document.getElementById("modal-rol").value
            };

            fetch(URL_BASE, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(nuevoUsuario)
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    alert("Usuario guardado exitosamente en SQLite");
                    userModal.style.display = "none";
                    addUserForm.reset();
                    cargarUsuarios();
                } else {
                    alert("Error del servidor: " + data.message);
                }
            })
            .catch(err => console.error("Error en la petición POST:", err));
        });
    }

    // =========================================================
    // ACCIÓN 4: Dar de baja con Efecto de Animación CSS/JS
    // =========================================================
    if(tableBody) {
        tableBody.addEventListener("click", (e) => {
            const botonEliminar = e.target.closest(".delete-user-btn");
            
            if (botonEliminar) {
                const usuarioId = botonEliminar.dataset.id;
                const filaObjetivo = document.getElementById(`user-${usuarioId}`);
                
                if (confirm(`¿Estás seguro de que deseas dar de baja al usuario con ID #${usuarioId}?`)) {
                    
                    fetch(`${URL_BASE}/${usuarioId}`, {
                        method: "DELETE",
                        headers: { "Content-Type": "application/json" }
                    })
                    .then(res => res.json())
                    .then(data => {
                        if (data.status === "success") {
                            // SI HAY ANIMACIÓN: Desvanecido gradual antes de limpiar del DOM
                            if (filaObjetivo) {
                                filaObjetivo.style.transition = "all 0.4s ease";
                                filaObjetivo.style.opacity = "0";
                                filaObjetivo.style.transform = "translateX(20px)";
                                
                                // Esperar a que la transición termine para refrescar la tabla limpia
                                setTimeout(() => {
                                    cargarUsuarios();
                                }, 400);
                            } else {
                                cargarUsuarios();
                            }
                        } else {
                            alert("Error del servidor: " + data.message);
                        }
                    })
                    .catch(err => {
                        console.error("Error en la petición DELETE:", err);
                        alert("No se pudo conectar con el servidor.");
                    });
                }
            }
        });
    }
});