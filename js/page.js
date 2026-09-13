(() => {
  ScrollCraft.mount(document.body);
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');

  /* ---------- masthead nav toggle (phone) ---------- */
  const masthead = document.querySelector('.masthead');
  const toggle = document.getElementById('nav-toggle');
  if (toggle) {
    toggle.addEventListener('click', () => {
      const open = masthead.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', String(open));
    });
    document.querySelectorAll('.masthead-nav a').forEach(a => a.addEventListener('click', () => {
      masthead.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false');
    }));
  }

  /* ---------- teardown progress: scroll position -> model frame ----------
     Same stops as the case study. The three module notes line up with the
     three modules the render isolates; the last two notes ride the reassembly. */
  const teardown = document.getElementById('teardown');
  const stage = document.getElementById('synth-stage');
  const label = document.getElementById('module-label');
  let ticking = false;
  function update() {
    ticking = false;
    if (!teardown || !stage) return;
    const rect = teardown.getBoundingClientRect();
    const readingLine = innerHeight * (innerWidth <= 650 ? .58 : .5);
    const positions = [0, ...['chaos-note','matrix-note','random-note','reassembly-note'].map(id => {
      const note = document.querySelector('#'+id+' .note-content');
      return note.getBoundingClientRect().top - rect.top - readingLine;
    }), rect.height - innerHeight];
    const stops = [0, .26, .51, .72, .82, 1];
    const distance = -rect.top;
    let progress = 0;
    for (let i=0; i<positions.length-1; i++) {
      if (distance >= positions[i]) {
        const t = Math.max(0,Math.min(1,(distance-positions[i])/Math.max(1,positions[i+1]-positions[i])));
        progress = stops[i] + (stops[i+1]-stops[i])*t;
      }
    }
    progress = Math.max(0,Math.min(1,progress));
    const activeModule = reduced.matches ? 'whole' : progress < .25 ? 'sample' : progress < .5 ? 'chaos' : progress < .72 ? 'matrix' : 'whole';
    const names = {sample:'Sample engine',chaos:'Organic Chaos',matrix:'Modulation matrix',whole:reduced.matches || progress < .84 ? 'The whole instrument' : progress < .995 ? 'Reassembly' : 'Reassembled'};
    label.textContent = names[activeModule];
    stage.dataset.activeModule = activeModule;
    teardown.style.setProperty('--teardown-progress', progress.toFixed(4));
    window.dispatchEvent(new CustomEvent('spasynth:progress', {detail:{progress,reducedMotion:reduced.matches,activeModule}}));
  }
  function queue() { if (!ticking) { ticking=true; requestAnimationFrame(update); } }
  addEventListener('scroll', queue, {passive:true});
  addEventListener('resize', queue, {passive:true});
  addEventListener('load', queue);
  reduced.addEventListener('change', queue);
  window.addEventListener('spasynth:ready', queue);
  update();

  /* ---------- audio: one track at a time, count stays honest ---------- */
  const players = document.querySelectorAll('.audio-track audio');
  players.forEach(audio => audio.addEventListener('play', () => {
    players.forEach(other => { if (other !== audio) other.pause(); });
  }));
  const words = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve'];
  const count = document.querySelector('[data-track-count]');
  const noun = document.querySelector('[data-track-noun]');
  if (count) count.textContent = players.length < words.length ? words[players.length] : String(players.length);
  if (noun) noun.textContent = players.length === 1 ? 'track' : 'tracks';

  /* ---------- Organic Chaos scope: a wandering random walk ---------- */
  function makeScope(canvas, opts) {
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    const dpr = Math.min(devicePixelRatio || 1, 2);
    let w, h, points;
    const color = opts.color, pointCount = opts.pointCount || 120, speed = opts.speed || 1;
    function resize() { w = canvas.clientWidth; h = canvas.clientHeight; canvas.width = w*dpr; canvas.height = h*dpr; ctx.setTransform(dpr,0,0,dpr,0,0); }
    function seed() { points = []; let v = h/2; for (let i=0;i<pointCount;i++){ v += (Math.random()-.5)*h*.18; v = Math.max(h*.08,Math.min(h*.92,v)); points.push(v);} }
    let frame = 0;
    function step() {
      frame++;
      if (frame % Math.round(3/speed) === 0) {
        points.shift();
        let next = points[points.length-1] + (Math.random()-.5)*h*.22;
        points.push(Math.max(h*.08,Math.min(h*.92,next)));
      }
      ctx.clearRect(0,0,w,h);
      ctx.beginPath(); ctx.lineWidth = opts.lineWidth || 1.6; ctx.strokeStyle = color; ctx.lineJoin='round'; ctx.lineCap='round';
      ctx.shadowColor = color; ctx.shadowBlur = opts.glow || 0;
      const sx = w/(points.length-1);
      points.forEach((y,i) => i ? ctx.lineTo(i*sx,y) : ctx.moveTo(0,y));
      ctx.stroke();
      requestAnimationFrame(step);
    }
    resize(); seed();
    addEventListener('resize', () => { resize(); seed(); });
    requestAnimationFrame(step);
  }
  if (!reduced.matches) makeScope(document.getElementById('chaos-scope'), {color:'#6dd6c2', pointCount:90, speed:1.3, lineWidth:1.6, glow:6});
})();
