
/* particles */
particlesJS("particles-js", { particles: { number:{value:80}, size:{value:3}, opacity:{value:0.25}, color:{value:"#60a5fa"}, line_linked:{enable:true, color:"#3b82f6", opacity:0.25, width:1}, move:{enable:true, speed:1} }, retina_detect:true });

/* theme */
const themeSel = document.getElementById('themeSel');
const applyTheme = (t)=> document.documentElement.setAttribute('data-theme', t==='dark'?'':t);
themeSel.value = localStorage.getItem('theme') || 'dark';
applyTheme(themeSel.value);
themeSel.onchange = ()=>{ localStorage.setItem('theme', themeSel.value); applyTheme(themeSel.value); };

/* tabs */
const tabs = document.querySelectorAll('.tab');
const tabButtons = document.querySelectorAll('.tablink');
tabButtons.forEach(btn => btn.onclick = (e)=>{
  e.preventDefault();
  tabs.forEach(t => t.classList.remove('active'));
  tabButtons.forEach(b => b.classList.remove('active'));
  document.getElementById(btn.dataset.tab).classList.add('active');
  btn.classList.add('active');
});

const metaToken = document.querySelector('meta[name=api-token]')?.content || '';
const h = { 'Authorization': 'Bearer ' + metaToken };
const statActiveEl = document.getElementById('statActivePeers');
const statIdleEl = document.getElementById('statIdlePeers');
const statTotalEl = document.getElementById('statTotalPeers');
const statLastRefreshEl = document.getElementById('statLastRefresh');
const statClientsEl = document.getElementById('statClients');
const statUptimeEl = document.getElementById('statUptime');

async function call(method, url, data, responseType='json') {
  const res = await axios({ method, url, data, headers: h, responseType });
  return res;
}

/* WG peers */
async function loadPeers() {
  try {
    const res = await call('get', '/api/peers');
    const peers = res.data;
    const s = (document.getElementById('search').value || '').toLowerCase();
    const tbody = document.getElementById('peerTable');
    const filtered = peers
      .filter(p => p.public_key.toLowerCase().includes(s) || p.endpoint.toLowerCase().includes(s));
    tbody.innerHTML = filtered
      .map(p => `
        <tr>
          <td>${p.interface}</td>
          <td><code>${p.public_key.slice(0,16)}…</code></td>
          <td>${p.endpoint}</td>
          <td>${p.allowed_ips}</td>
          <td>${p.latest_handshake_human}</td>
          <td>${p.rx_h}</td>
          <td>${p.tx_h}</td>
          <td><span class="status-pill ${p.status}">${p.status}</span></td>
        </tr>`).join('');
    const active = peers.filter(p => p.status === 'active').length;
    const idle = peers.length - active;
    if(statTotalEl) statTotalEl.textContent = peers.length;
    if(statActiveEl) statActiveEl.textContent = active;
    if(statIdleEl) statIdleEl.textContent = idle;
    if(statLastRefreshEl) statLastRefreshEl.textContent = new Date().toLocaleTimeString();
  } catch(e) {
    console.error(e);
  }
}
document.getElementById('search').addEventListener('input', loadPeers);
document.getElementById('btnRefresh').onclick = loadPeers;
setInterval(loadPeers, 10000); loadPeers();

/* charts */
const rxCtx = document.getElementById('rxChart').getContext('2d');
const txCtx = document.getElementById('txChart').getContext('2d');
const rxChart = new Chart(rxCtx, { type:'line', data:{ labels:[], datasets:[{label:'RX', data:[]}] }, options:{ animation:false, responsive:true }});
const txChart = new Chart(txCtx, { type:'line', data:{ labels:[], datasets:[{label:'TX', data:[]}] }, options:{ animation:false, responsive:true }});
async function loadStats(){
  const res = await call('get','/api/stats');
  const rows = res.data;
  const byTs = {};
  rows.forEach(r => {
    const t = new Date(r.ts).toLocaleTimeString();
    byTs[t] = byTs[t] || { rx:0, tx:0 };
    byTs[t].rx += r.rx;
    byTs[t].tx += r.tx;
  });
  const labels = Object.keys(byTs).slice(-60);
  const rx = labels.map(k=>byTs[k].rx);
  const tx = labels.map(k=>byTs[k].tx);
  rxChart.data.labels = labels; rxChart.data.datasets[0].data = rx; rxChart.update();
  txChart.data.labels = labels; txChart.data.datasets[0].data = tx; txChart.update();
}
setInterval(loadStats, 10000); loadStats();

/* controls */
document.getElementById('btnAdd').onclick = async()=>{ await call('post','/api/add-peer',{ public_key: document.getElementById('newPub').value, allowed_ips: document.getElementById('newIPs').value }); loadPeers(); };

/* Generate client */
const genPreview = document.getElementById('genPreview');
const btnGen = document.getElementById('btnGen');
const btnGenDl = document.getElementById('btnGenDl');
const btnGenQR = document.getElementById('btnGenQR');
btnGen.onclick = async()=>{
  const name = document.getElementById('genName').value.trim();
  if(!name) return alert('Enter a client name');
  const res = await call('post','/api/gen/client',{ name });
  const conf = res.data.conf;
  genPreview.textContent = conf;
  btnGenDl.href = URL.createObjectURL(new Blob([conf], {type:'text/plain'}));
  btnGenDl.download = `${name}.conf`;
};
btnGenQR.onclick = async()=>{
  const conf = genPreview.textContent.trim();
  if(!conf) return alert('Generate a config first');
  const res = await call('post','/api/gen/client/qr',{ conf }, 'arraybuffer');
  const blob = new Blob([res.data], { type: 'image/png' });
  const url = URL.createObjectURL(blob);
  openQRModalFromUrl(url, 'Generated Client');
};

