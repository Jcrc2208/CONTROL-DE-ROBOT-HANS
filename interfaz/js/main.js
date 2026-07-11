// CONTROL DE TRASLACIÓN DE IMÁGENES Y TEXTOS SINCRO-SCROLL (SCROLLYTELLING)
if (typeof gsap !== "undefined" && typeof ScrollTrigger !== "undefined") {
    gsap.registerPlugin(ScrollTrigger);
    const mainTimeline = gsap.timeline({
        scrollTrigger: {
            trigger: ".scrolly-container", 
            start: "top top",              
            end: "bottom bottom",          
            scrub: 1,                      
        }
    });

    const totalSteps = 4; 

    for (let i = 1; i < totalSteps; i++) {
        const currentStep = `.step-${i}`;
        const nextStep = `.step-${i + 1}`;
        const currentText = `#step-text-${i}`;
        const nextText = `#step-text-${i + 1}`;

        mainTimeline
            .to(currentStep, { opacity: 0, y: -30, duration: 1, ease: "power2.out" }, "+=0.5")
            .to(currentText, { opacity: 0, y: -30, duration: 1, ease: "power2.out" }, "<")
            
            .fromTo(nextStep, 
                { opacity: 0, y: 30, scale: 0.95 }, 
                { opacity: 1, y: 0, scale: 1, duration: 1.2, ease: "power3.out" }, 
                "<"
            )
            .fromTo(nextText, 
                { opacity: 0, y: 30 }, 
                { opacity: 1, y: 0, duration: 1, ease: "power3.out" }, 
                "<"
            );
    }
}

// DETECTOR DE SECCIÓN ACTIVA PARA EL MENÚ (OPTIMIZADO)
const menuLinks = document.querySelectorAll('.main-nav a');
const sections = document.querySelectorAll('.tab-content');
let isScrollingByClick = false;

function changeActiveMenu(id) {
    menuLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${id}`) {
            link.classList.add('active');
        }
    });
}

if (sections.length > 0) {
    const observerOptions = {
        root: null,
        rootMargin: "-40% 0px -40% 0px", 
        threshold: 0
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        if (isScrollingByClick) return;

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const currentId = entry.target.getAttribute('id');
                changeActiveMenu(currentId);
            }
        });
    }, observerOptions);

    sections.forEach(section => sectionObserver.observe(section));
}

menuLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        const targetId = link.getAttribute('href').replace('#', '');
        isScrollingByClick = true;
        changeActiveMenu(targetId);
        
        setTimeout(() => {
            isScrollingByClick = false;
        }, 800); 
    });
});

// CONTROL DE PESTAÑAS (TAB SYSTEM)
const tabButtons = document.querySelectorAll(".tab-btn");
const tabContents = document.querySelectorAll(".tab-content");

tabButtons.forEach(button => {
    button.addEventListener("click", (e) => {
        e.preventDefault();
        const target = button.dataset.tab;

        tabButtons.forEach(btn => btn.classList.remove("active"));
        tabContents.forEach(content => content.classList.remove("active"));

        button.classList.add("active");
        const element = document.getElementById(target);
        if (element) element.classList.add("active");

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
});

// =========================================================================
// SISTEMA DE AUTENTICACIÓN DINÁMICO
// =========================================================================
const loginForm = document.querySelector(".login-form");

if (loginForm) {
    loginForm.addEventListener("submit", (e) => {
        e.preventDefault();
        
        const correoInput = loginForm.querySelector('input[type="email"]').value.trim();
        const contrasenaInput = loginForm.querySelector('input[type="password"]').value;

     // fetch("http://localhost:5000/api/login", {
        fetch("/api/login", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                correo: correoInput,
                password: contrasenaInput
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                // Guardamos los datos de sesión devueltos automáticamente por la DB
                localStorage.setItem("userRole", data.rol.toLowerCase()); 
                localStorage.setItem("userName", data.nombre);

                alert(`¡Bienvenido, ${data.nombre}!`);

                // Ambos roles pueden entrar a telemetria, el script ocultará el resto
                window.location.replace("./telemetria.html");
            } else {
                alert(data.message || "Credenciales incorrectas.");
            }
        })
        .catch(err => {
            console.error("Error en la conexión:", err);
            alert("No se pudo conectar con el servidor HTTP de Flask.");
        });

        return false;
    });
}

// =========================================================================
// CONTROL DE VISIBILIDAD DE MENÚS, RUTA ACTIVA Y PROTECCIÓN DE RUTAS
// =========================================================================
document.addEventListener("DOMContentLoaded", () => {
    const currentRole = localStorage.getItem("userRole");
    const path = window.location.pathname.toLowerCase(); // Convertimos a minúsculas para evitar fallos de tipeo

    // 1. PROTECCIÓN DE RUTAS (Mejorada)
    // Validamos si la página actual es el login (index o raíz)
    const isLoginPage = path.endsWith("index.html") || path === "/" || path.endsWith("/");

    if (!currentRole) {
        // Si NO hay rol y NO estamos en el login, entonces sí redirigimos al login
        if (!isLoginPage) {
            console.warn("Acceso denegado: No se encontró un rol de usuario.");
            window.location.replace("./index.html");
            return;
        }
    } else {
        // Si SÍ hay un rol activo pero el usuario intenta entrar al login, lo mandamos a telemetría
        if (isLoginPage) {
            window.location.replace("./telemetria.html");
            return;
        }
    }

    // 2. RESTRICCIÓN DE ROLES
    // Si el usuario es un operador común ("user"), removemos las secciones de administrador
    if (currentRole === "user") {
        document.querySelectorAll('[data-role="admin"]').forEach(elemento => {
            if (elemento) {
                elemento.remove(); 
            }
        });
    }

   // 3. DETECCIÓN AUTOMÁTICA DE LA PÁGINA ACTIVA
    const menuLinks = document.querySelectorAll('.sidebar-nav .nav-item');
    const currentPage = path.split('/').pop(); 

    menuLinks.forEach(link => {
        const href = link.getAttribute('href');
        const targetPage = href ? href.split('/').pop().toLowerCase() : '';
        
        if (targetPage && (currentPage === targetPage || path.includes(targetPage))) {
            link.classList.add('active'); 
        } else {
            link.classList.remove('active'); 
        }
    });

    // 4. CONFIGURACIÓN DEL BOTÓN DE CERRAR SESIÓN
    const logoutBtn = document.getElementById("btn-logout");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.clear(); // Limpia por completo el rol y nombre
            window.location.replace("./index.html");
        });
    }
});

