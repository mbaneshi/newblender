# 04 — Singularity: how an agent could make it

| | |
|---|---|
| **Original** | Blender Studio (dir. Andy Goralczyk, art director Vivien Lulkowski), 2026, open movie: painterly NPR in 4K HDR · [Digital Production, 2026-05-15](https://digitalproduction.com/2026/05/15/blender-singularity-lands-in-4k-hdr/) |
| **Agent-readiness today** | **Taste-bound.** The machinery is highly agent-friendly: the released shot shows the look is almost entirely Geometry Nodes groups (1,799 GN modifiers in one shot) and it is all scriptable. The hard part is the watercolour judgement: stroke size, colour bleed and what to leave unpainted. That is human taste and cannot be verified numerically. |
| **Difficulty** | 4 (a short film, but the look itself is a research project, and the production pushed Blender 5.x development) |
| **First slice** | A painterly ice-shard belt around a black hole: shards scattered in a volume by GN, covered in brush strokes from the **Blender Studio Brushstroke GN library shipped in the 4.2 Gold splash** (`assets/nodes/brush_stroke_generation.blend`), with a glowing curve trail left by a small critter, rendered in Cycles next to the real Singularity shot (the 5.1 splash file). |

## 1. What the original actually is

- **Film:** "a painterly space adventure set in a universe before the beginning of our time", and Blender Studio's first film in 4K HDR ([Singularity premiere](https://studio.blender.org/blog/singularity-premiere/), verified).
- **Delivery:** 4K HDR to ITU-R BT.2100, with an SDR version ([Digital Production](https://digitalproduction.com/2026/05/15/blender-singularity-lands-in-4k-hdr/), verified).
- **Runtime and shot count:** not published in the sources I fetched.
- **Released under CC-BY:** character models and rigs, texture packs, compositing assets and production shots (premiere post).

**Concrete evidence on this machine.** The Blender 5.1 splash file `~/newblender-data/downloads/blender-5.1-splash.blend` is a Singularity production shot. Its embedded paths point to `/data/singularity/svn/pro/shots/020_ice0030-lighting.blend` and Singularity asset maps. Census figures (`~/newblender-data/census/downloads__blender-5.1-splash.blend.json`):

| Measure | Value |
|---|---|
| Render engine | Cycles |
| Objects | 1,111 (855 mesh, 201 hair-curves objects, 14 curves, 13 armatures, 11 lattices, 8 lights) |
| Faces | 5,425,533, of which **98.1% are triangles** (5,322,538 tris, 102,963 quads, 32 ngons) |
| GN modifiers | **1,799**, against 69 Subdivision, 64 Armature and 56 Decimate |
| Node groups | 95 geometry, 56 shader, 29 compositor |
| Top GN groups | `GN-LOD_asset` 447, `GN-edge_fade` 447, `.brushstroke_tools.pre_processing` 115, `GN-ice_belt-package_instance` 111, `.brushstroke_tools.surface_fill` 77, `.brushstroke_tools.surface_draw` 30, `GN-distance_to_silhouette` 62, `GN-ice_fungus_generic` 38, `GN-swarm_creature_wiggle` 18, `GN-scatter_ice_shards_in_volume` 6, `FX-swarm` 1 |

**Reading:**

- This is the opposite of the S01 census, where 94.5% of faces were quads. Singularity's shots are **generated, LOD'd, triangulated geometry dressed in procedural strokes**.
- The authored artefact is the node recipe, which is ledger L-006 in its purest form.

## 2. How the humans made it

**Facts:**

- **Stages:** S03, S04, S06, S07, S09, S10 ([index](00-index.md) §04).
- **The team expanded the Brushstroke Tools library** with new painterly assets ([Digital Production](https://digitalproduction.com/2026/05/15/blender-singularity-lands-in-4k-hdr/)).
- **Brushstroke Tools was created for Project Gold**, the Blender 4.2 splash ([search result, studio.blender.org](https://studio.blender.org/blog/blender-development-singularity-and-beyond/)). The local Gold splash confirms it: `gold-splash_screen.blend` uses `GN-surface_brush_strokes` 19 times, and `assets/nodes/brush_stroke_generation.blend` ships surface and volume stroke groups.
- **Procedural crowd systems** used Geometry Nodes, with node-based instancing and caching strategies (Digital Production).
- **The production ran on daily Blender 5.x builds**, and its optimisation needs fed into changes in Blender 5.0 and later 5.2 LTS (search result, Studio blog "Blender development, Singularity and beyond").

**Interpretation:**

- The watercolour look comes from **strokes as geometry**: hair-curve objects (201 in one shot) generated on surfaces by GN, then shaded with brush-texture alpha.
- It is not a post-process filter. Silhouette-distance and edge-fade groups control where paint thins out, which is how a painter leaves paper showing.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs | Tooling |
|---|---|---|---|
| S04 Geometry Nodes (environment) | Ice belt: a torus-shaped volume, with points distributed in it by density falloff, and shard meshes instanced with random scale and rotation. This mirrors `GN-scatter_ice_shards_in_volume` and `GN-ice_belt-package_instance`. LOD by camera distance (`GN-LOD_asset` pattern). | None (shards are procedural: a convex hull of random points) | GN built by script |
| S03 Shading (painterly) | Link the Studio's Brushstroke GN groups and painterly shaders from the Gold splash and apply them as modifiers; the agent sets stroke length, width, density and the colour source. | `blender-4.2-splash/assets/nodes/brush_stroke_generation.blend`, `shading_painterly.blend` (CC-BY) | `bpy.data.libraries.load`; GN inputs by identifier |
| S04 FX | Critter trail: a curve following an animated empty, resampled, with glow strength by age (the `GN-creature_trail-animated_character_trail` pattern). Black hole: an emissive accretion ring plus a lensing approximation (refraction sphere or compositor distortion). | None | GN, compositor |
| S06 Layout | The camera orbits at a declared radius, focal length and roll; composition rules (thirds, critter screen size) are checked numerically. | Storyboard frame (human) | Camera as data |
| S07 Animation | Swarm wiggle on background critters via GN noise over time. **The hero critter's acting is human.** | Human animation | GN time inputs |
| S09 Lighting & rendering | Cycles (as in the shot); a 4K render with an HDR-capable view transform and EXR output. | — | Headless Cycles |
| S10 Compositing | Paper-grain overlay, edge bleed and glare, as a declared compositor graph. Reuse `compositing.blend` from the Gold splash. | Gold splash `compositing.blend` | Compositor by script |

**Build order (for the first slice):**

1. Write the checks first (section 5), including the reference statistics taken from the real shot.
2. Headless pass: open `blender-5.1-splash.blend`, render a 1920 × 1080 reference frame, and save its colour histogram and stroke-coverage stats.
3. Live: clean slate. Build the ice-belt GN: about 3,000 shards in a 40 m-radius torus, instanced, with LOD by distance.
4. Link `brush_stroke_generation.blend` and add `GN-surface_brush_strokes` to the shard base, and to a large backdrop sphere for a painted nebula sky.
5. Black hole: an emissive ring (warm), a dark core, and a cool rim light on the shards.
6. Critter: a small proxy blob on a 120-frame path, leaving a glowing curve trail.
7. Show a `snap.py` progress screenshot after each step. Render 4K Cycles to EXR, plus a 1080p PNG for comparison.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Linking node groups across files.
  - Building GN trees and modifiers, and setting GN inputs.
  - Curves objects, Cycles, EXR output and the compositor by script.
  - Census-style measurement of a reference production file (already done).
- **Painful today:**
  - **Brushstroke Tools as an add-on** is a UI-driven workflow: you pick a surface, then draw or fill strokes. Hand-drawn "draw" strokes (30 `surface_draw` in the shot) are brush paths (L-009). Agent-native, they become declared 3D paths or flow fields.
  - **GN input sockets are addressed by generated identifiers** (`Socket_2`), not names, so recipes break when groups change. That is part of nodes-as-code (L-006).
  - **Version drift:** Gold groups were authored for 4.2. Opened in 5.2.2 they may show `NodeUndefined` nodes ([02-census](../discovery/s01-modeling/02-census.md)).
  - **No result diff after a GN rebuild.** Stroke counts must be re-measured from the evaluated depsgraph (L-003).
  - The Gold library uses mode-free GN, so none of the edit-mode ceremony (L-001) applies. This is the most agent-ready production style in the corpus.
- **Not feasible today:**
  - Judging whether the strokes look painted rather than noisy.
  - HDR grading decisions (what the master is).
  - The hero critter's performance.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Linked libraries resolve; `NodeUndefined` in used groups | 0 missing; 0 undefined |
| 1 Validity | Evaluated stroke geometry: curves with < 2 points, NaN positions | 0 / 0 |
| 2 Spec | Shard count in the belt / radial falloff (density at r = 40 m vs. r = 50 m) | 2,500–3,500 / ≥ 3:1 |
| 2 Spec | Brush-stroke curves generated on shards plus the sky | 20,000–200,000 curves |
| 2 Spec | Screen coverage: fraction of pixels whose alpha comes from stroke geometry (stroke-holdout pass) | ≥ 60% |
| 2 Spec | Critter trail length over 120 frames / glow decays with age | ≥ 10 m / monotonic |
| 2 Spec | Output: resolution, file type, view transform | 3840 × 2160, EXR half, HDR-capable transform |
| 3 Reference | Hue and value histograms vs. the 5.1 Singularity shot render (Earth Mover's Distance) | EMD ≤ 0.2 |
| 3 Reference | Triangle share and GN-modifier share vs. the real shot (style fingerprint) | tris ≥ 90%; GN ≥ 50% of modifiers |
| 4 Downstream | 4K Cycles render time and memory on this machine | ≤ 30 min, ≤ 80% of VRAM |
| 4 Downstream | Temporal stroke stability: stroke-ID flicker between frames 1 and 2 on a static camera | < 5% of strokes change |
| 5 Appearance (warning) | Vision model: "does this look like a watercolour painting of space?" plus a side-by-side with the Singularity still | warning if under 3/5 |
| 6 Taste (owner) | Is it beautiful, and does it feel like Singularity rather than "a filter"? | owner's call (this is the main gate for this item) |

## 6. Where the human is still needed

- **This item is taste-bound.** The art director decides the stroke vocabulary: length and width per material, how much paper shows, where colour bleeds, which edges stay crisp. Layer 5 can only warn.
- **Colour script and HDR mastering:** what the HDR peak is for, and how the SDR version is derived.
- **Character design and animation** of the critter (its appeal, and its grief when its home is destroyed).
- **Story:** a cosmic-scale fable told visually.
- **Calibrating "painterly":** the owner must score a sample of renders blind so that the layer-5 model can be tuned (R6 mechanism 5).

## 7. Effort

- **First slice (live demo, about 1 day):**
  - **On screen:** in the owner's window, a dark scene fills with a ring of thousands of pale-blue ice shards around an empty centre, appearing as the GN instancer runs.
  - When the Studio's brush-stroke modifier is applied, the hard shards turn into clusters of soft painted strokes. The viewport visibly shifts from 3D render to "painting".
  - A warm glowing accretion ring appears around a black core. On playback a tiny blob moves through the belt, trailing a fading glowing line.
  - The final 4K Cycles frame sits beside the real Singularity shot, with the histogram comparison and check report.
- **Full reproduction:**
  - **Agent work:** about 300–500 agent-hours for environments, crowd and swarm systems, stroke dressing, lighting and the compositing set-up per shot.
  - **Render compute:** the shot measured here has 5.4 M faces plus strokes. At 4K Cycles, expect about 20–60 min per frame, so a 10-minute film needs about 5,000–15,000 GPU-hours.
  - **Human work:** art direction is continuous and is the critical path, plus character animation and HDR mastering.

## 8. Risks and unknowns

- **Brushstroke version drift:** the Gold groups (4.2) may not match the Singularity-era library (`.brushstroke_tools.*` groups). The Singularity CC-BY asset release may be the better source; it has not been downloaded yet.
- **Stroke temporal stability** under camera motion is the classic NPR failure (it "swims"). It is untested here.
- **The film's runtime, shot count and production length are unverified.**
- **The 5.1 splash file is one shot.** It may not represent the whole film's style (e.g. the crowd sequences).

## 9. Sources

- [Digital Production: Blender Singularity lands in 4K HDR (2026-05-15)](https://digitalproduction.com/2026/05/15/blender-singularity-lands-in-4k-hdr/) (verified, fetched 2026-10-07)
- [Blender Studio: Singularity premiere](https://studio.blender.org/blog/singularity-premiere/) (verified, fetched 2026-10-07)
- [Blender Studio — Singularity](https://studio.blender.org/films/singularity/) (verified via search, per index)
- [Blender Studio blog: Blender development, Singularity and beyond](https://studio.blender.org/blog/blender-development-singularity-and-beyond/) (search snippet: Brushstroke Tools from Gold, 5.x builds; page not fetched)
- Local: `~/newblender-data/downloads/blender-5.1-splash.blend` (Singularity shot `020_ice0030`), its census JSON, and `~/newblender-data/extracted/blender-4.2-splash/` (Gold, CC-BY, with Brushstroke GN libraries)
- [`02-census.md`](../discovery/s01-modeling/02-census.md); [ledger](../discovery/ledger.md) L-001, L-003, L-006, L-009; [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`
