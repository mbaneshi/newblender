# 14 — The Junk Shop (Blender 2.81 splash): how an agent could make it

| | |
|---|---|
| **Original** | Alex Treviño (concept by Anaïs Maamar), 2019, stylised interior environment, Blender 2.81 splash · [BlenderNation](https://www.blendernation.com/2019/11/20/this-is-the-2-81-splash/) · [blender.org demo files](https://www.blender.org/download/demo-files/) |
| **Agent-readiness today** | **Taste-bound**: every mechanic (props as data, declared modifiers, set dressing by raycast, Cycles lighting) works through the live bridge today. What made this scene a landmark is a concept artist's design, hundreds of hand-shaped stylised props with personality, painted texture wear and a lighting mood. Those are judgement, and hand texture painting is also stroke-based (L-009). |
| **Difficulty** | 4 (a solo artist's months-long piece; an agent can block it in days, but closing the gap to the original's charm is the long tail) |
| **First slice** | A shop corner: a 2 m shelf unit and a counter built as data, filled with about 40 props from 6 parametric prop recipes (crates, jars, bottles, book stacks, a clock, a lamp) dropped onto their shelves by raycast, Poly Haven CC0 materials, a warm practical lamp against a cool window, rendered in Cycles. |

## 1. What the original actually is

- **One still image** (the 2.81 splash) and **one public `.blend`**: blender.org's demo-files page lists "Blender 2.81 – The Junk Shop", Alex Treviño, original concept by Anaïs Maamar (verified 2026-10-07; this settles the index's *unverified* concept credit).
- **Content (from the image, interpretation):** one interior room seen from a single camera; a counter, shelves and floor piled with props (radios, lamps, frames, boxes, bottles, a bicycle-scale piece of machinery), warm interior practicals, light from a window, stylised proportions and painted wear.
- **Afterlife:** a standard benchmark scene. Phoronix's `pts/blender` test added the Junkshop scene in version 4.1.0 (March 2024) and it is one of its most-run scenes (verified via search); it is believed to be one of the Blender Open Data benchmark scenes (*unverified*). It has also been ported to other renderers (e.g. a Guerilla Render version), which says the file is treated as a reference scene.

## 2. How the humans made it

Stages: **S01 Modeling, S02 UV & texturing, S03 Shading, S06 Layout, S09 Lighting & rendering.**

