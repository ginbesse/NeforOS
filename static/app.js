const appGrid = document.getElementById('appGrid');
const weatherValue = document.getElementById('weatherValue');
const quoteValue = document.getElementById('quoteValue');
const batteryValue = document.getElementById('batteryValue');
const storeValue = document.getElementById('storeValue');
const browserStatus = document.getElementById('browserStatus');
const messagesStatus = document.getElementById('messagesStatus');
const cameraStatus = document.getElementById('cameraStatus');
const contactPermissionLabel = document.getElementById('contactPermissionLabel');
const activeAppLabel = document.getElementById('activeAppLabel');
const streamStatus = document.getElementById('streamStatus');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const searchResults = document.getElementById('searchResults');
const galleryInput = document.getElementById('galleryInput');
const galleryButton = document.getElementById('galleryButton');
const galleryResults = document.getElementById('galleryResults');
const galleryTitle = document.getElementById('galleryTitle');
const galleryDescription = document.getElementById('galleryDescription');
const galleryUrl = document.getElementById('galleryUrl');
const galleryUploadButton = document.getElementById('galleryUploadButton');
const galleryAlbumButton = document.getElementById('galleryAlbumButton');
const appScreen = document.getElementById('appScreen');
const workflowPanel = document.getElementById('workflowPanel');
const timeLabel = document.getElementById('timeLabel');
const setupButton = document.getElementById('setupButton');
const chargeButton = document.getElementById('chargeButton');
const homeButton = document.getElementById('homeButton');

function updateClock() {
  const now = new Date();
  timeLabel.textContent = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

async function loadApps() {
  const response = await fetch('/api/apps');
  const payload = await response.json();
  appGrid.innerHTML = payload.apps.map((app) => `
    <article class="app-card" data-app-id="${app.id}">
      <div class="icon" style="background:${app.accent}">${app.icon}</div>
      <strong>${app.name}</strong>
      <small>${app.category}</small>
      <div>${app.installed ? 'Installed' : 'Available'}</div>
    </article>
  `).join('');

  appGrid.querySelectorAll('.app-card').forEach((card) => {
    card.addEventListener('click', async () => {
      const appId = card.getAttribute('data-app-id');
      const response = await fetch('/api/apps/launch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ appId }),
      });
      const payload = await response.json();
      activeAppLabel.textContent = payload.activeApp;
      appScreen.innerHTML = `<h3>${payload.screen.title}</h3><p>${payload.screen.content}</p>`;
      const streamResponse = await fetch(`/api/app/stream?appId=${appId}`);
      const streamPayload = await streamResponse.json();
      streamStatus.textContent = `${streamPayload.name}: ${streamPayload.status} (${streamPayload.buffer}%)`;
    });
  });
}

async function loadWeather() {
  const response = await fetch('/api/weather?city=Istanbul');
  const payload = await response.json();
  weatherValue.innerHTML = `<strong>${payload.temperature}°C</strong><br>${payload.city}`;
}

async function loadQuote() {
  const response = await fetch('/api/quote');
  const payload = await response.json();
  quoteValue.textContent = `“${payload.content}” — ${payload.author}`;
}

async function loadSystemInfo() {
  const response = await fetch('/api/system/status');
  const payload = await response.json();
  batteryValue.innerHTML = `<strong>${payload.battery}%</strong><br>${payload.batteryCharging ? 'Charging' : 'On battery'}`;
  storeValue.innerHTML = `<strong>${payload.installedApps.length} apps</strong><br>Store ready`;
  browserStatus.textContent = 'Ready';
  messagesStatus.textContent = 'Connected';
  cameraStatus.textContent = 'Ultra ready';
  contactPermissionLabel.textContent = payload.contactPermission || 'Pending';
  activeAppLabel.textContent = payload.activeApp || 'Home';
  renderWorkflowPanel();
}

