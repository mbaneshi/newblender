# Probe P04: a Rust/WASM kernel with a three.js viewer (north-star check 2)

- **Date:** 2026-10-17 · **Machine:** Apple M4 Max (ANGLE Metal), 14 cores · **Browser:** Chrome 155, headed · **Viewport:** 960x540, pixel ratio 1 · **Stack:** Rust 1.99.0, wasm-bindgen 0.2.129, three.js 0.186.0, Vite 7
- **Feeds:** [RFC 0001 R8](../../rfc/0001-newblender.md) star check "can a Rust/WASM viewer reach acceptable speed?", [RFC 0004](../../rfc/0004-platform-stack-and-scope.md) §7 Q2
- **Code and raw numbers:** [`tools/spikes/viewer/`](https://github.com/mbaneshi/newblender/tree/dev/tools/spikes/viewer) (`kernel/` Rust crate, `web/` Vite app, `results/p04-results.json`). No API calls.
- **Evidence level reached:** L2 (reproduced at runtime) for the two questions below; one machine, one run, synthetic grid mesh.

## What was tested, and a reframing

The star check was written as "Rust/WASM with wgpu or three.js". While scoping I found that `nexus-platform-ir` (the model stack) already ships a Rust kernel compiled to WASM (`wasm-bindgen`) with a **three.js** renderer (`packages/renderer`), not wgpu. So the useful question became: **does a WASM kernel plus three.js hold up at 3D mesh sizes?** A direct wgpu path was **not** built; it stays deferred until three.js hits a limit.

The kernel (167 lines of Rust) builds a grid mesh, does midpoint subdivision (each triangle becomes four) and computes vertex normals. A 70-line JavaScript twin implements the same algorithm for a fair comparison. The viewer renders the mesh with a plain normal-shading material and orbits the camera.

## Result 1: the kernel in WASM against JavaScript and native

Median of 3 runs (2 for the largest). Checksums of WASM and JS outputs agree to about 1e-12 relative, so the implementations compute the same mesh.

| Output triangles | Op | Native Rust | WASM (Chrome) | JavaScript (Chrome) | WASM speedup over JS |
|---|---|---|---|---|---|
| 401k | subdivide | 4.5 ms | 5.4 ms | 18.1 ms | 3.4x |
| 401k | normals | 1.6 ms | 1.9 ms | 18.7 ms | 9.8x |
| 1.6M | subdivide | 23.0 ms | 26.3 ms | 95.5 ms | 3.6x |
| 1.6M | normals | 6.9 ms | 7.6 ms | 45.1 ms | 5.9x |
| 6.4M | subdivide | 107.8 ms | 162.7 ms | 604.8 ms | 3.7x |
| 6.4M | normals | 33.5 ms | 33.5 ms | 183.2 ms | 5.5x |

WASM ran within 1.0x to 1.5x of native Rust. Same source runs on the server and in the browser, as the north star assumed.

## Result 2: rendering in three.js, fed from WASM memory

The camera orbit ran for 240 frames per case. `render ms` is a back-to-back synced render with no vsync wait (`readPixels` forces the GPU to finish; plain `gl.finish()` returned about 0.2 ms and is not a reliable sync in Chrome with ANGLE). The vsync-locked interval was 16.6 to 16.8 ms median in every case (60 Hz).

| Triangles | Source | Handoff | Mesh build | First frame (incl. upload) | Render ms, median / p95 |
|---|---|---|---|---|---|
| 100k | WASM | zero-copy view | 5.6 ms | 47 ms | 0.6 / 1.3 |
| 400k | WASM | zero-copy view | 18.7 ms | 88 ms | 1.0 / 2.5 |
| 1.6M | WASM | zero-copy view | 82 ms | 81 ms | 0.7 / 2.4 |
| 1.6M | JavaScript | n/a | 225 ms | 68 ms | 1.5 / 2.5 |
| 1.6M | WASM | copy (`slice`) | 79 ms | 58 ms | 1.2 / 2.8 |
| 6.4M | WASM | zero-copy view | 677 ms | 257 ms | 1.8 / 3.8 |

Observations:
- Static geometry up to 6.4M triangles stayed far inside a 16.7 ms frame on this GPU.
- Building the 1.6M mesh took 82 ms in WASM against 225 ms in JavaScript (2.7x).
- At 1.6M triangles the zero-copy view and the copy were within noise of each other on build time; the copy's cost was not isolated.
- The first frame (which includes uploading the buffers to the GPU) costs 47 to 257 ms. A whole-mesh re-upload on every edit would hitch; edits need partial buffer updates.

## Build facts

| Item | Value |
|---|---|
| `.wasm` size | 28.9 KB (13.1 KB gzip) |
| JS bundle | 522 KB (132 KB gzip), almost all three.js |
| WASM init | 24.5 ms |
| First `wasm-pack` build | 54 s (includes installing the matching `wasm-bindgen-cli`); native `cargo` release build 8 s; `vite build` 0.4 s |
| Code | 167 lines Rust, 70 lines JS twin, 131 lines page/bench harness |

## Verdict against the star check

**Feasible, with limits.** A Rust kernel in WASM feeding three.js is fast enough for the viewing and geometry-compute side of the north star on an M4 Max, and it is the same pattern nexus-platform-ir already uses. The spike does **not** show the editing experience is feasible, and it says nothing about weaker hardware.

## Not tested (read before relying on this)

- **Hardware.** An M4 Max is a top-end GPU. Integrated and older GPUs were not measured, and the star check asks for "acceptable speed" in general.
- **Editing interactions:** picking, selection overlays, gizmos, and partial buffer updates after an edit were not built. The whole-mesh re-upload cost above is an upper bound for edit hitches, not a measurement of them.
- **Scene complexity:** one mesh, one draw call, a trivial material, no lighting, shadows, textures, or antialiasing. Many-object scenes and draw-call overhead were not tested.
- **wgpu directly** and **WebGPU** were not built, so there is no comparison with the plain Rust-to-GPU path.
- **WASM memory.** A view into WASM memory is invalidated whenever memory grows; the page recreates views after each op. A real kernel API must make that a rule.
- Single run per case; the rAF p95 of 29.9 ms for the first case is one hiccup.

## Follow-ups

- Build a partial-update benchmark (edit 1% of vertices, update only that range) and picking on a 1M-triangle mesh.
- Repeat on a weaker GPU or with CPU throttling and a lower-end browser.
- Try a many-object scene (thousands of draw calls) with instancing.
- Only if three.js becomes the limit: a minimal wgpu comparison.
