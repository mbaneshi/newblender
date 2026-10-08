# 11 — Nashville International Airport Grand Lobby: how an agent could make it

| | |
|---|---|
| **Original** | Gentilhomme (Montreal), 2023, immersive motion graphics for two large-format LED walls · [blender.org user story](https://www.blender.org/user-stories/behind-the-scenes-nashville-international-airport/) |
| **Agent-readiness today** | **Partial**: the Geometry Nodes (GN) motion-design core, Cycles multipass output and scripted rendering work through the live bridge today. The 40-minute volume at 11,200 px wide needs a headless farm (L-011), and the design language (neon, distilleries, country music) is owner taste. |
| **Difficulty** | 4 (one capsule is a week; the full 40+ minutes is a studio-quarter project, dominated by render compute and art direction) |
| **First slice** | A 10-second seamless "Broadway neon grid" loop, built as one GN tree, framed for the 11,200 × 2,160 wall and rendered at quarter resolution (2,800 × 540) to 32-bit multilayer EXR, with a check script that proves the loop closes and nothing clips. |

## 1. What the original actually is

Facts from the blender.org user story (fetched 2026-10-07):

- **Display:** two LED walls in the Grand Lobby, each 21 m × 4.5 m. Standard canvas 7,360 × 2,160 px per wall; the maximum canvas is 11,200 × 2,160 px (an aspect of about 5.2 : 1).
- **Volume:** over 40 minutes of content in 13 segments.
- **CGI share:** 6 segments ("capsules") are fully CGI; themes include distilleries, country music and Broadway-style neon.
- **Two content families:** "traditional CGI" (rigging, animation, simulation) and motion design with slow ambient animation.
- **Output:** multipass EXR in 16- or 32-bit, composited in After Effects.

Deliverables, restated as an agent would track them: 13 timed segments × 2 walls; per segment a frame sequence at wall resolution, per-pass EXRs, a composited master, and loop points where the segment cycles in the lobby.

## 2. How the humans made it

Stages exercised: **S03 Shading, S04 Geometry Nodes, S09 Lighting & rendering, S10 Compositing.**

**Fact (user story):**
- Cycles was the render engine. GN was used "for creating diverse visual elements": grid distributions and texture-driven displacement, per the index entry.
- Neon tube assets were built in SideFX Houdini from Adobe Illustrator designs. Other assets came from Maya and Substance Designer. Smoke came from EmberGen.
- A 20-machine render farm ran custom scripts ("GH render" and "GH multipass") written by in-house creative coders. Denoising ran as part of the render-node process.
- Renders of a capsule at final resolution took "full nights or even several days".
- Team: CG supervisor Arnaud Mellinger, motion designer Maxime Roux, plus modelling, coding and Houdini specialists.

**Interpretation:** the studio already worked in an agent-shaped way for the parts that scale: procedural layouts in GN, scripted farm submission, scripted pass handling. The hand-made parts were design (Illustrator), hero assets (Houdini/Maya) and the look in After Effects.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free sources) | Tooling |
|---|---|---|---|
| S04 Geometry Nodes | One GN tree per capsule, the primary artefact (L-006): Grid → Instance on Points → per-instance phase from Random Value; Set Position driven by a Noise Texture sampled at `(x, y, t)` where `t` loops on a circle so the animation closes | Scene Time node; no external data | `tools/live/bl.py` builds the tree with `bpy.data.node_groups.new(..., "GeometryNodeTree")` |
| S01 Modeling (neon) | Neon letters as curves → Curve to Mesh with a circle profile, all in GN; letter shapes from a font via Text object → Curve, or SVG import | Free OFL fonts (Google Fonts), CC0 SVG | GN String to Curves node |
| S03 Shading | Emission shader with strength from a named attribute (`flicker`) written by GN; glass tubes as thin refractive shells | None | Shader Attribute node |
| S08 FX (smoke) | Not EmberGen: Blender Mantaflow smoke baked headless, or a cheap volumetric noise shader for ambient haze | None | Headless bake |
| S09 Rendering | Cycles, fixed seed, multilayer EXR, passes: Combined, Emission, Denoising Albedo/Normal, Cryptomatte | Poly Haven HDRI only if a reflection environment is wanted (CC0) | Headless `blender -b` per frame range |
| S10 Compositing | Blender compositor node tree written as code: glare (fog glow) on Emission, grade, output to the delivery codec | None | Compositor via Python |
| Farm | Split by frame range across machines; split very wide frames by render border and stitch | Local GPUs | Shell + `blender -b -P` |

**Build order:**

1. Write the checks first (§5): resolution, frame count, loop closure, clipping, determinism.
2. Set the canvas: 11,200 × 2,160 at 25% for look-dev, metric scene scale matching the 21 m wall.
3. Build the GN grid-and-displace tree on an empty object; declare every parameter as a group input (spacing, amplitude, speed, palette index).
4. Write the emission material reading the GN attribute.
5. Camera: orthographic, sized to the wall aspect, so pixels map 1:1 to the LED grid.
6. Render 3 test frames (0, mid, last) to EXR; run the checks; snap the viewport for the owner (`tools/live/snap.py`).
7. Owner reviews look; parameter edits only, no topology edits.
8. Full-resolution render by frame range headless; stitch borders; composite.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Building GN trees node by node from Python and wiring group inputs. The chair demo already showed declared modifiers built and checked live (`~/newblender-data/demos/001-chair/report.md`, 12/12 checks).
  - Setting Cycles samples, seed, resolution, passes and multilayer EXR from Python.
  - Reading a rendered EXR back and measuring pixels (`bpy.data.images.load`, `pixels.foreach_get`).
  - Screenshots of the owner's window for the review loop (`tools/live/snap.py`).