async function renderWorkflowPanel() {
  const [cameraResponse, callResponse] = await Promise.all([
    fetch('/api/camera/status'),
    fetch('/api/calls/state')
  ]);
  const cameraPayload = await cameraResponse.json();
  const callPayload = await callResponse.json();
  workflowPanel.innerHTML = `
    <div class="workflow-card">
      <h4>Camera</h4>
      <p>${cameraPayload.preview ? 'Preview active' : 'Ready for capture'}</p>
      <button data-action="camera-preview">Start Preview</button>
    </div>
    <div class="workflow-card">
      <h4>Messages</h4>
      <p>Compose a secure message instantly.</p>
      <input id="composeInput" placeholder="Type a message" />
      <button data-action="send-message">Send</button>
    </div>
    <div class="workflow-card">
      <h4>Call</h4>
      <p>${callPayload.active ? `In call with ${callPayload.peer}` : 'Ready for voice or video'}</p>
      <button data-action="start-call">Start Call</button>
    </div>
  `;

  workflowPanel.querySelectorAll('button').forEach((button) => {
    button.addEventListener('click', async () => {
      const action = button.getAttribute('data-action');
      if (action === 'camera-preview') {
        await fetch('/api/camera/preview', { method: 'POST' });
      }
      if (action === 'send-message') {
        const composeInput = document.getElementById('composeInput');
        if (composeInput && composeInput.value) {
          await fetch('/api/messages/thread', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contactId: 1, text: composeInput.value }),
          });
          composeInput.value = '';
        }
      }
      if (action === 'start-call') {
        await fetch('/api/calls/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ peer: 'Ayla', mode: 'video' }),
        });
      }
      await renderWorkflowPanel();
    });
  });
}

chargeButton.addEventListener('click', async () => {
  const response = await fetch('/api/system/charge', { method: 'POST' });
  const payload = await response.json();
  batteryValue.innerHTML = `<strong>${payload.battery}%</strong><br>Charging`;
});

homeButton.addEventListener('click', async () => {
  const response = await fetch('/api/system/home', { method: 'POST' });
  const payload = await response.json();
  activeAppLabel.textContent = payload.activeApp;
  appScreen.innerHTML = '<h3>Home</h3><p>You are back on the operating-system home screen.</p>';
});

async function runSearch(query) {
  if (!query) return;
  searchResults.innerHTML = '<div class="search-card"><p>Searching with premium intelligence…</p></div>';
  const response = await fetch(`/api/browser/search?q=${encodeURIComponent(query)}`);
  const payload = await response.json();
  searchResults.innerHTML = payload.results.map((item) => `
    <article class="search-card">
      <h3>${item.title}</h3>
      <p>${item.snippet}</p>
      <a href="${item.url}" target="_blank" rel="noreferrer">Open result</a>
    </article>
  `).join('');
}

searchButton.addEventListener('click', () => runSearch(searchInput.value));
searchInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    runSearch(searchInput.value);
  }
});

async function runGallery(query) {
  if (!query) return;
  galleryResults.innerHTML = '<div class="search-card"><p>Loading gallery feed…</p></div>';
  const response = await fetch(`/api/gallery?query=${encodeURIComponent(query)}`);
  const payload = await response.json();
  galleryResults.innerHTML = payload.items.map((item) => `
    <article class="gallery-card">
      <img src="${item.imageUrl}" alt="${item.title}" />
      <div class="gallery-card-content">
        <h3>${item.title}</h3>
        <p>${item.description}</p>
        <span>${item.likes} likes · ${item.source}</span>
        <div class="button-row" style="margin-top:8px">
          <button data-action="favorite" data-item-id="${item.id}">★ Favorite</button>
        </div>
      </div>
    </article>
  `).join('');

  galleryResults.querySelectorAll('[data-action="favorite"]').forEach((button) => {
    button.addEventListener('click', async () => {
      const itemId = button.getAttribute('data-item-id');
      await fetch(`/api/gallery/${itemId}/favorite`, { method: 'POST' });
      runGallery(galleryInput.value || 'technology');
    });
  });
}

galleryButton.addEventListener('click', () => runGallery(galleryInput.value));
galleryInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    runGallery(galleryInput.value);
  }
});

galleryUploadButton.addEventListener('click', async () => {
  const formData = new FormData();
  formData.append('title', galleryTitle.value || 'Untitled');
  formData.append('description', galleryDescription.value || '');
  formData.append('imageUrl', galleryUrl.value || '');
  await fetch('/api/gallery/upload', { method: 'POST', body: formData });
  galleryTitle.value = '';
  galleryDescription.value = '';
  galleryUrl.value = '';
  runGallery(galleryInput.value || 'technology');
});

galleryAlbumButton.addEventListener('click', async () => {
  const name = prompt('Album name', 'Travel');
  if (!name) return;
  await fetch('/api/gallery/albums', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  runGallery(galleryInput.value || 'technology');
});

setupButton.addEventListener('click', async () => {
  await Promise.all([loadApps(), loadWeather(), loadQuote(), loadSystemInfo()]);
  setupButton.textContent = 'Setup Complete';
});

updateClock();
setInterval(updateClock, 1000);
loadApps().catch(() => {});
loadWeather().catch(() => {});
loadQuote().catch(() => {});
loadSystemInfo().catch(() => {});
runGallery('technology').catch(() => {});
