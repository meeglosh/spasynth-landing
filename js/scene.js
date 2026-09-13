// Photoreal Blender sequence. Scroll chooses the frame; time never advances it.
// Compressed WebP blobs are retained, but only 20 explicitly releasable frames
// are decoded. No array of 181 live HTMLImageElements / GPU textures.
const stage = document.querySelector('#synth-stage');
if (stage) {
  const FRAME_COUNT = 181, MAX_FETCHES = 4, MAX_DECODED = 20, MAX_DECODES = 2;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const mobile = matchMedia('(max-width: 650px)');
  const poster = stage.querySelector('.scene-fallback');
  const originalPoster = poster?.getAttribute('src') || './assets/scene/studio-assembled.webp';
  const canvas = document.createElement('canvas');
  canvas.setAttribute('aria-hidden', 'true');
  canvas.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;pointer-events:none;opacity:0';
  const context = canvas.getContext('2d', {alpha: false});
  stage.append(canvas);
  let target = Math.round(Number(document.querySelector('#teardown')?.style.getPropertyValue('--teardown-progress') || 0) * 180);
  let displayed = -1, near = false, generation = 0, fetches = 0, decodes = 0, raf = 0;
  let variant = mobile.matches ? 'sequence-mobile' : 'sequence';
  let phase = 'poster', failedTarget = -1, posterRequest = 0;
  const blobs = new Map(), decoded = new Map(), fetching = new Map(), decoding = new Set(), failed = new Set();
  const modelVersion = encodeURIComponent(stage.dataset.modelVersion || '1');
  const frameURL = frame => `./assets/scene/${variant}/frame-${String(frame).padStart(3,'0')}.webp?v=${modelVersion}`;
  const limit = n => Math.max(0, Math.min(FRAME_COUNT - 1, n));

  function state() {
    stage.dataset.scVerifyState = `sequence:${variant};target:${target};displayed:${displayed};mode:${phase};decoded:${decoded.size};fetching:${fetches}`;
    stage.dataset.modelProgress = (target / 180).toFixed(3);
    stage.dataset.targetFrame = String(target);
    stage.dataset.displayedFrame = String(displayed);
  }
  function showPoster(reason = 'poster') {
    phase = reason; displayed = -1;
    canvas.style.opacity = '0';
    if (poster) poster.style.opacity = '1';
    stage.dataset.modelReady = reason === 'error' ? 'false' : 'poster';
    // Never replace a complete fallback until its replacement has loaded.
    const src = reduced.matches
      ? stage.dataset.posterExploded || './assets/scene/studio-exploded.webp'
      : stage.dataset.posterAssembled || originalPoster;
    const request = ++posterRequest;
    if (poster && poster.getAttribute('src') !== src) {
      const replacement = new Image();
      replacement.onload = () => {
        if (request === posterRequest) poster.src = src;
      };
      replacement.src = src;
    }
    state();
  }
  function release(frame) {
    const entry = decoded.get(frame);
    if (!entry) return;
    entry.close();
    decoded.delete(frame);
  }
  function touch(frame) {
    const entry = decoded.get(frame);
    if (entry) { decoded.delete(frame); decoded.set(frame, entry); }
    return entry;
  }
  function evict() {
    while (decoded.size > MAX_DECODED) release(decoded.keys().next().value);
  }
  function draw() {
    raf = 0;
    if (!context || reduced.matches || !near || document.hidden) return;
    const entry = touch(target);
    if (!entry) {
      if (failed.has(target)) showPoster('error');
      else { phase = 'buffering'; state(); }
      return;
    }
    const width = stage.clientWidth, height = stage.clientHeight;
    if (!width || !height) return;
    const ratio = Math.min(devicePixelRatio || 1, 1.5);
    const w = Math.round(width * ratio), h = Math.round(height * ratio);
    if (canvas.width !== w || canvas.height !== h) { canvas.width = w; canvas.height = h; }
    context.fillStyle = '#171d1a'; context.fillRect(0,0,w,h);
    const scale = Math.min(w / entry.width, h / entry.height);
    const dw = entry.width * scale, dh = entry.height * scale;
    context.drawImage(entry.image, (w-dw)/2, (h-dh)/2, dw, dh);
    displayed = target; phase = 'ready'; failedTarget = -1;
    canvas.style.opacity = '1'; if (poster) poster.style.opacity = '0';
    const first = stage.dataset.modelReady !== 'true';
    stage.dataset.modelReady = 'true'; state();
    if (first) window.dispatchEvent(new Event('spasynth:ready'));
  }
  function wake() { if (!raf) raf = requestAnimationFrame(draw); }
  function priorities() {
    const order = [target];
    // Immediate neighbors first, then progressively fill the whole timeline.
    for (let d=1; d<=6; d++) order.push(limit(target+d),limit(target-d));
    for (const stride of [16,8,4,2,1]) for (let f=0;f<FRAME_COUNT;f+=stride) order.push(f);
    order.push(180);
    return [...new Set(order)];
  }
  async function decodeFrame(frame, epoch) {
    decodes++; decoding.add(frame);
    let entry;
    try {
      if (typeof createImageBitmap === 'function') {
        const bitmap = await createImageBitmap(blobs.get(frame));
        entry = {image:bitmap,width:bitmap.width,height:bitmap.height,close:()=>bitmap.close()};
      } else {
        const url = URL.createObjectURL(blobs.get(frame));
        const image = new Image();
        try {
          await new Promise((resolve,reject)=>{image.onload=resolve;image.onerror=reject;image.src=url;});
          entry = {image,width:image.naturalWidth,height:image.naturalHeight,close:()=>{image.src='';URL.revokeObjectURL(url);}};
        } catch(error) { URL.revokeObjectURL(url); throw error; }
      }
      if (epoch !== generation || reduced.matches) { entry.close(); return; }
      decoded.set(frame,entry); evict();
      if (frame === target) wake();
    } catch(error) {
      if (epoch === generation) { failed.add(frame); if(frame === target) showPoster('error'); }
    } finally {
      if (epoch === generation) { decodes--;decoding.delete(frame);pumpDecodes();state(); }
    }
  }
  function pumpDecodes() {
    if (!near || reduced.matches || document.hidden || !context) return;
    const order = [target,limit(target+1),limit(target-1),limit(target+2),limit(target-2)];
    for (const frame of [...new Set(order)]) {
      if (decodes >= MAX_DECODES) break;
      if (blobs.has(frame) && !decoded.has(frame) && !decoding.has(frame) && !failed.has(frame)) decodeFrame(frame,generation);
    }
  }
  async function fetchFrame(frame, epoch) {
    const controller = new AbortController();fetching.set(frame,controller);fetches++;
    try {
      const response = await fetch(frameURL(frame),{signal:controller.signal,cache:'force-cache'});
      if (!response.ok) throw new Error(`Frame ${frame}: ${response.status}`);
      const blob = await response.blob();
      if (epoch !== generation) return;
      blobs.set(frame,blob);pumpDecodes();
    } catch(error) {
      if (epoch === generation && error.name !== 'AbortError') {
        failed.add(frame);
        if (frame === target) { failedTarget=frame;showPoster('error'); }
      }
    } finally {
      if (epoch === generation) { fetching.delete(frame);fetches--;state();pump(); }
    }
  }
  function pump() {
    if (!near || reduced.matches || document.hidden || !context) return;
    pumpDecodes();
    for (const frame of priorities()) {
      if (fetches >= MAX_FETCHES) break;
      if (!blobs.has(frame) && !fetching.has(frame) && !failed.has(frame)) fetchFrame(frame,generation);
    }
  }
  function reset() {
    generation++;
    for (const controller of fetching.values()) controller.abort();
    fetching.clear();decoding.clear();blobs.clear();failed.clear();
    for (const frame of [...decoded.keys()]) release(frame);
    fetches=0;decodes=0;displayed=-1;failedTarget=-1;
    variant=mobile.matches?'sequence-mobile':'sequence';
    showPoster();pump();wake();
  }
  window.addEventListener('spasynth:progress', event => {
    if (!Number.isFinite(event.detail?.progress)) return;
    const next = limit(Math.round(event.detail.progress * 180));
    if (next !== target) {
      target = next;
      // The next free request slot always takes the latest target. Keep at most
      // four requests in flight even when the user jumps across the timeline.
      if (failedTarget !== target && failed.has(target)) showPoster('error');
    }
    state();pump();wake();
  });
  reduced.addEventListener('change',reset);
  mobile.addEventListener('change',reset);
  document.addEventListener('visibilitychange',()=>{if(!document.hidden){pump();wake();}});
  new ResizeObserver(wake).observe(stage);
  new IntersectionObserver(entries=>{
    near=entries[0].isIntersecting;
    if(near){pump();wake();}
  },{rootMargin:'650px'}).observe(stage);
  showPoster();
  // Ask page.js for its latest progress even when module loading finished late.
  window.dispatchEvent(new Event('spasynth:ready'));
}
