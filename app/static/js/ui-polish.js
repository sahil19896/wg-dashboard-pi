
// v3.6-polished-ui enhancements (no API changes required)
(function(){
  // Theme toggle (requires an element with id=themeToggle if you want a visible control)
  const key='theme'; const apply=t=>{if(t==='light'){document.documentElement.setAttribute('data-theme','light');}else{document.documentElement.removeAttribute('data-theme');}localStorage.setItem(key,t);};
  apply(localStorage.getItem(key)||'dark');
  const btn=document.getElementById('themeToggle'); if(btn){ btn.addEventListener('click',()=>apply((localStorage.getItem(key)||'dark')==='dark'?'light':'dark')); }

  // Simple About modal logic (requires #aboutBtn, #aboutModal in HTML)
  const aboutBtn=document.getElementById('aboutBtn'); const modal=document.getElementById('aboutModal'); const close=document.getElementById('aboutClose');
  function open(){ if(modal){ modal.classList.add('show'); } }
  function shut(){ if(modal){ modal.classList.remove('show'); } }
  if(aboutBtn){ aboutBtn.addEventListener('click', async ()=>{
      open();
      const tgt=document.getElementById('aboutContent');
      if(!tgt) return;
      let rows=[];
      try{
        const r=await fetch('/api/health'); if(r.ok){ const h=await r.json(); if(h){ rows.push(`<div><b>Dashboard</b>: ${h.version||'v3.6-polished-ui'}</div>`); } }
      }catch{}
      try{
        const r2=await fetch('/api/stats'); if(r2.ok){ const s=await r2.json(); if(s){ rows.push(`<div><b>CPU</b>: ${s.cpu!=null?s.cpu.toFixed(1)+'%':'—'}</div>`); rows.push(`<div><b>Uptime</b>: ${s.uptime!=null?fmtUp(s.uptime):'—'}</div>`); } }
      }catch{}
      if(rows.length===0){ rows.push('<div>Private local build v3.6-polished-ui</div>'); }
      tgt.innerHTML = rows.join('');
  });}
  if(close){ close.addEventListener('click', shut); }
  if(modal){ modal.addEventListener('click', (e)=>{ if(e.target===modal) shut(); }); }

  function fmtUp(s){ const d=Math.floor(s/86400); s%=86400; const h=Math.floor(s/3600); s%=3600; const m=Math.floor(s/60); return `${d}d ${h}h ${m}m`; }
})();
