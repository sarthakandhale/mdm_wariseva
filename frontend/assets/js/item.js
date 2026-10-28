/**
 * WariSeva Lost & Found Item Assistance JS Module
 */

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('myLostItemsContainer')) {
    loadMyLostItems();
  }
  if (document.getElementById('foundItemsCatalogContainer')) {
    loadFoundItemsCatalog();
  }
  if (document.getElementById('storageCustodyDashboard')) {
    loadStorageCustodyDashboard();
  }
});

async function handleReportLostItemSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitLostItemBtn');
  btn.disabled = true;
  btn.innerText = 'Reporting Lost Item...';

  const payload = {
    item_category: document.getElementById('itemCategory').value,
    item_name: document.getElementById('itemName').value.trim(),
    brand: document.getElementById('itemBrand').value.trim(),
    model: document.getElementById('itemModel').value.trim(),
    color: document.getElementById('itemColor').value.trim(),
    approximate_value: parseFloat(document.getElementById('itemValue').value || 0),
    serial_number: document.getElementById('itemSerial').value.trim(),
    imei: document.getElementById('itemIMEI').value.trim(),
    description: document.getElementById('itemDesc').value.trim(),
    zone: document.getElementById('itemZone').value,
    landmark: document.getElementById('itemLandmark').value.trim(),
    location_description: document.getElementById('itemLocDesc').value.trim()
  };

  const res = await APIClient.post('/api/lost-items', payload);
  btn.disabled = false;
  btn.innerText = '📦 SUBMIT LOST ITEM REPORT';

  if (res.success) {
    const c = res.data;
    Auth.showToast(`Lost item report #${c.case_number} created!`, 'success');
    setTimeout(() => {
      window.location.href = `/lost-items/lost-item-success.html?case_id=${c.id}`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function handleReportFoundItemSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitFoundItemBtn');
  btn.disabled = true;
  btn.innerText = 'Registering Found Item...';

  const payload = {
    item_category: document.getElementById('foundCategory').value,
    item_name: document.getElementById('foundName').value.trim(),
    brand: document.getElementById('foundBrand').value.trim(),
    model: document.getElementById('foundModel').value.trim(),
    color: document.getElementById('foundColor').value.trim(),
    condition: document.getElementById('foundCondition').value,
    description: document.getElementById('foundDesc').value.trim(),
    zone: document.getElementById('foundZone').value,
    landmark: document.getElementById('foundLandmark').value.trim(),
    facility_name: document.getElementById('foundFacilityName').value.trim()
  };

  const res = await APIClient.post('/api/found-items', payload);
  btn.disabled = false;
  btn.innerText = '🟢 REGISTER FOUND ITEM';

  if (res.success) {
    const c = res.data;
    Auth.showToast(`Found item case #${c.case_number} registered!`, 'success');
    setTimeout(() => {
      window.location.href = `/found-items/found-item-success.html?case_id=${c.id}`;
    }, 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}

async function loadMyLostItems() {
  const container = document.getElementById('myLostItemsContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading lost items...</div>`;

  const res = await APIClient.get('/api/lost-items');
  if (res.success) {
    const items = res.data;
    if (items.length === 0) {
      container.innerHTML = `<div class="glass-card" style="padding:3rem;text-align:center;"><h3>No Lost Item Reports Filed</h3></div>`;
      return;
    }

    container.innerHTML = items.map(i => `
      <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-accent-gold);">
        <div class="d-flex justify-between align-center">
          <div>
            <div class="d-flex align-center gap-2">
              <h3>${i.case_number} - ${i.item_name}</h3>
              <span class="badge badge-pending">${i.status}</span>
            </div>
            <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.3rem;">
              Category: <strong>${i.item_category}</strong> | Lost Zone: <strong>${i.zone}</strong> (${i.landmark || 'No landmark'})
            </div>
          </div>
          <a href="/lost-items/lost-item-details.html?case_id=${i.id}" class="btn btn-sm btn-primary">View Details</a>
        </div>
      </div>
    `).join('');
  }
}

async function loadFoundItemsCatalog() {
  const container = document.getElementById('foundItemsCatalogContainer');
  if (!container) return;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Loading found items catalog...</div>`;

  const res = await APIClient.get('/api/found-items');
  if (res.success) {
    const items = res.data;
    container.innerHTML = items.map(i => `
      <div class="glass-card" style="padding:1.5rem; margin-bottom:1.25rem; border-left:4px solid var(--color-success);">
        <div class="d-flex justify-between align-center" style="flex-wrap:wrap;gap:1rem;">
          <div>
            <div class="d-flex align-center gap-2">
              <h3>${i.case_number} - ${i.item_name}</h3>
              <span class="badge badge-active">${i.condition} CONDITION</span>
              <span class="badge badge-pending">${i.status}</span>
            </div>
            <div style="font-size:0.85rem;color:var(--text-secondary);margin-top:0.3rem;">
              Category: <strong>${i.item_category}</strong> | Color: <strong>${i.color || 'N/A'}</strong> | Found Zone: <strong>${i.zone}</strong>
            </div>
          </div>
          <div class="d-flex gap-2">
            <a href="/found-items/found-item-details.html?case_id=${i.id}" class="btn btn-sm btn-primary">View Details</a>
            <a href="/claims/claim-item.html?case_id=${i.id}" class="btn btn-sm btn-success">🙋 Claim Ownership</a>
          </div>
        </div>
      </div>
    `).join('');
  }
}

async function loadStorageCustodyDashboard() {
  const container = document.getElementById('storageCustodyTableBody');
  if (!container) return;

  const res = await APIClient.get('/api/found-items');
  if (res.success) {
    const items = res.data;
    container.innerHTML = items.map(i => `
      <tr>
        <td><strong style="font-family:monospace;">${i.case_number}</strong></td>
        <td>${i.item_name} (${i.item_category})</td>
        <td>${i.zone}</td>
        <td><span class="badge badge-active">${i.status}</span></td>
        <td>
          <a href="/found-items/found-item-details.html?case_id=${i.id}" class="btn btn-sm btn-primary">Custody & Release</a>
        </td>
      </tr>
    `).join('');
  }
}
