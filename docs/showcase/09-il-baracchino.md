# 09 — Il Baracchino: how an agent could make it

| | |
|---|---|
| **Original** | Megadrago (Palermo; creators and directors Nicolò Cuccì and Salvo Di Paola) with Lucky Red, 2025, an adult animated TV series for Prime Video · [blender.org user story](https://www.blender.org/user-stories/creating-il-baracchino-italys-first-adult-animated-series-made-with-blender/) |
| **Agent-readiness today** | **Partial.** The series' signature tricks are unusually agent-friendly because they are *rigs and data*, not hand drawing: UV Warp tile swaps for cut-outs, stepped keys with holds, a GN-built mouth, EEVEE, and VSE editorial. What needs tooling or a human: Rigify generation and fitting (operator- and context-driven), facial acting, comedy timing, and the art of the puppets. |
| **Difficulty** | **4.** Six episodes, about 100 minutes, made by about 20 people. A single 30-second scene is a credible stretch goal. |
| **First slice** | A 10-second, black-and-white "comedy club" beat: a box-headed cut-out puppet whose face swaps between 5 expression tiles through a UV Warp modifier, a rubber-hose arm on bendy bones, everything keyed stepped on twos/threes, rendered in EEVEE and cut into 3 shots in the VSE. |

## 1. What the original actually is

- **Series:** 6 episodes, about 100 minutes in total. Italy's first adult animated series made in Blender, premiered on Prime Video on 3 June 2025 and presented at Blender Conference 2025. It follows an art director trying to save a failing comedy club.
- **Look:** "primarily black and white", with **one episode in colour** (user story). The series mixes 3D, stop-motion-style puppetry, paper cut-outs and 2D.
- **Characters (named in the source):**
  - **Claudia** (protagonist): Rigify with bendy bones for rubber-hose arms, and shape keys plus bones for the face.
  - **Leonardo da Vinci:** "five texture tiles mapped onto simple box geometry", driven by UV Warp.
- **Output rate:** "40 seconds per week" at peak.
- **Team and stack:** about 20 people, Blender 3.6 LTS, EEVEE, the VSE for editorial, Kitsu (tasks), Flamenco (render management), SVN (versioning).

## 2. How the humans made it

| Stage | Fact (user story) | Interpretation |
|---|---|---|
| S04 GN | Mouth = "curve connected to bones, with the gradient achieved procedurally through geometry nodes" | The mouth shape is driven by bones, and its look is computed rather than painted per frame |
| S05 Rigging | UV Warp is "foundation for multiple characters, allowing us to create paper cutout-style animations"; Rigify plus bendy bones; shape keys combined with "traditional rigging" | Cut-out = swap texture regions instead of deforming geometry |
| S07 Animation | "stepped mode with holds" only, no spline animation; timing on "twos, threes, fours" | Fakes stop-motion cadence. Animators choose the step per action. |
| S12 GP | Grease Pencil for "3D previews with 2D animated characters" (previz) | GP as a sketching layer, not the final look |
| S09 | EEVEE NPR; layout set lighting intent before the stop-motion integration | Fast renders made 40 s/week feasible |
| S11 | Blender VSE for editing | Editorial stays inside Blender |

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S02/S03 | **Expression atlas generated as pixels:** a 5×1 image atlas (eyes and mouth drawn as filled ellipses and arcs) written via `image.pixels`, black ink on paper colour, plus a paper-grain noise. Or use human-drawn tiles if the owner supplies them. | CC0 paper textures (Poly Haven / ambientCG) | bridge |
| S05 cut-out | **UV Warp as the expression switch:** a box head with UVs covering one tile; `UVWarpModifier` offset U = tile_index / 5. An integer "expression" custom property drives the offset through a driver. | — | modifiers, drivers |
| S05 body | Armature as data. Arms as one bone each with `bbone_segments = 8` and ease in/out keyed, giving the rubber hose. Rigify: enable the add-on, build a meta-rig and generate (`pose.rigify_generate`; context needs are untested) for the full version only. | — | bridge |
| S04 mouth | A GN group: a 3-point curve whose middle point follows a bone (Object Info), Curve to Mesh with a profile, and a gradient attribute from curve parameter → material | — | GN |
| S07 | **Stepped animation as data:** keys written straight into F-curves with `interpolation = 'CONSTANT'`; holds chosen per action (2s for gags, 3–4s for settles); expression index keyed the same way | a beat sheet (dialogue timing) | bridge |
| S09 | EEVEE, Standard view transform; B/W via a desaturating grade (comp Hue/Sat at 0); a spotlight "comedy club" key with a hard shadow | — | EEVEE |
| S11 | **VSE as data:** `sequence_editor.strips.new_scene` or `new_movie` per shot, with cut points from the beat sheet; title card as a text strip | — | VSE API (`new_scene`, `new_movie`, `new_effect` present in 5.2.2) |

**Build order**

1. Write the beat sheet and assertions (section 5).
2. Generate the atlas, then the head with UV Warp and the expression driver.
3. Body armature with bendy-bone arms, then the GN mouth.
4. Keys from the beat sheet, stepped.
5. Three camera angles = three scenes or three cameras with markers.
6. Render the shots, assemble them in the VSE, render the edit.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - The `UVWarpModifier` type, image pixel writes, drivers.
  - F-curves with `CONSTANT` interpolation, bendy-bone properties.
  - GN curve groups, EEVEE.
  - VSE strip creation (`StripsTopLevel.new_scene` / `new_movie` / `new_effect`, confirmed on 5.2.2 headless).
  - Declared modifiers plus render plus screenshot, as proven by demo 001.
- **Painful today:**
  - **Rigify generation** is an operator that expects an active meta-rig in Pose mode. It is mode-gated (L-001) and context-gated (L-004). Fitting a meta-rig to a mesh is placement by eye (L-009). Rigify is not enabled in a factory boot (probed), which is another hidden-default trap (L-011).
  - **Hand-keyed stepped animation is fine as data**, but there is no "result" back. Verifying holds means re-reading F-curves (L-003).
  - **Scripted edits leave no undo** (L-008). When the owner says "make that gag hold one frame longer", the agent re-writes the keys instead of stepping back.
- **Not feasible today:**
  - Comic *performance*: acting choices, the take, the timing of a punchline.
  - Lip-sync to Italian dialogue at production quality without a phoneme-to-tile mapping. Feasible with an external aligner, but not built.
  - Puppet and character design in the show's style.

## 5. Verification plan (RFC 0001 R6, six layers)

For the first slice: 10 s at 24 fps, 3 shots.

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Head and body meshes: manifold, normals out, UVs present (demo 001 checks) | 0 failures |
| 1 Validity | Atlas: correct size and no transparent holes in tile regions | 5 tiles; α = 1 over ≥ 99% of tile pixels |
| 2 Spec | Every animated F-curve uses stepped keys | 100% of keyframes `CONSTANT` |
| 2 Spec | Hold lengths (frame gaps between consecutive keys on body channels) | every gap ∈ {2, 3, 4} frames, except deliberate holds ≥ 6 |
| 2 Spec | Expression swaps: the UV Warp offset only ever lands on a tile boundary | offset ∈ {0, 0.2, 0.4, 0.6, 0.8} ± 1e-6 at every frame |
| 2 Spec | Rubber-hose arm: bendy bones with no kinks | `bbone_segments` ≥ 6; max angle between adjacent segments ≤ 35° |
| 2 Spec | B/W | max per-pixel chroma (HSV saturation) ≤ 0.02 on all final frames |
| 2 Spec | Edit | exactly 3 strips; cuts at beat-sheet frames ± 0; total 240 frames |
| 3 Reference | Stepped motion actually reads as stepped: the frame-to-frame pixel difference is zero on hold frames | ≥ 90% of in-hold frame pairs have mean abs diff < 0.5/255 in the character mask |
| 4 Downstream | Animator-friendliness: one "expression" integer property drives the face; no keys sit directly on the modifier; the rig is posable with no errors at extreme arm poses | 1 control; 0 direct keys; bendy arm length change ≤ 5% at ±150° |
| 5 Appearance (warning) | Vision model: "reads as paper cut-out / stop-motion puppet, black and white comedy" | warn if below 3 of 5 |
| 6 Taste (owner) | Is the beat funny? Does the timing land? | owner |

## 6. Where the human is still needed

- **Comedy.** Timing a punchline, choosing when to hold. The tooling can enforce "on twos", but not "funny".
- **Puppet and tile design.** Five expressions that read instantly are a drawing skill. Procedural ellipses are placeholders.
- **Acting and lip-sync choices** for dialogue-driven scenes.
- **Direction across 6 episodes:** tone, the colour-episode decision, edit rhythm.

## 7. Effort

- **First slice (live demo, ~1 day):** on screen in the owner's Blender:
  1. A paper-textured box head appears on a stick-figure body with long noodle arms.
  2. The face changes instantly as the agent sets `expression = 0…4` (neutral, smug, shocked, sad, laughing) through the UV Warp tiles.
  3. Scrubbing the timeline, the puppet moves in stop-motion jerks, on twos for the gag and threes for the settle. The arm bends in a smooth rubber-hose curve.
  4. Rendered view goes black-and-white under a single spotlight.
  5. The VSE shows 3 strips cut on the beats, and a 10-second MP4 plays back with the check report.
- **Full reproduction (a 30 s scene):**
  - **Agent:** about 30–60 hours, including a Rigify-based character and a lip-sync mapping.
  - **Compute:** minutes per shot of EEVEE.
  - **Human:** 10–20 hours of direction, design and acting passes.
  - **The series:** 100 minutes at the original's 40 s/week peak with 20 people. Agents could absorb rig setup, stepped-key cleanup, render wrangling and conform, not authorship.

## 8. Risks and unknowns

- Whether `pose.rigify_generate` runs through the bridge without GUI context is untested.
- The source is a single user story. Episode-level breakdowns, the exact UV Warp setups and the GN mouth graph are not public, so the agent's versions are reconstructions.
- Stepped renders mask in-between errors that would show on spline playback. That is intended, but it can hide rig bugs.
- "Prime Video original" and the 3 June 2025 date come from the index (Wikipedia via search), not from the fetched user story.

## 9. Sources

- [blender.org: Creating "Il Baracchino"](https://www.blender.org/user-stories/creating-il-baracchino-italys-first-adult-animated-series-made-with-blender/) (fetched 2026-10-07: ~20 people, 6 eps / 100 min, 3.6 LTS, EEVEE, VSE, UV Warp, Leonardo's 5 tiles, Rigify + bendy bones, GN mouth, stepped twos/threes/fours, 40 s/week, Kitsu/Flamenco/SVN, GP previz, B/W with one colour episode)
- [Wikipedia: Il Baracchino](https://en.wikipedia.org/wiki/Il_Baracchino) (via the index, verified via search)
- Local probes (headless 5.2.2, factory startup): `UVWarpModifier` present; VSE `StripsTopLevel` has `new_scene`, `new_movie`, `new_effect`; Rigify not enabled by default
- [`docs/discovery/ledger.md`](../discovery/ledger.md) L-001, L-003, L-004, L-008, L-009, L-011; [RFC 0001 R6](../rfc/0001-newblender.md); bridge: `tools/live/bl.py`, `snap.py`, demo 001 report
