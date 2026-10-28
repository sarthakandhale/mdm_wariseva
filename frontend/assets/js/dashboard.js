/**
 * ReuniteAI Dashboard & Control Panel Page Script
 */

document.addEventListener('DOMContentLoaded', () => {
  // Page Auto Loaders
  if (document.getElementById('pendingUsersTable')) {
    loadPendingUsers();
  }
  if (document.getElementById('allUsersTable')) {
    loadAllUsers();
  }
  if (document.getElementById('auditLogsTable')) {
    loadAuditLogs();
  }
  if (document.getElementById('profileForm')) {
    loadUserProfile();
  }
});

/* --- Pending Users Approval Screen --- */
async function loadPendingUsers() {
  const tableBody = document.getElementById('pendingUsersTableBody');
  if (!tableBody) return;

  tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;">Loading pending user accounts...</td></tr>`;

  const searchInput = document.getElementById('searchPendingInput');
  const searchVal = searchInput ? searchInput.value : '';

  const res = await APIClient.get(`/api/admin/users/pending?search=${encodeURIComponent(searchVal)}`);

  if (!res.success) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--color-accent-crimson);padding:2rem;">${res.message}</td></tr>`;
    return;
  }

  const users = res.data.users;
  const countBadge = document.getElementById('pendingCountBadge');
  if (countBadge) countBadge.innerText = `${res.data.total} Pending`;

  if (!users || users.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted);">No pending user approvals found.</td></tr>`;
    return;
  }

  tableBody.innerHTML = users.map(u => `
    <tr>
      <td>
        <div style="font-weight:600;">${u.full_name}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);">${u.uuid}</div>
      </td>
      <td>${u.mobile}</td>
      <td>${u.email || '<span style="color:var(--text-muted)">N/A</span>'}</td>
      <td><span class="badge badge-pending">${u.role_name.replace('_', ' ')}</span></td>
      <td>${new Date(u.created_at).toLocaleDateString()}</td>
      <td><span class="badge badge-pending">${u.status}</span></td>
      <td>
        <div style="display:flex;gap:0.4rem;">
          <button class="btn btn-sm btn-success" onclick="handleUserAction(${u.id}, 'approve')">Approve</button>
          <button class="btn btn-sm btn-danger" onclick="handleUserAction(${u.id}, 'reject')">Reject</button>
        </div>
      </td>
    </tr>
  `).join('');
}

/* --- Admin User Management Screen --- */
async function loadAllUsers() {
  const tableBody = document.getElementById('allUsersTableBody');
  if (!tableBody) return;

  tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;">Loading users directory...</td></tr>`;

  const statusFilter = document.getElementById('filterStatus') ? document.getElementById('filterStatus').value : '';
  const roleFilter = document.getElementById('filterRole') ? document.getElementById('filterRole').value : '';
  const searchVal = document.getElementById('searchUsersInput') ? document.getElementById('searchUsersInput').value : '';

  const queryParams = new URLSearchParams();
  if (statusFilter) queryParams.append('status', statusFilter);
  if (roleFilter) queryParams.append('role', roleFilter);
  if (searchVal) queryParams.append('search', searchVal);

  const res = await APIClient.get(`/api/admin/users?${queryParams.toString()}`);

  if (!res.success) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;color:var(--color-accent-crimson);padding:2rem;">${res.message}</td></tr>`;
    return;
  }

  const users = res.data.users;
  if (!users || users.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-muted);">No user accounts found matching criteria.</td></tr>`;
    return;
  }

  tableBody.innerHTML = users.map(u => `
    <tr>
      <td>
        <div style="font-weight:600;">${u.full_name}</div>
        <div style="font-size:0.75rem;color:var(--text-muted);">${u.uuid}</div>
      </td>
      <td>${u.mobile}</td>
      <td>${u.email || '<span style="color:var(--text-muted)">N/A</span>'}</td>
      <td><span class="badge badge-active">${u.role_name.replace('_', ' ')}</span></td>
      <td><span class="badge badge-${u.status.toLowerCase()}">${u.status}</span></td>
      <td>${u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Never'}</td>
      <td>
        <div style="display:flex;gap:0.35rem;">
          ${u.status !== 'ACTIVE' ? `<button class="btn btn-sm btn-success" onclick="handleUserAction(${u.id}, 'approve')">Activate</button>` : ''}
          ${u.status !== 'SUSPENDED' ? `<button class="btn btn-sm btn-warning" onclick="handleUserAction(${u.id}, 'suspend')">Suspend</button>` : ''}
          ${u.status !== 'BLOCKED' ? `<button class="btn btn-sm btn-danger" onclick="handleUserAction(${u.id}, 'block')">Block</button>` : ''}
        </div>
      </td>
    </tr>
  `).join('');
}

