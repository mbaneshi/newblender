# 17 — Bismuth Security Mech: how an agent could make it

| | |
|---|---|
| **Original** | Kevin Skok (S4G School for Games, Berlin), 2019, hard-surface / mechanical modelling · [80.lv](https://80.lv/articles/001agt-tips-for-mech-design-in-blender) |
| **Agent-readiness today** | **Partial.** The mechanics of hard-surface work mostly have declarative twins: Boolean, Bevel (angle- or weight-limited), Mirror, Array, Solidify, Weighted Normal, Shrinkwrap, and a headless Cycles normal bake. What does not: hand-placed support loops and cut paths (loop cut, knife, dissolve: no twin, [L-009](../discovery/ledger.md)), selection-scoped baking and UV unwrap ([L-001](../discovery/ledger.md), [L-002](../discovery/ledger.md)), and above all **the mech design itself**, which is taste. |
| **Difficulty** | **3.** A full game-ready mech (dozens of parts, high + low, bake, textures) is weeks of agent work plus real design direction; one module is a day. |
| **First slice** | One mech "hip actuator" module (housing, piston, cap, bolts) built as data with a live Boolean + Bevel + Weighted Normal stack, a derived low-poly, and a headless normal bake, with a check report and a turntable render in the live window. |

## 1. What the original actually is

- **One asset:** a game-ready security mech designed for a final thesis. Inspired by *Ghost in the Shell*, grounded in real mechanical references (80.lv).
- **Deliverables:**
  - a high-poly model (support-loop subdivision plus floating detail),
  - a low-poly game mesh with normal maps baked from the high poly,
  - textures made in Substance Painter, with decals from Photoshop,
  - cloth ammo covers simulated in Marvelous Designer.
- **Numbers:** the article gives no polycount, texture resolution or time spent (checked on fetch). Treat any figure below as a target, not a fact about the original.

## 2. How the humans made it

| Stage | Technique (from 80.lv) | Fact / interpretation |
|---|---|---|
| S01 Modeling | Blockout for proportions and silhouette, then high poly by "support loop workflow. All the support edges were placed by hand." Details as "floating geometry on top of that mesh", conformed with Shrinkwrap and vertex groups. | Fact (quoted) |
| S02 UV & texturing | High-poly detail baked into low-poly normal maps; texturing and decal placement in Substance Painter (planar projection); fine detail in Painter's height channel instead of the high poly. | Fact |
| S03 Shading | PBR materials from Painter. | Fact |
| S08 Simulation | Cloth covers in Marvelous Designer (the artist's first use). | Fact |
| S09 Rendering | Presentation renders. | Interpretation (renderer not stated) |
| Design method | "Think about how the design would work, like how it would move or how it would be interacted with." | Fact (quoted); the core of the work is functional design judgement |

Two of the five stages ran outside Blender (Painter, Marvelous). An agent-native version would replace them with in-Blender equivalents, or leave them out of scope.

## 3. How I would make it: the agent-native plan

The modern alternative to hand-placed support loops is the **bevel-plus-weighted-normals** workflow: keep the base mesh low, let a Bevel modifier (angle- or weight-limited) make the rounded edges, and let Weighted Normal fix shading. That is exactly the declarative twin pattern of the S01 trace (bevel: exact twin, same core `BM_mesh_bevel`; boolean: exact twin; [03-trace §3](../discovery/s01-modeling/03-trace.md)).

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 Blockout | **Parts as data:** boxes, cylinders and lathe profiles built in bmesh from a part list with real dimensions (piston Ø, stroke length, bolt pitch). Joints are Empties, so "how it moves" is a parent hierarchy you can rotate. | Industrial references: hydraulic cylinder catalogue dimensions | live bridge `bl.py` |
| S01 Detail | **Declared stack per part:** Boolean (Difference cutters for vents, slots, bolt holes; cutters kept as hidden objects so the cut stays editable) → Bevel (angle limit 30°, 3 segments, `harden_normals`) → Weighted Normal (keep sharp) → Mirror. Bolts are an Array or GN instances on a curve. Floating panels use Shrinkwrap with a vertex group, as the original did. | — | modifiers / GN |
| S01 Low poly | **Derived, not remodelled:** the same base parts without Bevel segments, triangulated; boolean cuts kept only where they change the silhouette. Panel lines live in the bake, not the mesh. | — | modifier toggles + apply into a copy |
| S02 UV | Box/cube projection written per loop for simple parts; for curved parts, seams from `sharp_edge` and a headless `uv.smart_project` call on the low poly. | — | bmesh UV writes; one scoped operator call |
| S02 Bake | Cycles **selected-to-active normal bake**, high → low, with cage extrusion. | — | `bpy.ops.object.bake` headless |
| S03 Shading | Instead of Painter: procedural PBR in Blender (painted metal base, edge wear from the bake's curvature/AO via a Geometry Pointiness or AO node, decals as projected image textures). Bake to texture maps for the game version. | Poly Haven metal/paint textures (CC0) | shader nodes, Cycles bake |
| S08 Cloth (optional) | Cloth modifier on a pinned cover mesh, baked headless; then applied as a mesh. Replaces Marvelous at lower fidelity. | — | Cloth sim, `ptcache` bake |
| S09 Render | Three-point + HDRI turntable, 36 frames, EEVEE preview / Cycles final. | Poly Haven HDRI | headless render |

**Build order**

1. Write the module spec and the checks (section 5) before any geometry.
2. Blockout: housing, piston rod, cylinder, end cap, 8 bolts. Pivot Empties at the joint.
3. Add cutters and the Boolean → Bevel → Weighted Normal stack. Compare the evaluated mesh against the spec.
4. Derive the low poly; unwrap; bake normals; build the material.
5. Render a 36-frame turntable plus a 2-pose test (piston retracted / extended).
6. Scale up later: legs, torso, sensor head as a kit of the same modules.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Geometry as data and declared modifiers: the chair demo already built parts this way with Mirror and Bevel (`tools/live/demos/chair_build.py`; `~/newblender-data/demos/001-chair/report.md`, 12/12 checks).
  - Booleans, bevels, weighted normals and Shrinkwrap are modifiers with plain RNA properties.
  - **Headless normal bake:** smoke-tested while writing this file on Blender 5.2.2. A bevelled high-poly cube baked onto a plain low cube with `object.bake(type='NORMAL', use_selected_to_active=True)` returned `FINISHED` and wrote a non-flat normal image (red channel spanning 0.02–0.98). Correctness of that bake was not measured; it proves only that the call runs without a GUI.
- **Painful today:**
  - **Baking is selection-scoped.** High and low must be *selected* and the low *active*; there is no "bake A onto B" function ([L-002](../discovery/ledger.md), [L-004](../discovery/ledger.md)).
  - **UV unwrap and seam marking are edit-mode, selection-scoped operators** ([L-001](../discovery/ledger.md), [L-002](../discovery/ledger.md)). Simple parts get analytic UVs; complex ones need a scoped call wrapped in a mode switch.
  - **Support loops, knife cuts, dissolves:** "local topology surgery" with no twin (59 operators; [05-brief §4](../discovery/s01-modeling/05-brief.md)). The plan avoids them by using the bevel workflow, but some shapes (a sharp transition from round to flat) still want a loop placed by hand ([L-009](../discovery/ledger.md)).
  - **Boolean results are only checked by looking.** Nothing reports that a cutter produced a sliver or a non-manifold seam; the agent must measure the evaluated mesh itself ([L-003](../discovery/ledger.md), [L-010](../discovery/ledger.md)).
- **Not feasible today:** a Substance-Painter-grade hand-painted texture pass and Marvelous-grade cloth. Blender's procedural materials and Cloth modifier are reasonable substitutes, not equals.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Evaluated high poly: non-manifold edges, loose verts, degenerate faces (area < 1e-10) | 0 / 0 / 0 |
| 1 Validity | Boolean slivers: faces with area < 1e-6 m² or any edge < 0.05 mm | 0 |
| 1 Validity | Normals outward per part (signed volume > 0) | all parts |
| 2 Spec | Dimensions from the evaluated mesh: piston rod Ø, cylinder Ø, stroke | each within ± 0.5 mm of spec |
| 2 Spec | Low-poly budget for the module | ≤ 2,500 triangles |
| 2 Spec | Naming `GEO-mech_hip_*`, cutters `CUT-*` hidden from render, scale applied | 100% compliant |
| 2 Spec | Low-poly UVs: no overlaps, inside [0,1]², texel density spread | 0 overlapping faces; density max/min ≤ 1.5 |
| 3 Reference | Bevel modifier vs `mesh.bevel` operator on the same base part (mesh-isomorphism compare, the trace's "same core" claim) | identical vertex count; Hausdorff distance < 1e-5 m |
| 3 Reference | Baked low poly vs high poly: render both from 8 views with the same lights | mean per-pixel luminance diff ≤ 3% inside the silhouette |
| 4 Downstream | **Motion test:** rotate the hip joint through its range (−30° to +45°) and extend the piston | 0 interpenetrations between rigid parts (BVH overlap test) at 16 sampled poses |
| 4 Downstream | Normal map sanity: tangent-space map mean blue ≥ 0.9; no unbaked (black) pixels inside UV islands | both pass |
| 4 Downstream | Game export: glTF round-trip of the low poly | same triangle count and material count after re-import |
| 5 Appearance (warning) | Vision model on the turntable vs the brief ("industrial hydraulic actuator, chamfered edges, vents, bolts") | warn on mismatch |
| 6 Taste (owner) | Does it read as a believable, functional mech part in the intended style? | owner yes / no + notes |

## 6. Where the human is still needed

- **Mech design.** The original's value is "believable, functional" design: deciding where a joint goes, how a cover protects a cable, what the silhouette says. An agent can follow engineering references and check that parts do not collide, but the design language (Ghost in the Shell, not Gundam) is the owner's call, best given as sketches or a reference board.
- **Detail density and rhythm.** Where to put panel lines, decals and greebles so the eye rests in the right places is taste (gray zone G1, [RFC R1](../rfc/0001-newblender.md)).
- **Texture storytelling:** wear that tells how the machine is used.

## 7. Effort

- **First slice (live demo, ~1 day):** in the live Blender window, the owner watches the actuator assemble part by part: grey blockout boxes and cylinders, then vents and bolt holes cut in as Boolean cutters appear (shown as wireframe), then edges round off as the Bevel modifier switches on. The joint Empty rotates and the piston slides to show the motion test. A side-by-side of high poly and baked low poly follows, then a turntable render and the check report in the Image and Text editors.
- **Full reproduction:** a mech kit of ~20 modules at ~3–4 agent-hours each plus assembly (~1–2 agent-weeks), bake and material work (~3 agent-days), renders (a few GPU-hours). Human direction: ~1–2 days of design review across the build, plus concept sketches if the owner wants a specific design language.

## 8. Risks and unknowns

- **Boolean robustness.** The Exact solver is slow on dense meshes and the Fast solver fails on coplanar faces; both need checks, not trust.
- **Bevel artefacts** on boolean seams (pinching where segments meet) are common; harden-normals may not fix them all.
- **The bake smoke test is not a quality test.** Cage extrusion, ray distance and skewed normals still need tuning per part.
- **Evaluating "functional" design automatically** beyond collision checks is an open problem.
- Whether a GN node tool can replace hand-placed loops for the remaining no-twin cases is an open S01 probe ([05-brief §8](../discovery/s01-modeling/05-brief.md)).

## 9. Sources

- [80.lv: 001AGT — tips for mech design in Blender](https://80.lv/articles/001agt-tips-for-mech-design-in-blender) (verified on fetch: support loops placed by hand, floating geometry, Shrinkwrap + vertex groups, Substance Painter, Marvelous Designer; no polycount or timings given)
- [00-index.md § 17](00-index.md)
- [S01 trace §3 declarative twins](../discovery/s01-modeling/03-trace.md), [S01 brief](../discovery/s01-modeling/05-brief.md)
- [Transformation ledger](../discovery/ledger.md) (L-001, L-002, L-003, L-004, L-009, L-010)
- [RFC 0001 § R6](../rfc/0001-newblender.md)
- Live bridge and chair demo: `tools/live/bl.py`, `tools/live/demos/chair_build.py`, `~/newblender-data/demos/001-chair/report.md`
- Bake smoke test: headless probe on Blender 5.2.2 LTS, run while writing this file.
