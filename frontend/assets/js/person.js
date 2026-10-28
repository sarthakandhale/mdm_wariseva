/**
 * ReuniteAI Person Profile & Multi-Step Wizard JavaScript Module
 */

let currentStep = 1;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('addPersonWizard')) {
    initWizard();
  }
  if (document.getElementById('personProfileContainer')) {
    loadPersonProfilePage();
  }
  if (document.getElementById('editPersonForm')) {
    loadEditPersonPage();
  }
});

/* --- Multi-Step Wizard Logic --- */
function initWizard() {
  showStep(1);
  const dobInput = document.getElementById('wizardDob');
  if (dobInput) {
    dobInput.addEventListener('change', updateAgePreview);
    dobInput.addEventListener('keyup', updateAgePreview);
  }
}

function updateAgePreview() {
  const dobVal = document.getElementById('wizardDob').value;
  const ageDisplay = document.getElementById('wizardAgePreview');
  const catDisplay = document.getElementById('wizardCategoryPreview');

  if (!dobVal) {
    if (ageDisplay) ageDisplay.innerText = '-';
    if (catDisplay) catDisplay.innerHTML = '';
    return;
  }

  const dob = new Date(dobVal);
  const today = new Date();
  let age = today.getFullYear() - dob.getFullYear();
  const m = today.getMonth() - dob.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) {
    age--;
  }
  age = Math.max(0, age);

  let cat = 'ADULT';
  let badgeClass = 'badge-active';

  if (age <= 12) {
    cat = 'CHILD';
    badgeClass = 'badge-rejected';
  } else if (age <= 17) {
    cat = 'MINOR';
    badgeClass = 'badge-suspended';
  } else if (age <= 59) {
    cat = 'ADULT';
    badgeClass = 'badge-active';
  } else {
    cat = 'ELDERLY';
    badgeClass = 'badge-pending';
  }

  if (ageDisplay) ageDisplay.innerText = `${age} years old`;
  if (catDisplay) catDisplay.innerHTML = `<span class="badge ${badgeClass}">${cat}</span>`;
}

function showStep(step) {
  currentStep = step;
  for (let i = 1; i <= 6; i++) {
    const stepElem = document.getElementById(`wizardStep${i}`);
    const indicatorElem = document.getElementById(`stepIndicator${i}`);
    if (stepElem) stepElem.style.display = (i === step) ? 'block' : 'none';
    if (indicatorElem) {
      if (i === step) {
        indicatorElem.className = 'step-node active';
      } else if (i < step) {
        indicatorElem.className = 'step-node completed';
      } else {
        indicatorElem.className = 'step-node';
      }
    }
  }

  if (step === 6) {
    populateReviewSummary();
  }
}

function nextStep() {
  if (validateStep(currentStep)) {
    if (currentStep < 6) showStep(currentStep + 1);
  }
}

function prevStep() {
  if (currentStep > 1) showStep(currentStep - 1);
}

function validateStep(step) {
  const alertBox = document.getElementById('wizardAlert');
  if (alertBox) alertBox.style.display = 'none';

  if (step === 1) {
    const name = document.getElementById('wizardName').value.trim();
    const dob = document.getElementById('wizardDob').value;
    if (!name || name.length < 2) {
      showWizardError('Please enter a valid Full Name (min 2 characters).');
      return false;
    }
    if (!dob) {
      showWizardError('Please select Date of Birth.');
      return false;
    }
  } else if (step === 4) {
    const hasSafetyData = document.getElementById('wizardMedicalCondition').value.trim() || document.getElementById('wizardAllergies').value.trim();
    const consent = document.getElementById('wizardConsentCheckbox').checked;
    if (hasSafetyData && !consent) {
      showWizardError('Please confirm consent checkbox for storing optional medical/safety information.');
      return false;
    }
  } else if (step === 5) {
    const emMobile = document.getElementById('wizardEmergencyMobile').value.trim();
    if (emMobile) {
      const res = Validators.validateMobile(emMobile);
      if (!res.valid) {
        showWizardError('Please enter a valid Indian mobile number for emergency contact.');
        return false;
      }
    }
  }
  return true;
}

