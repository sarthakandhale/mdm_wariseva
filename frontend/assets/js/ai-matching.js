/**
 * WariSeva AI-Assisted Matching & Intelligent Recommendation JS Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('aiDashboardMetrics')) {
    loadAIDashboard();
  }
  if (document.getElementById('sideBySideMatchContainer')) {
    loadSideBySideComparison();
  }
});

async function loadAIDashboard() {
  const metricsBox = document.getElementById('aiDashboardMetrics');
  const recentBox = document.getElementById('aiRecentMatchesBody');
  if (!metricsBox) return;

  metricsBox.innerHTML = `<div class="glass-card" style="padding:1.5rem;text-align:center;">Loading AI Engine Metrics...</div>`;

  const res = await APIClient.get('/api/ai/dashboard');
  if (res.success) {
    const m = res.data.metrics;
    const recent = res.data.recent_matches;

    metricsBox.innerHTML = `
      <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:1.25rem;">
        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-primary);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">TOTAL AI MATCHES</div>
          <div style="font-size:2rem; font-weight:700; margin-top:0.2rem;">${m.total_matches}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem;">Person: ${m.person_matches} | Item: ${m.item_matches}</div>
        </div>

        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-success);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">HIGH CONFIDENCE (≥80%)</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-success); margin-top:0.2rem;">${m.high_confidence}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem;">Candidate pairs ready for review</div>
        </div>

        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-accent-gold);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">AWAITING REVIEW</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-accent-gold); margin-top:0.2rem;">${m.awaiting_review}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem;">Human verification required</div>
        </div>

        <div class="glass-card" style="padding:1.25rem; border-top:4px solid var(--color-accent-crimson);">
          <div style="font-size:0.8rem; color:var(--text-secondary);">FALSE MATCHES</div>
          <div style="font-size:2rem; font-weight:700; color:var(--color-accent-crimson); margin-top:0.2rem;">${m.false_matches}</div>
          <div style="font-size:0.75rem; color:var(--text-muted); margin-top:0.3rem;">Operator rejected candidates</div>
        </div>
      </div>
    `;

    if (recentBox) {
      if (recent.length === 0) {
        recentBox.innerHTML = `<tr><td colspan="6" style="text-align:center;padding:2rem;">No AI recommendations generated yet.</td></tr>`;
        return;
      }

      recentBox.innerHTML = recent.map(r => `
        <tr>
          <td><span class="badge ${r.match_type === 'PERSON' ? 'badge-primary' : 'badge-active'}">${r.match_type}</span></td>
          <td><strong style="font-family:monospace;">Source #${r.source_case_id} ↔ Candidate #${r.candidate_case_id}</strong></td>
          <td>
            <div style="font-weight:700; color:${r.match_score >= 80 ? 'var(--color-success)' : 'var(--color-accent-gold)'};">
              ${r.match_score}% (Confidence: ${r.confidence_score}%)
            </div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Data Quality: ${r.data_quality_score}%</div>
          </td>
          <td><span class="badge badge-pending">${r.status}</span></td>
          <td>
            <a href="/ai/match-details.html?match_id=${r.id}" class="btn btn-sm btn-primary">🔍 Side-by-Side Review</a>
          </td>
        </tr>
      `).join('');
    }
  }
}

async function triggerPersonMatching(lostCaseId) {
  Auth.showToast("Executing AI Person Matching Pipeline A...", "info");
  const res = await APIClient.post(`/api/ai/match/person/${lostCaseId}`);
  if (res.success) {
    Auth.showToast(`AI engine identified ${res.data.length} candidate matches!`, "success");
    setTimeout(() => {
      window.location.reload();
    }, 800);
  } else {
    Auth.showToast(res.message, "error");
  }
}

async function triggerItemMatching(lostItemId) {
  Auth.showToast("Executing AI Item Matching Pipeline B...", "info");
  const res = await APIClient.post(`/api/ai/match/item/${lostItemId}`);
  if (res.success) {
    Auth.showToast(`AI engine identified ${res.data.length} candidate item matches!`, "success");
    setTimeout(() => {
      window.location.reload();
    }, 800);
  } else {
    Auth.showToast(res.message, "error");
  }
}

async function loadSideBySideComparison() {
  const container = document.getElementById('sideBySideMatchContainer');
  if (!container) return;

  const urlParams = new URLSearchParams(window.location.search);
  const matchId = urlParams.get('match_id');

  if (!matchId) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;">No Match ID specified.</div>`;
    return;
  }

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading AI Match Comparison...</div>`;

  const res = await APIClient.get(`/api/ai/matches/${matchId}`);
  if (!res.success) {
    container.innerHTML = `<div class="glass-card" style="padding:2rem;color:var(--color-accent-crimson);">${res.message}</div>`;
    return;
  }

  const m = res.data;
  const isPerson = m.match_type === 'PERSON';
  const src = m.source_case || {};
  const cand = m.candidate_case || {};
  const exp = m.explanation || { reasons: [] };

  container.innerHTML = `
    <!-- AI Disclaimer Banner -->
    <div style="background:rgba(234,179,8,0.15); border:1px solid var(--color-accent-gold); color:var(--color-accent-gold); padding:0.85rem 1.25rem; border-radius:var(--radius-md); margin-bottom:1.5rem; font-weight:600; font-size:0.9rem;" class="d-flex align-center gap-2">
      <span>⚠️</span>
      <span><strong>AI DECISION SUPPORT NOTICE:</strong> This is an AI-generated potential match recommendation. This result is NOT identity confirmation. Verification by authorized personnel is required.</span>
    </div>

    <!-- Match Header Card -->
    <div class="glass-card" style="padding:1.75rem; margin-bottom:1.5rem; text-align:center; border-top:4px solid var(--color-primary);">
      <div style="font-size:0.85rem; color:var(--text-secondary); text-transform:uppercase; letter-spacing:1px;">
        Pipeline ${isPerson ? 'A: Person Matching' : 'B: Item Matching'} Recommendation #${m.id}
      </div>
      <div style="font-size:2.5rem; font-weight:800; color:var(--color-success); margin:0.4rem 0;">
        ${m.match_score}% <span style="font-size:1.1rem; font-weight:500; color:var(--text-secondary);">Potential Match</span>
      </div>
      <div class="d-flex justify-center gap-3" style="font-size:0.85rem; color:var(--text-muted);">
        <span>Confidence: <strong>${m.confidence_score}%</strong></span> | 
        <span>Data Quality: <strong>${m.data_quality_score}%</strong></span> | 
        <span>Model Version: <strong>${m.model_version}</strong></span> | 
        <span>Status: <span class="badge badge-pending">${m.status}</span></span>
      </div>
    </div>

    <!-- Explainability Card -->
    <div class="glass-card" style="padding:1.5rem; margin-bottom:1.5rem; border-left:4px solid var(--color-accent-gold);">
      <h3 style="margin-bottom:0.75rem;">💡 AI Match Reasons & Contributing Evidence</h3>
      <ul style="margin:0; padding-left:1.25rem; line-height:1.8;">
        ${(exp.reasons || []).map(r => `<li style="color:var(--text-primary); font-size:0.95rem;">${r}</li>`).join('')}
      </ul>
    </div>

    <!-- Side-by-Side Comparison Grid -->
    <div style="display:grid; grid-template-columns:1fr 1fr; gap:1.5rem; margin-bottom:1.75rem;">
      <!-- Left: Source Lost Case -->
      <div class="glass-card" style="padding:1.5rem; border-top:4px solid var(--color-accent-gold);">
        <h3 style="margin-bottom:1rem; border-bottom:1px solid var(--bg-card-border); padding-bottom:0.5rem;">
          📦 Lost Case #${src.case_number || m.source_case_id}
        </h3>
        <div style="font-size:0.9rem; display:flex; flex-direction:column; gap:0.6rem;">
          <div><span style="color:var(--text-muted);">${isPerson ? 'Name' : 'Item Name'}:</span> <strong>${src.full_name || src.item_name || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Age / Gender' : 'Category'}:</span> <strong>${src.age || src.item_category || 'N/A'} / ${src.gender || src.brand || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Top Wear' : 'Model / Color'}:</span> <strong>${src.top_wear_color || ''} ${src.top_wear_type || src.model || ''} (${src.color || ''})</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Bottom Wear' : 'Description'}:</span> <strong>${src.bottom_wear_color || ''} ${src.bottom_wear_type || src.description || ''}</strong></div>
          <div><span style="color:var(--text-muted);">Zone / Landmark:</span> <strong>${(src.location || {}).zone || 'N/A'} (${(src.location || {}).landmark || 'N/A'})</strong></div>
        </div>
      </div>

      <!-- Right: Candidate Found Case -->
      <div class="glass-card" style="padding:1.5rem; border-top:4px solid var(--color-success);">
        <h3 style="margin-bottom:1rem; border-bottom:1px solid var(--bg-card-border); padding-bottom:0.5rem;">
          🟢 Found Case #${cand.case_number || m.candidate_case_id}
        </h3>
        <div style="font-size:0.9rem; display:flex; flex-direction:column; gap:0.6rem;">
          <div><span style="color:var(--text-muted);">${isPerson ? 'Name / Status' : 'Item Name'}:</span> <strong>${cand.full_name || cand.item_name || 'Unidentified'}</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Est. Age / Gender' : 'Category'}:</span> <strong>${cand.estimated_age || cand.item_category || 'N/A'} / ${cand.gender || cand.brand || 'N/A'}</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Top Wear' : 'Model / Color'}:</span> <strong>${cand.top_wear_color || ''} ${cand.top_wear_type || cand.model || ''} (${cand.color || ''})</strong></div>
          <div><span style="color:var(--text-muted);">${isPerson ? 'Bottom Wear' : 'Description'}:</span> <strong>${cand.bottom_wear_color || ''} ${cand.bottom_wear_type || cand.description || ''}</strong></div>
          <div><span style="color:var(--text-muted);">Zone / Landmark:</span> <strong>${(cand.location || {}).zone || 'N/A'} (${(cand.location || {}).landmark || 'N/A'})</strong></div>
        </div>
      </div>
    </div>

    <!-- Human Decision Action Bar -->
    <div class="glass-card" style="padding:1.5rem; text-align:center;">
      <h3 style="margin-bottom:0.5rem;">👮 Human Operator Decision Review</h3>
      <p style="color:var(--text-secondary); font-size:0.85rem; margin-bottom:1.25rem;">
        Authorize next steps for human verification. Accepting this candidate routes it to the formal identity verification desk.
      </p>
      <div class="d-flex justify-center gap-3">
        <button class="btn btn-success" onclick="handleMatchReview(${m.id}, 'ACCEPTED_FOR_VERIFICATION')">✅ ACCEPT FOR HUMAN VERIFICATION</button>
        <button class="btn btn-danger" onclick="handleMatchReview(${m.id}, 'FALSE_MATCH')">❌ REJECT AS FALSE MATCH</button>
      </div>
    </div>
  `;
}

async function handleMatchReview(matchId, decision) {
  const notes = prompt("Enter human operator review notes:", decision === 'ACCEPTED_FOR_VERIFICATION' ? "Confirmed strong clothing & location match signal." : "Divergent physical characteristics.");
  if (!notes) return;

  const res = await APIClient.patch(`/api/ai/matches/${matchId}/review`, { decision, notes });
  if (res.success) {
    Auth.showToast(`AI match decision updated to ${decision}!`, "success");
    setTimeout(() => {
      window.location.reload();
    }, 800);
  } else {
    Auth.showToast(res.message, "error");
  }
}
