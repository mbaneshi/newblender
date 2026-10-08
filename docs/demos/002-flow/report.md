# Demo 002: Flow, first slice — report

Flooded-forest shot from [docs/showcase/01-flow.md](../../../newblender/docs/showcase/01-flow.md), built live in Blender 5.2.2 through the Blender Lab bridge, then rendered headless.
Build script: `tools/live/demos/flow_build.py` · checks written first: `tools/live/checks/flow_checks.py`, `flow_hash.py`, `flow_render_checks.py`.

**Outputs:** `flow.blend` · `frames/` (240 × 3840×2160 PNG) · `flow_shot_4k.mp4` · `flow_shot_1080p.mp4` · `still_0001.png`, `still_0240.png`

## Final check results

| Result | Layer | Check | Measured |
|---|---|---|---|
| PASS | 1 | terrain: edges shared by >2 faces | 0 |
| PASS | 1 | terrain: degenerate faces | 0 |
| PASS | 1 | terrain: faces pointing down | 0 |
| PASS | 2 | terrain area below water line | 42.0% |
| PASS | 2 | tree instances with origin below water | 0 of 9900 |
| PASS | 2 | tree instances in camera frustum (frame 120) | 2239 |
| PASS | 1 | ocean evaluates on every frame | 240 of 240 |
| PASS | 2 | boat waterline gap, worst frame | 1.5 cm |
| PASS | 2 | camera jitter RMS | 0.41 deg |
| PASS | 2 | camera jitter frequency | 0.85 Hz |
| PASS | 2 | naming prefixes GEO-/ENV-/CAM-/LGT- | 100% |
| PASS | 3 | fresh headless rebuild gives an identical fingerprint | `91dd58a245c21001` in both (9,900 trees) |
| PASS | 4 | EEVEE 4K seconds per frame (median ≤ 10, max ≤ 20) | median 2.58 s, max 5.65 s, total 11.1 min |
| PASS | 4 | fully black pixels (worst frame) | 0 |
| PASS | 4 | flicker: max frame-to-frame luminance change (< 2%) | 0.27% (mean 0.079%) |
| WARN | 5 | agent's own look vs. Flow (warn under 3/5) — **self** | 2.5/5 (blind: 1.0, see below) — reads as a flooded forest valley; haze is too strong (low contrast), water has no reflections, no wake, trees are low-poly blobs, nothing like Flow's painterly detail |
| — | 6 | does it feel like Flow? | owner's call |

## What went wrong on the way (all caught by looking or by checks)

1. Terrain relief too flat (14 m): doubled the hill strength.
2. Forest too sparse (1,588 trees) and ocean too coarse (2,500 verts; the Ocean modifier has a separate viewport resolution).
3. World-volume haze turned the whole frame black in EEVEE (it absorbs the infinitely far sky): replaced with a bounded haze box.
4. Camera inside a tree, then aimed past the boat: placement now searches positions with a clear, canopy-aware line of sight.
5. Root cause of 4: the boat sat 2.2 m from shore in an inlet. It now goes to the most open deep water (10.7 m from land).
6. Checks run 1: 8/11. One tree base below water (filtered by face, not by point), only 954 trees in view, jitter 0.24°. Fixed with a per-point height filter, a denser forest and stronger noise.
7. Checks run 2: 10/11 (1,514 in view); a 26 mm lens gave 1,939, still under 2,000, so the forest was made denser again. The threshold was not changed.
8. Final: 11/11 live checks, plus layers 3 and 4.

## Deviations from the plan

- **Non-manifold check** redefined for an open heightfield: edges shared by more than 2 faces, not boundary edges.
- **Flicker** is measured on the whole frame, not "static areas", because the camera moves. It is a looser test.
- **Layer-5 vision check** is the agent's own judgement of the rendered stills, not a comparison against an actual Flow frame (none downloaded).
- **Camera height:** the plan pictured a low camera over water. This terrain has no open water wide enough, so the camera flies over land above the canopy (4.5 m above the water at the boat).

## Blind quality (RFC 0001 R7)

Session `s01-flow-charge`, scored by the owner on 2026-10-08 without knowing sources (12 items, 540 px wide). Full table: `~/newblender-data/blind/sessions/s01-flow-charge/results.md` (local only).

| | Agent (Flow slice) | Studio (Flow film) |
|---|---|---|
| Items | 3 (frames 1, 120, 240) | 4 |
| Mean quality (1–5) | **1.00** (1, 1, 1) | **3.75** (5, 4, 4, 2) |
| Taken for the other source | 0 of 3 | 1 of 4 (lake + sailboat, rated 2, guessed agent) |

- **Quality measure: 1.0 / 5.** All three agent frames got the floor score and none passed as studio work.
- **Self-score calibration:** the self score was 2.5, so the agent **overrated its own work by 1.5 points**. The vision self-check is not a reliable quality signal for this kind of shot.
- **Telling detail:** the one studio frame mistaken for agent work is the sparse lake-and-sailboat shot, the closest in composition to this slice. Composition without Flow's painterly detail and characters reads as "agent".
