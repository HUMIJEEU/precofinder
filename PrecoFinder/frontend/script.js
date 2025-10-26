// API base: tenta 1) localStorage, 2) valor por defeito (Render sugerido), 3) mesmo domínio
const FALLBACK_RENDER = 'https://melhorprecofinder.onrender.com'; // ajusta se o Render gerar outro domínio
function getApiBase() {
  return localStorage.getItem('API_BASE') || FALLBACK_RENDER || (location.origin.replace(/\/$/, ''));
}
function setApiBase(url) {
  localStorage.setItem('API_BASE', url);
  alert('API definida para: ' + url);
}

let lastItems = [];

// beep simples via WebAudio quando alerta é atingido
function beep() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const o = ctx.createOscillator();
    const g = ctx.createGain();
    o.connect(g); g.connect(ctx.destination);
    o.type = 'sine'; o.frequency.value = 880;
    g.gain.setValueAtTime(0.1, ctx.currentTime);
    o.start();
    setTimeout(() => { o.stop(); ctx.close(); }, 300);
  } catch(e) {}
}

async function searchNow() {
  const tipo = document.getElementById('tipo').value;
  const termo = document.getElementById('termo').value.trim();
  const alerta = parseFloat(document.getElementById('alertaPreco').value || '0');
  const status = document.getElementById('status');
  const body = document.getElementById('resultsBody');
  const bestBox = document.getElementById('bestBox');
  const bestLink = document.getElementById('bestLink');
  const bestPrice = document.getElementById('bestPrice');

  body.innerHTML = '';
  bestBox.classList.add('hidden');
  status.textContent = 'A procurar…';

  try {
    const res = await fetch(`${getApiBase()}/api/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ term: termo, tipo, max_links: 12 })
    });
    const data = await res.json();
    if (!data.ok) {
      status.textContent = data.error || data.message || 'Erro na procura.';
      return;
    }

    lastItems = data.items || [];
    status.textContent = `${lastItems.length} resultados encontrados.`;

    lastItems.forEach(it => {
      const tr = document.createElement('tr');
      tr.className = 'border-b';
      const tdUrl = document.createElement('td');
      const a = document.createElement('a');
      a.href = it.url; a.target = '_blank'; a.rel = 'noopener';
      a.textContent = new URL(it.url).host;
      a.className = 'underline';
      tdUrl.appendChild(a);
      const tdPrice = document.createElement('td');
      tdPrice.textContent = Number(it.price).toFixed(2);
      const tdScore = document.createElement('td');
      tdScore.textContent = it.score;
      tr.appendChild(tdUrl); tr.appendChild(tdPrice); tr.appendChild(tdScore);
      body.appendChild(tr);
    });

    if (data.best) {
      bestBox.classList.remove('hidden');
      bestLink.href = data.best.url;
      bestLink.textContent = new URL(data.best.url).host;
      const value = Number(data.best.price);
      bestPrice.textContent = `${value.toFixed(2)} €`;

      if (!isNaN(alerta) && alerta > 0 && value <= alerta) {
        // destaca e toca beep
        bestBox.classList.remove('bg-green-50');
        bestBox.classList.add('bg-yellow-100');
        beep();
        alert(`🎉 Alerta: Encontrado preço ${value.toFixed(2)} € (<= ${alerta.toFixed(2)} €)`);
      } else {
        bestBox.classList.add('bg-green-50');
      }
    }
  } catch (e) {
    status.textContent = 'Falha de rede ou CORS.';
  }
}

async function exportCSV() {
  if (!lastItems.length) return alert('Sem resultados para exportar.');
  const res = await fetch(`${getApiBase()}/api/export_csv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ items: lastItems })
  });
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'resultados.csv';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}

// PWA Install prompt
let deferredPrompt;
const installBtn = document.getElementById('installBtn');
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  installBtn.classList.remove('hidden');
});
installBtn?.addEventListener('click', async () => {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  await deferredPrompt.userChoice;
  deferredPrompt = null;
  installBtn.classList.add('hidden');
});

// Bind UI
window.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btnSearch').addEventListener('click', searchNow);
  document.getElementById('btnCSV').addEventListener('click', exportCSV);
  document.getElementById('btnAPI').addEventListener('click', () => {
    const current = getApiBase();
    const val = prompt('Definir URL da API (Render):', current);
    if (val) setApiBase(val);
  });
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./service-worker.js');
  }
});