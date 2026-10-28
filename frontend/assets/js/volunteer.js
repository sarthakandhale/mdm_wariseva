/**
 * WariSeva Volunteer Management & Task Assignment JS Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('volunteerDashboardContainer')) {
    loadVolunteerDashboard();
  }
  if (document.getElementById('coordinatorRecommendationsContainer')) {
    const urlParams = new URLSearchParams(window.location.search);
    const taskId = urlParams.get('task_id') || 1;
    loadCoordinatorRecommendations(taskId);
  }
});

async function loadVolunteerDashboard() {
  const container = document.getElementById('volunteerDashboardContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading Assigned Tasks...</div>`;

  const res = await APIClient.get('/api/volunteer-tasks');
  if (res.success) {
    const tasks = res.data;
    container.innerHTML = tasks.map(t => `
      <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid ${t.priority === 'HIGH' || t.priority === 'CRITICAL' ? 'var(--color-accent-crimson)' : 'var(--color-primary)'};">
        <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
          <div>
            <div class="d-flex align-center gap-2">
              <h3 style="font-size:1.2rem;">${t.title}</h3>
              <span class="badge badge-pending">${t.priority}</span>
              <span class="badge badge-active">${t.status}</span>
            </div>
            <p style="font-size:0.875rem; color:var(--text-secondary); margin-top:0.3rem;">${t.description}</p>
            <div style="font-size:0.8rem; color:var(--text-muted); margin-top:0.4rem;">
              Code: <strong>${t.task_code}</strong> | Zone: <strong>${t.zone}</strong> | Source: <strong>${t.source_module} (${t.source_case_id || 'N/A'})</strong>
            </div>
          </div>

          <div class="d-flex gap-2">
            ${t.status === 'ASSIGNED' ? `
              <button class="btn btn-sm btn-success" onclick="handleAcceptTask(${t.id})">✓ Accept Task</button>
              <button class="btn btn-sm btn-danger" onclick="handleDeclineTask(${t.id})">✕ Decline</button>
            ` : ''}
            ${t.status === 'ACCEPTED' || t.status === 'IN_PROGRESS' ? `
              <button class="btn btn-sm btn-primary" onclick="handleCompleteTask(${t.id})">🏁 Complete Task</button>
            ` : ''}
            ${t.status === 'UNASSIGNED' ? `
              <a href="/coordinator/volunteers/recommendations.html?task_id=${t.id}" class="btn btn-sm btn-warning">🎯 Review Recommendations</a>
            ` : ''}
          </div>
        </div>
      </div>
    `).join('');
  }
}

async function loadCoordinatorRecommendations(taskId) {
  const container = document.getElementById('coordinatorRecommendationsContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Calculating Rule-Based Recommendation Scores...</div>`;

  const res = await APIClient.get(`/api/volunteer-tasks/${taskId}/recommendations`);
  if (res.success) {
    const recs = res.data;
    container.innerHTML = `
      <div class="glass-card" style="padding:1rem 1.25rem; margin-bottom:1.5rem; background:rgba(234,179,8,0.1); border:1px solid var(--color-accent-gold);">
        <strong style="color:var(--color-accent-gold);">ℹ️ System Recommendation Disclaimer:</strong>
        <span style="font-size:0.875rem;"> These scores are calculated using a 100% weighted rule-based matrix (Skill: 30%, Zone: 20%, Availability: 15%, Language: 15%, Workload: 10%, Experience: 10%). Coordinator authorization is required for assignment.</span>
      </div>

      ${recs.map(r => `
        <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-primary);">
          <div class="d-flex justify-between align-center">
            <div>
              <div class="d-flex align-center gap-2">
                <h3 style="font-size:1.2rem;">${r.volunteer_name}</h3>
                <span class="badge badge-active">Score: ${r.total_score}%</span>
              </div>
              <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.3rem;">
                Code: <strong>${r.volunteer_code}</strong> | Zone: <strong>${r.preferred_zone}</strong>
              </div>
              <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.4rem;">
                Breakdown: Skill: ${r.breakdown.skill} | Zone: ${r.breakdown.zone} | Language: ${r.breakdown.language} | Workload: ${r.breakdown.workload}
              </div>
            </div>
            <button class="btn btn-sm btn-primary" onclick="handleAssignTask(${taskId}, ${r.volunteer_id})">👉 Assign to Volunteer</button>
          </div>
        </div>
      `).join('')}
    `;
  }
}

async function handleAcceptTask(taskId) {
  const res = await APIClient.post(`/api/volunteer-tasks/${taskId}/accept`, { volunteer_id: 1 });
  if (res.success) {
    Auth.showToast('Task accepted successfully!', 'success');
    setTimeout(() => window.location.reload(), 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function handleDeclineTask(taskId) {
  const reason = prompt('Reason for declining task:');
  if (!reason) return;

  const res = await APIClient.post(`/api/volunteer-tasks/${taskId}/decline`, { volunteer_id: 1, decline_reason: reason });
  if (res.success) {
    Auth.showToast('Task declined.', 'info');
    setTimeout(() => window.location.reload(), 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function handleCompleteTask(taskId) {
  const notes = prompt('Enter task completion notes:');
  if (notes === null) return;

  const res = await APIClient.post(`/api/volunteer-tasks/${taskId}/complete`, { volunteer_id: 1, completion_notes: notes });
  if (res.success) {
    Auth.showToast('Task completed! Submitted to coordinator for verification.', 'success');
    setTimeout(() => window.location.reload(), 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function handleAssignTask(taskId, volId) {
  const res = await APIClient.post(`/api/volunteer-tasks/${taskId}/assign`, { volunteer_id: volId });
  if (res.success) {
    Auth.showToast('Task assigned to volunteer successfully!', 'success');
    setTimeout(() => {
      window.location.href = '/volunteer/dashboard.html';
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}
