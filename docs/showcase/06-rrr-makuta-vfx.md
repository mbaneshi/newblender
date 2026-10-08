# 06 — RRR (Blender VFX by Makuta): how an agent could make it

| | |
|---|---|
| **Original** | Makuta Visual Effects (Hyderabad, CEO Pete Draper), 2022, blockbuster feature VFX · [blender.org user story](https://www.blender.org/user-stories/visual-effects-for-the-indian-blockbuster-rrr/) |
| **Agent-readiness today** | **Partial.** The CG side (environments, scattered foliage and crowds, volumetric atmosphere, Cycles renders, render-pass compositing) can be built today as data and declared Geometry Nodes. The plate side (camera tracking, solving, roto, plate-matched lighting) runs into GUI-gated operators (L-004, L-009) and judgement calls about what "matches the plate". |
| **Difficulty** | **5.** About 700 shots on a feature schedule, by a large team over roughly 2.5 years. Even a credible 10-shot sequence is a multi-week project. |
| **First slice** | A 6-second "forest gunfire establisher": a GN-scattered procedural forest with an instanced soldier crowd, volumetric smoke and animated muzzle-flash lights, rendered in Cycles with separate passes, then composited over a Poly Haven backplate whose camera matches by construction. |

## 1. What the original actually is

- **Deliverable:** about **700 VFX shots** for S. S. Rajamouli's *RRR* (2022). The user story credits Makuta with the shots; it does not say how many were rendered in Blender and how many in 3ds Max.
- **Sequences named in the source:**
  - **Police-station fight:** LiDAR processing, previz and postviz. Rendered with *Cycles for Max*, so this one is not a Blender render.
  - **Komaram Bheem song:** every exterior of Scott's Palace, including street shots outside the gates and side streets, built in Blender.
  - **Intermission fight:** the palace and seating-stand assets were re-lit and shaded in Blender, and the crowd assets, foliage and foreground gate were built in Blender. The fireworks were done in 3ds Max.
  - **Military compound and forest scenes:** compound establishers, and forest gunfire and explosions, using Blender's volumetric system.
- **Outputs:** CG renders (environments, crowds, foliage, atmosphere) handed to a separate compositing department. The source says pre-final assets were sent to comp during production.
- **Software span:** Blender 2.83 to 2.92. The studio switched from 3ds Max in November 2019.

## 2. How the humans made it

| Stage | What the source says (fact) | Interpretation |
|---|---|---|
| S01 Modeling | Palace, gate, seating stands and crowd assets were modelled in Blender, and LiDAR scans were processed. | Set extensions are built to match practical sets, so LiDAR gives true dimensions. |
| S03 Shading | Materials were randomised "without creating new materials". | Most likely per-instance attributes (Object Info random, GN attributes) feeding a single shader. |
| S04 Geometry Nodes | "Heavily leaned on Geometry Nodes for foliage distribution systems." | Scatter by density masks with randomised scale and rotation, the standard pattern from 2.92 onward. |
| S08 Simulation & FX | Volumetrics for the compound establishers and the forest gunfire and explosion atmosphere. Fireworks in 3ds Max. | Probably volume shaders plus some smoke sims; the source does not say which. |
| S09 Lighting & rendering | Cycles, inside Blender and through the Max plugin. | Plate-matched lighting, typically from on-set HDRIs. *Not stated in the source.* |
| S10 Compositing | Pre-final assets went to the compositors during production. | Comp software is not named. Comp happened outside Blender's compositor (*inference*). |

Not documented: camera tracking (which tool), roto, the render farm, team size per department. I make no claims about those.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 Modeling | Set-extension architecture as **data**: bmesh-built modules (walls, arches, columns), the pattern of `demos/chair_build.py`, plus declared Array, Mirror and Bevel. Treat a LiDAR stand-in as a point cloud imported as mesh vertices. | Real dimensions from the brief. Poly Haven models. A public photogrammetry scan (CC0) as the "LiDAR". | `tools/live/bl.py`; headless batch for kit generation |
| S03 Shading | One master shader per material family, with variation read from `Object Info → Random` or from GN-written attributes. That is exactly Makuta's "randomise without new materials". | Poly Haven textures (CC0) | Cycles |
| S04 Geometry Nodes | **Declared scatter recipe**: Distribute Points on Faces, density from a painted-free mask (noise plus distance to paths), Instance on Points, random scale and rotation, collision-free spacing for the crowd (Poisson radius). The GN tree is the artefact (L-006). | Procedural trees (GN, or the Sapling add-on), Poly Haven plants, low-poly crowd proxies | GN, built from Python node API |
| S06 Layout / camera | For CG-only shots, the camera is data. For plate shots, see the tracking row. | — | bridge |
| Tracking (S10-adjacent) | Insert tracks and markers as data (`clip.tracking.tracks.new`, `markers.insert_frame` exist). Run feature tracking and the camera solve through `clip.track_markers` and `clip.solve_camera` with a `temp_override` onto a Clip Editor area in the live window. Headless, their poll fails (probe below). | Tears of Steel raw / linear-EXR plates (CC-BY 3.0, [media.xiph.org/tearsofsteel](https://media.xiph.org/tearsofsteel/)) | live bridge only |
| S08 FX | Atmosphere as a **declared volume**: a domain cube with Principled Volume driven by noise and a density gradient, so there is no sim cache. Explosions get a Mantaflow smoke sim, scripted and baked headless. Muzzle flashes are emissive cards plus point lights keyed per frame as data. | — | Cycles volumes; `fluid` bake headless |
| S09 Lighting | HDRI world from the plate's location. Sun angle solved from the plate's shadow direction, which the agent proposes and a human confirms. View layers produce passes: beauty, shadow catcher, mist, cryptomatte. | Poly Haven HDRIs | Cycles, headless frames |
| S10 Compositing | Compositor node tree as data: plate + CG over (shadow catcher) + mist-driven haze + Lens Distortion and grain to match the plate. Optional Movie Distortion node from the solved camera. | Plate | compositor nodes |

**Build order**

1. Write the shot brief as assertions (section 5) before building anything.
2. Build the environment kit as data, then publish it to a collection.
3. Declare the GN scatter for foliage and the crowd proxies, and check the instance counts.
4. Declare the volume atmosphere, then animate the muzzle-flash lights as keyframes written directly to F-curves.
5. Set up the camera, either by data (CG establisher) or by solving (plate shot, live session only).
6. Render passes in Cycles, headless and deterministic (fixed seed, fixed samples).
7. Build the comp tree as data, render the final, and run the checks.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Modular architecture as bmesh data with declared modifiers, which demo 001 proved (12/12 checks, `~/newblender-data/demos/001-chair/report.md`).
  - GN scatter trees built from Python.
  - Volume shaders, lights, the camera, keyframes written as F-curve data.
  - Cycles passes and compositor trees as data.
  - Track and marker *data* (`MovieTrackingTracks.new`, `MovieTrackingMarkers.insert_frame` are exposed in 5.2.2; checked headless 2026-10-07).
- **Painful today:**
  - **Tracking and solving are GUI-gated.** `clip.track_markers` and `clip.solve_camera` share `ED_space_clip_tracking_poll`, which requires a `SpaceClip` with a clip in context (`editors/space_clip/clip_editor.cc:88`). Headless, both polls return False (probe on 5.2.2). This is a textbook L-004 case: the poll encodes where the button lives, not what the solver needs. A live `temp_override` onto a Clip Editor area is the expected workaround, but it is **unverified**.
  - **Roto and masks** are drawn by hand. Mask splines can be written as data, but placing them on a moving actor is the L-009 placement problem.
  - **Scripted calls push no undo** (L-008), so a wrong scatter tweak on a 700-shot-scale set can't be stepped back cleanly. Snapshots must be saved explicitly.
  - **Status, not result** (L-003): after a scatter there is no diff of instances created. The agent has to re-count them.
- **Not feasible today:**
  - Production plates, LiDAR and on-set HDRIs from the film. There are none, so substitutes are used.
  - Plate-accurate roto of actors at feature quality without a human or an external segmentation model.
  - The fireworks and Max-rendered shots, which are outside Blender in the original as well.

## 5. Verification plan (RFC 0001 R6, six layers)

Written for the first slice (6 s at 24 fps, 1920×1080).

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Environment meshes: manifold, no loose verts, no degenerate faces, outward normals (the reusable `chair_checks.py` pattern) | 0 failures |
| 1 Validity | Every frame renders without NaN/Inf pixels in any pass | 0 bad pixels across 144 frames |
| 2 Spec | Tree instances in the camera frustum | 400–1,500 |
| 2 Spec | Crowd proxies: count, and minimum pairwise distance | 150–250; ≥ 0.6 m, so nobody intersects |
| 2 Spec | Muzzle flashes: lit frames per flash, and flashes per second across the shot | 1–2 frames each; 3–8 per s |
| 2 Spec | Volume density near the camera vs. far away (mean mist-pass value, fore vs. back third) | back ≥ 2× front |
| 2 Spec | Render budget | ≤ 60 s per frame at 128 samples with denoise on this Mac |
| 3 Reference | Re-run from the same script and seed: per-pixel difference against the first render | max abs difference ≤ 1/255 on beauty (deterministic run) |
| 3 Reference | Plate shot (stretch goal): solve error | Blender solve average error ≤ 0.3 px |
| 4 Downstream | Comp readiness: required passes exist (beauty, shadow catcher, mist, cryptomatte object) and the CG over the backplate leaves no alpha holes | all 4 passes present; 0 px with 0 < α < 1 outside volume/foliage edges |
| 4 Downstream | Camera-match sanity: the HDRI horizon line and the CG ground plane horizon | ≤ 2 px apart at 1080p |
| 5 Appearance (warning) | Vision model compares the final frame against a brief ("dense jungle, dusk, gunfire haze, silhouetted soldiers") plus three film-still references | flag if fewer than 4 of 5 rubric items |
| 6 Taste (owner) | Does it read as a war-film establisher? Is the haze too clean, the crowd too uniform? | owner yes/no plus notes |

## 6. Where the human is still needed

- **Plate judgement.** Whether CG grain, black levels, defocus and haze *sit in* a specific plate. Machine metrics such as histogram matching only get you part of the way. A VFX supervisor's eye is the real gate on a feature.
- **Roto and paint-outs** on actors, and any shot where the CG has to interact with a performer.
- **Composition and storytelling** of establishers: where the eye goes and how the shot cuts with its neighbours.
- **The sun-direction and lens guesses** on a tracked plate. The agent can propose them, but a human confirms.
- **Client notes loops.** A large share of real VFX hours is revision rounds with the director.

## 7. Effort

- **First slice (live demo, ~1 day):** in the owner's live Blender window, through `tools/live/bl.py`:
  1. A ground plane, then a forest appearing as the GN scatter recipe is declared: the instance count goes from 0 to about 1,000 trees, with randomised scale and rotation.
  2. A column of low-poly soldier silhouettes scattered along a path.
  3. A grey-blue volumetric haze that thickens with depth, and orange flashes popping on and off as the timeline scrubs.
  4. The camera view rendered in Cycles: the CG forest sitting on a Poly Haven dusk HDRI backplate, then the comp tree adding haze, lens distortion and grain.
  5. `snap.py` screenshots after each step, and a check report in the style of demo 001 (section 5 thresholds).
- **Full reproduction (a 10-shot sequence with tracked plates):**
  - **Agent:** about 80–150 hours, mostly iteration on scatter and look.
  - **Compute:** about 20–60 GPU-hours of Cycles (10 shots × ~150 frames at 1080p; volumes dominate).
  - **Human:** about 20–40 hours of supervision (plate choices, lighting sign-off, roto).
  - **Full scale:** 700 shots at feature 2K/4K is a studio-year. Agents would compress the layout and scatter work, not the review loop.

## 8. Risks and unknowns

- **Live tracking override.** Whether a `temp_override` onto a Clip Editor actually lets the solver run is untested. If it fails, tracking falls back to a human in the GUI or to an external solver.
- **Volumes are slow and noisy.** The render budget could blow up; reducing step size and sample count is a trade-off against quality.
- **Determinism.** Cycles with OptiX or Metal denoise may not be bit-identical across runs, so the layer-3 threshold may need relaxing to a perceptual metric (for example SSIM ≥ 0.995).
- **Source thinness.** The user story is short. Shot-level breakdowns, the comp tool and the tracking tool are not documented, so section 2 stays deliberately narrow.
- **Licences.** The Tears of Steel plates are CC-BY 3.0 and need attribution. Poly Haven is CC0.

## 9. Sources

- [blender.org: Visual Effects for the Indian blockbuster "RRR"](https://www.blender.org/user-stories/visual-effects-for-the-indian-blockbuster-rrr/) (fetched 2026-10-07: 700 shots, Blender 2.83→2.92, sequences, GN foliage, volumetrics, Cycles for Max, Nov 2019 switch)
- [Tears of Steel footage at media.xiph.org](https://media.xiph.org/tearsofsteel/) (directory listing fetched: `raw/`, `linear-exr/`)
- Local source: `blender/source/blender/editors/space_clip/clip_editor.cc:88` (`ED_space_clip_tracking_poll`), and `tracking_ops_solve.cc:282,323`
- Local probe: headless Blender 5.2.2 `--factory-startup`; `bpy.ops.clip.solve_camera.poll()` and `track_markers.poll()` return False; `MovieTrackingTracks.new` and `MovieTrackingMarkers.insert_frame` are present
- [`docs/discovery/ledger.md`](../discovery/ledger.md) L-003, L-004, L-006, L-008, L-009; [RFC 0001 R6](../rfc/0001-newblender.md)
- Bridge evidence: `tools/live/bl.py`, `tools/live/snap.py`, `~/newblender-data/demos/001-chair/report.md`
