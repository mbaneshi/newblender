# 01 — Flow: how an agent could make it

| | |
|---|---|
| **Original** | Gints Zilbalodis / Dream Well Studio with Belgian and French co-producers, 2024, feature film (Oscar for Best Animated Feature, 2025) · [blender.org user story](https://www.blender.org/user-stories/making-flow-an-interview-with-director-gints-zilbalodis/) |
| **Agent-readiness today** | **Partial.** Environments, water set-up, layout cameras, EEVEE lighting and render orchestration are scriptable through the live bridge today. Animal performance, the long-take camera choreography and the story are human work. |
| **Difficulty** | 5 (the original took 5.5 years. Even with an agent doing the environment and render work, an 84-minute feature is a studio-year project.) |
| **First slice** | One 10-second flooded-forest shot: a terrain with GN-scattered trees, an Ocean-modifier flood plane, a proxy sailboat bobbing on the waves, and a handheld-feeling camera made from declared noise, rendered in EEVEE at 4K and timed per frame. |

## 1. What the original actually is

- **Film:** 84 minutes, with no dialogue ([Gateway Film Center listing](https://gatewayfilmcenter.org/movies/flow-2024/)).
- **Characters:** five animal leads (a cat, a capybara, a lemur, a secretary bird and a dog) plus herds and flocks.
- **Environments:** a flooded forest, ruined stone cities, open sea, and fields. Flood water is in almost every scene.
- **Shots:** the count is not published. The film is known for long, continuous, handheld-style takes rather than fast cutting.
- **Output:** 4K frames rendered in EEVEE on the director's own PC, with no compositing pass ([user story](https://www.blender.org/user-stories/making-flow-an-interview-with-director-gints-zilbalodis/)).
- **Data size:** scene files of about 300 MB compressed for small scenes and about 2 GB for the largest (same source).

## 2. How the humans made it

**Facts (from the user story, verified):**

- **Team:** about 15–20 people in total, but usually only 3–5 working at any one time, over 5.5 years (2019–2024). Belgian and French teams joined in 2022 for character animation.
- **Blender versions:** started on the 2.8 alpha/beta, moved through 2.9, 3.0 and 3.3 (animators), and finished lighting on 3.6.
- **S09 Lighting & rendering:** EEVEE only, at about 0.5–10 s per 4K frame on one PC. There was no compositing; "all the colors were tweaked and adjusted using shaders".
- **S08 Simulation:** two people did all the water. They combined Cell Fluids for large waves with FLIP Fluids for detail, plus a custom water add-on by Mārtiņš Upītis.
- **S04 / S06 Environments and layout:** GeoScatter for plant distribution, plus the Bagapie Vegetation and Rain generators. The director made previz, a concept artist refined it, and then 3D assets were built into it.
- **S07 Animation:** handheld, shaky camera moves were layered with the Animation Layers add-on. No motion capture is mentioned.
- **S02 Texturing:** shader-led rather than a painted-texture pipeline.

**Interpretation:** Flow's look is *shader-graded EEVEE plus procedural scatter plus simulated water*. These three parts are the most declarative parts of any feature pipeline, which is why a tiny team could finish it. The non-declarative parts are the animal acting and the director's camera, and those are what made the film work.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs | Tooling |
|---|---|---|---|
| S01 Modeling | Terrain as a GN recipe (grid, then noise displacement, then erosion-like terraces). Ruins as kitbash from a small library of declared parts: Array, Mirror, Bevel and Boolean modifiers on low cages (as in the chair demo). | Poly Haven CC0 rock and bark scans; Blender demo files | `bl.py`, bmesh-as-data, declared modifiers (L-006) |
| S04 Geometry Nodes | Scatter trees, bushes and grass by slope, height above the water line and a density map, with Poisson-disk spacing. Each rule is a named input. | Poly Haven CC0 tree and plant models; or GN trees built procedurally | GN modifier built by script; parameters stored as JSON |
| S03 Shading | Painterly, graded shaders in the Flow style: a colour ramp on lighting, AO and height, so the grade lives in the shader as it did on the film. | None | Shader nodes by script |
| S08 Simulation | **Water in two tiers.** (a) Open flood: the built-in Ocean modifier with declared wave scale, choppiness and a time keyframe. (b) Contact splashes: a Mantaflow liquid domain baked headless for hero moments only. FLIP Fluids and Cell Fluids are paid add-ons, so I would treat them as optional. | None | Ocean modifier; `bpy.ops.fluid.bake_all` in `-b` |
| S05 Rigging | Import or reuse quadruped rigs, or generate them with Rigify meta-rigs. **Rigging quality checks only; no acting.** | CC0 or CC-BY animal rigs (e.g. Blender Studio cloud rigs); Rigify | Rigify by script |
| S06 Layout | Cameras as data: a spline path, focal length, focus distance, and a declared "handheld" layer (an F-curve Noise modifier on rotation, with amplitude in degrees and frequency in Hz) instead of hand-layered keys. | Director's previz or storyboard | F-curve modifiers by script |
| S07 Animation | **Human.** The agent can do floating debris, boat bob driven by the ocean surface (a GN sample of the ocean height onto the boat empty), and flock or herd cycles from GN or Boids. It does not do the cat. | Human animation | Drivers and GN |
| S09 Lighting & render | Sun plus sky world, volumetric haze, EEVEE settings, 4K output; frames distributed over local GPU time with resume. | None | Headless `blender -b -a` batches; per-frame timing log |

**Build order:**

1. Write the shot spec and the checks (section 5) as files before any geometry.
2. Run a clean slate, set metric units, and set the frame range to 240 frames at 24 fps.
3. Build the terrain GN recipe and check that its height range matches the spec.
4. Add the Ocean modifier flood plane and set the water level so that a declared fraction of the terrain is submerged.
5. Scatter vegetation only where the terrain is above the water line, and check that no instance origin is underwater.
6. Add the proxy boat and drive its Z and tilt from the sampled ocean surface.
7. Add the camera path, then layer declared noise on top.
8. Light the shot and render a viewport preview with `snap.py`, then make a layer-5 vision check against the reference frame.
9. Render final EEVEE 4K frames headless, logging the seconds per frame.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Building GN trees and modifiers by script.
  - Ocean modifier parameters and keyframes.
  - Camera F-curve Noise modifiers.
  - EEVEE settings and headless animation renders.
  - Measuring evaluated geometry through `evaluated_get` (the chair checks already do this).
- **Painful today:**
  - **Mantaflow baking is operator-only.** It runs through `bpy.ops.fluid.*`, which has context polls (L-004), and returns a status rather than what it baked (L-003). I have to reopen the cache to see if the bake worked.
  - **Scatter "by eye" has no data-first API.** GeoScatter-style painting of density is a brush stroke (L-009), so I would replace it with a declared density field.
  - **Python edits leave no undo history** (L-008). A bad scatter cannot be stepped back; it has to be rebuilt from the recipe. That is fine *because* the recipe is the artefact (L-006).
  - **Viewport framing and screenshots need `temp_override` on a real window** (L-004, L-011). This is already worked around in `chair_build.py` and `snap.py`.
- **Not feasible today:**
  - Believable animal acting (the cat's ear flicks, hesitation and fear).
  - The director's long-take camera choreography as *storytelling*.
  - The paid add-ons the film relied on (Cell Fluids, FLIP Fluids, GeoScatter, Animation Layers) are not installed here. Their effects have to be approximated with built-ins.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Terrain and ruins evaluated mesh: non-manifold edges, degenerate faces, flipped normals | 0 / 0 / 0 |
| 1 Validity | Ocean bake: every frame of the range evaluates without error | 240 of 240 frames |
| 2 Spec | Fraction of the terrain area below the water line at frame 1 | 35–50% |
| 2 Spec | Vegetation instances whose origin is below the ocean surface (sampled) | 0 |
| 2 Spec | Instance count in the camera frustum (budget for EEVEE) | 2,000–20,000 |
| 2 Spec | Boat waterline: distance from the boat origin to the sampled ocean height, every frame | ≤ 5 cm |
| 2 Spec | Camera noise: rotation jitter RMS | 0.3–1.5° at 0.5–2 Hz |
| 2 Spec | Naming: `GEO-`, `ENV-`, `CAM-`, `LGT-` prefixes on every object | 100% |
| 3 Reference | Re-run the recipe from the same seed in a fresh headless session; compare the evaluated mesh hash and instance transforms | identical |
| 4 Downstream | EEVEE 4K render time per frame on this machine (the original's band) | median ≤ 10 s, max ≤ 20 s |
| 4 Downstream | Render artefacts: fully black or NaN pixels per frame | 0 |
| 4 Downstream | Temporal flicker: mean frame-to-frame luminance delta on static areas | < 2% |
| 5 Appearance (warning) | Vision model compares frame 120 to a Flow still: flooded forest, soft haze, painterly grade | warning if under 3/5 |
| 6 Taste (owner) | Does it feel like Flow: calm danger, scale, the handheld intimacy? | owner's call |

## 6. Where the human is still needed

- **Story and structure.** A wordless 84-minute film is carried entirely by the edit and staging choices.
- **Animal performance.** The film lives on the cat behaving like a real cat. Keyframe acting at that level is many animator-years. No agent today can judge whether a hesitation reads as fear.
- **Camera as character.** The long takes are direction, not just camera moves. The agent can execute a declared path, but the human chooses the path.
- **Art direction of the grade.** "Colour tweaked in shaders" means hundreds of small taste calls per sequence.
- **Water as performance.** Where a wave hits the boat is a story beat, not physics. The human places the beats; the agent makes the sim hit them.

## 7. Effort

- **First slice (live demo, about 1 day):**
  - **On screen:** in the owner's Blender window, a hilly terrain appears in steps, then a wide sea rises and floods the valleys. Trees then pop in only on the higher ground. A small grey sailboat sits on the water and rocks with the waves when the timeline plays.
  - A camera glides past the boat with a slight handheld wobble.
  - Material preview shows a soft, warm-graded look with haze.
  - At the end, a 4K EEVEE frame sequence of 240 frames renders headless, and a report lists the per-frame seconds and the section 5 checks.
- **Full reproduction:**
  - **Agent environment and render work:** about 400–800 agent-hours for the environments, water set-ups, layout passes and lighting across a feature.
  - **Render compute:** about 120,000 frames × ~5 s ≈ 170 GPU-hours for EEVEE, plus re-renders.
  - **Human work:** several animator-years for the characters, plus about 1,000+ hours of direction, layout approval and grading review. That is still a multi-year project, though it moves most of the non-performance labour.

## 8. Risks and unknowns

- **Ocean-modifier water is not Flow's water.** Breaking waves and boat wakes needed FLIP-class detail. Mantaflow at hero resolution may be too slow for a one-day slice.
- **EEVEE timing.** The 0.5–10 s figure came from 2.8–3.6 EEVEE Legacy. EEVEE Next in 5.2 has different costs (shadows, volumes), so the threshold may need recalibration.
- **Paid add-on dependency.** Matching the original's scatter density without GeoScatter is untested.
- **Vision-model scoring** of "painterly grade" is unreliable (R6 layer 5 is a warning only).
- **The studio name Dream Well Studio is unverified** in the index.

## 9. Sources

- [Making Flow — an interview with director Gints Zilbalodis, blender.org](https://www.blender.org/user-stories/making-flow-an-interview-with-director-gints-zilbalodis/) (verified, fetched 2026-10-07: team size, versions, EEVEE timings, water add-ons, Animation Layers, file sizes)
- [Gateway Film Center: Flow (2024)](https://gatewayfilmcenter.org/movies/flow-2024/) (verified via search: 84-minute runtime)
- [`docs/showcase/00-index.md`](00-index.md) §01
- [`docs/discovery/ledger.md`](../discovery/ledger.md): L-003, L-004, L-006, L-008, L-009, L-011
- [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge evidence: `tools/live/bl.py`, `tools/live/snap.py`, `tools/live/demos/chair_build.py`, `~/newblender-data/demos/001-chair/report.md` (12/12 checks)
