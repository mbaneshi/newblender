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
} else {
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
}

window.__P04 = R;
out.textContent = JSON.stringify(R, null, 1);
document.title = "P04 done";
