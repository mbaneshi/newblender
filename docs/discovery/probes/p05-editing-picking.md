# P05: picking, brush sculpt and partial upload (north-star viewer check, part 2)

Issue #13. Builds on P04 (`p04-viewer-spike.md`, PR #12). Code: `tools/spikes/viewer/kernel/src/edit.rs`, `examples/edit_bench.rs`, and the `mode=edit` branch of `web/src/main.js`. Raw numbers: `results/p05-native.jsonl`, `results/p05-wasm.json`.

## Verdict

**Feasible on this hardware, with the same caveat as P04: it is an M4 Max.** At 1M and 2M triangles an edit-to-pixels round trip (brush stroke, normal repair, BVH refit, upload, draw, GPU sync) took about 1 ms median, and picking took about 1 microsecond. The editing half of the viewer star check is no longer open on strong hardware. It stays open on weaker GPUs.

## What was built

A kernel module with: vertex-to-triangle adjacency; a median-split BVH (leaf size 4); closest-hit ray picking (Moller-Trumbore); a brush sculpt that finds vertices through the BVH, displaces them with a smooth falloff and repairs normals only for triangles that changed; and a local BVH refit that updates only changed leaves and climbs until bounds stop changing. The same code runs natively and as WASM.

## Numbers

Native Rust, release build (`edit_bench`, 20 strokes, 200 rays):

| Triangles | Build adjacency + BVH | Pick (BVH) | Pick (brute force) | Sculpt | Refit, local | Refit, full | Full normals |
|---|---|---|---|---|---|---|---|
| 0.4M | 57 ms | 0.8 us | 1.3 ms | 0.03 ms | 0.03 ms | 2.9 ms | 1.3 ms |
| 1.0M | 129 ms | 0.9 us | 3.2 ms | 0.05 ms | 0.07 ms | 6.6 ms | 3.7 ms |
| 2.0M | 275 ms | 1.0 us | 6.2 ms | 0.11 ms | 0.13 ms | 13.2 ms | 6.7 ms |

WASM in Chrome 155 on the same machine:

| Triangles | Build accel | Pick (BVH) | Pick (brute, WASM) | Pick (three.js Raycaster) | Edit to pixels, full upload | Edit to pixels, partial upload |
|---|---|---|---|---|---|---|
| 1.0M | 631 ms | below timer resolution | 7.5 ms | 43 ms | 1.2 ms (p95 1.8) | 0.6 to 0.8 ms (p95 0.8 to 1.2) |
| 2.0M | 749 ms | 1.1 us | 13.6 ms | 66 ms | 1.8 ms (p95 5.9) | 0.9 ms (p95 1.0 to 2.0) |

A typical stroke touched about 1,000 to 2,000 vertices; the contiguous dirty span in the vertex buffer was 25k to 50k vertices (about 5% of the mesh).

## What it means

- **Picking needs an acceleration structure, and the stock one is not enough at this size.** The three.js Raycaster takes 43 to 66 ms per pick, which is several frames. The BVH answers in about a microsecond, roughly 5 orders of magnitude faster than the Raycaster, and the answers agree (distance difference under 5e-7, no mismatched rays).
- **The BVH build is the cost to watch.** 0.6 to 0.75 s in WASM at 1 to 2M triangles. That is fine once per load or per topology change and not fine per edit. Native is about 2.4x faster, so WASM overhead is real here (P04 saw 1.0x to 1.5x on simpler kernels).
- **Refit must be local.** A full refit costs 6.6 ms at 1M triangles, more than recomputing every normal. Local refit costs 0.07 ms. Without it, the BVH would eat the frame.
- **Partial upload helps, but less than expected.** It halves upload plus draw (1.0 to 0.5 ms at 1M) and trims the tail, but a full re-upload of 1M vertices still costs only about 1 to 1.5 ms. That is almost certainly the unified memory of Apple silicon. A discrete GPU over PCIe is the case where partial upload should matter, and this run cannot show it.

## Bugs found while measuring

1. **The ray-box test returned NaN for axis-parallel rays whose origin sits exactly on a box bound** (`0 * inf`), so the BVH silently missed hits that brute force found. Grid-aligned rays are common in real editing. Fixed by treating a ray parallel to a slab as a containment test.
2. **A first "disagreement" between BVH and brute force was a tie, not a bug:** a ray through a shared vertex hits several triangles at the same distance. Agreement is now checked by hit distance, not triangle id.
3. **My first sculpt benchmark moved no vertices on most strokes** (brush centred at z=0 while the surface sat below it), so the early medians were of zeros. Fixed by centring the brush on the surface and recording the minimum moved-vertex count per stroke (337 to 1,683, never zero).

## Not tested

- Weaker or discrete GPUs, where upload cost differs most.
- A real topology edit (extrude, delete, subdivide locally). The BVH would need partial rebuilds, which cost far more than a refit.
- Many objects, instancing, lights, shadows.
- Undo, and concurrent edits from an agent and a human.
- Picking against a moving camera at interactive rates through the DOM (event latency, not kernel time).
- wgpu / WebGPU.
- Timer resolution: Chrome coarsens `performance.now()` to about 0.1 ms on pages that are not cross-origin isolated. Sub-0.1 ms WASM figures come from batch timing (10 x 200 picks) or are marked as below resolution. Edit-to-pixels medians of 0.6 to 1.8 ms are at 6 to 18 timer ticks and carry that granularity.

## Effect on the star check

The viewer check from RFC 0001 R8 now has evidence for loading, computing, drawing, picking and local editing at 1 to 2M triangles on strong hardware. What would move the star is a weak-GPU result, or a real topology-editing cost that breaks the frame budget. Both remain to be measured.
