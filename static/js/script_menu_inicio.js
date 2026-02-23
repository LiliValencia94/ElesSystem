const btn = document.getElementById("usuarioBtn");
const dropdown = document.getElementById("dropdown");

btn.addEventListener("click", () => {
  dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
});

document.addEventListener("click", function (e) {
  if (!btn.contains(e.target) && !dropdown.contains(e.target)) {
    dropdown.style.display = "none";
  }
});

/* ================= CHATBOT ================= */

const chatToggle = document.getElementById("chatToggle");
const chatContainer = document.getElementById("chatContainer");
const closeChat = document.getElementById("closeChat");
const messages = document.getElementById("messages");
const userInput = document.getElementById("userInput");
const sendBtn = document.getElementById("sendBtn");

function addMessage(text, sender) {
  const div = document.createElement("div");
  div.classList.add("message", sender);
  div.textContent = text;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function botResponse(input) {
  const pregunta = input.toLowerCase();
  if (pregunta.includes("objetivo")) {
    return "El objetivo del proyecto es desarrollar habilidades en programación y tecnología.";
  } else if (pregunta.includes("tecnologias")) {
    return "Estamos usando JavaScript como base del chatbot, pero también se aplica en Python.";
  } else if (pregunta.includes("integracion")) {
    return "La integración consiste en combinar el chatbot con tu proyecto formativo.";
  } else if (pregunta.includes("salir")) {
    return "Gracias por conversar conmigo. ¡Éxitos en tu proyecto! 👋";
  } else {
    return "Lo siento, aún no tengo respuesta para esa pregunta.";
  }
}

function sendMessage() {
  const text = userInput.value.trim();
  if (!text) return;

  addMessage(text, "user");
  userInput.value = "";

  const respuesta = botResponse(text);
  setTimeout(() => addMessage(respuesta, "bot"), 400);
}

chatToggle.addEventListener("click", () => {
  chatContainer.classList.add("active");
  userInput.focus();
});

closeChat.addEventListener("click", () => {
  chatContainer.classList.remove("active");
  messages.innerHTML = "";
});

sendBtn.addEventListener("click", sendMessage);

userInput.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

(function init() {
  addMessage('Hola — soy el asistente del proyecto. Puedes preguntar por "objetivo", "tecnologías" o "integración".', 'bot');
})();