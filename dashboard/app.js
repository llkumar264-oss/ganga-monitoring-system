const API_BASE = 'http://127.0.0.1:8000';
const VARANASI_CENTER = [25.3176, 82.9739];

let map, heatmapLayer, markersLayer;
let chemicalChart, complaintsChart;

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('view-' + tab.dataset.view).classList.add('active');
    if (tab.dataset.view === 'map') initMap();
    if (tab.dataset.view === 'heatmap') initHeatmap();
    if (tab.dataset.view === 'government') loadGovernmentPanel();
  });
});

// Initialize main map
function initMap() {
  if (map) {
    map.remove();
    map = null;
  }
  map = L.map('map').setView(VARANASI_CENTER, 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(map);
  markersLayer = L.layerGroup().addTo(map);
  loadMapData();
}

function getMarkerColor(riskLevel) {
  const r = (riskLevel || 'LOW').toUpperCase();
  if (r === 'CRITICAL') return '#c0392b';
  if (r === 'HIGH') return '#e74c3c';
  if (r === 'MEDIUM') return '#f39c12';
  return '#27ae60';
}

function getMarkerIcon(riskLevel) {
  return L.divIcon({
    className: 'custom-marker',
    html: `<span style="background:${getMarkerColor(riskLevel)};width:14px;height:14px;border-radius:50%;display:inline-block;border:2px solid #fff;box-shadow:0 1px 3px rgba(0,0,0,.3)"></span>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  });
}

function loadMapData() {
  Promise.all([
    fetch(`${API_BASE}/pollution-hotspots`).then(r => r.json()),
    fetch(`${API_BASE}/complaint/map`).then(r => r.json())
  ]).then(([hotspots, complaints]) => {
    markersLayer.clearLayers();
    hotspots.forEach(p => {
      const m = L.marker([p.lat, p.lon], { icon: getMarkerIcon(p.risk_level) })
        .bindPopup(`<strong>${p.location}</strong><br>pH: ${p.ph} | Turbidity: ${p.turbidity} | Chemical: ${p.chemical}<br><small>${p.status}</small>`);
      markersLayer.addLayer(m);
    });
    complaints.forEach(c => {
      const m = L.marker([c.lat, c.lon], {
        icon: L.divIcon({
          className: 'complaint-marker',
          html: '<span class="complaint-pin">📋</span>',
          iconSize: [24, 24],
          iconAnchor: [12, 24],
        })
      }).bindPopup(`<strong>${c.name}</strong><br>${c.description}<br><small>Status: ${c.status}</small>`);
      markersLayer.addLayer(m);
    });
    updateStatus();
  }).catch(err => {
    console.error(err);
    document.getElementById('lastUpdate').textContent = 'Error loading data';
  });
}

// Heatmap: green = pure, yellow = normal, red = highly risky
function initHeatmap() {
  if (heatmapLayer && window.heatmapMap) {
    heatmapLayer.remove();
    window.heatmapMap.remove();
  }
  const el = document.getElementById('heatmap');
  if (!el.offsetParent) return;
  window.heatmapMap = L.map('heatmap').setView(VARANASI_CENTER, 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap'
  }).addTo(window.heatmapMap);
  // Gradient: 0 = green (pure), 0.4 = yellow (normal), 1 = red (highly risky)
  const heatGradient = {
    0.0: '#22c55e',   // green - pure / safe
    0.35: '#84cc16',  // lime
    0.5: '#eab308',   // yellow - normal
    0.65: '#f97316',  // orange
    0.85: '#ef4444',  // red - risky
    1.0: '#b91c1c'    // dark red - highly risky
  };
  fetch(`${API_BASE}/heatmap-data`).then(r => r.json()).then(data => {
    heatmapLayer = L.heatLayer(data, {
      radius: 35,
      blur: 20,
      maxZoom: 17,
      gradient: heatGradient,
      max: 1,
      minOpacity: 0.6
    }).addTo(window.heatmapMap);
  }).catch(console.error);
}

// Sensor table
function loadSensorTable() {
  fetch(`${API_BASE}/pollution-hotspots`).then(r => r.json()).then(data => {
    const tbody = document.getElementById('sensorTable');
    tbody.innerHTML = data.map(p => `
      <tr class="risk-${(p.risk_level || 'low').toLowerCase()}">
        <td>${p.location}</td>
        <td>${p.ph}</td>
        <td>${p.turbidity}</td>
        <td>${p.chemical}</td>
        <td><span class="badge badge-${(p.risk_level || 'low').toLowerCase()}">${p.risk_level || 'LOW'}</span></td>
        <td>${p.status}</td>
      </tr>
    `).join('');
    updateStatus();
  }).catch(console.error);
}

document.getElementById('refreshSensors')?.addEventListener('click', loadSensorTable);

// Complaint form
document.getElementById('complaintForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  const form = e.target;
  const fd = new FormData();
  fd.append('name', form.name.value);
  fd.append('description', form.description.value);
  fd.append('lat', form.lat.value);
  fd.append('lon', form.lon.value);
  fd.append('file', form.file.files[0]);
  const res = document.getElementById('complaintResult');
  try {
    const r = await fetch(`${API_BASE}/complaint`, { method: 'POST', body: fd });
    const data = await r.json();
    if (r.ok) {
      res.innerHTML = `<span class="success">Complaint registered successfully. ID: ${data.id}</span>`;
      form.reset();
    } else {
      res.innerHTML = `<span class="error">${data.detail || 'Failed to submit'}</span>`;
    }
  } catch (err) {
    res.innerHTML = `<span class="error">Network error: ${err.message}</span>`;
  }
});

// Government panel
function loadGovernmentPanel() {
  fetch(`${API_BASE}/analytics`).then(r => r.json()).then(data => {
    const cs = data.complaint_stats || {};
    document.getElementById('totalComplaints').textContent = cs.total ?? '-';
    document.getElementById('pendingComplaints').textContent = cs.pending ?? '-';
    const criticalCount = (data.pollution_zones || []).filter(z => z.risk_count > 0).length;
    document.getElementById('criticalZones').textContent = criticalCount;

    // Chemical chart
    const zones = data.pollution_zones || [];
    if (chemicalChart) chemicalChart.destroy();
    const ctx = document.getElementById('chartChemical').getContext('2d');
    chemicalChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: zones.map(z => z.location),
        datasets: [{ label: 'Avg Chemical', data: zones.map(z => z.avg_chemical), backgroundColor: 'rgba(231,76,60,0.7)' }]
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });

    // Complaints pie
    if (complaintsChart) complaintsChart.destroy();
    const ctx2 = document.getElementById('chartComplaints').getContext('2d');
    complaintsChart = new Chart(ctx2, {
      type: 'doughnut',
      data: {
        labels: ['Pending', 'In Review', 'Resolved'],
        datasets: [{ data: [cs.pending || 0, cs.in_review || 0, cs.resolved || 0], backgroundColor: ['#e74c3c', '#f39c12', '#27ae60'] }]
      },
      options: { responsive: true }
    });

    // Zones table
    const tbody = document.getElementById('zonesTable');
    tbody.innerHTML = zones.map(z => `
      <tr>
        <td>${z.location}</td>
        <td>${z.avg_chemical.toFixed(1)}</td>
        <td>${z.avg_turbidity.toFixed(1)}</td>
        <td>${z.risk_count}</td>
      </tr>
    `).join('');
  }).catch(console.error);
}

function updateStatus() {
  document.getElementById('lastUpdate').textContent = 'Updated ' + new Date().toLocaleTimeString();
}

// Initial load
function init() {
  initMap();
  loadSensorTable();
  setInterval(() => {
    if (document.querySelector('.tab.active')?.dataset.view === 'map') loadMapData();
    if (document.querySelector('.tab.active')?.dataset.view === 'sensors') loadSensorTable();
  }, 15000);
}

init();
