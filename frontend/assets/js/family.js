/**
 * ReuniteAI Family Management JavaScript Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('familyDashboardContainer')) {
    loadFamilyDashboard();
  }
});

async function loadFamilyDashboard() {
  const container = document.getElementById('familyDashboardContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading family profiles...</div>`;

  const res = await APIClient.get('/api/families');

  if (!res.success) {
    container.innerHTML = `
      <div class="glass-card" style="padding:2rem;text-align:center;color:var(--color-accent-crimson);">
        ${res.message || 'Failed to load families.'}
      </div>
    `;
    return;
  }

  const families = res.data;
  if (!families || families.length === 0) {
    container.innerHTML = `
      <div class="glass-card" style="padding:3rem;text-align:center;">
        <div style="font-size:3rem;margin-bottom:1rem;">👨‍👩‍👧</div>
        <h3>No Family Registered Yet</h3>
        <p style="color:var(--text-secondary);margin:0.75rem 0 1.5rem 0;">
          Create your family profile for Puri Rath Yatra to keep your loved ones safe.
        </p>
        <a href="/family/create-family.html" class="btn btn-primary">+ Create New Family</a>
      </div>
    `;
    return;
  }

  container.innerHTML = families.map(f => renderFamilyCard(f)).join('');
}

function renderFamilyCard(family) {
  const members = family.members || [];
  return `
    <div class="glass-card" style="padding: 1.75rem; margin-bottom: 2rem; border-left: 4px solid var(--color-primary);">
      <!-- Header -->
      <div class="d-flex align-center justify-between" style="flex-wrap:wrap; gap:1rem; margin-bottom: 1.25rem;">
        <div>
          <div class="d-flex align-center gap-2">
            <h2 style="font-size:1.4rem;">${family.family_name}</h2>
            <span class="badge badge-active" style="font-family:monospace;font-size:0.8rem;">${family.family_code}</span>
          </div>
          <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.2rem;">
            Primary Contact: <strong>${family.primary_contact_name}</strong> (${family.primary_contact_mobile})
            | Emergency Contact: <strong>${family.emergency_contact_name}</strong> (${family.emergency_contact_mobile})
          </div>
        </div>
        <div class="d-flex gap-2">
          <a href="/person/add-person.html?family_id=${family.id}" class="btn btn-sm btn-primary">+ Add Member</a>
          <a href="/family/edit-family.html?id=${family.id}" class="btn btn-sm btn-secondary">✏️ Edit Family</a>
        </div>
      </div>

      <!-- Members Grid -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.25rem;">
        ${members.length === 0 ? `
          <div style="grid-column: 1 / -1; padding: 1.5rem; text-align: center; color: var(--text-muted); background: rgba(255,255,255,0.02); border-radius: var(--radius-md);">
            No family members added yet. Click <strong>+ Add Member</strong> to register children, adults, or elderly relatives.
          </div>
        ` : members.map(m => renderMemberCard(family.id, m)).join('')}
      </div>
    </div>
  `;
}

function renderMemberCard(familyId, member) {
  const categoryBadgeClass = {
    'CHILD': 'badge-rejected',      // Crimson highlight for priority
    'ELDERLY': 'badge-pending',     // Amber highlight
    'MINOR': 'badge-suspended',
    'ADULT': 'badge-active'
  }[member.age_category] || 'badge-active';

  const avatar = member.primary_photo ? `<img src="${member.primary_photo}" style="width:100%;height:100%;object-fit:cover;border-radius:50%;">` : member.full_name.substring(0, 2).toUpperCase();

  return `
    <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid var(--bg-card-border); border-radius: var(--radius-md); padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem;">
      <div class="d-flex align-center gap-2">
        <div class="avatar-circle" style="width:50px;height:50px;font-size:1.1rem;flex-shrink:0;overflow:hidden;">
          ${avatar}
        </div>
        <div style="flex-grow:1;min-width:0;">
          <div style="font-weight:700;font-size:1rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${member.full_name}</div>
          <div style="font-size:0.75rem;font-family:monospace;color:var(--color-accent-gold);">${member.person_code}</div>
        </div>
      </div>

      <div style="font-size:0.85rem;display:grid;grid-template-columns:1fr 1fr;gap:0.4rem;padding:0.5rem 0;border-top:1px solid var(--bg-card-border);border-bottom:1px solid var(--bg-card-border);">
        <div><span style="color:var(--text-muted)">Age:</span> <strong>${member.calculated_age} yrs</strong></div>
        <div><span style="color:var(--text-muted)">Rel:</span> <strong>${member.relationship}</strong></div>
        <div><span style="color:var(--text-muted)">Category:</span> <span class="badge ${categoryBadgeClass}" style="font-size:0.68rem;">${member.age_category}</span></div>
        <div><span style="color:var(--text-muted)">Safety ID:</span> <span style="font-size:0.72rem;color:var(--text-secondary)">Unlinked</span></div>
      </div>

      <div class="d-flex justify-between align-center" style="margin-top:auto;">
        <a href="/person/person-profile.html?person_id=${member.id}" class="btn btn-sm btn-secondary" style="font-size:0.78rem;">View Profile</a>
        <div class="d-flex gap-1">
          <a href="/person/edit-person.html?person_id=${member.id}" class="btn btn-sm btn-secondary" style="font-size:0.78rem;">Edit</a>
          <button class="btn btn-sm btn-danger" style="font-size:0.78rem;" onclick="handleDeactivateMember(${familyId}, ${member.id}, '${member.full_name}')">Deactivate</button>
        </div>
      </div>
    </div>
  `;
}

async function handleCreateFamilySubmit(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('button[type="submit"]');

  const payload = {
    family_name: document.getElementById('famName').value.trim(),
    primary_contact_name: document.getElementById('famPrimaryName').value.trim(),
    primary_contact_mobile: document.getElementById('famPrimaryMobile').value.trim(),
    emergency_contact_name: document.getElementById('famEmergencyName').value.trim(),
    emergency_contact_mobile: document.getElementById('famEmergencyMobile').value.trim(),
    preferred_language: document.getElementById('famLanguage').value,
    notes: document.getElementById('famNotes').value.trim()
  };

  btn.disabled = true;
  btn.innerText = 'Creating Family...';

  const res = await APIClient.post('/api/families', payload);

  btn.disabled = false;
  btn.innerText = 'Create Family Group';

  if (res.success) {
    Auth.showToast(`Family ${res.data.family_name} created successfully!`, 'success');
    setTimeout(() => {
      window.location.href = `/family/family-dashboard.html`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function handleDeactivateMember(familyId, personId, memberName) {
  const confirmMsg = `Are you sure you want to deactivate ${memberName}? Historical records will be retained safely for missing person matching.`;
  if (!confirm(confirmMsg)) return;

  const res = await APIClient.patch(`/api/families/${familyId}/members/${personId}/deactivate`, {});
  if (res.success) {
    Auth.showToast(res.message, 'success');
    loadFamilyDashboard();
  } else {
    Auth.showToast(res.message, 'error');
  }
}
