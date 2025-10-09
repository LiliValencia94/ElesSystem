let usuarios = [];
let idEditar = null;

function agregarUsuario() {
  const usuario = document.getElementById('nuevoUsuario').value;
  const contrasena = document.getElementById('nuevaContrasena').value;
  const rol = document.getElementById('rol').value;

  if (!usuario || !contrasena) return alert("Todos los campos son obligatorios.");

  usuarios.push({ id: Date.now(), usuario, contrasena, rol });
  document.getElementById('nuevoUsuario').value = '';
  document.getElementById('nuevaContrasena').value = '';
  actualizarTabla();
}

function actualizarTabla() {
  const tbody = document.querySelector('#tablaUsuarios tbody');
  tbody.innerHTML = '';

  usuarios.forEach((u, index) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${index + 1}</td>
      <td>${u.usuario}</td>
      <td>${u.rol}</td>
      <td>
        <button onclick="abrirEditar(${u.id})">Editar</button>
        <button onclick="eliminarUsuario(${u.id})" class="cancelar">Eliminar</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function eliminarUsuario(id) {
  usuarios = usuarios.filter(u => u.id !== id);
  actualizarTabla();
}

function abrirEditar(id) {
  const usuario = usuarios.find(u => u.id === id);
  if (!usuario) return;

  idEditar = id;
  document.getElementById('editarUsuario').value = usuario.usuario;
  document.getElementById('editarRol').value = usuario.rol;
  document.getElementById('editarContrasena').value = '';
  document.getElementById('modalEditar').style.display = 'flex';
}

function guardarCambios() {
  const usuario = document.getElementById('editarUsuario').value;
  const rol = document.getElementById('editarRol').value;
  const contrasena = document.getElementById('editarContrasena').value;

  usuarios = usuarios.map(u => {
    if (u.id === idEditar) {
      return {
        ...u,
        usuario,
        rol,
        contrasena: contrasena || u.contrasena
      };
    }
    return u;
  });

  cerrarModal();
  actualizarTabla();
}

function cerrarModal() {
  document.getElementById('modalEditar').style.display = 'none';
}

function toggleMenu() {
  const menu = document.getElementById('menuPopup');
  menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
}
