/* UK Rail Live — Main JavaScript */

// ── Theme toggle ────────────────────────────────────────────────────────
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    try {
        localStorage.setItem('theme', next);
    } catch (e) {}
}

// Apply saved theme on load
(function() {
    try {
        const saved = localStorage.getItem('theme');
        if (saved) {
            document.documentElement.setAttribute('data-theme', saved);
        }
    } catch (e) {}
})();

// ── Tab switching (station detail page) ─────────────────────────────────
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    const activeBtn = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeBtn) activeBtn.classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    const activeContent = document.getElementById(`${tabName}-tab`);
    if (activeContent) activeContent.classList.add('active');

    // Trigger HTMX load on the newly visible board
    if (tabName === 'departures' || tabName === 'arrivals') {
        const board = document.getElementById(`${tabName}-board`);
        if (board && typeof htmx !== 'undefined') {
            htmx.trigger(board, 'load');
        }
    }
}

// ── Update "last updated" timestamps ────────────────────────────────────
function updateTimestamps() {
    document.querySelectorAll('time[id$="-updated"]').forEach(el => {
        const now = new Date();
        const time = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        el.textContent = time;
    });
}

// Update timestamps every 30s
setInterval(updateTimestamps, 30000);

// ── HTMX after-request hook ──────────────────────────────────────────────
document.addEventListener('htmx:afterRequest', function(event) {
    const target = event.detail.target;
    if (target) {
        const timeEl = target.closest('.tab-content')?.querySelector('time[id$="-updated"]');
        if (timeEl) {
            const now = new Date();
            timeEl.textContent = now.toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' });
        }
    }
});

// ── Keyboard shortcuts ───────────────────────────────────────────────────
document.addEventListener('keydown', function(e) {
    // "/" focuses search
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
        e.preventDefault();
        const searchInput = document.querySelector('.search-input, .search-input-large');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // "m" goes to map
    if (e.key === 'm' && document.activeElement.tagName !== 'INPUT') {
        window.location.href = '/map/';
    }
});