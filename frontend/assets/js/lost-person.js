/**
 * WariSeva Lost Person Assistance JS Module
 */

let selectedLostPersonId = null;
let selectedLostFamilyId = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('reportLostWizardContainer')) {
    initReportLostWizard();
  }
  if (document.getElementById('myLostCasesContainer')) {
    loadMyLostCases();
  }
  if (document.getElementById('policeLostDashboard')) {
    loadPoliceLostDashboard();
  }
  if (document.getElementById('helpCenterLostDashboard')) {
    loadHelpCenterLostDashboard();
  }
});

/* --- Report Lost Person Wizard --- */
async function initReportLostWizard() {
  const familySelect = document.getElementById('lostFamilySelect');
  if (!familySelect) return;

  const res = await APIClient.get('/api/families');
  if (res.success && res.data.length > 0) {
    familySelect.innerHTML = res.data.map(f => `
      <option value="${f.id}">${f.family_name} (${f.family_code})</option>
    `).join('');
    selectedLostFamilyId = res.data[0].id;
    loadMembersForSelectedFamily(selectedLostFamilyId);
  } else {
    familySelect.innerHTML = `<option value="">No families registered</option>`;
  }
}

async function loadMembersForSelectedFamily(familyId) {
  const grid = document.getElementById('familyMembersGrid');
  if (!grid) return;

  grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:1rem;">Loading family members...</div>`;

  const res = await APIClient.get(`/api/families/${familyId}`);
  if (res.success) {
    const members = res.data.members || [];
    if (members.length === 0) {
      grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:1rem;color:var(--text-muted);">No members registered in this family.</div>`;
      return;
    }

    grid.innerHTML = members.map(m => `
      <div class="glass-card" style="padding:1.25rem; border-left:4px solid var(--color-primary); cursor:pointer;" onclick="selectMemberToReportLost(${m.id}, '${m.full_name}')">
        <div class="d-flex align-center gap-2">
          <div class="avatar-circle" style="width:45px;height:45px;font-size:1rem;overflow:hidden;flex-shrink:0;">
            ${m.primary_photo ? `<img src="${m.primary_photo}" style="width:100%;height:100%;object-fit:cover;">` : m.full_name.substring(0, 2).toUpperCase()}
          </div>
          <div>
            <div style="font-weight:700;">${m.full_name}</div>
            <div style="font-size:0.75rem;color:var(--text-muted);">${m.relationship} | ${m.calculated_age} yrs (${m.age_category})</div>
          </div>
        </div>
        <button type="button" class="btn btn-sm btn-danger btn-block" style="margin-top:0.75rem;">🚨 Report Missing</button>
      </div>
    `).join('');
  }
}

async function selectMemberToReportLost(personId, personName) {
  // Check Duplicate Active Case First!
  const dupRes = await APIClient.get(`/api/lost-person/active-case/person/${personId}`);
  if (dupRes.success && dupRes.has_active_case) {
    const active = dupRes.data;
    alert(`⚠️ Cannot file duplicate report!\n\nThis person (${personName}) already has an active lost-person case:\nCase Number: #${active.case_number}\nStatus: ${active.status}\nReported: ${active.created_at}`);
    return;
  }

  selectedLostPersonId = personId;
  Auth.showToast(`Selected ${personName} for missing report.`, 'info');

  // Pre-fill Profile details
  const personRes = await APIClient.get(`/api/persons/${personId}`);
  if (personRes.success) {
    const p = personRes.data;
    document.getElementById('verifyName').innerText = p.full_name;
    document.getElementById('verifyAgeCat').innerText = `${p.calculated_age} years old (${p.age_category})`;
    
    const c = p.clothing || {};
    document.getElementById('lostTopType').value = c.top_type || 'T-Shirt';
    document.getElementById('lostTopColor').value = c.top_color || 'Red';
    document.getElementById('lostBottomType').value = c.bottom_type || 'Shorts';
    document.getElementById('lostBottomColor').value = c.bottom_color || 'Navy Blue';

    document.getElementById('reportWizardStep1').style.display = 'none';
    document.getElementById('reportWizardStep2').style.display = 'block';
  }
}

