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
