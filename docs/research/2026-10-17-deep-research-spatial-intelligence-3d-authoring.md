# Deep research: spatial intelligence and 3D authoring

Date: 2026-10-17. Answers the seven questions in the [reframe notes](2026-10-17-reframe-spatial-intelligence-and-first-principles.md). This page is a condensed record. The full report (about 3,000 words, with links) and the six researchers' notes are local only, in `labs/deep-research/` (gitignored).

## Conclusion

The north star holds, in a narrower form. The durable value is the layer that checks and edits 3D, not the layer that imagines it. The platform's moat is the verified state of a scene: exact data going in, a strict checker judging what comes out, and an edit history that can be rolled back.

## Verdicts on the three hypotheses

| Hypothesis | Verdict |
|---|---|
| H1. Three layers: understand space / simulate and act / author and edit | Supported as a map, weak as an architecture. No source shows one model spanning the layers. "Understand" is the thinnest: world models give video, embeddings or dense splats, not editable scenes. Only Marble and TRELLIS.2 / Hunyuan3D emit files Blender opens, and nobody shows those are metric or editable. |
| H2. Math-first core, without rewriting mature numerics | Supported, with a firm limit. Read it as "invariants-first". Rust owns the data model, typed units and frames, the invariant list, the verifier API and cheap checks. Wrap Manifold, OpenCASCADE and CGAL. Rust has no production B-rep kernel (`truck` is experimental, Fornjot shut down). |
| H3. Programmatic or hybrid wins for tolerance work, generative tolerates appearance | Mostly supported, with two cracks. Programmatic models also fail on complex CAD, and generated 3D still needs cleanup (topology). In every architecture found, a deterministic kernel is the final judge, so the real question is who verifies. |

## Where to put effort

- **Author and edit:** build here.
- **Simulate and act:** borrow it (MuJoCo, Newton, OpenCASCADE). "Agent proposes, simulator checks" already has a worked example (SceneSmith, 96% physical stability, preprint).
- **Understand space:** buy it as an import (Marble, TRELLIS.2). Do not promise it until scale and topology are measured.

## Key evidence

- Frontier models trail humans by 25 to 45 points on spatial benchmarks (SpatiaLab 54.9% vs 87.6%). The scores are one to three model generations old.
- Exact scene data and tools close part of the gap: +9 and +12 points (GR3D), 58% to 76% (Reasmory). Preprints, self-reported.
- Running is not being right: error feedback lifted executability from about 0.70 to 0.97 while shape metrics did not move (3DCodeBench). Blender 4.x to 5.0 API drift is the top failure.
- VLM judges are moderate: 0.66 agreement with humans against 0.79 between humans (BlenderGym). Kernel checks do better (CADSmith IoU 0.81 to 0.96).
- Checks come in three layers: index topology, exact predicates, tolerance checks. A constraint solver may have several valid answers, so the oracle checks residuals near zero.
- Blender is GPL, which favours "own the core, call out to Blender" over embedding or forking. OpenUSD Core Specification 1.0 (2025-12-17) is the credible interchange format.
- Taste, which valid solution is wanted, and tolerance choice stay with the human.

## No-regret path, in order

1. Build the typed scene API and the layered verifier behind a trait, and run it against Blender, Manifold and OCCT outputs.
2. Rerun BlenderGym and BenchCAD on current models, with and without exact scene data. This could change the conclusion most. Needs a budget number from the owner first.
3. Add import adapters for Marble and TRELLIS.2 and measure scale and topology.

Defer the Rust B-rep kernel, the WASM build and any generative-native bet until these show where the verifier and the model each fall short.

## Evidence gaps (ranked)

1. No October 2026 frontier scores on BlenderGym, BenchCAD or CADEngBench. Most likely to change the answer.
2. No head-to-head of scene-graph JSON vs renders vs both.
3. No controlled test of a small typed vocabulary vs raw bpy.
4. Marble and TRELLIS.2 output scale and editability unknown; no full chain demo.
5. Rust kernel maturity not sourced (truck activity, Manifold Rust bindings).
6. Licence texts for Unity, Unreal, Godot, OpenCASCADE and CadQuery not fetched.
7. Determinism and undo per engine not researched.
8. No primary LeCun or Fei-Fei Li sources; quotes are secondhand.

## How far to trust it

Most evidence is preprint, vendor or secondary, and almost none is replicated. Several 2026 arXiv IDs are unverified. Treat the verdicts as a ranked set of bets, not findings. No RFC has been changed by this page; any change to RFC 0001 R8, RFC 0003 or RFC 0004 needs the owner's approval first.