async function handleReportLostSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitLostBtn');
  btn.disabled = true;
  btn.innerText = 'Filing Missing Case Alert...';

  const lastSeenDate = document.getElementById('lastSeenDate').value;
  const lastSeenTime = document.getElementById('lastSeenTime').value || '12:00';
  const lastSeenStr = `${lastSeenDate} ${lastSeenTime}:00`;

  const payload = {
    family_id: selectedLostFamilyId,
    person_id: selectedLostPersonId,
    reporter_relationship: document.getElementById('reporterRel').value,
    last_seen_at: lastSeenStr,
    zone: document.getElementById('lostZone').value,
    landmark: document.getElementById('lostLandmark').value.trim(),
    route_section: document.getElementById('lostRouteSection').value.trim(),
    location_description: document.getElementById('lostLocDesc').value.trim(),
    clothing: {
      top_type: document.getElementById('lostTopType').value.trim(),
      top_color: document.getElementById('lostTopColor').value.trim(),
      bottom_type: document.getElementById('lostBottomType').value.trim(),
      bottom_color: document.getElementById('lostBottomColor').value.trim(),
      footwear: document.getElementById('lostFootwear').value.trim(),
      footwear_color: document.getElementById('lostFootwearColor').value.trim(),
      headwear: document.getElementById('lostHeadwear').value.trim(),
      accessories: document.getElementById('lostAccessories').value.trim(),
      confirmed_from_profile: true
    },
    additional_information: document.getElementById('lostNotes').value.trim()
  };

  const res = await APIClient.post('/api/lost-person/cases', payload);

  btn.disabled = false;
  btn.innerText = '🚨 SUBMIT MISSING PERSON ALERT';

  if (res.success) {
    const c = res.data;
    Auth.showToast(`Missing Person Case #${c.case_number} reported! Priority: ${c.priority_level}`, 'success');
    setTimeout(() => {
      window.location.href = `/lost-person/lost-success.html?case_id=${c.id}`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

/* --- Family Lost Cases Monitor --- */
async function loadMyLostCases() {
  const container = document.getElementById('myLostCasesContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading lost person cases...</div>`;

  const res = await APIClient.get('/api/lost-person/cases?my_cases=1');
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const cases = res.data;
  if (!cases || cases.length === 0) {
    container.innerHTML = `
      <div class="glass-card" style="padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">🚩</div>
        <h3>No Lost Person Reports Filed</h3>
        <p style="color:var(--text-secondary);margin:0.75rem 0 1.5rem 0;">You have not reported any missing family members.</p>
        <a href="/lost-person/report-lost.html" class="btn btn-primary">Report Lost Person</a>
      </div>
    `;
    return;
  }

  container.innerHTML = cases.map(c => `
    <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid ${c.priority_level === 'CRITICAL' ? 'var(--color-accent-crimson)' : 'var(--color-accent-gold)'};">
      <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
        <div>
          <div class="d-flex align-center gap-2">
            <h3 style="font-size:1.2rem;">${c.case_number}</h3>
            <span class="badge ${c.priority_level === 'CRITICAL' ? 'badge-rejected' : 'badge-pending'}">${c.priority_level} PRIORITY</span>
            <span class="badge badge-active">${c.status}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.3rem;">
            Person: <strong>${c.temp_person_name || 'Registered Member'}</strong> | Last Seen Zone: <strong>${c.zone}</strong> (${c.landmark || 'No landmark'})
          </div>
        </div>
        <div class="d-flex gap-2">
          <a href="/lost-person/lost-case-details.html?case_id=${c.id}" class="btn btn-sm btn-primary">View Case Details</a>
          <a href="/lost-person/withdraw-case.html?case_id=${c.id}" class="btn btn-sm btn-secondary">Withdraw Report</a>
        </div>
      </div>
    </div>
  `).join('');
}

/* --- Police Dashboard Loader --- */
async function loadPoliceLostDashboard() {
  const container = document.getElementById('policeLostTableBody');
  if (!container) return;

  const res = await APIClient.get('/api/lost-person/cases');
  if (res.success) {
    const cases = res.data;
    container.innerHTML = cases.map(c => `
      <tr style="${c.priority_level === 'CRITICAL' ? 'background:rgba(239,68,68,0.1);' : ''}">
        <td><strong style="font-family:monospace;">${c.case_number}</strong></td>
        <td>${c.temp_person_name || (c.person_id ? 'Registered Pilgrim' : 'Unidentified')}</td>
        <td><span class="badge ${c.priority_level === 'CRITICAL' ? 'badge-rejected' : 'badge-pending'}">${c.priority_level} (${c.priority_score})</span></td>
        <td>${c.zone}</td>
        <td><span class="badge badge-active">${c.status}</span></td>
        <td>${c.last_seen_at}</td>
        <td>
          <a href="/lost-person/lost-case-details.html?case_id=${c.id}" class="btn btn-sm btn-primary">Review & Override</a>
        </td>
      </tr>
    `).join('');
  }
}
