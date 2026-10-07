# S01 Modeling — Stage brief (pilot)

- **Date:** 2026-10-07 · **Status:** draft for owner review
- **Blender:** 5.2.2 LTS
- **Built from:**
  - [01 Workflow script](01-workflow-script.md): 73 cited human steps
  - [02 Census](02-census.md): 78 free production files
  - [03 Trace](03-trace.md): 320 operators, 70 poll bodies read, ~70 traced to the core
  - [04 Why](04-why.md): 38 sources, 34 opened
  - [Capability cards](../capabilities/): 320 YAML
  - [Transformation ledger](../ledger.md)
- **Evidence level:** L1 (documented and traced in source). Nothing here has been changed or benchmarked yet. The runtime probes are listed in §8.

## 1. What modelling is, as professionals do it

Blender Studio models in eight stages. Each stage is built for the next one.

| Stage | Hard-surface prop | Organic character |
|---|---|---|
| Reference and design | Real dimensions, blueprints | Hand-off from the design sculpt (T-pose, hero pose, deformation tests) |
| Setup → blocking | Low cage plus **live modifiers**: Mirror, Solidify, Bevel, Array, Edge Split, Boolean | Sculpt with voxel remesh / dyntopo, symmetry |
| Movement test / design check | Collections, instances, shape keys | Expression and pose tests |
| Refinement / retopology | Selective apply, retopo where needed, small detail | **Manual retopology** over the sculpt (annotate loops, snap, Poly Build), then Multires reprojection |
| UV hand-over | Seams follow topology, unwrap, minimise stretch | Same |
| Delivery and hand-off | 10-item cleanup checklist, naming, Asset Pipeline publish, review in Kitsu (the production-tracking tool), hand-off to rigging and shading | Same |

**The census agrees with the docs:**

- **The authored artefact is a live recipe, not a final mesh.**
  - 91% of mesh objects in asset files carry modifiers.
  - Subdivision Surface alone is 54% of all modifiers.
  - The median mesh has only 111 vertices.
