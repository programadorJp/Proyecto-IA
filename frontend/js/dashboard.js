/**dashboard.js — Pfinance BVL
 * Lógica del dashboard (index.html). Requiere config.js cargado antes
 * (expone la constante global API) y Chart.js.
 */

let barChart = null, donutChart = null;
let tickersMap = {}, ultimosTickers = [], ultimoPerfil = 'Moderado';

const PERFIL_MSGS = {
  Conservador: 'Prioriza seguridad del capital. Activos estables, baja volatilidad, caídas máx. 1.5%.',
  Moderado:    'Busca equilibrio entre seguridad y rendimiento. Tolera caídas de hasta 2%.',
  Agresivo:    'Maximiza retorno asumiendo mayor riesgo. Horizonte largo, alta tolerancia a volatilidad.'
};
const PERFIL_CLS = {Conservador:'conservador',Moderado:'moderado',Agresivo:'agresivo'};

document.addEventListener('DOMContentLoaded', async () => {
  await checkBackend();
  await cargarTickers();
  await cargarTickerBar();
});

async function checkBackend() {
  try {
    const r = await fetch(`${API}/`, {signal:AbortSignal.timeout(4000)});
    const d = await r.json();
    if (d.status === 'ok') {
      document.getElementById('stext').textContent = 'Sistema activo';
    }
  } catch {
    document.getElementById('sdot').classList.add('offline');
    document.getElementById('stext').textContent = 'Backend offline';
  }
}

async function cargarTickerBar() {
  try {
    const r    = await fetch(`${API}/activos`);
    const data = await r.json();
    const html = data.map(a => {
      const up  = a.crecimiento >= 0;
      return `<div class="ticker-item">
        <span class="t-name">${a.empresa.toUpperCase()}</span>
        <span class="t-price">S/. ${a.precio}</span>
        <span class="${up?'t-up':'t-dn'}">${up?'▲':'▼'}${Math.abs(a.crecimiento)}%</span>
      </div>`;
    }).join('');
    const track = document.getElementById('ticker-track');
    track.innerHTML = html + html; // duplicar para loop
  } catch { /* silencioso */ }
}

async function cargarTickers() {
  try {
    const r = await fetch(`${API}/tickers`);
    const d = await r.json();
    tickersMap = d.tickers;
    const grid = document.getElementById('activos-grid');
    grid.innerHTML = '';
    const defaultSel = Object.keys(tickersMap).slice(0, 3);
    for (const [ticker, nombre] of Object.entries(tickersMap)) {
      const sel  = defaultSel.includes(ticker);
      const item = document.createElement('div');
      item.className = 'activo-item' + (sel ? ' selected' : '');
      item.dataset.ticker = ticker;
      item.innerHTML = `<div class="activo-check">${sel?'✓':''}</div><span class="activo-label">${nombre}</span>`;
      item.onclick = () => {
        item.classList.toggle('selected');
        item.querySelector('.activo-check').textContent = item.classList.contains('selected') ? '✓' : '';
      };
      grid.appendChild(item);
    }
  } catch {
    document.getElementById('activos-grid').innerHTML =
      '<p style="color:var(--muted);font-size:.78rem;">Error al cargar.</p>';
  }
}

function cambiarPerfil(perfil) {
  const el = document.getElementById('perfil-msg');
  el.className = 'perfil-msg ' + PERFIL_CLS[perfil];
  el.textContent = PERFIL_MSGS[perfil];
  ultimoPerfil = perfil;
}

async function analizar() {
  const tickers = Array.from(document.querySelectorAll('.activo-item.selected'))
    .map(i => i.dataset.ticker).filter(Boolean);
  if (!tickers.length) { alert('Selecciona al menos un activo.'); return; }

  ultimosTickers = tickers;
  ultimoPerfil   = document.getElementById('sel-perfil').value;

  document.getElementById('loading').classList.add('show');
  document.getElementById('dashboard').style.display = 'none';

  try {
    const ts = tickers.join(',');
    const [rA, rR] = await Promise.all([
      fetch(`${API}/activos?tickers=${ts}`).then(r => r.json()),
      fetch(`${API}/reglas?tickers=${ts}&perfil=${ultimoPerfil}`).then(r => r.json())
    ]);
    renderMetricas(rA);
    renderGraficas(rA);
    renderReglas(rR, ultimoPerfil);
    actualizarInfoPanel(rA, rR);
    document.getElementById('ia-output').innerHTML = '';
    document.getElementById('dashboard').style.display = 'block';
  } catch(e) {
    alert('Error: ' + e.message);
  } finally {
    document.getElementById('loading').classList.remove('show');
  }
}

function actualizarInfoPanel(activos, reglas) {
  document.getElementById('info-activos').textContent = `${activos.length} activos analizados`;
  document.getElementById('info-reglas').textContent  = `${reglas.length} reglas CLIPS activadas`;
  document.getElementById('info-perfil').textContent  = ultimoPerfil;
  document.getElementById('info-hora').textContent    = new Date().toLocaleTimeString('es-PE');
}

