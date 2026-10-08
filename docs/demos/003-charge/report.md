# Demo 003: Charge, first slice — report

Battery-factory bay from [docs/showcase/03-charge.md](../../../newblender/docs/showcase/03-charge.md), built live in Blender 5.2.2 through the Blender Lab bridge.
Build: `tools/live/demos/charge_build.py`. Checks, written before the build: `tools/live/checks/charge_checks.py`. Later scripts: `charge_l3_l4.py`, `charge_render_still.py`.
Textures: Poly Haven CC0 (concrete_floor_worn_001, concrete_floor_02, blue_metal_plate, metal_plate, corrugated_iron), 1K, in `~/newblender-data/assets/polyhaven/`.

**Outputs:** `charge.blend` · `still.png` / `still.exr` (Cycles, 1080p, frame 56) · `charge_pushin_eevee_1080p.mp4` (96 frames) · `eevee_frames/`

## Results

| Result | Layer | Check | Measured |
|---|---|---|---|
| PASS | 1 | kit parts: non-manifold / degenerate / inward / loose | 0 in 9 parts |
| PASS | 1 | boolean wall: self-intersecting face pairs | 0 |
| PASS | 2 | bay bounding box 20 x 12 x 6 m +-2% | 20.00 x 12.00 x 6.00 |
| PASS | 2 | racks: 2 rows x 8 | [8, 8] |
| PASS | 2 | rack pitch 2.0 m +- 1 cm | 2.000-2.000 |
| PASS | 2 | face budget <= 1.5 M | 20,295 |
| PASS | 2 | PBR sanity (metal roughness 0.15-0.7; dielectric luminance 0.03-0.9) | all ok |
| PASS | 2 | muzzle flash visible frames (2-3) | [48, 49] |
| PASS | 2 | smoke lifetime 24-48 frames | 42 |
| PASS | 2 | scale applied | all 1.0 |
| PASS | 2 | naming GEO-/FX-/LGT-/CAM- | 100% |
| PASS | 3 | fresh headless rebuild gives an identical fingerprint | `2c844a062d01ce49` in both (768 cell instances) |
| **FAIL** | 4 | UV stretch: ≥ 95% of faces within 1.15 area-distortion | **12.4% of faces**. By surface area: rack 95.9%, ceiling 95.6%, back wall 99.2%, **pillars 94.2%**. Unbevelled parts are 100%. The failing faces are 8–15 mm Bevel chamfers whose UVs interpolate between two box projections. |
| PASS | 4 | Cycles still, 1080p, 256 samples + denoise, < 15 min | 13.0 min on Apple M4 Max (GPU - 32 cores) |
| PASS | 4 | NaN/Inf pixels | 0 |
| **FAIL** | 4 | fireflies < 20 (pixels > 50× the median of their 5×5 neighbourhood) | **24**. All 24 sit in the spark burst, with RGB 1 : 0.53 : 0.19 = the spark emission (1 : 0.55 : 0.2). They are spark streaks, not render noise, but the rule as written counts them. |
| PASS | 4 | EEVEE preview, ≤ 5 s per frame | median 1.04 s, max 2.78 s (96 frames, 1080p) |
| WARN | 5 | agent's own look vs. Charge (warn under 3/5) — **self** | 2.5/5 (blind: 2.33, see below). Reads as a real industrial aisle: textured painted-steel racks, concrete, steel pillars, slatted ceiling, spark burst. Lighting is too even and bright for Charge's dark, high-contrast look; cells read as plastic tubs, not glowing batteries; smoke is faint in Cycles and **missing in the EEVEE preview**. |
| — | 6 | does it read as Charge's world? | owner's call |

## Fixes along the way

- **Look:**
  - Cells blew out to white (emission 3.6–6): lowered to 0.65–1.35 with saturated cyan.
  - Muzzle flash was a tiny star: made 2.5× larger.
  - Smoke was invisible: density raised about 4×, radius larger.
- **Smoke in EEVEE:** still invisible after the fix. A Cycles render of the same frame shows it, so the shader is correct. This is an EEVEE limitation with a volume object nested in the haze volume.
- **Haze:** milky in Cycles, so the density was halved (0.035 → 0.018).
- **PBR (first run 10/11):** corrugated iron roughness averaged 0.702 against a 0.70 limit. The fix was an art adjustment (× 0.9 roughness node, now about 0.63). The checker was **also** corrected: it sampled the raw texture and ignored nodes between texture and shader, so it now applies multiply-by-constant nodes on that path. Both changes are listed here because one touched the checker.

## Deviations from the plan

- **Frame range:** 96 frames, not 72, so the 42-frame smoke fits inside the range. The push-in spans all 96.
- **Firefly rule:** uses a local 5×5 median instead of the global median, so a bright light source isn't counted. Even so, the sparks count.
- **No compositor pass** (glare, lens distortion, grain), no droid and no character. The plan's first slice didn't require them.
- **Cycles device:** the live session renders Cycles on the CPU (about 37 s at 32 samples, half resolution), so the final still was rendered headless on the GPU. GPU was enabled only inside that factory-startup process; the owner's preferences were not changed.

## For the owner to decide

1. **UV metric:** should UV stretch be area-weighted? By face count, tiny bevel chamfers dominate.
2. **Firefly rule:** should known emitters (sparks) be masked out?

## Blind quality (RFC 0001 R7)

Session `s01-flow-charge`, scored by the owner on 2026-10-08 without knowing sources (12 items, 540 px wide). Full table: `~/newblender-data/blind/sessions/s01-flow-charge/results.md` (local only).

| | Agent (Charge slice) | Studio (Charge) |
|---|---|---|
| Items | 3 (Cycles f56, EEVEE f48, EEVEE f80) | 2 (film frame, production scene 050_0160 rendered locally) |
| Mean quality (1–5) | **2.33** (2, 3, 2) | **4.50** (4, 5) |
| Taken for the other source | **1 of 3** (EEVEE f48, muzzle flash, rated 3, guessed studio) | 0 of 2 |

- **Quality measure: 2.33 / 5.** It's the better of the two slices, and the only agent item in the session that passed as studio work.
- **Self-score calibration:** the self score was 2.5, so the agent was **close (0.17 over)**.
- **Telling detail:** the frame that fooled the owner is the muzzle-flash frame. Strong light and motion hide the even lighting and plastic-looking cells that give the other frames away. That points to lighting contrast as the next quality lever, which matches the self review.
