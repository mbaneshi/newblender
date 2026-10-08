# 03 — Charge: how an agent could make it

| | |
|---|---|
| **Original** | Blender Studio (dir. Hjalti Hjálmarsson, art director Andy Goralczyk, lead animator Rik Schutte), 2022, open movie: photoreal action · [Blender Studio — Charge](https://studio.blender.org/films/charge/) |
| **Agent-readiness today** | **Partial.** The hard-surface factory, the PBR materials, the GN smoke, fire and muzzle-flash FX, and the lighting and rendering are agent-buildable today. The realistic digital human (Einar), his hair groom, facial performance and combat animation are not. |
| **Difficulty** | 5 (only about 3 minutes, but a believable digital human in heavy action is among the hardest things in CG) |
| **First slice** | A battery-factory bay built as a modular kit: arrayed shelving racks of glowing battery cells, declared-bevel walls and pipes, CC0 PBR metal and concrete, volumetric haze and a GN muzzle-flash and smoke burst, rendered as a Cycles still plus a short EEVEE camera push-in. |

## 1. What the original actually is

- **Film:** "a high-visual-impact, action-packed 3-minutes-long animation inspired by the game cinematics and realtime demos formats" ([Blender Studio](https://studio.blender.org/films/charge/), verified 2026-10-07).
- **Hero assets:**
  - **Einar:** a realistic old man, sculpted in layers, with a curves-hair groom and facial rig.
  - **The security robot:** many modelling iterations.
  - **Packbot:** a smaller robot with driving tests.
  - **The battery factory:** a hard-surface environment.
- **FX:** smoke, fire and muzzle flashes made with Geometry Nodes.
- **Output:** rendered with both EEVEE and Cycles comparisons ("EEVEE and Cycles rendering comparisons", same page).
- **Released:** the "Charge Material Asset Library", as a freebie. Shot files are for subscribers.
- **Shots:** the count is not published. For a 3-minute action short, roughly 40–80 is my estimate (interpretation).

## 2. How the humans made it

**Facts:**

- **Stages:** S01, S02, S03, S04, S05, S07, S08, S09, S10 ([index](00-index.md) §03).
- **Einar** was built with layered sculpting and the then-new curves hair system ([index](00-index.md); [Layered sculpting for Einar](https://studio.blender.org/blog/layered-sculpting-for-einar), unverified).
- **Geometry Nodes** for smoke and fire, curve-stitching tools for modelling, and advanced facial rigging ([Blender Studio](https://studio.blender.org/films/charge/), verified).
- **The project began as "Project Heist"** and pursued realism through interactive PBR workflows (same page; index).

**Interpretation:** Charge splits cleanly in two.

- **The world:** factory, robots, materials, lighting and FX. This is engineering-shaped: dimensions, modular repetition, physically based values and procedural FX. It is the agent's natural territory.
- **The human:** skin, hair, micro-expression and weight in a fight. This is the uncanny-valley problem, where small errors are fatal and judgement is entirely perceptual.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs | Tooling |
|---|---|---|---|
| S01 Modeling (environment) | A modular kit as data: wall panel, floor tile, pillar, pipe run and battery rack. Each part is a low cage with declared Bevel (harden normals), Array, Mirror and Solidify. Racks are a GN instancer over a grid with per-instance variation. | Real dimensions for industrial racking (e.g. 2.0 m bays, 0.6 m deep); reference photos | `bl.py`, bmesh-as-data, L-006 |
| S01 Modeling (droid) | Blockout as declared primitives plus Booleans, then a support-loop pass. The final hero droid needs a human design pass. | Concept art (human) | Declared Boolean, Bevel and Weighted Normal stack |
| S01 Modeling (Einar) | **Not attempted.** Use a CC-BY base mesh only as a stand-in. | `human-base-meshes-bundle-v1.4.1` (local) | — |
| S02 UV & texturing | Box or cube projection on the kit; trim-sheet UVs on panels; numeric stretch checks. | Poly Haven CC0 metal, concrete, painted-steel and rust textures; the Charge material library (download) | UV by script |
| S03 Shading | PBR from measured values: metalness 0/1, roughness bands, emissive battery cells with a declared colour temperature. | Charge Material Asset Library (CC-BY freebie) | Shader nodes and asset linking |
| S04 / S08 FX | Muzzle flash as GN instanced emissive cards with a 2–3 frame lifetime. Smoke as a Mantaflow gas burst, or GN points to Volume with animated noise density. Sparks as GN points with gravity. | None | GN simulation zone; Mantaflow `-b` bake |
| S05 Rigging | Droid: a mechanical rig of bones parented to parts, with joint limits as data (no skin weights needed). | — | Armature by script |
| S07 Animation | Droid patrol paths and mechanical cycles are scriptable. **Einar's performance and the fight choreography are human.** | Previs (human) | F-curves by script |
| S09 Lighting & rendering | Practical lights from the declared rack emitters, cold key and warm rim, volumetric haze; Cycles finals and an EEVEE preview. | — | Headless renders |
| S10 Compositing | Glare on the emitters, lens distortion and grain as a declared compositor graph. | — | Compositor nodes by script |

**Build order (for the first slice):**

1. Write the checks first: bay dimensions, rack count, PBR value ranges, haze and emission levels, FX timing.
2. Set up a clean slate with metric units. Build the kit parts as data, each with its declared modifier stack, and check validity per part.
3. Lay out a 20 × 12 × 6 m bay: two rows of racks via GN, pillars arrayed at 6 m, and pipe runs along the ceiling.
4. Import Poly Haven materials (or link the Charge library) and assign them by naming rule (`GEO-rack_*` gets painted steel, and so on).
5. Battery cells: an emissive shader with per-instance random flicker driven by a GN attribute.
6. Add a volume cube with haze density, a key light through a ceiling grille, and the emitters as practicals.
7. FX beat at frame 48: a GN muzzle flash (2 frames), a spark burst, and a smoke puff.
8. A camera push-in of 72 frames. Show progress in the window with `snap.py`, render the Cycles still headless at 1920 × 1080, and render an EEVEE preview of the 72 frames.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Kit parts as bmesh data with declared stacks (proven by the chair demo).
  - GN instancing and simulation zones built by script.
  - Material import and assignment.
  - Volumes, light set-up, the compositor graph, and headless Cycles and EEVEE.
- **Painful today:**
  - **Hard-surface refinement** (support loops, knife cuts, inset panel lines) is local topology surgery with no declarative twin. 59 such operators need edit mode plus selection ([05-brief](../discovery/s01-modeling/05-brief.md) §4; L-001, L-002, L-005). Declared Bevel and Boolean cover most of it, but not all.
  - **Boolean cleanup:** the results are hard to validate without a returned diff (L-003). The validity check catches non-manifold output after the fact.
  - **Mantaflow bakes** are operator-only with context polls (L-004).
  - **Hair grooming** (curves) is brush-driven: comb, cut and puff strokes (L-009). That is a human act with no data API for "comb this way".
- **Not feasible today:**
  - A believable realistic human: skin shading tuned by eye, facial performance, hair groom.
  - Fight choreography with weight and intent.
  - The robot's character design.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Each kit part, evaluated: non-manifold edges, degenerate faces, flipped normals, loose verts | 0 / 0 / 0 / 0 |
| 1 Validity | Boolean results: self-intersecting faces (BVH overlap test) | 0 |
| 2 Spec | Bay bounding box | 20 × 12 × 6 m ± 2% |
| 2 Spec | Rack count / bay spacing | 2 rows × 8 racks / 2.0 m ± 1 cm |
| 2 Spec | Face budget of the whole bay, evaluated | ≤ 1.5 M faces |
| 2 Spec | PBR sanity: every metal has metallic = 1 and roughness 0.15–0.7; every dielectric has base-colour luminance 0.03–0.9 | 100% of materials |
| 2 Spec | Muzzle flash visible frames / smoke lifetime | 2–3 frames / 24–48 frames |
| 2 Spec | Applied scale and naming (`GEO-`, `FX-`, `LGT-`) | all 1.0 / 100% |
| 3 Reference | Rebuild from the recipe in a fresh headless session: evaluated mesh hash per kit part | identical |
| 4 Downstream | UV stretch (area-distortion ratio) on textured parts | ≤ 1.15 for 95% of faces |
| 4 Downstream | Cycles 1080p still at 256 samples with denoise: time, NaN or fireflies (pixels > 50 × the median luminance) | < 15 min; 0; < 20 |
| 4 Downstream | EEVEE preview of 72 frames: seconds per frame | ≤ 5 s |
| 5 Appearance (warning) | Vision model compares to Charge stills: an industrial, dim, cold-key, photoreal bay | warning if under 3/5 |
| 6 Taste (owner) | Does it read as Charge's world (oppressive, game-cinematic, real)? | owner's call |

## 6. Where the human is still needed

- **Einar end to end:** the likeness, sculpt detail, skin shading, groom and facial rig. Realism means perceptual judgement in every iteration.
- **Action choreography and animation:** weight, impact, and the old man's desperation.
- **Robot design:** the silhouette and the threat it reads as.
- **Art direction:** Andy Goralczyk's palette, the haze level, where the light falls in each shot.
- **The cinematic edit:** pacing a 3-minute action piece.

## 7. Effort

- **First slice (live demo, about 1 day):**
  - **On screen:** in the owner's window, an empty grid fills with a concrete floor. Then two long rows of steel shelving racks appear and multiply down the hall as the Array and GN instancers take effect. Ceiling pipes and pillars follow.
  - Hundreds of battery cells light up cyan with a slight random flicker. Fog fills the hall, and light shafts come through a ceiling grille.
  - Scrubbing to frame 48 shows a bright muzzle flash, a shower of sparks and a smoke puff.
  - The final Cycles still and a short EEVEE push-in clip render headless, with the check report.
- **Full reproduction:**
  - **Agent work:** about 200–400 agent-hours for the environment, droid modelling support, FX, lighting and render.
  - **Render compute:** about 4,300 frames × 5–20 min Cycles ≈ 360–1,400 GPU-hours.
  - **Human work:** the Einar package alone is months of specialist time (sculpt, groom, shading, face rig), plus animation of about 3 minutes of action by a small team. Overall about 1 studio-year, as the original took.

## 8. Risks and unknowns

- The Charge material library licence and download format are not verified here. Fall back to Poly Haven CC0 if needed.
- The GN smoke look versus Mantaflow: which reads as "real" at the Charge level is untested.
- EEVEE Next and Cycles parity for emissive-heavy, volumetric scenes may differ from 2022 behaviour.
- No Charge shot files are on this machine (they are subscriber-only), so layer-3 reference checks against the original are not possible; only self-consistency.

## 9. Sources

- [Blender Studio — Charge](https://studio.blender.org/films/charge/) (verified, fetched 2026-10-07: 3-minute runtime, Einar, robots, GN smoke and fire, EEVEE/Cycles, material library freebie)
- [befores & afters: how Blender Studio's realistic-human film was made](https://beforesandafters.com/2023/03/13/how-blender-studios-latest-film-with-a-realistic-human-character-was-made/) (unverified, per index)
- [Layered sculpting for Einar](https://studio.blender.org/blog/layered-sculpting-for-einar) (unverified, per index)
- [Poly Haven](https://polyhaven.com/) (CC0 textures)
- Local: `~/newblender-data/extracted/human-base-meshes-bundle-v1.4.1/` (stand-in base mesh)
- [`05-brief.md`](../discovery/s01-modeling/05-brief.md); [ledger](../discovery/ledger.md) L-001, L-002, L-003, L-004, L-005, L-006, L-009; [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`, `tools/live/demos/chair_build.py`, `tools/live/checks/chair_checks.py`