/* --- Admin User Status Action Handler --- */
async function handleUserAction(userId, action) {
  const confirmMsg = `Are you sure you want to ${action.toUpperCase()} user ID ${userId}?`;
  if (!confirm(confirmMsg)) return;

  const res = await APIClient.put(`/api/admin/users/${userId}/${action}`, {});

  if (res.success) {
    Auth.showToast(res.message, 'success');
    if (document.getElementById('pendingUsersTable')) loadPendingUsers();
    if (document.getElementById('allUsersTable')) loadAllUsers();
  } else {
    Auth.showToast(res.message, 'error');
  }
}

/* --- Audit Logs Screen --- */
async function loadAuditLogs() {
  const tableBody = document.getElementById('auditLogsTableBody');
  if (!tableBody) return;

  tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;">Loading audit logs...</td></tr>`;

  const actionFilter = document.getElementById('filterAction') ? document.getElementById('filterAction').value : '';

  let query = '/api/admin/audit-logs?limit=100';
  if (actionFilter) query += `&action=${encodeURIComponent(actionFilter)}`;

  const res = await APIClient.get(query);

  if (!res.success) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--color-accent-crimson);padding:2rem;">${res.message}</td></tr>`;
    return;
  }

  const logs = res.data.logs;
  if (!logs || logs.length === 0) {
    tableBody.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;color:var(--text-muted);">No audit log events recorded yet.</td></tr>`;
    return;
  }

  tableBody.innerHTML = logs.map(l => `
    <tr>
      <td style="font-size:0.8rem;color:var(--text-muted);">${new Date(l.created_at).toLocaleString()}</td>
      <td><strong>${l.user_name || 'System / Anonymous'}</strong> ${l.role_name ? `(${l.role_name})` : ''}</td>
      <td><span class="badge badge-active" style="background:rgba(79, 70, 229, 0.2);color:#a5b4fc;border-color:rgba(79,70,229,0.3);">${l.action}</span></td>
      <td style="font-size:0.85rem;font-family:monospace;max-width:300px;word-break:break-all;">${l.details || '-'}</td>
      <td style="font-size:0.8rem;">${l.ip_address || '127.0.0.1'}</td>
    </tr>
  `).join('');
}

/* --- User Profile Management Screen --- */
async function loadUserProfile() {
  const res = await APIClient.get('/api/users/me');

  if (!res.success) {
    Auth.showToast('Failed to load user profile details.', 'error');
    return;
  }

  const u = res.data;

  // Populate Form Fields
  document.getElementById('profileFullName').value = u.full_name || '';
  document.getElementById('profileMobile').value = u.mobile || '';
  document.getElementById('profileEmail').value = u.email || '';
  document.getElementById('profileLanguage').value = u.preferred_language || 'en';
  document.getElementById('profileRole').innerText = u.role_name ? u.role_name.replace('_', ' ') : '-';
  document.getElementById('profileStatus').innerHTML = `<span class="badge badge-${u.status.toLowerCase()}">${u.status}</span>`;
  document.getElementById('profileUuid').innerText = u.uuid || '-';
  document.getElementById('profileCreated').innerText = u.created_at ? new Date(u.created_at).toLocaleDateString() : '-';
  document.getElementById('profileLastLogin').innerText = u.last_login_at ? new Date(u.last_login_at).toLocaleString() : 'Never';

  // Initials Avatar
  const avatarElem = document.getElementById('profileAvatar');
  if (avatarElem) {
    const initials = u.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    avatarElem.innerText = initials;
  }
}

async function handleProfileUpdate(event) {
  event.preventDefault();
  const form = event.target;

  const full_name = document.getElementById('profileFullName').value.trim();
  const email = document.getElementById('profileEmail').value.trim();
  const preferred_language = document.getElementById('profileLanguage').value;
  const mobile = document.getElementById('profileMobile').value.trim();
  const mobile_otp = document.getElementById('profileOtpInput') ? document.getElementById('profileOtpInput').value.trim() : null;

  const payload = { full_name, email, preferred_language, mobile };
  if (mobile_otp) payload.mobile_verification_code = mobile_otp;

  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  btn.innerText = 'Saving Changes...';

  const res = await APIClient.put('/api/users/me', payload);

  btn.disabled = false;
  btn.innerText = 'Save Profile Changes';

  if (res.success) {
    Auth.showToast('Profile updated successfully!', 'success');
    // Update Local User Object
    const currentUser = Auth.getCurrentUser();
    if (currentUser) {
      currentUser.full_name = full_name;
      currentUser.email = email;
      currentUser.preferred_language = preferred_language;
      localStorage.setItem('reunite_user', JSON.stringify(currentUser));
    }
    loadUserProfile();
  } else {
    Auth.showToast(res.message, 'error');
  }
}
