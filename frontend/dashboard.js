/**dashboard.js — BVL Agent Dashboard
 * JavaScript puro que consume la FastAPI backend
 */

const API = 'http://127.0.0.1:8000';
let barChart = null;
let donutChart = null;

// ── Al cargar la página ──
document.addEventListener('DOMContentLoaded', async () => {
  await cargarTickers();
  verificarBackend();
});

// ── Verificar que el backend esté vivo ──
async function verificarBackend() {
  try {
    const r = await fetch(`${API}/`);
    const data = await r.json();
    if (data.status === 'ok') {
      document.getElementById('status-text').textContent = 'Backend activo';
    }
  } catch {
    document.getElementById('status-badge').style.borderColor = '#ff4757';
    document.getElementById('status-badge').style.color = '#ff4757';
    document.getElementById('status-text').textContent = 'Backend offline';
  }
}

// ── Cargar tickers disponibles ──
async function cargarTickers() {
  try {
    const r = await fetch(`${API}/tickers`);
    const data = await r.json();
    const select = document.getElementById('select-tickers');
    select.innerHTML = '';
    for (const [ticker, nombre] of Object.entries(data.tickers)) {
      const opt = document.createElement('option');
      opt.value = ticker;
      opt.textContent = nombre;
      opt.selected = ['BAP','SCCO','ALICORC1.LM'].includes(ticker);
      select.appendChild(opt);
    }
  } catch(e) {
    console.error('Error cargando tickers:', e);
  }
}

// ── Analizar mercado ──
async function analizarMercado() {
  const select  = document.getElementById('select-tickers');
  const perfil  = document.getElementById('select-perfil').value;
  const tickers = Array.from(select.selectedOptions).map(o => o.value);

  if (!tickers.length) { alert('Selecciona al menos un activo.'); return; }

  mostrarLoading(true);

  try {
    const tickersStr = tickers.join(',');

    // Llamadas paralelas al backend
    const [resActivos, resReglas] = await Promise.all([
      fetch(`${API}/activos?tickers=${tickersStr}`).then(r => r.json()),
      fetch(`${API}/reglas?tickers=${tickersStr}&perfil=${perfil}`).then(r => r.json())
    ]);

    renderMetricas(resActivos);
    renderGraficas(resActivos);
    renderReglas(resReglas, perfil);
    renderLisp(resActivos);

    document.getElementById('dashboard-content').style.display = 'block';
    document.getElementById('btn-ia').dataset.tickers = tickersStr;
    document.getElementById('btn-ia').dataset.perfil  = perfil;

  } catch(e) {
    alert('Error al conectar con el backend: ' + e.message);
  } finally {
    mostrarLoading(false);
  }
}

// ── Render métricas ──
function renderMetricas(activos) {
  const grid = document.getElementById('metrics-grid');
  grid.innerHTML = activos.map(a => {
    const up    = a.crecimiento >= 0;
    const signo = up ? '▲' : '▼';
    const cls   = up ? 'up' : 'down';
    return `
      <div class="metric-card">
        <div class="metric-label">${a.empresa}</div>
        <div class="metric-value">S/. ${a.precio}</div>
        <div class="metric-delta ${cls}">${signo} ${Math.abs(a.crecimiento)}%</div>
        <div style="font-size:.7rem;color:#6c7a95;margin-top:4px;">${a.sector}</div>
      </div>`;
  }).join('');
}