- **The topology rules are real.** 94.5% of faces are quads and 0.1% are ngons.
- **Geometry Nodes (GN, Blender's node-based geometry system) is production infrastructure.** There are 836 GN modifiers in asset files and 8,423 in shot files.
- **Bias:** the sample is stylised animated film, so hard-surface is under-represented.

## 2. What survives: the essential maths and data

| Asset | Where | Why it survives |
|---|---|---|
| **SoA `Mesh` with generic named attributes** | `blenkernel` mesh, `geometry::` | The stable, attribute-generic layer. Upstream finished the migration in 2026, and new algorithms land here (GN Mesh Bevel, merge, triangulate). |
| **BMesh topology kernel** | `bmesh/` | Euler operators: each is valid by construction, has an inverse, and costs time proportional to local detail. **83 bmops** with typed slots already form an internal command vocabulary. |
| **Core algorithms** | `BM_mesh_bevel`, `BM_mesh_decimate_*`, `BKE_mesh_remesh_voxel`, `BM_mesh_boolean`, … | The modifier and the operator often call **the same function**. Imperative vs declarative is a split at the wrapper, not the algorithm. |
| **The modifier stack / GN trees** | `modifiers/`, `nodes/` | Already the professional's primary artefact, and declarative, reviewable and diffable (nodes-as-code via `nodebpy`). |
| **Topology and UV conventions** | Studio docs, census | Quads, edge flow, seams as attributes (`uv_seam`, `sharp_edge`): checkable rules, not taste. |

## 3. What goes: the ceremony

| Ceremony | Evidence | Dead fact |
|---|---|---|
| **Modes.** Edit mode is a human session: a hidden BMesh copy, synced back only on mode exit. | 178/320 operators are gated by mode alone. `mode_set` dispatches another operator *by name*. In edit mode `Mesh` is stale until exit. Conversion cost was reduced but never removed. | DF1 |
| **Selection as scope.** Select, then act. | 56 cards proposed **remove**. `loop_select`'s exec is already index-driven, but its poll demands a 3D view. | DF1 |
| **The modal veneer.** Drag to set a value. | 51 of 66 modal operators also have `exec`. Bevel's modal loop restores a snapshot and **re-runs the whole operation on every mouse move**. | DF1, DF3 |
| **Polls that encode where the button lives** | Polls describe the UI location, not what the function needs (loop_select, transform, loopcut). The name heuristic was wrong for 50%. | DF2 |
| **Hidden context defaults** | Exec reads the 3D cursor (bisect plane), the view axis (extrude_repeat), tool settings (bevel profile), and local view (multi-object filter). | DF2 |
| **Status instead of result** | Operators return FINISHED/CANCELLED. The new geometry is seen by drawing it. | DF4 |
| **Snapshot undo** | Every edit-mesh undo step stores a full BMesh→Mesh copy. Python calls push **no** undo at all by default. | DF1 |
| **Eye-based QA** | Face Orientation, overlays, "inspect from different angles". Only doubles, manifold and applied scale are numeric today. | DF4 |

## 4. Numbers

| Measure | Value |
|---|---|
| Operators in Blender 5.2.2 | 2,498 (2,210 C++, 288 Python) |
| Fail headless poll in every mode (factory scene) | 1,605 (64%), all categories |
| Modelling operators studied | 320 |
| …pass poll headless given the right mode/data | 270 (84%) |
| …truly need a GUI | 50 (16%): 23 need a region, 27 need an event stream |
| …modal / no exec | 66 / 26 |
| Geometry-changing operators with a declarative twin | 125 of 184 (68%): 55 exact, 70 approximate |
| No twin: "local topology surgery" | 59 (dissolve, fill, bridge, knife, loopcut, rip, polybuild, connect, slide, poke, …) |

## 5. Verdicts (proposed, 320 cards)

| Verdict | Count | Meaning |
|---|---|---|
| **declare** | 124 | Express as a declared outcome (modifier / GN node) that already exists. 70 need a parity check first. |
| **free** | 73 (3 contested) | Real logic trapped behind mode/selection/GUI. Make it a typed function over explicit inputs that returns a diff. |
| **keep** | 67 | Usable as a function today: stack management, object-level data ops. |
| **remove** | 56 | Ceremony: selection state, mode switches, menus. |

44 cards link back to workflow-script rows, so the human path and the code path meet on them.

## 6. The agent-native shape for modelling (proposal, interpretation)

1. **One source of truth.** SoA `Mesh` is canonical. BMesh becomes an *explicit, scoped editing session*: `open(mesh) → edits → flush() → diff`. There is no "mode" and no implicit sync.
2. **Three verb families.**
   - **Declare:** add, edit and reorder modifier / GN steps. This is the primary artefact, stored as code.
   - **Edit:** typed topology functions over **explicit element sets** (indices or attribute masks). They are generated from the bmop slot schema and the `geometry::` functions.
   - **Commit:** apply or bake a declared step into data.
3. **Explicit inputs.** Every hidden default (cursor, view axis, tool settings, local view) becomes a parameter. Preconditions are declared machine-readably, not inferred from polls.
4. **Results, not statuses.** Every call returns a diff (elements created, deleted, changed) plus validity checks. A mesh-isomorphism compare (`mesh_comparison` exists upstream) is the reference check.
5. **Transactions.** Undo and branching are built from Euler-operator inverses (differential), not whole-mesh snapshots.
6. **Placement becomes data.** Knife → a cut path or plane. Poly Build / retopology → target loops or patches. Brush → a declared deformation field or 3D path. No headless shim that fakes a mouse.
7. **Machine QA gates.** Quad ratio, ngons, manifold, doubles, normals consistency, applied scale and naming run as checks on every commit. That replaces the eye for everything except taste.

## 7. Needs the owner (contested)

| Card | Question |
|---|---|
| `sculpt.brush_stroke` | Should an agent sculpt by strokes at all, or only by declared fields? This is gray zone G1 (human-like 3D action). |
| `mesh.polybuild_*` (retopology) | The Studio says final retopology must be manual. Rigging accepts "messy automatic retopo" for previz. Is machine retopology acceptable for *final* topology? |
| `object.quadriflow_remesh` | Same question, for the automatic remesher. |

## 8. Open questions and next probes

- **Runtime probes (cheap, I can run them):**
  - Does `temp_override(area, region)` make the 23 gui-region operators work in `-b`?
  - Can a brush stroke be replayed headless?
  - Do Python calls really push no undo step?
  - Result parity of "exact" twins with different implementations (Solidify, Smooth, GN Extrude/Subdivide) via an isomorphism test.
- **Census v2:** applied scale, duplicate vertices, flipped normals, naming compliance, UDIMs, pivot Empties. Also explain the 2,606 `NodeUndefined` nodes.
- **Corpus gap:** add a hard-surface / archviz set before ruling on bevel/boolean/array usage.
- **Node tools:** enumerate the essentials node tools in 5.2. They are registered per asset and missing from the registry dump. Do any cover the 59 no-twin operators?
- **Upstream:** will GN Mesh Bevel replace `BM_mesh_bevel`? Two bevel implementations exist today.

## 9. Pilot retrospective: tune before fanning out to other stages

| What happened | Change for the next stages |
|---|---|
| The name-based gate heuristic was wrong for 50% | Pass 3 must read poll bodies. Keep the heuristic only as triage. |
| The static scan missed transform operators and macros | Extend `scan_source.py` for constant idnames and macros, so the registry and the scan agree. |
| The workflow script cites keys, not operator ids, so the step→operator map was done by hand afterwards | Pass 1 records the operator id for each step (from the keymap file). |
| The census sample is biased toward one studio style | Each stage names a counter-corpus up front. |
| Pass 3 is the expensive pass (~19 min, ~300k tokens) | Split it into parallel trace agents by operator family. |
| Cards are per operator, but many operators span stages | Cards live in the shared `docs/discovery/capabilities/`. Later stages add `human` rows and re-verdict. |
