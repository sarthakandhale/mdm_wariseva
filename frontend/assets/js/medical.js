/**
 * WariSeva Medical Emergency Assistance JS Module
 */

let selectedPatientType = 'SELF'; // 'SELF', 'FAMILY', 'UNIDENTIFIED'
let selectedFamilyPersonId = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('medicalReportWizard')) {
    initReportWizard();
  }
  if (document.getElementById('myMedicalCasesContainer')) {
    loadMyCases();
  }
  if (document.getElementById('nearbyFacilitiesContainer')) {
    loadNearbyFacilities();
  }
  if (document.getElementById('medicalStaffDashboard')) {
    loadMedicalStaffDashboard();
  }
  if (document.getElementById('ambulanceDashboardContainer')) {
    loadAmbulanceDashboard();
  }
});

/* --- Emergency Reporting Wizard --- */
function initReportWizard() {
  loadFamilyMemberOptions();
}

async function loadFamilyMemberOptions() {
  const familySelect = document.getElementById('familyMemberSelect');
  if (!familySelect) return;

  const res = await APIClient.get('/api/families');
  if (res.success && res.data.length > 0) {
    const members = res.data[0].members || [];
    familySelect.innerHTML = members.map(m => `
      <option value="${m.id}">${m.full_name} (${m.relationship}, ${m.calculated_age} yrs - ${m.person_code})</option>
    `).join('');
  } else {
    familySelect.innerHTML = `<option value="">No registered family members found</option>`;
  }
}

function selectPatientMode(mode) {
  selectedPatientType = mode;
  document.getElementById('modeSelfCard').className = mode === 'SELF' ? 'glass-card active-mode' : 'glass-card';
  document.getElementById('modeFamilyCard').className = mode === 'FAMILY' ? 'glass-card active-mode' : 'glass-card';
  document.getElementById('modeUnidentifiedCard').className = mode === 'UNIDENTIFIED' ? 'glass-card active-mode' : 'glass-card';

  document.getElementById('familySelectionBox').style.display = mode === 'FAMILY' ? 'block' : 'none';
  document.getElementById('unidentifiedFormBox').style.display = mode === 'UNIDENTIFIED' ? 'block' : 'none';
}

function captureGPSLocation() {
  const btn = document.getElementById('gpsLocateBtn');
  const display = document.getElementById('gpsDisplayNote');
  if (!navigator.geolocation) {
    Auth.showToast('Geolocation is not supported by your browser.', 'error');
    return;
  }

  btn.disabled = true;
  btn.innerText = '📡 Locating GPS...';

  navigator.geolocation.getCurrentPosition(
    (pos) => {
      btn.disabled = false;
      btn.innerText = '✅ Location Captured';
      document.getElementById('medLat').value = pos.coords.latitude.toFixed(7);
      document.getElementById('medLon').value = pos.coords.longitude.toFixed(7);
      document.getElementById('medLocSource').value = 'GPS';
      display.innerHTML = `<span style="color:var(--color-accent-emerald);">GPS Coordinates Captured: ${pos.coords.latitude.toFixed(4)}, ${pos.coords.longitude.toFixed(4)}</span>`;
    },
    (err) => {
      btn.disabled = false;
      btn.innerText = '📍 Use GPS Location';
      Auth.showToast('Could not fetch GPS. Please select zone and landmark manually.', 'error');
    },
    { timeout: 10000 }
  );
}

