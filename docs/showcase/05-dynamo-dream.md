# 05 — Dynamo Dream: how an agent could make it

| | |
|---|---|
| **Original** | Ian Hubert (with help from friends), 2021 onward, indie live-action and CG sci-fi VFX series · [BlenderNation, 2021-05-26](https://www.blendernation.com/2021/05/26/first-episode-of-ian-huberts-dynamo-dream-is-out/) |
| **Agent-readiness today** | **Partial.** Kitbash city-building, photo-projected texturing, fog and lighting, compositor keying graphs and render orchestration are scriptable today. Camera tracking runs through Clip Editor operators that need a GUI context, and the live-action half (actors, shooting, performance, the edit) is human. |
| **Difficulty** | 4 (one shot is a 1–2 day job; a 22-minute episode took a dedicated solo artist about 3 years) |
| **First slice** | One locked-off cyberpunk street shot: a kitbashed block of buildings made from declared Array, Boolean and Bevel stacks, dressed with photo textures by camera projection (UV Project modifier), neon signs, wet street and volumetric fog, with a keyed green-screen actor plate composited into the street in Blender's compositor. |

## 1. What the original actually is

- **Series:** a live-action sci-fi series set in a dense, gently absurd cyberpunk city.
- **Episodes:**
  - Episode 1, "Salad Mug" (26 May 2021, YouTube), runs about 22 minutes ([TheTVDB, via search](https://thetvdb.com/series/dynamo-dream/episodes/8452700)).
  - Later episodes: "A Single Point in Space", "A Pete Episode", "Prepare for Execution" ([index](00-index.md) §05).
- **Deliverables per episode:**
  - Tens of minutes of footage of actors shot on a tiny budget, mostly against green screen or in partial practical sets.
  - Nearly every environment is CG built in Blender: streets, interiors, vehicles, skylines.
  - Compositing and the edit were also done in Blender ([index](00-index.md) §05).
- **Time:** "basically everything I've posted over the past 3 years has been for this first episode" ([BlenderNation](https://www.blendernation.com/2021/05/26/first-episode-of-ian-huberts-dynamo-dream-is-out/), verified).
- **Context:** Ian Hubert previously directed the Blender open movie *Tears of Steel* (same source), and is widely known for 1-minute "lazy tutorials" (*unverified as a source here*).

## 2. How the humans made it

**Facts (index and BlenderNation):**

- **Stages:** S01, S02, S03, S06, S08, S09, S10, S11.
- **Techniques:** rapid kitbash modelling, photo-projected textures, camera tracking, green-screen keying and compositing in Blender, Cycles, and editing.
- **Scale:** essentially solo, about 3 years for episode 1.

**Interpretation:** Hubert's method is **cheap geometry, expensive-looking images**.

- **Geometry:** boxes and kitbash parts, rarely modelled in detail.
- **Detail:** comes from photographs projected from the camera onto that crude geometry, from fog and from light.
- **Why it works:** the camera only sees one side, and live action anchors belief.
- **Fit for an agent:** this is a strong fit. Most decisions are rule-like (scale the building, project a photo, add fog, match the plate's light direction). The "lazy" shortcuts are exactly the kind of compression an agent can apply consistently across hundreds of shots.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs | Tooling |
|---|---|---|---|
| S01 Modeling | City blocks as data: building masses from a GN "lot" recipe (footprint, floors, set-backs), plus kitbash parts (AC units, pipes, signs, balconies) instanced by rule on facades. Hero props as declared modifier stacks. | CC0 kitbash parts (Poly Haven models; Blender demo files) | GN, bmesh-as-data, L-006 |
| S02 UV & texturing | **Camera projection as a declared modifier:** UV Project from the shot camera onto facades, with the photo as the image. Off-camera faces get tiled CC0 materials. | Poly Haven CC0 textures and HDRIs; the owner's own photos of real buildings | UV Project modifier by script |
| S03 Shading | Emissive neon from SVG text converted to curves; wet asphalt (low roughness plus a puddle mask); window-light randomisation per instance. | Free fonts (OFL) | Shader nodes, Text objects |
| S06 Layout | The camera is matched to the plate: focal length, sensor and height from the shoot notes. For a locked-off shot, a solved camera is not needed. | Plate metadata | Camera as data |
| S08 Simulation & FX | Steam vents (Mantaflow or a GN volume), rain streaks (GN particles), holographic flicker (driver noise). | — | GN, `-b` bakes |
| S09 Lighting & rendering | Match the plate: sun or key direction estimated from the plate (manual input at first), volumetric fog, neon as area lights. View-layer passes for the composite. | HDRI from Poly Haven | Headless Cycles |
| S10 Compositing | A declared node graph: Keying node on the plate, despill, edge erode/blur, light-wrap from the CG, colour match (lift/gamma/gain to the CG histogram), fog depth pass, grain. | Green-screen plate (see below) | Compositor by script |
| S10 Tracking (moving shots) | `clip.detect_features`, `track_markers`, `solve_camera`, scripted under `temp_override` with a Clip Editor area; check the solve error. | Moving plate | Clip Editor ops (L-004) |
| S11 Editing | Assemble the episode in the VSE from an EDL and the rendered shots; the agent conforms, but does not cut creatively. | Edit decisions (human) | VSE by script |

**Plate source for the first slice:** *Tears of Steel* (2012, CC-BY, directed by Ian Hubert) released its green-screen footage. Exact availability and URL are *unverified*. If it can't be fetched, the owner films a 5-second locked-off phone clip in front of any evenly lit green or blue sheet.

**Build order (for the first slice):**

1. Write the checks first (section 5).
2. Load the plate as a movie clip. Read its resolution, frame rate and length. Create a camera matching a 26 mm-equivalent phone lens (or the plate metadata).
3. GN street: two facades of 5–8 buildings each, 12–40 m tall, along a 60 m street, with a perspective vanishing point near frame centre.
4. Kitbash dressing on the facades by rule: AC units on 30% of windows, signs every 6–10 m, cables between buildings.
5. Camera-project 2–4 CC0 photos onto the front facades with UV Project from the shot camera. Off-camera faces get tiled materials.
6. Neon text signs, a wet-street shader, volumetric fog with density falling off with height, and rain particles.
7. Render CG passes (combined, mist/depth, emission) headless in Cycles.
8. Compositor: key the plate, despill, light-wrap, colour-match it to the CG, and merge over the street with a fog-depth blend. Write 1080p PNG frames and an MP4 preview.
9. Show progress in the window with `snap.py` at each step.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - GN city recipes and instanced kitbash.
  - The UV Project modifier from a camera.
  - Text and curve neon, volumes and Cycles passes.
  - The compositor graph built by script, and VSE strips by script.
  - Loading a movie clip as data (`bpy.data.movieclips.load`).
- **Painful today:**
  - **Camera tracking** is Clip Editor operator-shaped: detect, track, solve and set-up-scene all poll for a Clip Editor area and read its current clip and frame from context (L-004). The solve returns a status. The reprojection error must be read back from the tracking object afterwards (L-003).
  - **Manual track clean-up** (deleting bad tracks, placing markers by hand) is a mouse act with no data API for "place a marker on that corner" (L-009).
  - **Choosing which photo to project where** is a placement decision that Hubert makes by eye. As data, it becomes "projector camera plus image plus target faces" (L-002: explicit element sets, not selection).
  - **Previews** need the live window; headless renders need a separate session (L-011).
- **Not feasible today:**
  - Writing, casting, acting and shooting the live action.
  - Hubert's humour and tone.
  - Creative editing: rhythm, comedic beats.
  - Estimating plate lighting fully automatically to VFX-supervisor quality.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Building and kitbash meshes evaluated: non-manifold edges, flipped normals, degenerate faces | 0 / 0 / 0 |
| 1 Validity | Plate loads: frames readable, frame rate matches the scene | 100% of frames / exact |
| 2 Spec | Street length / building count / height range | 60 m ± 5% / 10–16 / 12–40 m |
| 2 Spec | Facade faces visible to the camera that have projected (not tiled) texture | ≥ 70% of visible facade area |
| 2 Spec | Projection stretch: on projected faces, angle between the face normal and the camera ray | ≤ 70° for 90% of the area |
| 2 Spec | Neon signs in frame / fog density at street level vs. 30 m up | ≥ 5 / ≥ 3:1 |
| 2 Spec | Output: 1920 × 1080, plate frame rate, frame count equals plate length | exact |
| 3 Reference | Rebuild from the recipe in a fresh session: identical instance transforms and node graph JSON | identical |
| 3 Reference | (Moving plates only) camera solve average reprojection error | ≤ 0.5 px |
| 4 Downstream | Key quality: residual green in matte-interior pixels (G > max(R, B) + 0.05) | ≤ 0.5% of foreground pixels |
| 4 Downstream | Matte edge: alpha in 0.05–0.95 confined to a band ≤ 4 px around the silhouette | ≥ 95% of soft-alpha pixels |
| 4 Downstream | Colour match: mean luminance of the actor vs. the nearby CG background | ratio 0.6–1.6 |
| 4 Downstream | Cycles render time per frame at 1080p | ≤ 3 min |
| 5 Appearance (warning) | Vision model: "a person standing in a cyberpunk street, not pasted on", plus a side-by-side with a Dynamo Dream still | warning if under 3/5 |
| 6 Taste (owner) | Does it have Hubert's charm: dense, lived-in, funny? | owner's call |

## 6. Where the human is still needed

- **The live-action half:** writing, actors, wardrobe, shooting the plates (the lighting on set decides most of the composite's fate).
- **Tone:** the deadpan, whimsical world-building (salad mugs, odd signage) is authorship, not procedure.
- **Plate-light judgement** at hero quality: the agent can match statistics, but a VFX eye decides "it sits".
- **The edit:** pacing and comedic timing across a 22-minute episode.
- **Hero-shot tracking clean-up** when automatic tracks fail (motion blur, low texture).

## 7. Effort

- **First slice (live demo, about 1 day):**
  - **On screen:** the owner's window first shows the plate as a camera background, an actor on green.
  - Two rows of grey box buildings rise along a street receding to the horizon. AC units, pipes, cables and signs then snap onto the facades.
  - When the photo projection turns on, the boxes suddenly look like real, grimy buildings from the camera's view (and visibly smeared from any other angle, which is the trick).
  - Neon signs glow pink and cyan, fog thickens near the ground, and rain streaks appear.
  - Finally the compositor output shows the actor standing in the street, keyed, colour-matched and fogged, plus a short MP4 and the check report.
- **Full reproduction:**
  - **Agent work, per 22-minute episode:** about 150–250 CG shots. At about 2–4 agent-hours per shot (layout, projection, lighting, composite set-up, checks), that is about 400–900 agent-hours.
  - **Render compute:** 32,000 frames × ~2 min ≈ 1,000 GPU-hours.
  - **Human work:** shooting days, the actors, about 100–200 hours of direction and composite approval, and the edit. This would turn about 3 years of solo work into a few months of human-led production.

## 8. Risks and unknowns

- **Tears of Steel plate availability and format are unverified.** The fallback is an owner-shot clip.
- **Scripted camera tracking** under `temp_override` has not been probed in 5.2.2. It is the main technical unknown for moving shots.
- **The keyer** depends on plate quality. Uneven green with motion blur will fail layer 4 regardless of the agent.
- Episode runtime comes from a TV-database snippet. Hubert's exact techniques per shot are inferred from his public tutorials, not documented production notes.

## 9. Sources

- [BlenderNation: first episode of Ian Hubert's Dynamo Dream is out](https://www.blendernation.com/2021/05/26/first-episode-of-ian-huberts-dynamo-dream-is-out/) (verified, fetched 2026-10-07: 3 years, solo, Tears of Steel director)
- [TheTVDB: Dynamo Dream — Salad Mug](https://thetvdb.com/series/dynamo-dream/episodes/8452700) (search snippet: 22 minutes, 26 May 2021; page not fetched)
- [Core77: cityscape VFX split-screen](https://core77.com/posts/100290/A-Bad-Ass-Food-Truck-and-a-Cyberpunk-City-VFX-Split-Screen-Sequence) (unverified, per index)
- [Poly Haven](https://polyhaven.com/) (CC0 textures, HDRIs, models)
- [`00-index.md`](00-index.md) §05; [ledger](../discovery/ledger.md) L-002, L-003, L-004, L-006, L-009, L-011; [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`, `tools/live/demos/chair_build.py`