- **Painful today:**
  - Wiring large GN trees through `nodes.new` / `links.new` is verbose and position-less. The tree *is* the artefact (L-006), but there is no first-class text form of it; `nodebpy` is the upstream answer.
  - GN evaluation returns no diff or summary: to know what the tree produced, the checker must evaluate the depsgraph and count (L-003).
  - Farm rendering needs a clean headless boot with no default cube and no UI-only settings (L-011).
  - Python edits push no undo step by default, so art-direction iterations are not transactional (L-008). Workaround: save versioned `.blend` files per accepted look.
- **Not feasible today:**
  - Houdini-quality neon tube assets with physically plausible glass and gas glow at hero distance, without a human modeller's eye.
  - EmberGen-speed smoke iteration; Mantaflow works but is slow at this scale.
  - 40 minutes at 11,200 × 2,160 on one workstation. Estimate: at 30 fps, 40 min ≈ 72,000 frames; at an assumed 2 GPU-minutes per frame that is ≈ 2,400 GPU-hours (interpretation; the source gives no fps or per-frame times).

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every output EXR opens; resolution exact; required passes present; no NaN/Inf pixels | 11,200 × 2,160 (or the declared test scale); passes {Combined, Emission, Denoising Albedo, Denoising Normal} present; 0 NaN/Inf |
| 1 Validity | GN evaluated geometry is valid | 0 non-manifold edges on tube meshes; 0 degenerate faces |
| 2 Spec | Segment length and frame count | Exactly the declared frames (e.g. 250 at 25 fps for 10 s); no gaps in the sequence |
| 2 Spec | Seamless loop | Mean absolute difference between frame 0 and frame N+1 (rendered) < 0.5% of mean luminance |
| 2 Spec | No clipping on the LED wall | < 0.1% of pixels with any channel > 1.0 after the delivery transform |
| 2 Spec | Temporal flicker | Frame-to-frame mean luminance change < 2% except at declared cuts |
| 3 Reference | Determinism: same `.blend`, seed and frame rendered twice | PSNR ≥ 45 dB; GN evaluated vertex positions identical (hash match) |
| 3 Reference | Tile stitch equals full render | Max abs difference across the stitch seam < 1/255 |
| 4 Downstream | Compositor reads the EXR; Emission + other light passes recombine to Combined | Recombined vs Combined mean abs error < 1% |
| 4 Downstream | Delivery encode plays at wall resolution | Encoded file decodes with exact frame count; bitrate within the venue's spec (owner provides) |
| 5 Appearance (warning) | Vision model scores a 6-frame contact sheet against the brief ("Broadway neon, warm, readable from 20 m") | Warn if score < 7/10 or if text legibility is flagged |
| 6 Taste (owner) | Owner watches the loop on a scaled-down wall preview | Owner sign-off; notes become parameter changes |

## 6. Where the human is still needed

- **The design language.** What "Nashville" looks like as neon and distillery copper is a cultural and brand decision; Gentilhomme started in Illustrator for a reason.
- **Pacing at architectural scale.** How slow is calm for a lobby where people stand for 30 seconds? That is judged in the room, not by a metric.
- **Hero assets.** Neon lettering with believable glass, gas glow and bracket hardware needs a modeller's eye; the agent can produce a clean first pass.
- **Sign-off with the venue.** Brightness limits, content approvals and loop points are contractual.

## 7. Effort

- **First slice (live demo, ~1 day):** the owner sees, in their open Blender window, an empty scene become a wide orthographic frame filled with a grid of glowing tube segments. Pressing play, waves of brightness and displacement roll across the grid and loop after 10 s. Changing one group input (say `speed` or `palette`) on the GN modifier changes the whole wall. Three quarter-resolution EXR frames land in `~/newblender-data/demos/`, with a check report like the chair's.
- **Full reproduction:** roughly 60–120 agent-hours to build 6 capsule systems and their checks; ≈ 2,000–3,000 GPU-hours of render (estimate above); 40–80 human-hours of direction (style frames, pacing reviews, venue sign-off), plus whatever hero assets are hand-modelled.

## 8. Risks and unknowns

- Frame rate, codec and LED processor constraints are not in the source; the checks above need the venue spec.
- A vision model judging "neon mood" is unreliable (R6 layer 5 is a warning only).
- Very wide frames stress GPU memory; border-split rendering adds a seam risk (hence the stitch check).
- Our version of GN shading parity with Houdini neon is unproven.

## 9. Sources

- [Behind the Scenes: Nashville International Airport (blender.org user story)](https://www.blender.org/user-stories/behind-the-scenes-nashville-international-airport/) (verified, fetched 2026-10-07)
- [Showcase index entry 11](00-index.md)
- [RFC 0001 R6 verification model](../rfc/0001-newblender.md)
- [Transformation ledger L-003, L-006, L-008, L-011](../discovery/ledger.md)
- [S01 brief §6, agent-native shape](../discovery/s01-modeling/05-brief.md)
- Live bridge: [`tools/live/bl.py`](../../tools/live/bl.py), [`tools/live/snap.py`](../../tools/live/snap.py); chair evidence `~/newblender-data/demos/001-chair/report.md`
- [Poly Haven HDRIs (CC0)](https://polyhaven.com/hdris)
