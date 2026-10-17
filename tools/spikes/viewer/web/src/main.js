import * as THREE from "three";
import init, { Kernel } from "../../kernel/pkg/p04_kernel.js";
import * as js from "./jskernel.js";

const q = new URLSearchParams(location.search);
const mode = q.get("mode") || "bench";
const out = document.getElementById("out");
const median = (a) => [...a].sort((x, y) => x - y)[Math.floor(a.length / 2)];
const p95 = (a) => [...a].sort((x, y) => x - y)[Math.floor(a.length * 0.95)];
const time = (fn) => { const t = performance.now(); const r = fn(); return [performance.now() - t, r]; };
const R = { env: { ua: navigator.userAgent, dpr: devicePixelRatio, cores: navigator.hardwareConcurrency }, rows: [] };

const t0 = performance.now();
const wasm = await init();
R.wasm_init_ms = +(performance.now() - t0).toFixed(1);

function wasmRun(n, doSub) {
  const k = new Kernel(n);
  let sub = 0, nrm = 0;
  if (doSub) sub = time(() => k.subdivide())[0];
  nrm = time(() => k.compute_normals())[0];
  return { k, sub, nrm };
}
function jsRun(n, doSub) {
  let m = js.grid(n), sub = 0;
  if (doSub) { const [ms, r] = time(() => js.subdivide(m)); sub = ms; m = r; }
  const [nrm] = time(() => js.computeNormals(m));
  return { m, sub, nrm };
}

