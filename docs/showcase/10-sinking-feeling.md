# 10 — Sinking Feeling (Blue Zoo): how an agent could make it

| | |
|---|---|
| **Original** | Blue Zoo Animation Studio (London) for PAPYRUS UK, 2021, studio short / charity campaign · [blender.org user story](https://www.blender.org/?p=78797) · [BlenderNation](https://www.blendernation.com/2021/12/22/how-blue-zoo-animation-studio-used-blender-to-create-sinking-feeling/) |
| **Agent-readiness today** | **Taste-bound.** The *look* (2D Grease Pencil ripples on 3D, swappable flat GP faces, a grainy illustrative shader) can be built as data and declared modifiers today. The film's value is 80 seconds of emotionally precise character acting by 18 animators on a mental-health subject, and that is performance and judgement. |
| **Difficulty** | **3.** Short runtime and a simple world, but at studio scale (about 30 artists) with acting-heavy shots. |
| **First slice** | A 5-second shot of a simple 3D character slowly sinking into a dark mud floor, with procedurally drawn 2D Grease Pencil ripples spreading from the body, a flat GP face on the 3D head swapping between three drawn expressions, and a grainy illustrative EEVEE look. |

## 1. What the original actually is

- **Deliverable:** one animated short, **1 min 20 s** (blender.org), about loneliness and peer support. It was made pro bono for PAPYRUS UK, a youth-suicide-prevention charity, as part of the Blue Zoo Shorts programme, and launched on World Suicide Prevention Day 2021 (index).
- **Crew:** about **30 artists including 18 animators**, one animator per shot. Most were new to Blender and "paid to learn Blender" on it. Rigging was by external rigger Chris McFall. Director Mark Spokes (blender.org).
- **Look:** "2D/3D hybrid", a "grainy illustrative design look" built from online tutorials and shaders. 2D effects "like the ripples spreading out around him, and him interacting with this mud floor". Flat viewport shading was used to keep silhouettes strong.
- **Rig feature:** a system to "swap out the characters' face rigs for a flat 2D Grease Pencil face, so you can draw onto those". Also the Dynamic Parent add-on for constraint switching.

## 2. How the humans made it

| Stage | Fact | Interpretation |
|---|---|---|
| S05 Rigging | External rigger; GP face-swap system; Dynamic Parent add-on (blender.org) | 3D body rig with a 2D drawable face layer: the hybrid's key enabler |
| S06 Layout | Simple staging in a mud world (blender.org quotes) | Minimal sets put the budget into animation |
| S07 Animation | 18 animators, one shot each, all learning Blender on the job (blender.org, BlenderNation) | Performance-led film. The pipeline had to be simple enough for first-timers. |
| S12 GP | 2D ripples and mud interaction; drawn faces (blender.org) | Hand-drawn FX and faces over 3D |
| S09 Rendering | "grainy illustrative design look" from community tutorials and shaders (blender.org) | Likely EEVEE with noise-textured shading. **Engine not named** in blender.org's text. The index's "EEVEE" and "LoUPE" come from search snippets and are not confirmed by the fetched pages. |

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 | A simple stylised character (pill body, round head, stubby arms) as bmesh data plus Subdivision, following demo 001 | — | bridge |
| S05 | Armature as data (root, spine, head, arms), automatic weights. **GP face rig:** a GP object parented to the head bone, one layer per feature (eyes, brows, mouth). An integer `expression` property picks which layer frame is visible. | — | bridge |
| S12 face | **Drawn expressions as stroke data:** eyes = small closed strokes with fill; brows and mouth = 5–9 point strokes with tapered `radius`. Three expressions (neutral, sad, hopeful) on frames 1, 2 and 3 of each layer; Time Offset modifier in fixed-frame mode, keyed by the expression. | — | `add_strokes`, `GREASE_PENCIL_TIME` |
| S12 ripples | **Procedural ripples:** for each ring k, a cyclic stroke of 64 points; radius grows with `r(t) = r0 + v·(t − t_k)`, opacity fades; one drawing per frame written as data (`frames.new(f)`), or one drawing plus scale keys; a Noise modifier gives a hand wobble | — | `add_strokes`, GP Noise / Thickness |
| S07 | Sinking: a body Z curve keyed with ease-in plus a small sway; secondary arm flail as offset sine keys. The acting stays placeholder. | a 4-beat brief from the owner | bridge |
| S03/S09 | **Grainy illustrative shader:** Diffuse → Shader to RGB → 2-step ramp → multiply by a screen-space noise (Texture Coordinate *Window* → Noise at high scale), flat shadow colour; mud = dark glossy plane with a soft Fresnel rim | — | EEVEE |
| S10 | Grain overlay plus slight vignette in the compositor, all as nodes | — | compositor |

**Build order**

1. Write the assertions (section 5).
2. Character mesh, then the armature and weights.
3. GP face object and the three expressions as stroke data, with the switching property.
4. Mud plane, then the sinking keys.
5. Ripple generator: one ring spawns every 12 frames when the body crosses the surface.
6. Shader, comp, render, checks.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Mesh and armature as data. Demo 001 is the precedent for declared modifiers plus render plus `snap.py`.
  - GP v3 strokes, frames and point attributes written directly: on 5.2.2, 12,800 points in 0.04 s headless.
  - GP Time and Noise modifiers, shader nodes, compositor nodes, EEVEE.
- **Painful today:**
  - **Drawn faces, the way animators do them**, go through the GP brush operator, which is event-driven (poll False headless). Data-written strokes lose pressure dynamics and brush texture (L-009).
  - **Automatic weights** (`object.parent_set` with `ARMATURE_AUTO`) is selection-scoped and mode-sensitive. That is the L-001/L-002 ceremony around what is really a function of (mesh, armature).
  - **Mixed 2D/3D depth sorting.** GP stroke depth against the mud plane needs a per-layer depth-order setting to avoid ripples clipping into the mud. That is a hidden setting, not a declared outcome (L-004).
  - **No diff after edits** (L-003). Ripple counts and face states must be re-queried to check.
- **Not feasible today:**
  - The 18 animators' acting: subtle weight shifts, hesitation, the moment a friend reaches out. An agent can block a sink; it cannot be trusted with the emotional beat on a suicide-prevention film.
  - Hand-drawn mud splashes with appeal (procedural rings are the floor, not the ceiling).

## 5. Verification plan (RFC 0001 R6, six layers)

For the first slice: 120 frames at 24 fps, 1920×1080.

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Character mesh: manifold, normals out, scale applied (demo 001 checks) | 0 failures |
| 1 Validity | GP: every stroke has ≥ 2 points, finite positions, and radius > 0; ripple strokes are cyclic | 0 violations; 100% cyclic |
| 2 Spec | Sinking: body origin height | z(1) ≥ 0, z(120) ≤ −0.6 × body height; monotonic except sway ≤ 3 cm |
| 2 Spec | Ripples: spawn interval, growth, fade | a new ring every 12 ± 1 frames once submerged; each ring's radius strictly increasing; opacity reaches ≤ 0.05 by ring age 36 frames |
| 2 Spec | Ripples lie on the mud surface | all ripple points within ±5 mm of mud z |
| 2 Spec | Face swap: exactly one expression visible per feature at any frame; the expression changes on keyed beats | 1 visible drawing per feature layer; 3 distinct expressions used |
| 2 Spec | Face stays on the head through motion | GP face pivot within 1 cm of the head bone's face anchor on all frames |
| 2 Spec | Grain present but not noisy | high-frequency luminance std in flat regions between 0.01 and 0.04 |
| 3 Reference | Determinism: re-render frame 60 from the script | max abs diff ≤ 1/255 (EEVEE, fixed seed) |
| 4 Downstream | Animator-friendliness: face expression = 1 integer control; body rig poses at ±90° spine bend with no mesh self-intersection | 1 control; 0 intersecting faces (BVH overlap test) |
| 5 Appearance (warning) | Vision model: "2D/3D hybrid, grainy illustrated, mud ripples drawn" | warn if below 3 of 5 |
| 6 Taste (owner) | Does the shot feel lonely, not comic? Is it appropriate for the subject? | owner, required before any external use |

## 6. Where the human is still needed

- **Acting and emotion.** The film's whole job is to make a young viewer feel seen. That requires animators' performance and a director's care, and on this subject also the charity's sign-off on tone.
- **Drawn faces with appeal.** Generated eyes and mouths are placeholders. The GP face system exists so a *human* can draw onto it.
- **Ethics and messaging.** Content touching suicide must follow safe-messaging guidance from the charity. That is not a machine check.
- **Art direction** of grain amount, palette and silhouette clarity.

## 7. Effort

- **First slice (live demo, ~1 day):** on screen in the owner's Blender:
  1. A soft pill-shaped character standing on a dark, glossy mud plane.
  2. A flat, hand-drawn-looking face pops onto the 3D head: two dot eyes, brows and a line mouth that move with the head. Setting `expression` to 0, 1 or 2 swaps it between neutral, sad and hopeful.
  3. Scrubbing the timeline, he slowly sinks, and 2D ink rings spread across the mud from where he enters, wobbling slightly and fading out.
  4. Rendered view: banded flat shading with a fine film grain over everything.
  5. A 5-second EEVEE render and the check report.
- **Full reproduction (80 s):**
  - **Agent:** about 40–80 hours for rigs, the face system, FX generators, look and render.
  - **Human:** the original's 18 animators × one shot each is weeks of performance work, plus direction. Agents cut the setup and FX time, not the acting.
  - **Compute:** under an hour of EEVEE for the whole short.

## 8. Risks and unknowns

- **The render engine and remote tools are unconfirmed.** EEVEE and LoUPE come only from search snippets. The fetched blender.org text names neither.
- **GP-over-3D depth sorting and parenting** may need per-layer tweaks that are hard to verify without viewing renders (layer 5).
- **Generic outcome.** Procedural ripples risk looking like a "screensaver"; the original's mud interaction was hand-crafted.
- **Sensitivity.** Any demo touching this film's subject should avoid casually recreating it. The slice copies the *technique*, not the story.

## 9. Sources

- [blender.org: Sinking Feeling — Using Blender to do good](https://www.blender.org/?p=78797) (fetched 2026-10-07: 1:20, ~30 artists / 18 animators, director Mark Spokes, rigger Chris McFall, GP face swap, 2D ripples and mud, grainy illustrative look, Dynamic Parent, one animator per shot)
- [BlenderNation: how Blue Zoo used Blender to create Sinking Feeling](https://www.blendernation.com/2021/12/22/how-blue-zoo-animation-studio-used-blender-to-create-sinking-feeling/) (fetched: first Blender film, animators paid to learn, GP as the attraction)
- [80.lv: using Blender to make a short film for charity](https://80.lv/articles/using-blender-to-make-a-short-film-for-charity) (unverified, from the index)
- Local: `blender-manual/manual/grease_pencil/modifiers/edit/time_offset.rst`, `deform/noise.rst`; GP architecture dev doc (point attributes `radius`, `opacity`, `cyclic`)
- Local probes (headless 5.2.2): `add_strokes` throughput; GP modifier list includes `GREASE_PENCIL_TIME`, `GREASE_PENCIL_NOISE`; `grease_pencil.brush_stroke.poll()` = False
- [`docs/discovery/ledger.md`](../discovery/ledger.md) L-001, L-002, L-003, L-004, L-009; [RFC 0001 R6](../rfc/0001-newblender.md); bridge: `tools/live/bl.py`, `snap.py`, demo 001 report
