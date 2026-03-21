/* ═══════════════════════════════════════════════════════════
   GyanUday University — Main JS
   Phase 1: Flash message auto-dismiss + active nav highlight
   Phase 5+: Chart data fetch helpers added here
═══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', function () {

  // ── Auto-dismiss flash messages after 4 seconds ─────────
  document.querySelectorAll('.alert').forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.4s ease';
      alert.style.opacity = '0';
      setTimeout(function () { alert.remove(); }, 400);
    }, 4000);
  });


  // ── Highlight active sidebar nav item from URL ───────────
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-item').forEach(function (link) {
    const href = link.getAttribute('href');
    if (href && currentPath.startsWith(href) && href !== '/') {
      link.classList.add('active');
    }
  });


  // ── Confirm before delete actions ───────────────────────
  document.querySelectorAll('[data-confirm]').forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const msg = btn.getAttribute('data-confirm') || 'Are you sure?';
      if (!window.confirm(msg)) {
        e.preventDefault();
      }
    });
  });


  // ── API helper: fetch JSON from DRF endpoints (Phase 5+) ─
  window.apiGet = async function (url) {
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
    });
    if (!response.ok) throw new Error('API error: ' + response.status);
    return response.json();
  };

  window.apiPost = async function (url, data) {
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      credentials: 'same-origin',
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('API error: ' + response.status);
    return response.json();
  };


  // ── CSRF cookie helper ───────────────────────────────────
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      document.cookie.split(';').forEach(function (cookie) {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
        }
      });
    }
    return cookieValue;
  }

});
