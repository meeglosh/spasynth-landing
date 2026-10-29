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

  /* ---------- audio playlist + video: one player at a time, count stays honest ---------- */
  const playlist = document.querySelector('[data-playlist]');
  const links = playlist ? [...playlist.querySelectorAll('.track-play')] : [];
  if (playlist && links.length) {
    const deck = playlist.querySelector('[data-playlist-deck]');
    const audio = deck.querySelector('audio');
    const toggle = deck.querySelector('[data-pl="toggle"]');
    const seek = deck.querySelector('[data-pl-seek]');
    const timeEl = deck.querySelector('[data-pl-time]');
    const durEl = deck.querySelector('[data-pl-duration]');
    const rows = links.map(a => a.closest('.audio-track'));
    const fmt = t => { t = Math.max(0, Math.floor(t || 0)); return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0'); };
    let current = 0, seeking = false;
    const setProgress = v => { seek.value = v; seek.style.setProperty('--p', v / 10 + '%'); };
    const select = (i, play) => {
      current = (i + links.length) % links.length;
      rows.forEach((r, j) => { r.classList.toggle('is-current', j === current); if (j === current) r.setAttribute('aria-current', 'true'); else r.removeAttribute('aria-current'); });
      const row = rows[current];
      deck.querySelector('[data-pl-title]').textContent = row.querySelector('h3').textContent;
      deck.querySelector('[data-pl-artist]').textContent = row.querySelector('.track-artist').textContent;
      durEl.textContent = row.querySelector('.track-time').textContent;
      const src = links[current].getAttribute('href');
      if (audio.getAttribute('src') !== src) { audio.src = src; setProgress(0); timeEl.textContent = '0:00'; }
      if (play) audio.play().catch(() => {});
    };
    links.forEach((a, i) => a.addEventListener('click', e => {
      e.preventDefault();
      if (i === current && !audio.paused) audio.pause(); else select(i, true);
    }));
    toggle.addEventListener('click', () => { if (audio.paused) audio.play().catch(() => {}); else audio.pause(); });
    deck.querySelector('[data-pl="prev"]').addEventListener('click', () => {
      if (audio.currentTime > 3) audio.currentTime = 0; else select(current - 1, !audio.paused);
    });
    deck.querySelector('[data-pl="next"]').addEventListener('click', () => select(current + 1, !audio.paused));
    const sync = () => {
      const playing = !audio.paused;
      playlist.classList.toggle('is-playing', playing);
      toggle.setAttribute('aria-label', playing ? 'Pause' : 'Play');
    };
    audio.addEventListener('play', sync);
    audio.addEventListener('pause', sync);
    audio.addEventListener('emptied', sync);
    audio.addEventListener('loadedmetadata', () => { durEl.textContent = fmt(Math.round(audio.duration)); });
    audio.addEventListener('timeupdate', () => {
      if (seeking || !audio.duration) return;
      setProgress(Math.round(audio.currentTime / audio.duration * 1000));
      timeEl.textContent = fmt(audio.currentTime);
    });
    // Play straight through the list, then rest on the first track.
    audio.addEventListener('ended', () => select(current + 1, current < links.length - 1));
    seek.addEventListener('input', () => {
      seeking = true;
      seek.style.setProperty('--p', seek.value / 10 + '%');
      if (audio.duration) timeEl.textContent = fmt(seek.value / 1000 * audio.duration);
    });
    seek.addEventListener('change', () => {
      seeking = false;
      if (audio.duration) audio.currentTime = seek.value / 1000 * audio.duration; else setProgress(0);
    });
    select(0, false);
    deck.hidden = false;
  }
  const media = document.querySelectorAll('.playlist audio, .video-demo video');
  media.forEach(el => el.addEventListener('play', () => {
    media.forEach(other => { if (other !== el) other.pause(); });
  }));
  const words = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve'];
  const count = document.querySelector('[data-track-count]');
  const noun = document.querySelector('[data-track-noun]');
  if (count) count.textContent = links.length < words.length ? words[links.length] : String(links.length);
  if (noun) noun.textContent = links.length === 1 ? 'track' : 'tracks';

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