- **Fact (index, BlenderNation):** solo artist; prop modelling, UV and texture work, layout and set dressing, Cycles lighting. The article itself gives no process detail; the artist's [Blender Artists thread](https://blenderartists.org/t/the-junk-shop/1121171) is where process notes would be (not fetched).
- **Interpretation (typical for this kind of scene):** each prop is box-modelled with Subdivision and Bevel, shapes exaggerated for style; textures mix procedural grime with painted masks; set dressing is by hand in the viewport, prop by prop, judged through the camera; lighting is a small number of warm practicals plus a cool key, tuned by eye.
- **Interpretation:** the S01 census pattern holds here too: a low-poly cage plus live modifiers is the dominant authored artefact (91% of asset meshes carry modifiers; Subdivision 54% of all modifiers; median mesh 111 vertices; `docs/discovery/s01-modeling/02-census.md`).

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free sources) | Tooling |
|---|---|---|---|
| S01 Room and furniture | Walls, floor, shelf unit, counter as bmesh data with real dimensions; Bevel and Subdivision declared, not applied (chair-demo method) | Real furniture dimensions | `tools/live/bl.py`, `bmesh` → Mesh |
| S01 Props | ~6–10 parametric prop recipes as GN groups or Python builders (crate, jar, bottle via revolve, book stack, clock, lamp, radio box); each prop a seed + parameters, stored in a JSON prop manifest | None | GN; data builders |
| S01 Props (hero) | Imported CC0 models where a recipe would be poor (old radio, tools, chairs) | [Poly Haven models](https://polyhaven.com/models) (CC0), [Kenney](https://kenney.nl) (CC0, stylised low-poly) | glTF import |
| S02 UVs | Recipes emit UVs as data (the chair demo learnt that `calc_uvs` needs an existing layer); imported assets keep theirs | None | bmesh |
| S03 Shading | Library materials: worn wood, rusty metal, glass, cardboard, plus a GN-written `wear` attribute (edge curvature, height) feeding a dirt mix | [Poly Haven textures](https://polyhaven.com/textures), [ambientCG](https://ambientcg.com) (CC0) | Shader Attribute, Geometry > Pointiness in Cycles |
| S06 Set dressing | Placement as data (L-009): for each manifest entry, raycast down onto a declared support surface, random yaw within limits, reject on BVH overlap; "clutter density" per shelf as an input | None | `mathutils.bvhtree` |
| S09 Lighting | One cool area light at the window, 2–3 warm point/area practicals inside lamp props, low world fill; camera from the concept (owner gives framing) | Optional Poly Haven HDRI (CC0) seen through the window | Cycles, fixed seed |

**Build order:**

1. Owner supplies or approves a framing and a mood reference (the 2.81 splash itself is the obvious one).
2. Write checks (§5).
3. Room shell and furniture as data; camera locked to the framing.
4. Prop recipes one by one; contact sheet of seeds for owner review.
5. Prop manifest (counts per shelf), then raycast set dressing; overlap and floating checks.
6. Materials and wear attribute.
7. Lighting pass; test renders at 25%; owner review; full render.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Geometry as data with declared modifiers, validity and spec checks: proven by demo 001 (12/12 checks, `~/newblender-data/demos/001-chair/report.md`).
  - Raycast and BVH overlap tests for placement; reading evaluated geometry.
  - Importing glTF/FBX assets; assigning library materials; Cycles render to file; viewport screenshots for the owner.
- **Painful today:**
  - Set dressing in stock Blender assumes a mouse: drag, snap, rotate in the viewport. Placement has to be re-expressed as data (L-009), which we do in our own code; the editor gives no "place on surface" function with explicit inputs (L-004: snapping reads hidden tool settings).
  - Hand texture painting is a brush stroke stream with no data form (L-009); we substitute procedural wear masks, which look procedural.
  - Iterative look tweaks from Python push no undo (L-008); the owner cannot step back through agent changes.
  - No machine-readable result for a placement batch (what moved, what collided): our checker reconstructs it (L-003).
- **Not feasible today:**
  - Props with the original's stylised character (exaggerated bends, hand-sculpted dents) from recipes alone. Recipes give tidy, plausible props; charm needs either a human pass or an image-to-3D model whose output we would then have to clean.
  - Painted texture storytelling (labels, stickers, specific scuffs) at the original's density.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | All meshes clean after modifiers | 0 non-manifold edges (closed props), 0 degenerate faces, 0 loose verts, normals outward |
| 1 Validity | Every texture path resolves | 0 missing images |
| 2 Spec | Prop count and spread | ≥ 40 props in the slice; every declared shelf holds its manifest count ± 1 |
| 2 Spec | Physical set dressing | Every prop's lowest point within 2 mm of its support; 0 pairwise BVH overlaps |
| 2 Spec | Hygiene | Scale applied (1.0) on all objects; Studio naming `GEO-<prop>_<n>`; UVs on every mesh; material on every face |
| 2 Spec | Budget | Slice < 1.5 M faces; 1920 × 1080 Cycles render < 15 min on the owner's GPU |
| 3 Reference | Statistical comparison with the public Junk Shop `.blend` (fetch later from blender.org demo files; not downloaded now): props per visible m², light count, materials count, faces per prop, camera focal length | Report deltas; gate only on light count within ±2 and focal length within ±10 mm of the reference |
| 4 Downstream | Render health | 0 NaN; fireflies < 0.01% pixels > 20× local median; noise after denoise: SSIM vs a 4× sample render ≥ 0.97 |
| 4 Downstream | Scene opens headless and renders with the same result | Headless vs live render PSNR ≥ 45 dB |
| 5 Appearance (warning) | Vision model compares the render with the 2.81 splash on "cluttered, warm, cosy junk shop" and lists missing prop categories | Warn below 6/10 |
| 6 Taste (owner) | Owner judges charm, clutter rhythm and light mood | Sign-off; notes become manifest and light parameter changes |

## 6. Where the human is still needed

- **The concept.** The original had a concept artist before a 3D artist; someone must decide what this shop is, who owns it, what story the clutter tells.
- **Prop personality.** Exaggeration, asymmetry and wear that read as "loved objects" are a modeller's touch; the agent's recipes are the blocking pass.
- **Composition through clutter.** Leading lines and quiet zones in a busy frame are placed with intent; random-with-limits fills space evenly, which reads as noise.
- **Light mood.** The balance of warm practicals against cool daylight is tuned by eye, usually over many small iterations.

## 7. Effort

- **First slice (live demo, ~1 day):** in the owner's Blender window, an empty room becomes a wall corner with a wooden shelf unit and a counter. Then shelves fill: jars, bottles, crates, book stacks, a clock and a lamp drop into place one shelf at a time, each resting on its board, none overlapping. Changing a shelf's `density` input re-dresses that shelf. The viewport switches to rendered mode: warm lamp glow on the counter, cool window light on the back wall. A Cycles still and a check report (counts, contact, overlaps, hygiene) land in `~/newblender-data/demos/`.
- **Full reproduction:** 80–150 agent-hours for room, 30+ prop recipes, set dressing and checks; 1–3 GPU-hours of final renders; 40–100 human-hours of concept, prop polish and lighting direction to approach the original's quality.

## 8. Risks and unknowns

- Recipe props may look generic; the gap to the original could be mostly in the long tail of hand detail.
- The demo-files link goes to the old Blender Cloud gallery; the file may now be hosted on Blender Studio. Licence of the `.blend` is not stated on the listing (check before reuse).
- Vision-model scoring of "cosy" is unreliable (R6 layer 5 is a warning only).
- Image-to-3D models could raise prop quality but bring licence and topology questions (L-010 QA gates would catch topology, not licence).

## 9. Sources

- [BlenderNation: this is the 2.81 splash](https://www.blendernation.com/2019/11/20/this-is-the-2-81-splash/) (verified, fetched 2026-10-07)
- [blender.org demo files](https://www.blender.org/download/demo-files/): "Blender 2.81 – The Junk Shop", Alex Treviño, concept Anaïs Maamar (verified listing, 2026-10-07)
- [OpenBenchmarking pts/blender](https://openbenchmarking.org/test/pts/blender): Junkshop scene added in test version 4.1.0 (verified via search)
- [Blender Artists thread: The Junk Shop](https://blenderartists.org/t/the-junk-shop/1121171) (unverified, linked from BlenderNation)
- [Blender 2.81 manual: splash screen](https://docs.blender.org/manual/en/2.81/interface/splash.html) (from index)
- CC0 inputs: [Poly Haven](https://polyhaven.com), [ambientCG](https://ambientcg.com), [Kenney](https://kenney.nl)
- [Ledger L-003, L-004, L-008, L-009, L-010](../discovery/ledger.md); [S01 census](../discovery/s01-modeling/02-census.md); [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: [`tools/live/bl.py`](../../tools/live/bl.py), [`tools/live/demos/chair_build.py`](../../tools/live/demos/chair_build.py), [`tools/live/checks/chair_checks.py`](../../tools/live/checks/chair_checks.py)
