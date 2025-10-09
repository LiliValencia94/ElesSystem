// static/js/script_nuevo_empleado.js

// Lógica para mostrar/ocultar el menú
document.getElementById("menuToggle").addEventListener("click", () => {
    const menu = document.getElementById("menu");
    // Usa classList.toggle para manejo de CSS (es mejor práctica que style.display)
    menu.classList.toggle("open"); 
});

// 🚨 CÓDIGO CRÍTICO: Eliminamos la intercepción (e.preventDefault())
// para que Flask pueda procesar el envío, guardar el empleado y redirigir.
// También eliminamos el alert, ya que Flask mostrará el mensaje flash.
document.getElementById("empleadoForm").addEventListener("submit", function (e) {
    // e.preventDefault();  <--- ¡ESTO ESTABA CAUSANDO EL PROBLEMA Y DEBE ELIMINARSE!
    // alert("Empleado agregado exitosamente."); <-- Y esta alerta debe eliminarse.
    
    // Dejar vacío o con otras validaciones que no detengan el submit.
    // Si solo tenías el código de arriba, ¡déjalo así!
});