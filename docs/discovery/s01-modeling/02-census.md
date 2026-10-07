# S01 Pass 2 — Dissect: what real production files actually contain

- **Date:** 2026-10-07 · **Blender:** 5.2.2 LTS, headless, `--factory-startup --disable-autoexec` (embedded scripts and Python drivers never ran; the logs show blocked PyDrivers, as intended)
- **Tools:** `tools/census/census.py` (per file) → `tools/census/aggregate.py`
- **Raw data:** `~/newblender-data/census/*.json`, `~/newblender-data/census_summary.json`

## Corpus (78 files, all free downloads)

| Group | Files | What |
|---|---|---|
| **Assets** (authored data) | 51 | Sprite Fright shot library (5 chars, 9 env sets, 13 props, node libs, camera rig, light templates), Gold splash asset pipeline (published chars, corals, kelp, FX, node toolkits incl. `procedural_modeling.blend`), Human Base Meshes v1.4.1, Cube Diorama, VDM brush demo, 3 sculpt demos, cloth-brush demo |
| **Shots** (assembly) | 27 | Sprite Fright 030_0020_A anim/A/B/C/lighting files, splash scenes 4.2 / 4.3 / 4.5 / 5.1 / 5.2 |

**Counting rules:** topology counts only meshes local to their file, so linked data is never counted twice. Modifier counts are per file and include linked objects.

**Bias warning:**

- The sample is dominated by Blender Studio stylised animated films: organic forms, subdivision workflows.
- Hard-surface, archviz, game and CAD-like modelling are under-represented.
- Treat the numbers as "how this studio models", not "how everyone models".

## Findings (asset files; facts)

| Measure | Value | Plain meaning |
|---|---|---|
| Local meshes | 1,403 meshes, 1.19M faces | |
| Face mix | **94.5% quads**, 5.4% tris, **0.1% ngons** | Production topology is almost all quads. Only 13.5% of meshes contain any ngon at all. |
| UVs | **92.2%** of meshes have UV layers | UV unwrapping is part of nearly every asset (S02 matters to modelling) |
| Shape keys | 46 meshes | Mostly character faces/correctives |
| Median mesh size | **111 vertices** | Most meshes are small parts; detail comes from modifiers |
| Modifiers | **9,317** on asset objects | Non-destructive stacks are the norm, not the exception |
| Top modifiers | SUBSURF 5,003 (54%) · DISPLACE 920 · **NODES (Geometry Nodes) 836** · SIMPLE_DEFORM 741 · SMOOTH 416 · SOLIDIFY 399 · VERTEX_WEIGHT_MIX 191 · ARMATURE 137 · MULTIRES 91 · LATTICE 90 · MIRROR 80 | Low-poly cage + live subdivision is the dominant modelling pattern |
| Rare modifiers | BEVEL 59 · DECIMATE 14 · ARRAY 9 · BOOLEAN 6 · WELD 1 | Hard-surface modifiers are rare in this corpus (see bias) |
| Stack depth | 1 modifier: 3,584 objects · 2: 1,265 · 3: 552 · 4+: 315 (max 15) | Mostly shallow stacks, with a long tail |
| Node groups | 170 Geometry Nodes · 650 shader · 3 compositor | GN is already a modelling tool in production |
| GN nodes used most | Join Geometry, Realize Instances, Object Info, Set Shade Smooth, Collection Info, Boolean Math, Edge Angle | Assembly and shading-prep utilities more than "procedural modelling from scratch" |
| Unresolved nodes | `NodeUndefined` 1,512 in assets, 1,094 in shots | Node types this 5.2.2 build doesn't recognise (add-on or version drift). **Open question.** |
| Linking | 162 library references; 5,996 linked objects; 127 overrides | Assets are themselves assembled from other assets |

## Findings (shot files; facts)

| Measure | Value | Plain meaning |
|---|---|---|
| Overrides | **9,266** library overrides | Shot assembly is override-heavy: the redesign target from 03c S06 |
| Linked objects | 16,946 | Shots are mostly links, not authored geometry |
| Modifiers | 35,275: SUBSURF 9,248 · **NODES 8,423** · LATTICE 3,722 · ARMATURE 3,553 · HOOK 2,078 · CORRECTIVE_SMOOTH 1,350 | Deformation and GN evaluation dominate at shot time |
| GN trees | 651; most common nodes: Switch, Capture Attribute, Compare, Field on Domain, Position, Set Position, Random Value, Named Attribute | Field-based attribute logic is the production idiom |
| Deep stacks | 123 objects with 14 modifiers, 124 with 15 | Character rigs with long deform stacks |

## What this means for the workflow script (Pass 1) — interpretation

1. **Modelling output is a live recipe, not a final mesh** [DF3]. 91% of mesh objects in asset files carry modifiers. The authored artefact is a small cage plus a stack of declared operations. That is already close to an agent-native "declare the outcome" form. The destructive edit-mode steps happen mostly on the cage.
2. **Topology rules are strict and checkable** [DF4]. A 94.5% quad / 0.1% ngon outcome means the human "eyeball the wireframe" check can become a measured gate.
3. **Geometry Nodes is already production modelling infrastructure** in both assets and shots. An agent-native modelling layer should treat GN trees as first-class output, not an afterthought.
4. **Hard-surface ops (bevel, boolean, array) are rare here.** That reflects the studio's style, not a general truth. A hard-surface corpus is needed before any verdict on those capabilities.

## Answers to Pass 1's open questions

| Pass 1 question | Answer |
|---|---|
| Modifiers live vs applied? | Live: 91% of mesh objects carry modifiers in asset files |
| Ngon/tri ratio | 0.1% ngons, 5.4% tris |
| Mirror usage | 80 Mirror modifiers (assets), 309 (shots) |
| Shape keys | 46 meshes (assets), 224 (shots) |
| Multires kept? | 91 Multires modifiers (assets) |
| Leftover booleans | 6 Boolean modifiers (assets) |
| Applied scale, duplicate vertices, flipped normals, naming compliance, UDIM count, pivot Empties | **Not yet measured.** Needs census v2. |

## Gaps and next steps

- **Explain `NodeUndefined`:** add-on node types, removed nodes, or version drift in 4.2–4.5 files opened in 5.2.2.
- **Add a hard-surface / archviz corpus:** Cycles demos (Classroom, Barcelona Pavilion), benchmark scenes, the GN demo set.
- **Per-object census of edit-mode history is impossible.** `.blend` files store results, not the steps that made them. The human steps come only from Pass 1 docs and (optionally) live GUI sessions.