if (mode === "bench") {
  for (const n of [224, 447, 894]) {
    const reps = n === 894 ? 2 : 3;
    const w = [], j = [];
    let wk, jm;
    for (let r = 0; r < reps; r++) {
      if (wk) wk.free();
      const a = wasmRun(n, true); wk = a.k; w.push(a);
      const b = jsRun(n, true); jm = b.m; j.push(b);
    }
    R.rows.push({
      grid_n: n, out_tris: wk.tri_count(),
      wasm: { subdivide_ms: +median(w.map((x) => x.sub)).toFixed(2), normals_ms: +median(w.map((x) => x.nrm)).toFixed(2) },
      js: { subdivide_ms: +median(j.map((x) => x.sub)).toFixed(2), normals_ms: +median(j.map((x) => x.nrm)).toFixed(2) },
      checksum_wasm: wk.checksum(), checksum_js: js.checksum(jm.pos, jm.idx),
    });
    wk.free();
  }
} else if (mode === "render") {
  // render mode: ?mode=render&n=447&sub=0|1&impl=wasm|js&handoff=view|copy
  const n = +(q.get("n") || 224), doSub = q.get("sub") === "1", impl = q.get("impl") || "wasm", handoff = q.get("handoff") || "view";
  const frames = +(q.get("frames") || 240);
  const row = { n, sub: doSub, impl, handoff };
  let pos, idx, nrm, k;
  const [buildMs] = time(() => {
    if (impl === "wasm") {
      const a = wasmRun(n, doSub); k = a.k;
      const mem = wasm.memory.buffer;
      pos = new Float32Array(mem, k.pos_ptr(), k.pos_len());
      idx = new Uint32Array(mem, k.idx_ptr(), k.idx_len());
      nrm = new Float32Array(mem, k.nrm_ptr(), k.nrm_len());
      if (handoff === "copy") { pos = pos.slice(); idx = idx.slice(); nrm = nrm.slice(); }
    } else {
      const a = jsRun(n, doSub); pos = a.m.pos; idx = a.m.idx; nrm = a.m.nrm;
    }
  });
  row.build_ms = +buildMs.toFixed(1);
  row.tris = idx.length / 3;

  const W = 960, H = 540;
  const renderer = new THREE.WebGLRenderer({ antialias: false });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H);
  document.body.appendChild(renderer.domElement);
  const gl = renderer.getContext();
  row.gl = gl.getParameter(gl.VERSION);
  const dbg = gl.getExtension("WEBGL_debug_renderer_info");
  row.gpu = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : "unknown";

  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(50, W / H, 0.01, 100);
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
  geo.setAttribute("normal", new THREE.BufferAttribute(nrm, 3));
  geo.setIndex(new THREE.BufferAttribute(idx, 1));
  scene.add(new THREE.Mesh(geo, new THREE.MeshNormalMaterial()));
  cam.position.set(0, -2.2, 1.6);
  cam.lookAt(0, 0, 0);

  const px = new Uint8Array(4);
  // readPixels forces the GPU to finish (gl.finish() is not a reliable sync in Chrome/ANGLE).
  const sync = () => gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  const [firstMs] = time(() => { renderer.render(scene, cam); sync(); });
  row.first_frame_ms = +firstMs.toFixed(1); // includes buffer upload
  const cost = [], raf = [];
  let last = performance.now();
  await new Promise((done) => {
    let f = 0;
    const tick = () => {
      const a = f * 0.02;
      cam.position.set(Math.sin(a) * 2.6, -Math.cos(a) * 2.6, 1.6);
      cam.lookAt(0, 0, 0);
      const s = performance.now();
      renderer.render(scene, cam);
      sync();
      cost.push(performance.now() - s);
      const now = performance.now(); raf.push(now - last); last = now;
      if (++f < frames) requestAnimationFrame(tick); else done();
    };
    requestAnimationFrame(tick);
  });
  // Throughput: back-to-back synced renders with no vsync wait; the achievable frame time.
  const thr = [];
  for (let i = 0; i < 60; i++) {
    const a = i * 0.05;
    cam.position.set(Math.sin(a) * 2.6, -Math.cos(a) * 2.6, 1.6);
    cam.lookAt(0, 0, 0);
    const s = performance.now();
    renderer.render(scene, cam);
    sync();
    thr.push(performance.now() - s);
  }
  row.throughput_ms = { median: +median(thr).toFixed(2), p95: +p95(thr).toFixed(2), fps_equiv: +(1000 / median(thr)).toFixed(0) };
  row.render_cost_ms = { median: +median(cost).toFixed(2), p95: +p95(cost).toFixed(2) };
  row.frame_interval_ms = { median: +median(raf.slice(5)).toFixed(2), p95: +p95(raf.slice(5)).toFixed(2) };
  R.rows.push(row);
} else if (mode === "edit") {
  // ?mode=edit&n=707 : picking + brush sculpt + partial upload, all through the WASM kernel
  const n = +(q.get("n") || 707);
  const row = { n };
  const k = new Kernel(n);
  k.compute_normals();
  row.build_accel_ms = +time(() => k.build_accel())[0].toFixed(1);
  row.tris = k.tri_count(); row.verts = k.vert_count();
  const views = () => {
    const mem = wasm.memory.buffer;
    return [new Float32Array(mem, k.pos_ptr(), k.pos_len()), new Uint32Array(mem, k.idx_ptr(), k.idx_len()), new Float32Array(mem, k.nrm_ptr(), k.nrm_len())];
  };
  let lastMem = wasm.memory.buffer;
  let [pos, idx, nrm] = views();
  const W = 960, H = 540;
  const renderer = new THREE.WebGLRenderer({ antialias: false });
  renderer.setPixelRatio(1); renderer.setSize(W, H); document.body.appendChild(renderer.domElement);
  const gl = renderer.getContext();
  const dbg = gl.getExtension("WEBGL_debug_renderer_info");
  row.gpu = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : "unknown";
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(50, W / H, 0.01, 100);
  const geo = new THREE.BufferGeometry();
  const posA = new THREE.BufferAttribute(pos, 3), nrmA = new THREE.BufferAttribute(nrm, 3);
  posA.setUsage(THREE.DynamicDrawUsage); nrmA.setUsage(THREE.DynamicDrawUsage);
  geo.setAttribute("position", posA); geo.setAttribute("normal", nrmA); geo.setIndex(new THREE.BufferAttribute(idx, 1));
  const mesh = new THREE.Mesh(geo, new THREE.MeshNormalMaterial());
  scene.add(mesh);
  cam.position.set(0, -2.2, 1.6); cam.lookAt(0, 0, 0);
  const px = new Uint8Array(4);
  const sync = () => gl.readPixels(0, 0, 1, 1, gl.RGBA, gl.UNSIGNED_BYTE, px);
  renderer.render(scene, cam); sync();

  // --- picking ---
  const rays = Array.from({ length: 200 }, (_, i) => { const a = i * 2.399; return [Math.sin(a) * 0.9 + 0.0013, Math.cos(a) * 0.9 * ((i % 7) / 7 + 0.2) + 0.0007, 3]; });
  // performance.now() is coarsened to ~0.1 ms outside cross-origin-isolated pages, so time the whole batch and divide.
  const pbTotal = time(() => { for (let rep = 0; rep < 10; rep++) for (const r of rays) k.pick(r[0], r[1], r[2], 0, 0, -1); })[0];
  const pb = [pbTotal / (10 * rays.length)];
  const pbr = rays.slice(0, 10).map((r) => time(() => k.pick_brute(r[0], r[1], r[2], 0, 0, -1))[0]);
  const rc = new THREE.Raycaster();
  mesh.updateMatrixWorld(); geo.computeBoundingSphere(); geo.computeBoundingBox();
  const pr = rays.slice(0, 5).map((r) => { rc.set(new THREE.Vector3(r[0], r[1], r[2]), new THREE.Vector3(0, 0, -1)); return time(() => rc.intersectObject(mesh, false))[0]; });
  // agreement of hit distance between kernel and Raycaster on the same rays
  let maxDiff = 0, misses = 0;
  for (const r of rays.slice(0, 5)) {
    rc.set(new THREE.Vector3(r[0], r[1], r[2]), new THREE.Vector3(0, 0, -1));
    const h = rc.intersectObject(mesh, false)[0];
    const id = k.pick(r[0], r[1], r[2], 0, 0, -1);
    if (!h || id < 0) { misses++; continue; }
    maxDiff = Math.max(maxDiff, Math.abs(h.distance - k.hit_t()));
  }
  row.pick = { wasm_bvh_ms: +pb[0].toFixed(5), wasm_brute_ms: +median(pbr).toFixed(2), threejs_raycaster_ms: +median(pr).toFixed(2), raycaster_vs_kernel_max_dist_diff: maxDiff, mismatched_rays: misses };

  // --- sculpt strokes, three upload strategies, each over 30 strokes ---
  async function strokes(strategy) {
    const sc = [], rf = [], up = [], tot = [], span = [], touched = [];
    let growth = 0;
    for (let i = 0; i < 30; i++) {
      const cx = -0.6 + 0.04 * i, cy = 0.1, cz = 0.1 * Math.sin(cx * 6) * Math.cos(cy * 6);
      const t0 = performance.now();
      const tc = k.sculpt(cx, cy, cz, 0.05, 0.02);
      const t1 = performance.now();
      k.refit_local();
      const t2 = performance.now();
      if (wasm.memory.buffer !== lastMem) { lastMem = wasm.memory.buffer; [pos, idx, nrm] = views(); posA.array = pos; nrmA.array = nrm; growth++; }
      const lo = k.dirty_lo(), hi = k.dirty_hi();
      posA.clearUpdateRanges(); nrmA.clearUpdateRanges();
      if (strategy === "partial") { posA.addUpdateRange(lo * 3, (hi - lo + 1) * 3); nrmA.addUpdateRange(lo * 3, (hi - lo + 1) * 3); }
      posA.needsUpdate = true; nrmA.needsUpdate = true;
      renderer.render(scene, cam); sync();
      const t3 = performance.now();
      sc.push(t1 - t0); rf.push(t2 - t1); up.push(t3 - t2); tot.push(t3 - t0); span.push(hi - lo + 1); touched.push(tc);
    }
    return { strategy, sculpt_ms: +median(sc).toFixed(3), refit_local_ms: +median(rf).toFixed(3), upload_render_ms: +median(up).toFixed(2), edit_to_pixels_ms: +median(tot).toFixed(2), edit_to_pixels_p95_ms: +p95(tot).toFixed(2), median_dirty_span_verts: median(span), median_touched_verts: median(touched), memory_growth_events: growth };
  }
  row.strokes = [await strokes("full"), await strokes("partial"), await strokes("partial")];
  // after all edits: kernel and brute force must still agree
  let agree = true;
  for (const r of rays.slice(0, 10)) {
    const id = k.pick(r[0], r[1], r[2], 0, 0, -1), t = k.hit_t();
    const bid = k.pick_brute(r[0], r[1], r[2], 0, 0, -1);
    if ((id < 0) !== (bid < 0)) agree = false;
  }
  row.agree_after_edits = agree;
  R.rows.push(row);
}

window.__P04 = R;
out.textContent = JSON.stringify(R, null, 1);
document.title = "P04 done";