// ── Render gráficas ──
function renderGraficas(activos) {
  const labels  = activos.map(a => a.empresa);
  const valores = activos.map(a => a.crecimiento);
  const precios = activos.map(a => a.precio);
  const bgCol   = valores.map(v => v >= 0 ? 'rgba(0,229,160,.7)' : 'rgba(255,71,87,.7)');
  const brdCol  = valores.map(v => v >= 0 ? '#00e5a0' : '#ff4757');
  const COLORS  = ['#00e5a0','#4ecdc4','#ffd700','#ff6b35','#a855f7','#3b82f6','#ef4444'];

  // Destruir gráficas anteriores
  if (barChart)   { barChart.destroy();   barChart = null; }
  if (donutChart) { donutChart.destroy(); donutChart = null; }

  barChart = new Chart(document.getElementById('bar-chart'), {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Crecimiento %',
        data: valores,
        backgroundColor: bgCol,
        borderColor: brdCol,
        borderWidth: 2,
        borderRadius: 6,
        borderSkipped: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#141b2d',
          titleColor: '#e8eaf6',
          bodyColor: '#00e5a0',
          borderColor: '#1e2a42',
          borderWidth: 1,
          callbacks: {
            label: ctx => ` ${ctx.parsed.y.toFixed(2)}%  |  S/. ${precios[ctx.dataIndex]}`
          }
        }
      },
      scales: {
        x: { ticks: { color: '#6c7a95', font: { size: 11 } }, grid: { color: '#1e2a42' } },
        y: { beginAtZero: true, ticks: { color: '#6c7a95', callback: v => v + '%' }, grid: { color: '#1e2a42' } }
      }
    }
  });

  donutChart = new Chart(document.getElementById('donut-chart'), {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: valores.map(Math.abs),
        backgroundColor: COLORS,
        borderColor: '#0e1420',
        borderWidth: 3,
        hoverOffset: 6
      }]
    },
    options: {
      responsive: true,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { color: '#6c7a95', font: { size: 10 }, boxWidth: 10, padding: 8 }
        }
      }
    }
  });
}

// ── Render reglas CLIPS ──
function renderReglas(reglas, perfil) {
  const container = document.getElementById('rules-container');
  const subtitle  = document.getElementById('rules-subtitle');
  subtitle.textContent = `Perfil: ${perfil} · ${reglas.length} regla(s) activadas · vía API /reglas`;

  container.innerHTML = reglas.map(r => `
    <div class="rule-card" style="border-left-color:${r.color}">
      <div class="rule-icon">${r.icono}</div>
      <div>
        <div class="rule-empresa">${r.empresa}</div>
        <div class="rule-id">${r.regla}</div>
        <div class="rule-accion" style="color:${r.color}">→ ${r.accion}</div>
      </div>
    </div>`).join('');
}

// ── Render LISP generado ──
function renderLisp(activos) {
  let lisp = `<span class="cmt">; hechos_mercado.lisp — generado automáticamente</span>\n`;
  lisp += `<span class="cmt">; Motor: MarketSensor → ExpertBrain → CLIPS</span>\n\n`;
  lisp += `(<span class="kw">setq</span> <span class="fn">hechos-mercado</span> <span class="str">'</span>(\n`;
  activos.forEach(a => {
    const color = a.crecimiento >= 0 ? '#00e5a0' : '#ff4757';
    lisp += `  (<span class="str">"${a.empresa}"</span> `;
    lisp += `<span class="num">${a.precio}</span> `;
    lisp += `<span style="color:${color}">${a.crecimiento}</span> `;
    lisp += `<span class="str">"${a.sector}"</span>)\n`;
  });
  lisp += `))\n`;
  document.getElementById('lisp-code').innerHTML = lisp;
}

// ── Generar análisis IA ──
async function generarAnalisisIA() {
  const btn     = document.getElementById('btn-ia');
  const tickers = btn.dataset.tickers;
  const perfil  = btn.dataset.perfil;
  const output  = document.getElementById('ia-output');

  if (!tickers) { alert('Primero analiza el mercado.'); return; }

  output.innerHTML = '<div class="loading"><div class="spinner"></div> Consultando Gemini AI via backend...</div>';

  try {
    const r    = await fetch(`${API}/analisis-ia?tickers=${tickers}&perfil=${perfil}`);
    const data = await r.json();
    output.innerHTML = `
      <div style="background:#0a0f1a;border:1px solid #1e2a42;border-radius:10px;padding:20px;
                  font-size:.9rem;line-height:1.7;white-space:pre-wrap;">${data.analisis}</div>`;
  } catch(e) {
    output.innerHTML = `<div style="color:#ff4757;">❌ Error: ${e.message}</div>`;
  }
}

// ── Tabs ──
function switchTab(tab) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.querySelector(`[data-tab="${tab}"]`).classList.add('active');
  document.getElementById(`tab-${tab}`).classList.add('active');
}

// ── Loading ──
function mostrarLoading(show) {
  document.getElementById('loading').style.display = show ? 'flex' : 'none';
  if (show) document.getElementById('dashboard-content').style.display = 'none';
}