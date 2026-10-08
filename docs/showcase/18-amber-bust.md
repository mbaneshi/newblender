# 18 — Amber Bust: how an agent could make it

| | |
|---|---|
| **Original** | RoseRedTiger (Rose), 2020, stylised character sculpting · [BlenderNation](https://www.blendernation.com/2020/10/07/behind-the-scenes-amber-bust/) |
| **Agent-readiness today** | **Taste-bound.** Every mechanical step has a scriptable route, but the brush strokes that carry the character's form are GUI-gated (`sculpt.brush_stroke` needs an area + region, [03-trace](../discovery/s01-modeling/03-trace.md) row `sculpt.brush_stroke`), and even with a perfect stroke API the hard part is the face: proportion, charm, the read of a personality. That is human judgement. |
| **Difficulty** | **4.** Getting *a* stylised bust is a 2. Getting one the owner would call good is a 4, mostly in direction loops, not compute. |
| **First slice** | Start from the CC base-mesh stylised head (4,118 verts, 12 face sets), push it toward a brief with declared deformations (Lattice, Hooks, Displace masked by face sets on a Multires stack), grow curl hair as GN curve tubes, paint flat vertex colours from face sets, and render an EEVEE three-point portrait, with a check report and an honest "this is a mannequin, not Amber" verdict. |

## 1. What the original actually is

- **One still image** (plus breakdown shots): a stylised female bust (head, neck, torso, ears, voluminous curly hair) sculpted, painted and rendered **entirely in Blender**.
- **Assets:** separate sculpt objects for head, neck, torso, ears and hair (BlenderNation).
- **Colour:** no texture maps; all colour is sculpt-mode vertex colour, a feature new in the 2.91 alpha at the time.
- **Render:** EEVEE.
- **Not stated:** polycount, time spent, base mesh.

## 2. How the humans made it

| Stage | Technique (BlenderNation) | Fact / interpretation |
|---|---|---|
| S01 Modeling (sculpt) | Separate objects for head, neck, torso, ears, hair. Brushes: Snake Hook, Clay Strips, Crease, Smooth, with periodic **remesh** for more resolution. | Fact |
| S01 Hair | **Dynamic topology** to pull long curls; Clay Strips to block strands; Crease for sharp edges; **Mask Extract** for short side hair. | Fact |
| S03 Shading / colour | Vertex painting in Sculpt mode: flat base colours, freckles via a cloud texture on the brush, dirty mask and colour filters for hair highlights. Principled BSDF with "vertex color as color, high roughness, and a little bit of SSS". | Fact |
| S09 Lighting & render | EEVEE; HDRI fill, point-light key, two sun lights as backlights. | Fact |

Interpretation: almost everything that makes this piece good lives in thousands of brush strokes, each one a decision made by looking. There is no recipe to recover from the result.

## 3. How I would make it: the agent-native plan

The S01 brief left one question open for the owner: should an agent sculpt by strokes at all, or only by declared fields ([05-brief §7](../discovery/s01-modeling/05-brief.md), gray zone G1)? This plan uses **declared deformations first** and treats stroke replay as an experiment.

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 Base | **Imported asset, not sculpted from a sphere.** The Blender Studio *Human Base Meshes* stylised head: `GEO-head_stylized`, 4,118 verts, 4,134 faces (99% quads), 12 face sets, plus separate eyes (measured locally). Clean topology means everything later stays quad-based. | `~/newblender-data/extracted/human-base-meshes-bundle-v1.4.1/` | append from `.blend` via `bpy.data.libraries.load` |
| S01 Primary forms | **Declared, coarse:** a Lattice (4×4×4) for overall head shape (jaw width, cranium volume, chin length), Hook modifiers on vertex groups for features (nose tip, cheekbones, lips), each driven by a named parameter in a spec dict. Like a character creator's sliders. | — | Lattice / Hook modifiers, vertex groups from face sets |
| S01 Secondary forms | **Multires + displacement:** subdivide to level 3–4, then Displace modifiers masked by vertex groups for soft volumes (cheek fullness, brow ridge), or `multires_reshape` from a declared target. GN `Set Position` with fields (distance to a point, noise) for lip and eyelid creases. | — | Multires, Displace, GN |
| S01 Hair | **GN curves instead of dyntopo strands:** hair as a set of guide curves (spirals with jittered radius and twist), turned into tubes with `Curve to Mesh` and a tapering profile; clumps are Instance on Points along a scalp curve. Each curl's parameters live in data, so "make the curls tighter" is one number. | — | GN tree as code ([L-006](../discovery/ledger.md)) |
| S01 Torso, ears | Append base-mesh body and ears; the bust cut is a Boolean with a plane, and a Solidify for the shoulder shell (the original used Mask Extract + Solidify). | base-mesh bundle | Boolean, Solidify |
| S03 Colour | **Vertex colour as an attribute written from data:** base colours per face set (skin, lips, eyebrows, hair), freckles from a thresholded noise field restricted to the cheek/nose region, hair highlights from curve parameter + a Pointiness-like term. GN `Store Named Attribute` or direct `color_attributes` writes. | — | GN / RNA |
| S03 Shading | Principled BSDF: colour attribute → Base Color, roughness 0.6–0.7, subsurface weight ≈ 0.1, matching the original's notes. | — | shader nodes |
| S09 Render | EEVEE: HDRI fill, point-light key, two sun rims; a 3/4 portrait camera at 85 mm. | Poly Haven studio HDRI (CC0) | headless or live render |
| (experiment) | **Stroke replay:** feed `sculpt.brush_stroke` a synthetic `stroke` collection with stored 3D locations under `temp_override(area, region)`. The trace says exec exists but each point still carries a screen-space `mouse_event` and needs a `ViewContext` (`paint_stroke.cc:1652`, `:863`). | — | live bridge only (needs the real window) |

**Build order**

1. Write the brief as numbers (head-to-neck ratio, eye spacing, hair volume) and the checks (section 5).
2. Append the stylised head, eyes, a body; cut the bust.
3. Primary shape via Lattice + Hooks; render front/side/¾ for the owner. **Stop for direction.**
4. Multires + masked Displace for secondary forms.
5. GN hair. **Stop for direction** (hair is half the character's silhouette).
6. Vertex colour, shading, lighting, final render.
7. Optional: run the stroke-replay probe and report whether a single Clay Strips stroke along a 3D path works from the bridge.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:** appending base meshes, all the declared modifiers (Lattice, Hook, Multires, Displace, Boolean, Solidify), GN hair, colour attributes, EEVEE rendering. The base-mesh bundle and the Blender sculpt demo files are local and were opened headless while writing this (`03_multires_displacement_smear.blend` carries 11 Multires modifiers at levels 3–5; `01_sculpt_grab_silhouette.blend` meshes reach 86,779 verts).
- **Painful today:**
  - **Brush strokes are GUI-gated.** `sculpt.brush_stroke`'s poll needs an area and region; replay is keyed on screen-space mouse events ([03-trace](../discovery/s01-modeling/03-trace.md) §1.2, row `sculpt.brush_stroke`; [L-009](../discovery/ledger.md): "brush → field or 3D path"). Snake Hook, Clay Strips and Crease have no declarative twin.
  - **Dyntopo, Mask Extract, `sculpt.expand` and cloth filters** are mode- or event-gated (`sculpt.expand` has no exec: [03-trace](../discovery/s01-modeling/03-trace.md) §1.2) ([L-001](../discovery/ledger.md)).
  - **Sculpt undo is separate** from the edit-mesh undo, and Python calls push no undo by default, so iterating on a sculpt from the bridge has no history ([L-008](../discovery/ledger.md)).
  - **Vertex-group masks for Displace** must be written by hand from face sets; sculpt masks (`.sculpt_mask`) are attributes but not a modifier input.
- **Not feasible today:** the expressive, stroke-by-stroke sculpting that defines the original. Even if replay works, an agent has no sense of where the next stroke should go except by rendering and looking, which is layer 5 (a warning, not a gate).

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Evaluated head + body: non-manifold edges (excluding the intended neck/bust boundary), degenerate faces | 0 outside the boundary loop; 0 degenerate |
| 1 Validity | Self-intersection after deformation (BVH overlap of the head with itself) | 0 intersecting face pairs |
| 2 Spec | Proportions measured from landmark vertices (stored as vertex indices from the base mesh): head height / eye spacing, chin-to-nose / nose-to-brow | each within ± 5% of the brief |
| 2 Spec | Bilateral symmetry of the face region (mirror-distance RMS) before deliberate asymmetry | ≤ 1 mm |
| 2 Spec | Topology kept from the base mesh | quad ratio ≥ 98%; base vertex count unchanged under the modifiers |
| 2 Spec | Colour coverage: every face has a non-default colour; freckles only inside the cheek/nose face sets | 100%; 0 freckle samples outside |
| 3 Reference | Undeformed stack vs the original base mesh (all deform weights = 0) | Hausdorff distance < 1e-5 m |
| 4 Downstream | Readiness for rigging: neck boundary is one clean loop; eyes fit sockets | 1 boundary loop; eye-to-socket gap 0.5–2 mm all round |
| 4 Downstream | Render artefacts: no NaN/black pixels, hair tubes not z-fighting the scalp | 0 black pixels inside the silhouette; min hair-to-scalp offset ≥ 0.5 mm |
| 5 Appearance (warning) | Vision model on front / side / ¾ renders vs the brief ("stylised young woman, voluminous red curls, freckles, soft smile") | warn on any mismatch |
| 6 Taste (owner) | Does it have charm and a readable personality? Would you put it next to the original? | owner judgement, expected to fail on the first pass |

## 6. Where the human is still needed

- **The face.** Likeness, appeal, the exact curve of a smile or the asymmetry that makes a face alive. This is the whole artwork, and today's vision models judge it worse than people (RFC R6 layer 5 note). The agent can make parameter sweeps (30 variants of jaw and eye spacing) for the owner to pick from, which turns taste into choosing.
- **Hair design.** Silhouette and flow of the curls carry the character; the agent can generate options, not choose.
- **Whether declared deformation is enough.** The owner must decide the G1 question in the S01 brief: do we want agent strokes at all, or an agent that stays declarative and hands the last 20% to a human sculptor?

## 7. Effort

- **First slice (live demo, ~1 day):** in the live window, a grey stylised head appears from the base-mesh bundle. A lattice cage shows around it and the head reshapes as parameters change (wider jaw, smaller chin), each step captured by `snap.py`. The mesh densifies under Multires and soft cheek volumes swell. Red curls grow out of the scalp as GN tubes. Then the colours flood in (skin, lips, freckles) and the viewport switches to Rendered (EEVEE) with the three-point light. The day ends with a front / side / ¾ contact sheet and the check report. Expect it to read as a competent mannequin, not as Amber.
- **Full reproduction to the original's quality:** realistically **not** an agent-only job today. With a human sculptor doing the final form pass: ~1–2 agent-days of setup, hair and colour plus ~1–3 human-days of sculpting and direction. Render compute is trivial (EEVEE stills).

## 8. Risks and unknowns

- **Stroke replay headless or via the bridge is unproven** (open probe 2 in [03-trace §7](../discovery/s01-modeling/03-trace.md)).
- **Lattice/Hook control is coarse;** faces need fine control near the eyes and lips, which may push us back to strokes.
- **GN curve hair can look "procedural"** (too regular) without hand-placed guides.
- **Licence of the base meshes:** the `License` text inside `human_base_meshes_bundle.blend` reads "Creative Commons Attribution 4.0 … © Blender Foundation" (and names the Rain rig, apparently copied). Treat the bundle as CC-BY 4.0 and credit it until confirmed otherwise.
- **Vision checks are weak on faces;** do not let a layer-5 pass suggest the bust is good.

## 9. Sources

- [BlenderNation: Behind the Scenes — Amber Bust](https://www.blendernation.com/2020/10/07/behind-the-scenes-amber-bust/) (verified on fetch: separate objects, brushes, dyntopo hair, mask extract, sculpt-mode vertex colour, EEVEE 3-point + HDRI, Principled with SSS)
- [00-index.md § 18](00-index.md)
- [S01 brief §7 (G1 question)](../discovery/s01-modeling/05-brief.md), [S01 trace](../discovery/s01-modeling/03-trace.md) (`sculpt.brush_stroke`, `sculpt.expand`)
- [Transformation ledger](../discovery/ledger.md) (L-001, L-006, L-008, L-009)
- [RFC 0001 § R1 gray zones, § R6](../rfc/0001-newblender.md)
- [Human Base Meshes bundle v1.4.1](https://download.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip), local copy; sculpt demo files from [download.blender.org/demo/sculpt_mode/](https://download.blender.org/demo/sculpt_mode/); facts above measured headless on Blender 5.2.2 while writing this file.
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`