/* PiVPN Clients */
async function loadClients(){
  const res = await call('get','/api/pivpn/list');
  const rows = res.data.rows || [];
  const tbody = document.getElementById('clientTable');
  tbody.innerHTML = rows.map((r,i)=>`
    <tr>
      <td>${i+1}</td>
      <td><span style="font-family:'JetBrains Mono','SFMono-Regular',monospace;font-size:.85rem;">${r.raw}</span></td>
      <td>
        <div class="duo" style="gap:8px;flex-wrap:nowrap;">
          <button class="btn secondary" style="padding:8px 12px;font-size:.8rem;" onclick="openQRModal('${(r.cols&&r.cols[0])?r.cols[0]:''}')">QR</button>
          <a class="btn ghost" style="padding:8px 12px;font-size:.8rem;border-color:var(--border);" href="/api/pivpn/download/${(r.cols&&r.cols[0])?r.cols[0]:''}" target="_blank">Config</a>
          <button class="btn" style="padding:8px 12px;font-size:.8rem;background:var(--danger);" onclick="revokeClient('${(r.cols&&r.cols[0])?r.cols[0]:''}')">Revoke</button>
        </div>
      </td>
    </tr>
  `).join('');
  if(statClientsEl) statClientsEl.textContent = rows.length;
}
async function addClient(){ const name=document.getElementById('clientName').value.trim(); const days=+document.getElementById('clientDays').value||365; if(!name) return alert('Enter a name'); await call('post','/api/pivpn/add',{name,days}); loadClients(); }
async function revokeClient(name){ if(!name) return alert('Missing name'); if(!confirm('Revoke '+name+'?')) return; await call('post','/api/pivpn/revoke',{name}); loadClients(); }
document.getElementById('btnAddClient').onclick = addClient;
setInterval(loadClients, 15000); loadClients();

/* System */
async function loadSystem(){
  const res = await call('get','/api/system/');
  const d = res.data;
  const box = document.getElementById('sysBox');
  const fmt = (n)=> typeof n==='number' ? n.toFixed(1) : '—';
  const fmtTime = (s)=> `${Math.floor(s/3600)}h ${Math.floor(s/60)%60}m`;
  box.innerHTML = `
    <div class="stat-card"><p>CPU</p><h3>${fmt(d.cpu)}%</h3></div>
    <div class="stat-card"><p>Memory</p><h3>${fmt(d.mem)}%</h3></div>
    <div class="stat-card"><p>Disk</p><h3>${fmt(d.disk)}%</h3></div>
    <div class="stat-card"><p>Temperature</p><h3>${d.temp_c ? d.temp_c.toFixed(1)+' °C' : 'N/A'}</h3></div>
    <div class="stat-card"><p>Uptime</p><h3>${fmtTime(d.uptime_sec)}</h3></div>
    <div class="stat-card"><p>Load</p><h3>${d.load.map(x=>x.toFixed(2)).join(', ')}</h3></div>
    <div class="stat-card" style="grid-column:span 2;">
      <p>Top processes</p>
      <ul class="top-list">${(d.top||[]).map(t=>`<li>${t[1]||'proc'} · ${t[2]||0}%</li>`).join('')}</ul>
    </div>
  `;
  if(statUptimeEl) statUptimeEl.textContent = fmtTime(d.uptime_sec);
}
setInterval(loadSystem, 10000); loadSystem();

async function wgCtl(action){
  await call('post','/api/'+action,{});
  setTimeout(loadPeers, 1500);
}
async function loadLogs(kind){
  const res = await call('get','/api/system/logs?kind='+kind);
  document.getElementById(kind==='wg'?'logWg':'logSys').textContent = res.data.output || '';
}
async function power(action){
  if(!confirm('Are you sure you want to '+action+'?')) return;
  await call('post','/api/system/power',{action});
  alert('Command sent.');
}

/* Tools */
async function runCmd(){
  const cmd = document.getElementById('cmdSel').value;
  const res = await call('post','/api/tools/console',{cmd});
  document.getElementById('cmdOut').textContent = (res.data.output||'') + (res.data.stderr?('\n[stderr]\n'+res.data.stderr):'');
}

/* Backup */
async function doBackup(){
  const res = await call('get','/api/tools/backup', null, 'blob');
  const url = URL.createObjectURL(res.data);
  const a = document.createElement('a');
  a.href = url; a.download = 'wg-backup.zip'; a.click();
  URL.revokeObjectURL(url);
}

/* QR Modal */
const modal = document.getElementById('qrModal');
const qrContainer = document.getElementById('qrContainer');
const qrName = document.getElementById('qrName');
const qrDownload = document.getElementById('qrDownload');
const qrClose = document.getElementById('qrClose');

function openQRModal(name){
  qrContainer.innerHTML = '';
  qrName.textContent = name;
  const img = new Image();
  img.alt = 'QR';
  img.onload = ()=>{ qrContainer.appendChild(img); };
  img.onerror = ()=>{ qrContainer.innerHTML = '<div class="text-slate-600 text-sm">Failed to load QR. Check config path or PUBLIC_QR_ACCESS.</div>'; };
  img.src = `/api/pivpn/qr/${encodeURIComponent(name)}`;
  qrDownload.href = `/api/pivpn/download/${encodeURIComponent(name)}`;
  modal.classList.add('active');
}
function openQRModalFromUrl(url, label){
  qrContainer.innerHTML=''; const img=new Image(); img.onload=()=>qrContainer.appendChild(img); img.src=url; qrName.textContent=label; qrDownload.removeAttribute('href'); modal.classList.add('active');
}
qrClose.onclick = ()=> modal.classList.remove('active');
modal.addEventListener('click', (e)=>{ if(e.target===modal) modal.classList.remove('active'); });
