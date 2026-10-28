/**
 * WariSeva Dindi Route, Location & Movement JS Module
 * Powered by Leaflet.js & OpenStreetMap
 */

let wariLeafletMap = null;

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('wariMapContainer')) {
    initWariMap('wariMapContainer');
  }
  if (document.getElementById('nearbyServicesContainer')) {
    initNearbyServicesView();
  }
});

function initWariMap(elementId) {
  const container = document.getElementById(elementId);
  if (!container || typeof L === 'undefined') return;

  // Initialize Leaflet Map centered around Pune/Saswad Wari region
  wariLeafletMap = L.map(elementId).setView([18.5204, 73.8567], 10);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors | WariSeva'
  }).addTo(wariLeafletMap);

  // Draw Alandi -> Pune -> Saswad -> Jejuri -> Pandharpur Polyline
  const routePoints = [
    [18.6773, 73.8968], // Alandi
    [18.5204, 73.8567], // Pune
    [18.3450, 74.0320], // Saswad
    [18.2750, 74.1590], // Jejuri
    [18.0400, 74.1860], // Lonand
    [17.9870, 74.4330], // Phaltan
    [17.6980, 74.9080], // Malshiras
    [17.6778, 75.3278]  // Pandharpur
  ];

  L.polyline(routePoints, {
    color: '#3b82f6',
    weight: 5,
    opacity: 0.8,
    dashArray: '8, 8'
  }).addTo(wariLeafletMap);

  loadMapLocations(wariLeafletMap);
}

async function loadMapLocations(map) {
  const res = await APIClient.get('/api/locations');
  if (res.success) {
    const locations = res.data;
    locations.forEach(loc => {
      let iconColor = 'blue';
      if (loc.location_type === 'MEDICAL_CAMP') iconColor = 'green';
      if (loc.location_type === 'HELP_CENTER') iconColor = 'orange';
      if (loc.location_type === 'WATER_POINT') iconColor = 'cyan';

      const popupHtml = `
        <div style="font-family:sans-serif; padding:4px;">
          <strong style="font-size:1rem; color:#1e293b;">${loc.name}</strong><br>
          <span style="font-size:0.8rem; color:#64748b;">Type: ${loc.location_type} | Zone: ${loc.zone}</span><br>
          <p style="font-size:0.85rem; margin-top:4px;">${loc.description || ''}</p>
          <div style="font-size:0.8rem; margin-top:4px;">📞 ${loc.contact_number || 'N/A'}</div>
        </div>
      `;

      L.marker([loc.latitude, loc.longitude])
        .addTo(map)
        .bindPopup(popupHtml);
    });
  }
}

async function initNearbyServicesView() {
  const container = document.getElementById('nearbyServicesContainer');
  if (!container) return;

  // Default to Saswad coordinates (18.345, 74.032)
  const lat = 18.3450;
  const lon = 74.0320;

  container.innerHTML = `<div class="glass-card" style="padding:2rem;text-align:center;">Searching nearby facilities within 5 km...</div>`;

  const res = await APIClient.get(`/api/locations/nearby?latitude=${lat}&longitude=${lon}&radius=5.0`);
  if (res.success) {
    const items = res.data;
    if (items.length === 0) {
      container.innerHTML = `<div class="glass-card" style="padding:2rem;">No nearby facilities found within 5 km.</div>`;
      return;
    }

    container.innerHTML = items.map(i => `
      <div class="glass-card" style="padding:1.25rem; margin-bottom:1rem; border-left:4px solid var(--color-success);">
        <div class="d-flex justify-between align-center">
          <div>
            <h4 style="font-size:1.1rem;">${i.name}</h4>
            <div style="font-size:0.85rem; color:var(--text-secondary); margin-top:0.2rem;">
              Type: <strong>${i.location_type}</strong> | Zone: <strong>${i.zone}</strong>
            </div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:1.2rem; font-weight:700; color:var(--color-primary);">${i.distance_km} km</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">Straight-line distance</div>
          </div>
        </div>
      </div>
    `).join('');
  }
}

async function handleUpdateLocationSubmit(e) {
  e.preventDefault();
  const btn = document.getElementById('submitLocBtn');
  btn.disabled = true;
  btn.innerText = 'Updating Location...';

  const payload = {
    latitude: parseFloat(document.getElementById('locLat').value),
    longitude: parseFloat(document.getElementById('locLon').value),
    location_source: document.getElementById('locSource').value,
    status: document.getElementById('locStatus').value
  };

  const res = await APIClient.post('/api/dindis/1/location', payload);
  btn.disabled = false;
  btn.innerText = '📍 UPDATE DINDI LOCATION';

  if (res.success) {
    Auth.showToast('Dindi location updated successfully!', 'success');
    setTimeout(() => window.location.reload(), 800);
  } else {
    Auth.showToast(res.message, 'error');
  }
}