async function handleEmergencyReportSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('reportSubmitBtn');
  btn.disabled = true;
  btn.innerText = 'Dispatching Emergency Alert...';

  // Gather symptoms
  const symptomBoxes = document.querySelectorAll('input[name="symptoms"]:checked');
  const symptoms = Array.from(symptomBoxes).map(b => b.value);
  const otherSym = document.getElementById('otherSymptomsInput').value.trim();
  if (otherSym) symptoms.push(otherSym);

  let patient_person_id = null;
  let temp_patient_name = null;
  let temp_patient_age = null;
  let temp_patient_gender = null;
  let temp_patient_description = null;

  if (selectedPatientType === 'FAMILY') {
    patient_person_id = document.getElementById('familyMemberSelect').value;
  } else if (selectedPatientType === 'UNIDENTIFIED') {
    temp_patient_name = document.getElementById('tempName').value.trim() || 'Unidentified Pilgrim';
    temp_patient_age = document.getElementById('tempAge').value || 35;
    temp_patient_gender = document.getElementById('tempGender').value;
    temp_patient_description = document.getElementById('tempDesc').value.trim();
  }

  const payload = {
    patient_person_id: patient_person_id,
    temp_patient_name: temp_patient_name,
    temp_patient_age: temp_patient_age,
    temp_patient_gender: temp_patient_gender,
    temp_patient_description: temp_patient_description,
    emergency_type: document.getElementById('medEmergencyType').value,
    reported_severity: document.getElementById('medSeverity').value,
    description: document.getElementById('medDescription').value.trim(),
    symptoms: symptoms,
    zone: document.getElementById('medZone').value,
    route: document.getElementById('medRoute').value.trim(),
    landmark: document.getElementById('medLandmark').value.trim(),
    latitude: document.getElementById('medLat').value ? parseFloat(document.getElementById('medLat').value) : null,
    longitude: document.getElementById('medLon').value ? parseFloat(document.getElementById('medLon').value) : null,
    location_description: document.getElementById('medLocDesc').value.trim(),
    location_source: document.getElementById('medLocSource').value
  };

  const res = await APIClient.post('/api/medical/cases', payload);

  btn.disabled = false;
  btn.innerText = 'DISPATCH EMERGENCY ALERT';

  if (res.success) {
    const c = res.data;
    Auth.showToast(`Emergency Case ${c.case_number} reported! Priority: ${c.priority_level}`, 'success');
    setTimeout(() => {
      window.location.href = `/medical/emergency-success.html?case_id=${c.id}`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

/* --- Warkari Case Monitor Page --- */
async function loadMyCases() {
  const container = document.getElementById('myMedicalCasesContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading your reported emergency cases...</div>`;

  const res = await APIClient.get('/api/medical/cases?my_cases=1');
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const cases = res.data;
  if (!cases || cases.length === 0) {
    container.innerHTML = `
      <div class="glass-card" style="padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">🚑</div>
        <h3>No Medical Emergencies Reported</h3>
        <p style="color:var(--text-secondary);margin:0.75rem 0 1.5rem 0;">You have not filed any medical emergency cases for yourself or family members.</p>
        <a href="/medical/report-emergency.html" class="btn btn-primary">Report Medical Emergency</a>
      </div>
    `;
    return;
  }

  container.innerHTML = cases.map(c => `
    <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid ${c.priority_level === 'CRITICAL' ? 'var(--color-accent-crimson)' : 'var(--color-accent-gold)'};">
      <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;margin-bottom:0.75rem;">
        <div>
          <div class="d-flex align-center gap-2">
            <h3 style="font-size:1.2rem;">${c.case_number}</h3>
            <span class="badge ${c.priority_level === 'CRITICAL' ? 'badge-rejected' : 'badge-pending'}">${c.priority_level} PRIORITY</span>
            <span class="badge badge-active">${c.status}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.25rem;">
            Emergency Type: <strong>${c.emergency_type}</strong> | Zone: <strong>${c.zone}</strong> (${c.landmark || 'No landmark'})
          </div>
        </div>
        <div>
          <a href="/medical/medical-case-details.html?case_id=${c.id}" class="btn btn-sm btn-primary">View Case & Track Ambulance</a>
        </div>
      </div>
    </div>
  `).join('');
}

/* --- Nearby Medical Facilities Finder --- */
async function loadNearbyFacilities() {
  const container = document.getElementById('nearbyFacilitiesContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Searching nearby medical camps & hospitals along Dindi route...</div>`;

  const res = await APIClient.get('/api/medical/facilities/nearby');
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const facilities = res.data;
  container.innerHTML = facilities.map(f => `
    <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-accent-emerald);">
      <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
        <div>
          <div class="d-flex align-center gap-2">
            <h3 style="font-size:1.2rem;">${f.name}</h3>
            <span class="badge badge-active">${f.facility_type}</span>
            <span class="badge badge-active">${f.status}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.4rem;">
            Zone: <strong>${f.zone}</strong> | Distance: <strong style="color:var(--color-accent-gold);">${f.distance_km} km</strong> | Approx Response: <strong>${f.estimated_response_mins} mins</strong>
          </div>
          <div style="font-size:0.825rem;margin-top:0.4rem;">
            Services: ${f.services.map(s => `<span class="badge" style="background:rgba(255,255,255,0.05);margin-right:0.3rem;">${s}</span>`).join('')}
          </div>
        </div>
        <div>
          <a href="tel:${f.contact_number}" class="btn btn-sm btn-success">📞 Call ${f.contact_number}</a>
        </div>
      </div>
    </div>
  `).join('');
}

/* --- Medical Staff Triage Console --- */
async function loadMedicalStaffDashboard() {
  const container = document.getElementById('medicalStaffDashboard');
  if (!container) return;

  // Load summary metrics
  const dashRes = await APIClient.get('/api/medical/dashboard');
  if (dashRes.success) {
    const d = dashRes.data;
    document.getElementById('statTotalCases').innerText = d.total_cases;
    document.getElementById('statActiveCases').innerText = d.active_cases;
    document.getElementById('statCriticalCases').innerText = d.critical_cases;
    document.getElementById('statCampsAvailable').innerText = d.camps_available;
    document.getElementById('statAmbulancesAvailable').innerText = d.ambulances_available;
  }

  // Load active emergency cases
  const casesRes = await APIClient.get('/api/medical/cases');
  if (casesRes.success) {
    const cases = casesRes.data;
    const casesContainer = document.getElementById('activeCasesTableContainer');
    if (casesContainer) {
      casesContainer.innerHTML = cases.map(c => `
        <tr style="${c.priority_level === 'CRITICAL' ? 'background:rgba(239,68,68,0.1);' : ''}">
          <td><strong style="font-family:monospace;">${c.case_number}</strong></td>
          <td>${c.temp_patient_name || (c.patient_person_id ? 'Registered Pilgrim' : 'Unidentified')}</td>
          <td><strong>${c.emergency_type}</strong></td>
          <td><span class="badge ${c.priority_level === 'CRITICAL' ? 'badge-rejected' : 'badge-pending'}">${c.priority_level} (${c.priority_score})</span></td>
          <td>${c.zone}</td>
          <td><span class="badge badge-active">${c.status}</span></td>
          <td>
            <a href="/medical-staff/treatment.html?case_id=${c.id}" class="btn btn-sm btn-primary">Triage & Treat</a>
          </td>
        </tr>
      `).join('');
    }
  }
}