function showWizardError(msg) {
  const alertBox = document.getElementById('wizardAlert');
  if (alertBox) {
    alertBox.innerText = msg;
    alertBox.style.display = 'flex';
  } else {
    Auth.showToast(msg, 'error');
  }
}

function populateReviewSummary() {
  const summaryElem = document.getElementById('reviewSummaryContainer');
  if (!summaryElem) return;

  const name = document.getElementById('wizardName').value;
  const dob = document.getElementById('wizardDob').value;
  const gender = document.getElementById('wizardGender').value;
  const relationship = document.getElementById('wizardRelationship').value;
  const height = document.getElementById('wizardHeight').value;
  const topType = document.getElementById('wizardTopType').value;
  const topColor = document.getElementById('wizardTopColor').value;
  const medical = document.getElementById('wizardMedicalCondition').value;
  const emName = document.getElementById('wizardEmergencyName').value;
  const emMobile = document.getElementById('wizardEmergencyMobile').value;

  summaryElem.innerHTML = `
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.9rem;">
      <div><span style="color:var(--text-muted)">Full Name:</span> <strong>${name}</strong></div>
      <div><span style="color:var(--text-muted)">Date of Birth:</span> <strong>${dob}</strong></div>
      <div><span style="color:var(--text-muted)">Gender:</span> <strong>${gender}</strong></div>
      <div><span style="color:var(--text-muted)">Relationship:</span> <strong>${relationship}</strong></div>
      <div><span style="color:var(--text-muted)">Height:</span> <strong>${height || 'N/A'}</strong></div>
      <div><span style="color:var(--text-muted)">Clothing:</span> <strong>${topColor} ${topType || 'N/A'}</strong></div>
      <div><span style="color:var(--text-muted)">Medical Note:</span> <strong>${medical || 'None'}</strong></div>
      <div><span style="color:var(--text-muted)">Emergency Contact:</span> <strong>${emName || 'N/A'} (${emMobile || 'N/A'})</strong></div>
    </div>
  `;
}

async function handleWizardSubmit(e) {
  e.preventDefault();
  const urlParams = new URLSearchParams(window.location.search);
  const familyId = urlParams.get('family_id') || 1;

  const btn = document.getElementById('wizardSubmitBtn');
  btn.disabled = true;
  btn.innerText = 'Registering Person Profile...';

  const payload = {
    full_name: document.getElementById('wizardName').value.trim(),
    date_of_birth: document.getElementById('wizardDob').value,
    gender: document.getElementById('wizardGender').value,
    relationship: document.getElementById('wizardRelationship').value,
    height: document.getElementById('wizardHeight').value.trim(),
    approx_weight: document.getElementById('wizardWeight').value.trim(),
    hair_color: document.getElementById('wizardHairColor').value.trim(),
    eye_color: document.getElementById('wizardEyeColor').value.trim(),
    skin_tone: document.getElementById('wizardSkinTone').value.trim(),
    identification_mark: document.getElementById('wizardIdMark').value.trim(),
    glasses: document.getElementById('wizardGlasses').checked,
    hearing_aid: document.getElementById('wizardHearingAid').checked,
    walking_assistance: document.getElementById('wizardWalkingAid').checked,
    top_type: document.getElementById('wizardTopType').value.trim(),
    top_color: document.getElementById('wizardTopColor').value.trim(),
    bottom_type: document.getElementById('wizardBottomType').value.trim(),
    bottom_color: document.getElementById('wizardBottomColor').value.trim(),
    footwear: document.getElementById('wizardFootwear').value.trim(),
    footwear_color: document.getElementById('wizardFootwearColor').value.trim(),
    headwear: document.getElementById('wizardHeadwear').value.trim(),
    accessories: document.getElementById('wizardAccessories').value.trim(),
    clothing_description: document.getElementById('wizardClothingNotes').value.trim(),
    medical_condition: document.getElementById('wizardMedicalCondition').value.trim(),
    medication_requirement: document.getElementById('wizardMedication').value.trim(),
    allergy_information: document.getElementById('wizardAllergies').value.trim(),
    blood_group: document.getElementById('wizardBloodGroup').value,
    mobility_assistance: document.getElementById('wizardMobilityNotes').value.trim(),
    communication_difficulty: document.getElementById('wizardCommDifficulty').value.trim(),
    cognitive_assistance_required: document.getElementById('wizardCognitiveAid').checked,
    consent_given: document.getElementById('wizardConsentCheckbox').checked,
    emergency_contact_name: document.getElementById('wizardEmergencyName').value.trim(),
    emergency_relationship: document.getElementById('wizardEmergencyRel').value.trim(),
    emergency_contact_mobile: document.getElementById('wizardEmergencyMobile').value.trim(),
    emergency_alternate_mobile: document.getElementById('wizardEmergencyAltMobile').value.trim()
  };

  const res = await APIClient.post(`/api/families/${familyId}/members`, payload);

  btn.disabled = false;
  btn.innerText = 'Confirm & Save Member Profile';

  if (res.success) {
    const personId = res.data.id;
    // Check if photo uploaded
    const photoInput = document.getElementById('wizardPhotoInput');
    if (photoInput && photoInput.files.length > 0) {
      await uploadPhotoFile(personId, photoInput.files[0]);
    }
    Auth.showToast(`Person ${res.data.full_name} (${res.data.person_code}) registered successfully!`, 'success');
    setTimeout(() => {
      window.location.href = `/person/person-profile.html?person_id=${personId}`;
    }, 1000);
  } else {
    showWizardError(res.message);
  }
}

