document.addEventListener("DOMContentLoaded", () => {
    const URL_BASE = "http://localhost:5000/api/usuarios";
    
    const btnAddUser = document.getElementById("btn-add-user");
    const userModal = document.getElementById("user-modal");
    const btnCloseModal = document.getElementById("btn-close-modal");
    const addUserForm = document.getElementById("add-user-form");
    const tableBody = document.getElementById("users-table-body");

    // =========================================================
    // ACCIÓN 1: Control de apertura y cierre del Modal Emergente
    // =========================================================
    btnAddUser.addEventListener("click", () => userModal.style.display = "flex");
    btnCloseModal.addEventListener("click", () => userModal.style.display = "none");

    // =========================================================
    // ACCIÓN 2: Cargar y renderizar usuarios reales de SQLite
    // =========================================================
    function cargarUsuarios() {
        fetch(URL_BASE)
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    // Limpiar las filas estáticas de muestra del HTML
                    tableBody.innerHTML = ""; 

                    // Iterar sobre cada usuario de la BD e inyectar la fila
                    data.usuarios.forEach(usuario => {
                        // Determinar la clase CSS del tag de rol según corresponda
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

    // Ejecutar la carga automática al entrar a la pantalla
    cargarUsuarios();

    // =========================================================
    // ACCIÓN 3: Interceptar formulario y enviar POST a Flask
    // =========================================================
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
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(nuevoUsuario)
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                alert("Usuario guardado exitosamente en SQLite");
                userModal.style.display = "none";
                addUserForm.reset();
                cargarUsuarios(); // Recarga la tabla de inmediato sin refrescar toda la página
            } else {
                alert("Error del servidor: " + data.message);
            }
        })
        .catch(err => console.error("Error en la petición POST:", err));
    });
});