// AI Deploy Network - Client Interactivity
document.addEventListener('DOMContentLoaded', () => {
  // Global quick-focus search shortcut: '/'
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      e.preventDefault();
      const searchInput = document.querySelector('input[name="q"]');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

  // Copy hash utility
  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const text = btn.getAttribute('data-copy');
      if (!text) return;
      try {
        await navigator.clipboard.writeText(text);
        const originalText = btn.innerHTML;
        btn.innerHTML = `<span class="text-emerald-400">Copied</span>`;
        setTimeout(() => {
          btn.innerHTML = originalText;
        }, 1500);
      } catch (err) {
        console.warn('Clipboard write failed:', err);
      }
    });
  });
});

async function apiLogout() {
  try {
    await fetch('/aideploy/api/auth/logout', { method: 'POST' });
    window.location.href = '/aideploy/';
  } catch (err) {
    console.error('Logout error:', err);
    window.location.href = '/aideploy/';
  }
}
