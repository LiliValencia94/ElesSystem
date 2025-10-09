function togglePassword() {
  const p = document.getElementById('password');
  if (p) p.type = p.type === 'password' ? 'text' : 'password';
}
