# S01 Modeling — Pass 1 "Read": the workflow script

> **Pass 1 of the S01 Modeling pilot.** This is the *human lens*: how professionals model in Blender,
> written as ordered steps, so Pass 2 can trace each step into the source and Pass 3 can judge it.
> Facts are cited. Anything that is not stated by a source is marked **Interpretation:** or `†`.
> Date: 2026-10-07.

---

## 1. Scope & sources

**In scope:** mesh modeling of a production asset from approved design to hand-off — hard-surface props
and organic characters (sculpt → retopology), up to UVs and delivery to rigging and shading.
**Out of scope:** texturing, shading networks, rig building, Geometry Nodes asset authoring, sets (the
Studio's own "Sets" section is still empty — `SG:asset-creation/modeling.md:132-136`).

Citation prefixes (local root `~/agent-native-lab-data/sources/blender/projects.blender.org/`):

| Prefix | Location | What it is |
|---|---|---|
| `SG:` | `studio/blender-studio-tools/docs/artist-guide/` | Blender Studio pipeline / artist guide (primary). `modeling.md` is marked *WIP, Oct 2023* (`:3-5`) |
| `NC:` | `studio/blender-studio-tools/docs/naming-conventions/` | Studio naming conventions |
| `AP:` | `studio/blender-studio-tools/docs/addons/asset_pipeline.md` | Studio Asset Pipeline add-on (task layers) |
| `BM:` | `blender/blender-manual/manual/` | Blender reference manual (what the UI does, keys) |
| `MAS:` | `~/agent-native-lab/knowledge/blender/MASTERY.md` | Prior lab synthesis (4 layers: UI / operator / data / internals) |
| `GT:` | `~/agent-native-lab/lab/blender/golden-table.md` | Prior lab trace: human path vs AI path for `bevel_smooth`, `array_row`, … |
| `W1` | https://studio.blender.org/blog/gold-modelling-the-boat/ | "Project Gold: Boat Modeling" (free blog post, 28 Nov 2024) |
| `W2` | https://studio.blender.org/blog/live-retopology-at-bcon22/ | "Live Retopology at BCON22" (free; linked from `SG:asset-creation/modeling.md:38`) |
| `W3` | https://studio.blender.org/training/stylized-character-workflow/ | Stylized Character Workflow course index (lesson titles only; free ones listed below) |
| `W4` | https://studio.blender.org/training/blender-2-8-fundamentals/ | Blender 2.8 Fundamentals, Modeling chapter (all 8 lessons free) |

Not used / not found: a "Blender 4.5 Fundamentals" course URL returned 404
(`/training/blender-4-5-fundamentals/`, `/training/blender-fundamentals/`); W4 is the fallback.
Paywalled lessons were **not** read — only their titles from the public index.

**W3 free lessons on the sculpt → retopo → UV path** (titles verbatim from the index):
Intro: *Introduction*, *Introduction Update* · Ch.1 Head Sculpting: *Defining Goals*, *Timelapse: Sculpting
Rain's Head* · Ch.2 Body & Outfit: *Creating a Primitive Body*, *Timelapse: Rains Summer Outfit* · Ch.4 Clean
Retopology: *Planning the Facial Retopology*, *Timelapse: Body Retopology* · Ch.5 Bonus: live sessions on
retopology, UV mapping, shading, rendering (index says "mostly Free"). Paid titles that name the steps (not
read): *Sculpting a Primitive Head Shape*, *Creating Clothing Basemeshes*, *Retopology Setup*, *Facial
Retopology – Edge Flow & Articulation*, *– Patches & Poles*, *– Creases & Tweaking*. The index as fetched
showed no Chapter 3.

**W4 free modeling lessons:** *Modeling Introduction, Creating Meshes, Object and Edit Mode, Mesh Selection
Mode, Extrude, Loop Cut, Bevel Tool, Knife Tool.*

---

## 2. The pipeline as the Studio practises it

```
            ┌───────────── hard-surface / static prop ─────────────┐
Reference → Setup → Blocking (live modifiers) → Movement test → Refinement ─┐
                                                                            ├→ UV → Delivery cleanup → Hand-off
Concept sculpt → Expression/pose tests → Retopology → Multires/shapes ──────┘     (Kitsu review; rigging,
            └───────────── organic character ──────────────────┘                  shading task layers)
```

- **Hard-surface variant** — stages *Reference → Setup → Blocking → Refinement* are named sections in
  `SG:asset-creation/modeling.md:90-129`; delivery list `:139-152`.
- **Organic variant** — modeling starts from a handed-over sculpt (T-pose, optional hero pose), deformation
  tests and style guides (`SG:asset-creation/modeling.md:16-20`); "the outcome usually is a final topology"
  (`:22`) via retopology (`:37`), with UVs "added at this stage" (`:35`), then multires reprojection and
  shape keys (`:65-85`).
- Task breakdown per asset type in production tracking: Characters need *Concept, Modeling, Sculpting,
  Rigging, Shading, Anim Test*; Props need *Concept, Modeling, Shading, Rigging* (`SG:kitsu.md:76`).
- Modeling is one **task layer** in the Asset Pipeline add-on, alongside Rigging and Shading
  (`AP:10`); each task layer typically has its own file (`AP:10`, example files `AP:34-37`).

---

## 3. Step tables

Column legend: **Look at** = what the artist inspects to decide; **Verify** = how they check it worked.
`†` = the cell restates generic manual behaviour, not a Studio statement of practice.

### A. Reference & design hand-over (both variants)

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 1 | Start only from an approved design | (outside Blender) obtain approved concept; stages may overlap | concept art / approval status | task status in Kitsu | `SG:asset-creation/modeling.md:9-11` |
| 2 | Organic: receive the design sculpt and its tests | open handed-over T-pose sculpt, hero pose, deformation tests, style guide | expressions & poses, limitations | — | `SG:asset-creation/modeling.md:16-20` |
| 3 | Hard-surface: get real dimensions | webshops / manufacturer sites; ideally hold and measure the object | dimensions, photos, videos | — | `SG:asset-creation/modeling.md:92` |
| 4 | Understand moving parts | build a collage: videos, photos, technical diagrams, multi-angle blueprints | how parts slide/move | — | `SG:asset-creation/modeling.md:94-96`; W1 (Pen Duick research, model-builder forum images) |
| 5 | Make blueprints trustworthy | straighten blueprint lines before modeling | vertical/horizontal lines | lines perfectly straight | `SG:asset-creation/modeling.md:96` |
| 6 | Put reference into the viewport | add an Image Empty (reference / blueprint) | the image behind the mesh | † image aligned to axis view | `BM:modeling/empties.rst:70-71`, `:91-113` |

### B. Setup

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 7 | Work in real-world scale | Scene Properties → Units → Unit System (Metric) | unit fields | † dimensions read in metres | `BM:scene_layout/scene/properties.rst:56-62` |
| 8 | Create a scale guide | `Shift-A` → Mesh → Cube; set display to *Wire*; match rough dimensions | cube vs reference images | dimensions match reference | `SG:asset-creation/modeling.md:100`; `BM:modeling/meshes/primitives.rst:9-10` |
| 9 | Check scale against users of the prop | link existing assets/characters (e.g. the character's hands) | proportions side-by-side | visual match | `SG:asset-creation/modeling.md:100` |
| 10 | Compare against orthographic refs | `Numpad1/3/7` front/right/top views | silhouette vs blueprint | † overlap in ortho view | `BM:editors/3dview/navigate/viewpoint.rst:11-13` |

### C. Blocking (hard-surface)

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 11 | Block the basic shape | simple shapes, simple topology | proportions vs reference | W1: "match the proportions and shape of the hull" | `SG:asset-creation/modeling.md:104`; W1 |
| 12 | Edit geometry | `Tab` into Edit Mode; `1/2/3` vertex/edge/face select | selected elements highlight | † | `BM:editors/3dview/modes.rst:27`; `BM:modeling/meshes/selecting/introduction.rst:21-22`; W4 *Object and Edit Mode*, *Mesh Selection Mode* |
| 13 | Add form | `E` extrude, `I` inset, `Ctrl-R` loop cut (wheel = number of cuts), `K` knife | the preview while dragging | † LMB confirm / RMB cancel | `BM:modeling/meshes/tools/extrude_region.rst:12`; `BM:…/face/inset_faces.rst:13`; `BM:…/edge/loopcut_slide.rst:11-33,64`; `BM:…/mesh/knife_topology_tool.rst:13`; W4 *Extrude, Loop Cut, Knife Tool* |
| 14 | Select efficiently | `Alt-LMB` edge loop, `Ctrl-L` linked, `Ctrl-LMB` shortest path | loop highlight | — | `BM:modeling/meshes/selecting/loops.rst:16-17`; `BM:…/selecting/linked.rst:15-16,48-49` |
| 15 | Fix the last operation's values | Adjust Last Operation panel or `F9` | operator values | re-executed result in viewport | `BM:interface/undo_redo.rst:46-58`; `GT:50` (bevel step 5); `MAS:48-51` |
| 16 | Back out of a mistake | `Ctrl-Z` / `Shift-Ctrl-Z` | — | — | `BM:interface/undo_redo.rst:21-41` |
| 17 | Model one half only | add **Mirror** modifier (axis, optional Clipping, Bisect) | the mirrored half live | seam closed at plane (Clipping) | `SG:asset-creation/modeling.md:108`; `BM:modeling/modifiers/generate/mirror.rst:8,30,45-48` |
| 18 | Give planar parts thickness | **Solidify** modifier | thickness | — | `SG:asset-creation/modeling.md:109`; `BM:…/generate/solidify.rst:8` |
| 19 | Chamfer edges non-destructively | **Bevel** modifier (with Solidify), Limit Method Angle/Weight | edge highlights | — | `SG:asset-creation/modeling.md:110`; `BM:…/generate/bevel.rst:81-91`; `GT:38-53` |
| 20 | Repeat parts | **Array** modifier (relative/object offset for radial) | count, spacing | — | `SG:asset-creation/modeling.md:111`; `GT:21-34` (`array_row`; Array is GN asset in 5.2, classic one "Legacy") |
| 21 | Non-destructive part lines | **Edge Split** + *Mark Sharp* in Edit Mode, with Solidify + Bevel | shading breaks | sharp edges read in shading | `SG:asset-creation/modeling.md:112`; `BM:…/generate/edge_split.rst:11-16`; `BM:modeling/meshes/editing/edge/edge_data.rst:65` |
| 22 | Cut shapes quickly | **Boolean** modifier (Union/Difference/…, Exact/Fast solver) | resulting shape | — | `SG:asset-creation/modeling.md:113`; `BM:…/generate/booleans.rst:46-72` |
| 23 | Bend repeated parts | **Curve** modifier combined with Array | deformation along curve | — | `SG:asset-creation/modeling.md:114` |
| 24 | (Gold, real case) panel stack | plane + Solidify, EdgeSplit, Bevel, Subdivision Surface; Shrinkwrap "to avoid warping" | hull surface | — | W1 |

### D. Movement test (hard-surface, no armature)

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 25 | Make parts movable | split asset into collections; parent instanced collections to Empties | collection layout | — | `SG:asset-creation/modeling.md:116-119` |
| 26 | Simple movement | shape keys | slider motion | — | `SG:asset-creation/modeling.md:120` |
| 27 | Quick pivot set-ups | 3D cursor + basic object parenting | rotation about cursor | — | `SG:asset-creation/modeling.md:121` |
| 28 | Learn from motion | make a simplified animated version; feed findings back into the model | the animation | changes visible via instances | `SG:asset-creation/modeling.md:123` |
| 29 | Edit once, update everywhere | instance collections for repeated parts (blocks, shackles, chocks) | instances | "changes to the original are propagated" | W1 |

### E. Refinement (hard-surface)

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 30 | Commit selectively | apply chosen modifiers (`Ctrl-A` over modifier panel) | stack | — | `SG:asset-creation/modeling.md:127`; `BM:modeling/modifiers/introduction.rst:141-144` |
| 31 | Clean booleans / curvature | retopologise where needed | surface shading | — | `SG:asset-creation/modeling.md:127` |
| 32 | Add believability | screws, cables, insets, small details | close-up silhouette | — | `SG:asset-creation/modeling.md:129` |
| 33 | Control smoothness & edge sharpness | Subdivision Surface modifier; `Shift-E` crease; manual `Ctrl-B` bevels | highlights on edges | — | `SG:asset-creation/modeling.md:129`; `BM:…/generate/subdivision_surface.rst:59-60`; `BM:…/edge/edge_data.rst:37-38`; `BM:…/edge/bevel.rst:15` |
| 34 | Make sure big shapes survive | inspect from different angles; † `NumpadSlash` local view | silhouette from many angles | "avoid errors" by eye | `SG:asset-creation/modeling.md:129`; `BM:editors/3dview/navigate/local_view.rst:15` |
| 35 | Spend detail where the camera is | lower detail away from camera; bevel "worn" detail pass | layout camera | render iterations reviewed in the VSE | W1 |

### F. Organic: sculpt → retopology → multires

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 36 | Start the design sculpt | primitive head / primitive body, then planar forms, then smooth & stylise | silhouette, planes | — | W3 lesson titles (*Creating a Primitive Body*, free) |
| 37 | Get even resolution fast | Sculpt Mode: `R` set voxel size, `Ctrl-R` voxel remesh | density | manifold, no overlaps | `BM:sculpt_paint/sculpting/introduction/adaptive.rst:11-42` |
| 38 | Sculpt complex base shapes | Dyntopo (adds/removes topology under brush) | local detail | — | `BM:…/introduction/adaptive.rst:53-64` |
| 39 | Sculpt symmetrically | Symmetry X (tool settings) | both sides | — | `BM:sculpt_paint/sculpting/tool_settings/symmetry.rst:3-9` |
| 40 | Clothing | separate clothing base meshes, then wrinkles & folds | stretch vs compression | — | W3 lesson titles (Ch.2) |
| 41 | Answer design questions before topology | expression & pose tests | expressions | design approved | W2; `SG:asset-creation/modeling.md:19` |
| 42 | Plan the topology | draw loops on the sculpt with the Annotate tool | "patches" and "structure" | — | W2; W3 *Planning the Facial Retopology* (free) |
| 43 | Start the new mesh over the sculpt | new mesh overlapping original; Retopology overlay (see-through) | both meshes at once | fully covers & matches shape | `BM:modeling/meshes/retopology.rst:166-173`; `BM:editors/3dview/display/overlays.rst:317-321` |
| 44 | Stick verts to the surface | Snapping (header toggle or hold `Ctrl`) to original mesh | snapped vertex | — | `BM:modeling/meshes/retopology.rst:176`; `BM:editors/3dview/controls/snapping.rst:18-20` |
| 45 | Lay faces quickly | Poly Build tool | new faces | — | `BM:modeling/meshes/retopology.rst:174-175`; `BM:modeling/meshes/tools/poly_build.rst:13-14,42` |
| 46 | Retopo one side | Mesh Symmetry / X-Mirror (+ Topology Mirror) in tool settings, or Mirror modifier | mirrored side | — | `BM:modeling/meshes/tools/tool_settings.rst:45-62` |
| 47 | Follow form & deformation | edge flow along shapes/muscles; ≥3 loops + 2 proximity loops at eyes/brows/mouth | loop direction | — | W2 ("Three Curve Principle") |
| 48 | Don't over-build | "extrude and insert whatever is just enough"; add loops, realign, relax later | density | — | W2 |
| 49 | Keep quads, allow exceptions | quads with low stretching; tris/ngons in some cases | face types | — | W2; `SG:asset-creation/modeling.md:68` ("relatively evenly distributed quads") |
| 50 | Why not automatic? | (Voxel/Quadriflow remesh rejected for deforming meshes) | — | — | `BM:modeling/meshes/retopology.rst:57-63,117-119,163-165` |
| 51 | Restore sculpted detail | Multires modifier on the retopo; subdivide; reproject details | surface detail | — | `SG:asset-creation/modeling.md:67-68`; `BM:modeling/modifiers/generate/multiresolution.rst:9-25` |
| 52 | Make hand-off easier | helper shape keys (eyes/mouth open-close, can be driven by one property); hero-pose shape keys | shape sliders | used by texturing/rigging | `SG:asset-creation/modeling.md:28-29,78-85` |
| 53 | Keep sculpt detail as data | bake sculpted details to textures | baked maps | — | `SG:asset-creation/modeling.md:26,76` |

### G. UV hand-over (both variants)

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 54 | Place seams with topology | Edge → Mark Seam (topology dictates seams; vital for clothing) | edge loops | — | `SG:asset-creation/modeling.md:51`; `BM:modeling/meshes/editing/edge/edge_data.rst:59`; `BM:modeling/meshes/uv/unwrapping/introduction.rst:68` |
| 55 | Unwrap | `U` → Unwrap / Smart UV Project | UV Editor islands | — | `BM:modeling/meshes/editing/uv.rst:12-20,100` |
| 56 | Minimise stretch, even texel density | UV Editor *Display Stretch*; UDIMs ordered by detail; reduce hidden parts | stretch colours, island size | — | `SG:asset-creation/modeling.md:53-56`; `BM:editors/uv/overlays.rst:53-63` |
| 57 | Align texture patterns (cloth) | add a secondary, pattern-aligned UV map | pattern on surface | — | `SG:asset-creation/modeling.md:58-60` |
| 58 | Serve shading's needs | "a UV pass based on the requirements from Shading" | shading requirements | — | W1; `SG:asset-creation/shading.md:38-40` |

### H. Delivery cleanup & hand-off

| # | Human intent | What they do in the UI | Look at | Verify | Source |
|---|---|---|---|---|---|
| 59 | Remove doubles | `M` → By Distance (Merge by Distance) | vertex count change | — | `SG:asset-creation/modeling.md:143`; `BM:modeling/meshes/editing/mesh/merge.rst:14,31` |
| 60 | Consistent normals | *Face Orientation* overlay; `Shift-N` Recalculate Outside | red faces on outside | no red visible | `SG:asset-creation/modeling.md:144`; `BM:editors/3dview/display/overlays.rst:204-210`; `BM:…/mesh/normals.rst:53-61` |
| 61 | Smooth shading | Object → Shade Smooth | shading | — | `SG:asset-creation/modeling.md:145`; `BM:scene_layout/object/editing/shading.rst:6-20` |
| 62 | Clean transforms | `Ctrl-A` → Scale (and Location/Rotation if needed) | N-panel scale = 1 | — | `SG:asset-creation/modeling.md:146`; `BM:scene_layout/object/editing/apply.rst:9-25` |
| 63 | Bake the stack where static | apply "most modifiers … best to have static" | modifier stack | — | `SG:asset-creation/modeling.md:147` |
| 64 | Protect UVs | re-check UV maps after cleanup | UV Editor | — | `SG:asset-creation/modeling.md:148` |
| 65 | Name and sort | rename objects/collections to convention (`GEO-…`, `CH-…`); Batch Rename | Outliner | Asset Pipeline add-on enforces `_00x` | `SG:asset-creation/modeling.md:149`; `NC:datablock-names.md:27-58` |
| 66 | Help shading/animation start | placeholder materials with viewport colours | viewport colour | — | `SG:asset-creation/modeling.md:150` |
| 67 | Strip noise | delete unused attributes/data | Data properties | — | `SG:asset-creation/modeling.md:151` |
| 68 | Mark deformation pivots | add Empties at joints/pivots | empties in viewport | — | `SG:asset-creation/modeling.md:27,152` |
| 69 | Organic cleanup | applied transforms, manifold check, naming, dummy materials | — | manifold check | `SG:asset-creation/modeling.md:30` |
| 70 | Get sign-off | Kitsu status `WIP → WFA` (show director) → `DONE` / `GO` / `RTK` | review feedback | approval | `SG:kitsu.md:58-70` |
| 71 | Publish modeling data | Asset Pipeline: modeling task layer owns objects; push owned data to publish, pull the rest | Asset Pipeline sidebar | — | `AP:10-18,40` |
| 72 | Hand to rigging | rig generated (CloudRig) on final retopo **or** "messy automatic retopo" for previz | — | — | `SG:asset-creation/rigging.md:10` |
| 73 | Close the loop | animation stress tests → rigging decides whether modeling tweaks are needed; repeat | deformations | — | `SG:asset-creation/animation-testing.md:21-27` |

73 steps (35 hard-surface-specific or shared blocking/refinement, 18 organic, 20 shared UV/delivery/hand-off).

---

## 4. Conventions & hand-off rules

| Topic | Rule (as stated) | Source |
|---|---|---|
| Naming case | `lower_underscore_case`, ALL-CAPS prefixes/suffixes; `-` hierarchy, `.` symmetry/variant | `NC:datablock-names.md:7-12` |
| Unique namespace | asset identifier in every datablock name (e.g. `esprite`) | `NC:datablock-names.md:14-21` |
| Asset root collection | type prefix + name: `CH-`, `PR-`, `LI-`, `SE-`, `LG-`, `CA-` | `NC:datablock-names.md:27-35` |
| Object prefixes | `GEO` rendered geometry, `HLP` helpers/empties, `TMP` placeholder, `RIG`, `WGT`, … | `NC:datablock-names.md:39-49` |
| Mesh names | mesh & shape-key datablocks named as the object; `.00x` → `_00x` | `NC:datablock-names.md:56-58` |
| Symmetry suffix | exactly `.L` / `.R` only for truly symmetric pieces | `NC:datablock-names.md:66-68` |
| Modifiers in blocking | use modifiers for speed and later flexibility | `SG:asset-creation/modeling.md:104` |
| Modifiers in refinement | "strategically apply" to stay flexible before committing | `SG:asset-creation/modeling.md:127` |
| Modifiers at delivery | "Apply most modifiers" — those best static | `SG:asset-creation/modeling.md:147` |
| Modifiers as transferable data | Modifiers are a task-layer-owned transferable data type (so some survive the publish) | `AP:18-22` |
| Topology (organic) | optimized for shading/texturing/rigging/animation; evenly distributed quads for multires | `SG:asset-creation/modeling.md:34,68` |
| Topology (deforming) | must follow form; automatic remesh not suitable, done manually | `BM:modeling/meshes/retopology.rst:60-63,163-165` |
| Scale/units | match real dimensions; apply object scale at delivery | `SG:asset-creation/modeling.md:100,146` |
| Origin / pivots | apply location/rotation "if needed"; pivots marked with Empties | `SG:asset-creation/modeling.md:146,152` |
| Mirror | Mirror modifier "if the asset is symmetrical"; mirrors across object origin | `SG:asset-creation/modeling.md:108`; `BM:modeling/modifiers/generate/mirror.rst:8` |
| Object data sharing | multiple objects sharing one mesh not supported by Asset Pipeline | `AP:12` |
| Shading data under topology change | data layers (UVs, colour attributes) must be re-checked after topology changes | `SG:asset-creation/shading.md:36` |

---

## 5. Observations through the four "dead facts"

**[DF1] human is the operator**
- Every stage's decision input is a human-held artefact: approved concept (`SG:…/modeling.md:9`), a person
  physically measuring the object (`:92`), director review in Kitsu (`SG:kitsu.md:58-70`).
- Retopology is explicitly human-only: "no perfect automatic tools exist … it has to be done manually"
  (`BM:modeling/meshes/retopology.rst:61-63`).
- Rigging accepts a "messy automatic retopo" for previz (`SG:…/rigging.md:10`) — the only place the guide
  accepts machine topology. *Interpretation:* the human retopo gate is about final quality, not about
  downstream tools being unable to proceed.

**[DF2] humans write the code**
- The Studio's productivity tools are add-ons written by staff (CloudRig, Easy Weight, Pose Shape Keys,
  Asset Pipeline) — `SG:…/rigging.md:9-29`, `AP:4`. Sculpt Layers is third-party (`SG:…/modeling.md:71`).
- Naming conventions are "enforced by add-ons wherever possible" (`NC:datablock-names.md:16,57`).
  *Interpretation:* the convention layer is already half-machine; rules exist in prose plus custom code.

**[DF3] tiny imperative steps**
- Blocking is a long chain of single operators (`E`, `I`, `Ctrl-R`, `K`, `Ctrl-B`) each tweaked through F9 —
  rows 13–15. The golden table measured `bevel_smooth` at 7 steps / 11 inputs / 7 operators vs one
  declarative modifier write (`GT:15,38-53`).
- The Studio itself prefers declarative, live modifiers during blocking (`SG:…/modeling.md:104`) and
  applies them only at the end (`:127,147`). *Interpretation:* the experts already route around DF3 in the
  modifier stack; the imperative residue is topology work (retopo, cleanup, seams).
- Delivery is a 10-item manual checklist (`SG:…/modeling.md:143-152`) with no stated automation.

**[DF4] viewport + human eye verify**
- Verification is visual in almost every row: Face Orientation red faces (`BM:…/overlays.rst:204-210`),
  "inspecting the model from different angles" (`SG:…/modeling.md:129`), Retopology overlay
  (`BM:…/overlays.rst:317-321`), UV stretch display (`BM:editors/uv/overlays.rst:53-63`), rendered
  iterations reviewed in the VSE (W1).
- Only a few checks are numeric/structural: Merge by Distance, manifold check, applied scale
  (`SG:…/modeling.md:30,143,146`). *Interpretation:* these are the obvious first candidates for
  machine-checkable assertions.

---

## 6. Open questions for the Dissect pass

Count in real Studio `.blend` files (Sprite Fright, Charge, Gold, Wing It assets where available):

1. **Modifiers live vs applied** at delivery: per `GEO-` object, modifier count and types; which survive in
   published files (Mirror? Subsurf? Bevel?). Tests "apply most modifiers" (`:147`).
2. **Ngon / tri / quad ratio** on hard-surface vs organic meshes; tests "evenly distributed quads" (`:68`)
   and W2's "tris/ngons in some cases".
3. **Mirror usage**: Mirror modifier present, applied (symmetric vertex positions), or `.L/.R` split objects.
4. **Applied transforms**: share of objects with scale ≠ 1 or non-identity rotation.
5. **Doubles / non-manifold / flipped normals** remaining after delivery (checklist compliance).
6. **UV maps**: count per mesh, presence of secondary pattern-aligned maps, UDIM tiles.
7. **Shape keys**: helper/hero-pose keys present on characters; drivers linking eyes/mouth keys.
8. **Pivot Empties** (`HLP-`) per asset; **instanced collections** for repeated parts (W1).
9. **Naming compliance**: % datablocks matching the prefix + namespace pattern; leftover `.00x`.
10. **Multires**: retained on published meshes or baked out?
11. **Boolean residue**: Boolean modifiers or cutter objects left in published files.
12. **Density**: face count per asset type, to size what an agent must reason about.

Also for Trace (Pass 2): map rows 13, 15, 17–22, 37, 43–45, 55, 59–62 to their operators / RNA in source,
reusing `GT:` for bevel and array.