function renderMetricas(activos) {
  document.getElementById('metrics-grid').innerHTML = activos.map(a => {
    const up  = a.crecimiento >= 0;
    const cls = a.crecimiento >= 1 ? 'up-card' : a.crecimiento <= -1 ? 'dn-card' : '';
    return `<div class="mcard ${cls}">
      <div class="mlabel">${a.empresa}</div>
      <div class="mval">S/. ${a.precio}</div>
      <div class="mdelta ${up?'up':'dn'}">${up?'▲':'▼'} ${Math.abs(a.crecimiento)}%</div>
      <div class="msector">${a.sector} · ${a.ticker}</div>
    </div>`;
  }).join('');
}

function renderGraficas(activos) {
  const labels  = activos.map(a => a.empresa);
  const valores = activos.map(a => a.crecimiento);
  const precios = activos.map(a => a.precio);
  const COLORS  = ['#2979ff','#00e5ff','#00e676','#ffd740','#ff6d00','#ea80fc','#ff1744'];

  if (barChart)   barChart.destroy();
  if (donutChart) donutChart.destroy();

  barChart = new Chart(document.getElementById('bar-chart'), {
    type:'bar',
    data:{labels,datasets:[{
      data:valores,
      backgroundColor:valores.map(v=>v>=0?'rgba(41,121,255,.5)':'rgba(255,23,68,.5)'),
      borderColor:valores.map(v=>v>=0?'#2979ff':'#ff1744'),
      borderWidth:1,borderRadius:4,borderSkipped:false
    }]},
    options:{
      responsive:true,
      plugins:{
        legend:{display:false},
        tooltip:{
          backgroundColor:'#141414',titleColor:'#f5f5f5',
          bodyColor:'#00e5ff',borderColor:'#2a2a2a',borderWidth:1,
          callbacks:{label:c=>` ${c.parsed.y.toFixed(2)}%  ·  S/. ${precios[c.dataIndex]}`}
        }
      },
      scales:{
        x:{ticks:{color:'#606060',font:{size:10,family:'JetBrains Mono'}},grid:{color:'#1a1a1a'}},
        y:{beginAtZero:true,ticks:{color:'#606060',font:{family:'JetBrains Mono'},callback:v=>v+'%'},grid:{color:'#1a1a1a'}}
      }
    }
  });

  donutChart = new Chart(document.getElementById('donut-chart'), {
    type:'doughnut',
    data:{labels,datasets:[{
      data:valores.map(Math.abs),
      backgroundColor:COLORS,
      borderColor:'#141414',borderWidth:3,hoverOffset:5
    }]},
    options:{
      responsive:true,cutout:'70%',
      plugins:{
        legend:{position:'bottom',labels:{color:'#606060',font:{size:9,family:'JetBrains Mono'},boxWidth:8,padding:8}},
        tooltip:{backgroundColor:'#141414',titleColor:'#f5f5f5',bodyColor:'#ffd740',borderColor:'#2a2a2a',borderWidth:1}
      }
    }
  });
}

function renderReglas(reglas, perfil) {
  document.getElementById('clips-meta').textContent =
    `PERFIL: ${perfil.toUpperCase()} · ${reglas.length} reglas activadas · Motor: ClipsRulesEngine v2.0 · 90 reglas totales`;
  document.getElementById('rules-list').innerHTML = reglas.map(r=>`
    <div class="rule-card" style="border-left-color:${r.color}">
      <div class="rule-icon">${r.icono}</div>
      <div>
        <div class="rule-empresa">${r.empresa}</div>
        <div class="rule-id">${r.regla}</div>
        <div class="rule-accion" style="color:${r.color}">→ ${r.accion}</div>
      </div>
    </div>`).join('');
}

function markdownAHtml(texto) {
  return texto
    .replace(/^\s*\*{0,2}(\d+\.\s+[^\n]+)\*{0,2}/gm,(_,t)=>`<h2>${t.replace(/\*\*/g,'').trim()}</h2>`)
    .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
    .replace(/(?<!\n)\*(?!\s)(.+?)\*/g,'<em>$1</em>')
    .replace(/^[\*\-]\s+(.+)$/gm,'<li>$1</li>')
    .replace(/((?:<li>[\s\S]*?<\/li>\s*)+)/g,'<ul>$1</ul>')
    .split('\n').map(line=>{
      const t=line.trim();
      if(!t) return '';
      if(t.startsWith('<h2>')||t.startsWith('<ul>')||t.startsWith('<li>')||t.startsWith('<p>')) return t;
      return `<p>${t}</p>`;
    }).filter(Boolean).join('\n');
}

async function generarIA() {
  if (!ultimosTickers.length) { alert('Primero analiza el mercado.'); return; }
  const output = document.getElementById('ia-output');
  output.innerHTML = '<div class="ia-loading"><div class="spinner"></div> Procesando con Gemini Transformer...</div>';
  try {
    const r = await fetch(`${API}/analisis-ia?tickers=${ultimosTickers.join(',')}&perfil=${ultimoPerfil}`);
    const d = await r.json();
    output.innerHTML = `<div class="ia-output">${markdownAHtml(d.analisis)}</div>`;
  } catch(e) {
    output.innerHTML = `<div style="color:var(--red);padding:16px;font-family:'JetBrains Mono',monospace;font-size:.8rem;">ERROR: ${e.message}</div>`;
  }
}

function switchTab(name, btn) {
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
  btn.classList.add('active');
  document.getElementById('tab-'+name).classList.add('active');
}