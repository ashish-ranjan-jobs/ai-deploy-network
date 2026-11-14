// AI Deploy Network Frontend Interactions
document.addEventListener('DOMContentLoaded', () => {
  // Auto-dismiss alerts if any
  const alerts = document.querySelectorAll('.auto-dismiss');
  alerts.forEach(el => {
    setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 4000);
  });
});

async function apiLogout() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
    window.location.href = '/';
  } catch (err) {
    console.error('Logout error:', err);
    window.location.href = '/';
  }
}
