# 07 — Unicorn Wars: how an agent could make it

| | |
|---|---|
| **Original** | Alberto Vázquez (writer and director), with the Blender pipeline by ADV Studios (technical supervisors Christophe Seux and Samuel Bernou), 2022, a 2D-in-3D Grease Pencil feature (Goya 2023, Best Animated Film) · [BlenderNation](https://www.blendernation.com/2023/01/06/unicorn-wars-made-with-blender-animated-feature-now-in-french-cinemas/) |
| **Agent-readiness today** | **Taste-bound.** The *mechanical* half already works today: 3D-to-2D line tracing (the Line Art modifier and bake), stroke data written directly, procedural walk cycles, background-plane layout. But the film *is* hand-drawn character acting and drawn backgrounds, and that is the human's line, timing and design. Interactive drawing goes through an event-stream stroke operator (L-009). |
| **Difficulty** | **5.** A feature film, roughly 90 minutes of drawn animation. |
| **First slice** | A 4-second shot of a 3D "teddy-bear soldier" marching on a procedural walk cycle, turned into 2D Grease Pencil lines by Line Art and baked to editable strokes, in front of three background planes of procedurally drawn trees, rendered in EEVEE from the camera. In short, the GP Tracer and Auto-walk pipeline rebuilt as data. |

## 1. What the original actually is

- **Feature film:** an adult war fable described as "Bambi meets Apocalypse Now". Teddy-bear recruits march into an enchanted forest to fight unicorns.
- **Look:** "Everything except the unicorns in the film were drawn using Grease Pencil." The unicorns were animated in 3D, then converted to editable 2D drawings.
- **Pipeline deliverables (tools as well as frames):**
  - **Background Plane Manager** (Samuel Bernou): manages many Grease Pencil background layers and planes across shots.
  - **GP Tracer** (Christophe Seux): "converts 3D objects into GP drawings neatly projected on a canvas accurately positioned in space", so 2D artists retouch rather than draw every frame.
  - **Auto-walk** (Samuel Bernou): automates walk-cycle setup so animators "focus on the acting".
  - Shot count, team size and duration are not in the fetched sources. The index marks the duration *unverified*.
- **Lineage:** the same people previously worked on *I Lost My Body*. They also maintain the open GP Toolbox add-on.

## 2. How the humans made it

| Stage | Fact (source) | Interpretation |
|---|---|---|
| S12 Grease Pencil | All characters (except unicorns) and the drawn elements are GP strokes, drawn by 2D animators in Blender (BlenderNation) | The core of the film, and pure hand drawing |
| S06 Layout | GP drawings sit on canvases "accurately positioned in space" relative to the camera; a Background Plane Manager organises them (BlenderNation) | 2.5D multiplane: flat drawn planes at depth, so camera moves get parallax for free |
| S07 Animation | Unicorns are animated in 3D, traced to GP, then refined by 2D artists; Auto-walk generates walk cycles (BlenderNation) | Hybrid: 3D for complex locomotion, 2D for acting and style |
| S09 Rendering | Not detailed in the fetched source | Almost certainly the GP engine inside EEVEE (*inference*) |

The GP Tracer itself is not public as far as I could verify. The modern Blender equivalent is the **Line Art** modifier, which generates GP strokes from visible 3D edges as seen from the active camera.

## 3. How I would make it: the agent-native plan

**What an agent can and cannot generate in Grease Pencil, precisely:**

| Kind of stroke | Possible today? | How |
|---|---|---|
| Lines traced from 3D geometry | **Yes, declaratively** | Line Art modifier (`LINEART`) on a GP object, set to Scene/Collection/Object source. Bake to editable strokes with `object.lineart_bake_strokes` (works headless with a `temp_override`; probed). |
| Procedural strokes (grass, trees, rain, ripples, hatching) | **Yes, as data** | `drawing.add_strokes(sizes)`, then write `position`, `radius`, `opacity` and `vertex_color` per point. 200 strokes × 64 points took 0.04 s headless (probe). |
| Stroke styling (wobble, taper, dashes, outline, "drawn-on" build) | **Yes, declared** | GP modifiers: Noise, Thickness, Smooth, Simplify, Dash, Envelope, Outline, Build, Time Offset, Multiple Strokes (26 types in 5.2.2) |
| Animated drawings (frame-by-frame) | **Yes, as data** | `layer.frames.new(f)` per drawing. Hold, timing and steps are just frame numbers. |
| *Good* hand-drawn character acting, appeal and line quality | **No.** This is taste and hand. | A human 2D animator. An agent can produce rough key poses from 3D, and the human draws over them. |
| Interactive drawing like a person | Only by faking events | `grease_pencil.brush_stroke` poll is False headless; it is an event-stream operator (L-009) |

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 (proxy) | The teddy soldier built from primitives as bmesh data (capsules, spheres), with a helmet and rifle, following the chair-demo pattern | none | bridge |
| S05 | A minimal armature (hips, spine, legs, arms, head) created as data, with automatic weights | — | bridge |
| S07 | **Auto-walk as maths:** a parametric walk cycle (stride length, cadence, bounce, arm swing) written as F-curve keyframes, plus a path follow. A crowd of N soldiers with phase offsets. | — | bridge |
| S12 lines | **GP Tracer as a declared modifier:** a Line Art collection source, chaining on, crease threshold set, Thickness and Noise modifiers for a hand-made wobble; optionally bake to strokes for a human to retouch | — | GP modifiers |
| S12 backgrounds | Procedural "drawn" trees, ferns and ground marks as stroke data on 3 to 4 planes at depth, with vertex colour washes and fill strokes for flat colour shapes | a palette from the brief | `add_strokes` |
| S06 | **Plane manager as data:** a collection per depth plane, each plane scaled so it fills the frame at its distance (`scale = 2·d·tan(fov/2)`), parented to a camera rig | — | bridge |
| S09 | EEVEE render of the GP plus 3D scene; a Colorize, Rim or Blur shader effect for the stylised atmosphere | — | EEVEE |

**Build order**

1. Write the checks first (section 5).
2. Camera, then the plane rig with fill-frame maths.
3. Procedural background strokes per plane.
4. Teddy proxy, armature, and the walk cycle as data.
5. Line Art GP object reading the "characters" collection, with styling modifiers.
6. Bake the lines (optional), render, and check.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - GP v3 data API: layers, frames, `add_strokes`, and point attributes (`position`, `radius`, `opacity`, `vertex_color`), confirmed on 5.2.2 headless. The underlying model is `CurvesGeometry` with named attributes ([dev docs, GP architecture](https://developer.blender.org/docs/features/grease_pencil/architecture/), local copy).
  - Line Art evaluation: the factory cube gives 3 chained strokes and 12 points in 3 ms. Bake works through `temp_override` even though its plain poll is False.
  - All 26 GP modifier types, and shader effects, declared from Python.
  - Armature, keyframes and EEVEE render.
- **Painful today:**
  - **Drawing as an action** goes through `grease_pencil.brush_stroke`, an event-stream operator with no data entry point. L-009 proposes "brush → field or 3D path". Today the honest route is to write strokes as data and skip the brush, which loses the brush engine's pressure, jitter and texture behaviour.
  - **Line Art cost.** Each Line Art modifier recomputes occlusion for the whole scene unless *Use Cache* is set (manual note), which gets slow on multi-character shots.
  - **Polls that hide needs** (L-004): the bake operator's poll fails headless although the operation runs fine with an override.
  - **No diff back** (L-003): after a bake the agent must re-count strokes to know what happened.
- **Not feasible today:**
  - Feature-quality *drawn* character animation without a human 2D animator. The agent can generate traced roughs and procedural FX, not the hand.
  - Matching Vázquez's specific line and design language from text alone.

## 5. Verification plan (RFC 0001 R6, six layers)

For the first slice: 96 frames at 24 fps, 1920×1080.

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every GP stroke has ≥ 2 points, finite positions, and radius > 0 | 0 violations |
| 1 Validity | Every frame renders, with no empty Line Art frames | stroke count > 0 on all 96 frames |
| 2 Spec | Walk cycle: feet never below the ground, and stride period | min foot z ≥ −0.005 m; period 12 ± 1 frames (twos-friendly) |
| 2 Spec | Foot sliding during stance phase | planted foot moves ≤ 1 cm per frame |
| 2 Spec | Background planes exactly fill the frame | each plane's projected bounds cover 100–105% of the frame |
| 2 Spec | Parallax order: a nearer plane moves more on screen than a farther one during the camera truck | strictly monotonic with depth |
| 2 Spec | Line Art density (character silhouette and inner lines) | 20–400 strokes per frame per character |
| 3 Reference | The baked strokes match the live modifier output on frame 1 | identical stroke count; point positions within 1e-5 |
| 4 Downstream | Retouchability: baked strokes live on their own named layer with a single material, and the strokes are editable (no modifier left that changes the topology) | layer `LINES_baked` exists; 1 material; 0 topology-changing modifiers after bake |
| 5 Appearance (warning) | Vision model: does the frame read as "2D drawn character in a drawn forest", not CG? | warn if it scores below 3 of 5 |
| 6 Taste (owner) | Does it feel like *Unicorn Wars* (cute vs. menace) or just like generic Line Art? | owner judgement |

## 6. Where the human is still needed

- **The drawing itself.** Character design, line confidence, squash and stretch, acting poses, mouth shapes. None of this is mechanical. Traced 3D lines read as "CG with outlines" until a 2D artist redraws them, which is exactly why ADV kept 2D artists in the loop after GP Tracer.
- **Backgrounds** with a painter's composition. Procedural trees fill a plane but do not compose a frame.
- **Timing choices** for comedy and horror: holds, smears, on-ones vs. on-twos.
- **Story and direction:** Vázquez's tone shift from cute to brutal is authorship, not pipeline.

## 7. Effort

- **First slice (live demo, ~1 day):** on screen in the owner's Blender:
  1. Three flat planes appearing at increasing depths in front of the camera, filling with drawn-looking tree trunks, foliage scribbles and ground strokes in a muted palette.
  2. A chunky primitive teddy soldier marching along a path, legs and arms swinging, at first as grey 3D.
  3. Switched to camera view, the 3D bear disappears behind its own **Line Art** silhouette and inner lines, wobbling slightly from a Noise modifier, so he reads as a 2D drawing walking through a 2D forest with parallax as the camera trucks.
  4. Bake: the strokes become selectable, editable GP data that a human could retouch.
  5. A 4-second EEVEE render, and the check report.
- **Full reproduction:** the mechanics (tracing, auto-walk, plane management, procedural FX) take roughly 100–200 agent-hours to build as reusable tools. The *film* is dominated by human drawing: thousands of 2D-animator days on a feature. Agents could save meaningful time on unicorn-style traced roughs and on background and FX passes, but not on the acting.

## 8. Risks and unknowns

- Line Art lines from simple primitives look mechanical. Creases and contour chaining need tuning per model.
- GP Tracer's exact behaviour (canvas projection, temporal coherence) is unknown. Line Art may flicker between frames where GP Tracer did not.
- The GP v3 Python API is young (Blender 4.3+). Helper classes like `_bpy_internal/grease_pencil/stroke.py` are internal and could change.
- Shot counts, team size and schedule are unverified, so the effort estimate rests on the format, not on production data.

## 9. Sources

- [BlenderNation: Unicorn Wars, made with Blender](https://www.blendernation.com/2023/01/06/unicorn-wars-made-with-blender-animated-feature-now-in-french-cinemas/) (fetched 2026-10-07: tools, quotes, team, the "everything except the unicorns" claim)
- [Wikipedia: Unicorn Wars](https://en.wikipedia.org/wiki/Unicorn_Wars) (Goya 2023; via the index, verified via search)
- [GP Toolbox (Autour de Minuit / Bernou and Seux)](https://git.autourdeminuit.com/autour_de_minuit/gp_toolbox/src/tag/v1.5.1) (search result)
- Local: `blender-developer-docs/docs/features/grease_pencil/architecture.md` (drawings are CurvesGeometry with attributes); `blender-manual/manual/grease_pencil/modifiers/generate/line_art.rst` (per-modifier occlusion cost, Use Cache); `blender/source/blender/makesrna/intern/rna_grease_pencil_api.cc:794` (`add_strokes`)
- Local probes (headless 5.2.2, factory startup, 2026-10-07): `add_strokes` 200×64 points in 0.041 s; 26 GP modifier types; Line Art cube eval 3 strokes / 12 points; bake via `temp_override` = FINISHED; `brush_stroke.poll()` = False
- [`docs/discovery/ledger.md`](../discovery/ledger.md) L-003, L-004, L-006, L-009; [RFC 0001 R6](../rfc/0001-newblender.md); bridge: `tools/live/bl.py`, `snap.py`, demo 001 report