/* --- Detail Person Profile Page Loader --- */
async function loadPersonProfilePage() {
  const container = document.getElementById('personProfileContainer');
  if (!container) return;

  const urlParams = new URLSearchParams(window.location.search);
  const personId = urlParams.get('person_id');

  if (!personId) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;">No person ID provided.</div>`;
    return;
  }

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading person profile details...</div>`;

  const res = await APIClient.get(`/api/persons/${personId}`);
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const p = res.data;
  const photoUrl = p.primary_photo || '';
  const avatar = photoUrl ? `<img src="${photoUrl}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">` : p.full_name.substring(0, 2).toUpperCase();

  const c = p.clothing || {};
  const s = p.safety || {};
  const ems = p.emergency_contacts || [];

  container.innerHTML = `
    <!-- Header Card -->
    <div class="glass-card d-flex align-center gap-3" style="padding: 2rem; margin-bottom: 1.5rem;">
      <div class="avatar-circle" style="width:90px;height:90px;font-size:2.2rem;overflow:hidden;flex-shrink:0;">
        ${avatar}
      </div>
      <div style="flex-grow:1;">
        <div class="d-flex align-center justify-between" style="flex-wrap:wrap;gap:1rem;">
          <div>
            <h2 style="font-size:1.8rem;">${p.full_name}</h2>
            <div class="d-flex align-center gap-2" style="margin-top:0.4rem;">
              <span class="badge badge-active" style="font-family:monospace;font-size:0.85rem;">${p.person_code}</span>
              <span class="badge badge-${p.age_category === 'CHILD' ? 'rejected' : 'active'}">${p.age_category}</span>
              <span class="badge badge-active">${p.status}</span>
            </div>
          </div>
          <div class="d-flex gap-2">
            <a href="/person/edit-person.html?person_id=${p.id}" class="btn btn-primary">✏️ Edit Profile</a>
            <a href="/family/family-dashboard.html" class="btn btn-secondary">← Back to Family</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Details Grid -->
    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
      
      <!-- Basic & Physical -->
      <div class="glass-card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; border-bottom: 1px solid var(--bg-card-border); padding-bottom: 0.5rem;">Basic & Physical Details</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.9rem;">
          <div><span style="color:var(--text-muted)">Date of Birth:</span> <strong>${p.date_of_birth}</strong></div>
          <div><span style="color:var(--text-muted)">Calculated Age:</span> <strong>${p.calculated_age} years</strong></div>
          <div><span style="color:var(--text-muted)">Gender:</span> <strong>${p.gender}</strong></div>
          <div><span style="color:var(--text-muted)">Relationship:</span> <strong>${p.family.relationship_type || 'Relative'}</strong></div>
          <div><span style="color:var(--text-muted)">Height:</span> <strong>${p.height || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Weight:</span> <strong>${p.approx_weight || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Hair Color:</span> <strong>${p.hair_color || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Eye Color:</span> <strong>${p.eye_color || 'N/A'}</strong></div>
          <div style="grid-column:span 2;"><span style="color:var(--text-muted)">ID Mark:</span> <strong>${p.identification_mark || 'None'}</strong></div>
        </div>
      </div>

      <!-- Clothing Profile -->
      <div class="glass-card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; border-bottom: 1px solid var(--bg-card-border); padding-bottom: 0.5rem;">Expected Yatra Clothing Profile</h3>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.9rem;">
          <div><span style="color:var(--text-muted)">Top Wear:</span> <strong>${c.top_color || ''} ${c.top_type || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Bottom Wear:</span> <strong>${c.bottom_color || ''} ${c.bottom_type || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Footwear:</span> <strong>${c.footwear_color || ''} ${c.footwear || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Headwear:</span> <strong>${c.headwear || 'None'}</strong></div>
          <div style="grid-column:span 2;"><span style="color:var(--text-muted)">Accessories:</span> <strong>${c.accessories || 'None'}</strong></div>
          <div style="grid-column:span 2;"><span style="color:var(--text-muted)">Notes:</span> <strong>${c.description || 'None'}</strong></div>
        </div>
      </div>

      <!-- Optional Medical Safety Profile -->
      <div class="glass-card" style="padding: 1.5rem; border-top: 3px solid var(--color-accent-gold);">
        <div class="d-flex justify-between align-center" style="margin-bottom:1rem; border-bottom:1px solid var(--bg-card-border); padding-bottom:0.5rem;">
          <h3>🔒 Optional Medical & Safety Profile</h3>
          <span class="badge badge-pending">CONFIDENTIAL</span>
        </div>
        <div style="font-size:0.78rem; color:var(--color-accent-gold); margin-bottom:1rem; padding:0.5rem; background:rgba(245,158,11,0.1); border-radius:var(--radius-sm);">
          🛡️ Sensitive Information: Accessible only by authorized operational staff during missing person searches.
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:0.75rem; font-size:0.9rem;">
          <div><span style="color:var(--text-muted)">Blood Group:</span> <strong>${s.blood_group || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted)">Medical Condition:</span> <strong>${s.medical_condition || 'None'}</strong></div>
          <div><span style="color:var(--text-muted)">Medication:</span> <strong>${s.medication_requirement || 'None'}</strong></div>
          <div><span style="color:var(--text-muted)">Allergies:</span> <strong>${s.allergy_information || 'None'}</strong></div>
          <div><span style="color:var(--text-muted)">Mobility Aid:</span> <strong>${s.mobility_assistance || 'None'}</strong></div>
          <div><span style="color:var(--text-muted)">Cognitive Aid:</span> <strong>${s.cognitive_assistance_required ? 'Required' : 'No'}</strong></div>
        </div>
      </div>

      <!-- Emergency Contacts -->
      <div class="glass-card" style="padding: 1.5rem;">
        <h3 style="margin-bottom: 1rem; border-bottom: 1px solid var(--bg-card-border); padding-bottom: 0.5rem;">Emergency Contacts</h3>
        ${ems.length === 0 ? `<div style="color:var(--text-muted)">No emergency contact specified.</div>` : ems.map(e => `
          <div style="padding:0.75rem; background:rgba(255,255,255,0.03); border-radius:var(--radius-sm); margin-bottom:0.5rem;">
            <div style="font-weight:700;">${e.contact_name} (${e.relationship})</div>
            <div style="font-size:0.85rem; color:var(--text-secondary);">Mobile: <strong>${e.mobile}</strong> ${e.alternate_mobile ? `| Alt: ${e.alternate_mobile}` : ''}</div>
          </div>
        `).join('')}
      </div>

    </div>
  `;
}
