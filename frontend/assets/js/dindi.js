/**
 * WariSeva Dindi Management & Warkari Group Coordination JS Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('dindiDirectoryContainer')) {
    loadDindiDirectory();
  }
  if (document.getElementById('dindiLeaderDashboardContainer')) {
    loadDindiLeaderDashboard();
  }
});

async function loadDindiDirectory() {
  const container = document.getElementById('dindiDirectoryContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading Dindi Directory...</div>`;

  const res = await APIClient.get('/api/dindis');
  if (res.success) {
    const dindis = res.data;
    container.innerHTML = dindis.map(d => `
      <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-primary);">
        <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
          <div>
            <div class="d-flex align-center gap-2">
              <h3 style="font-size:1.2rem;">Dindi #${d.dindi_number} - ${d.name}</h3>
              <span class="badge badge-active">${d.status}</span>
            </div>
            <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.3rem;">
              Code: <strong>${d.dindi_code}</strong> | Route: <strong>${d.start_location} → ${d.destination}</strong> | Active Members: <strong>${d.active_member_count || 0}</strong>
            </div>
          </div>
          <a href="/dindi/details.html?dindi_id=${d.id}" class="btn btn-sm btn-primary">🚩 View Schedule & Details</a>
        </div>
      </div>
    `).join('');
  }
}

async function loadDindiLeaderDashboard() {
  const container = document.getElementById('dindiLeaderDashboardContainer');
  if (!container) return;

  const res = await APIClient.get('/api/dindis/1');
  if (res.success) {
    const d = res.data;
    const m = d.member_stats || {};

    container.innerHTML = `
      <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap:1.25rem; margin-bottom:1.5rem;">
        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-primary);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">MY DINDI NUMBER</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-primary); margin-top:0.2rem;">Dindi No. ${d.dindi_number}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">${d.name}</div>
        </div>

        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-success);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">ACTIVE MEMBERS</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-success); margin-top:0.2rem;">${m.active_members || 0}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">Registered: ${m.registered_members || 0}</div>
        </div>

        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-accent-gold);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">ACTIVE ANNOUNCEMENTS</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-accent-gold); margin-top:0.2rem;">${(d.announcements || []).length}</div>
          <div style="font-size:0.75rem; color:var(--text-muted);">Published to members</div>
        </div>
      </div>
    `;
  }
}

async function handleCreateDindiSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitDindiBtn');
  btn.disabled = true;
  btn.innerText = 'Creating Dindi...';

  const payload = {
    dindi_number: parseInt(document.getElementById('dindiNumber').value),
    name: document.getElementById('dindiName').value.trim(),
    description: document.getElementById('dindiDesc').value.trim(),
    start_location: document.getElementById('dindiStartLoc').value.trim(),
    destination: document.getElementById('dindiDest').value.trim(),
    expected_member_count: parseInt(document.getElementById('dindiExpectedCount').value || 100),
    contact_name: document.getElementById('dindiContactName').value.trim(),
    contact_number: document.getElementById('dindiContactNum').value.trim()
  };

  const res = await APIClient.post('/api/dindis', payload);
  btn.disabled = false;
  btn.innerText = '🚩 SUBMIT DINDI REGISTRATION';

  if (res.success) {
    Auth.showToast(`Dindi No. ${payload.dindi_number} created successfully!`, 'success');
    setTimeout(() => {
      window.location.href = `/dindi/directory.html`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}
