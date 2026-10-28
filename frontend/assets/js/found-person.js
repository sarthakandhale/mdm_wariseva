/**
 * WariSeva Found Person Assistance JS Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('reportFoundWizardContainer')) {
    initReportFoundWizard();
  }
  if (document.getElementById('foundCasesContainer')) {
    loadFoundCasesList();
  }
  if (document.getElementById('helpCenterFoundDashboard')) {
    loadHelpCenterFoundDashboard();
  }
});

function initReportFoundWizard() {
  const wizard = document.getElementById('reportFoundWizardContainer');
  if (!wizard) return;
  // Wizard setup
}

async function handleReportFoundSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitFoundBtn');
  btn.disabled = true;
  btn.innerText = 'Registering Found Person Case...';

  const payload = {
    identification_status: document.getElementById('foundIdentStatus').value,
    approximate_name: document.getElementById('foundApproxName').value.trim(),
    approximate_age: parseInt(document.getElementById('foundApproxAge').value || 30),
    gender: document.getElementById('foundGender').value,
    language: document.getElementById('foundLanguage').value,
    communication_status: document.getElementById('foundCommStatus').value,
    medical_attention_required: document.getElementById('foundMedReq').checked ? 1 : 0,
    special_assistance_required: document.getElementById('foundSpecialAssist').value.trim(),
    zone: document.getElementById('foundZone').value,
    landmark: document.getElementById('foundLandmark').value.trim(),
    route_section: document.getElementById('foundRouteSection').value.trim(),
    location_description: document.getElementById('foundLocDesc').value.trim(),
    safe_location_name: document.getElementById('foundSafeLocName').value.trim(),
    facility_type: document.getElementById('foundFacilityType').value,
    clothing: {
      top_type: document.getElementById('foundTopType').value.trim(),
      top_color: document.getElementById('foundTopColor').value.trim(),
      bottom_type: document.getElementById('foundBottomType').value.trim(),
      bottom_color: document.getElementById('foundBottomColor').value.trim(),
      footwear: document.getElementById('foundFootwear').value.trim(),
      footwear_color: document.getElementById('foundFootwearColor').value.trim(),
      headwear: document.getElementById('foundHeadwear').value.trim(),
      accessories: document.getElementById('foundAccessories').value.trim()
    }
  };

  const res = await APIClient.post('/api/found-person/cases', payload);

  btn.disabled = false;
  btn.innerText = '🟢 SUBMIT FOUND PERSON REPORT';

  if (res.success) {
    const c = res.data;
    Auth.showToast(`Found Person Case #${c.case_number} created successfully!`, 'success');
    setTimeout(() => {
      window.location.href = `/found-person/found-person-success.html?case_id=${c.id}`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

/* --- Found Person Cases Monitor --- */
async function loadFoundCasesList() {
  const container = document.getElementById('foundCasesContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading found person cases...</div>`;

  const res = await APIClient.get('/api/found-person/cases');
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const cases = res.data;
  if (!cases || cases.length === 0) {
    container.innerHTML = `<div class="glass-card" style="padding:3rem;text-align:center;"><h3>No Found Persons Registered</h3></div>`;
    return;
  }

  container.innerHTML = cases.map(c => `
    <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-success);">
      <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
        <div>
          <div class="d-flex align-center gap-2">
            <h3 style="font-size:1.2rem;">${c.case_number} (${c.temporary_person_id})</h3>
            <span class="badge badge-active">${c.identification_status}</span>
            <span class="badge badge-pending">${c.status}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.3rem;">
            Person: <strong>${c.approximate_name || 'Unidentified Pilgrim'}</strong> (${c.approximate_age} yrs, ${c.gender}) | Safe Location: <strong>${c.safe_location_name || 'Help Center'}</strong>
          </div>
        </div>
        <div class="d-flex gap-2">
          <a href="/found-person/found-person-case-details.html?case_id=${c.id}" class="btn btn-sm btn-primary">View Case & Clues</a>
          <a href="/found-person/verification.html?case_id=${c.id}" class="btn btn-sm btn-secondary">Verify Identity</a>
        </div>
      </div>
    </div>
  `).join('');
}

/* --- Help Center Dashboard --- */
async function loadHelpCenterFoundDashboard() {
  const container = document.getElementById('helpCenterFoundTableBody');
  if (!container) return;

  const res = await APIClient.get('/api/found-person/cases');
  if (res.success) {
    const cases = res.data;
    container.innerHTML = cases.map(c => `
      <tr>
        <td><strong style="font-family:monospace;">${c.case_number}</strong></td>
        <td>${c.approximate_name} (${c.approximate_age}y ${c.gender})</td>
        <td><span class="badge badge-active">${c.identification_status}</span></td>
        <td>${c.safe_location_name || 'Help Center'}</td>
        <td><span class="badge badge-pending">${c.status}</span></td>
        <td>
          <a href="/found-person/found-person-case-details.html?case_id=${c.id}" class="btn btn-sm btn-primary">Manage Custody</a>
        </td>
      </tr>
    `).join('');
  }
}
