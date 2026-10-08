# Transformation ledger

Every candidate change that would turn Blender into newblender, with its evidence. The ledger is cross-stage: later stages add evidence to existing entries or open new ones.

- **Status values:**
  - `proposed`: from discovery
  - `probing`: a runtime test is running
  - `accepted` / `rejected`: decided by the owner
- **Evidence levels** (lab #9 ladder, simplified):
  - **L1:** documented and traced in source
  - **L2:** reproduced at runtime
  - **L3:** prototyped
  - **L4:** benchmarked against stock Blender
  - **L5:** proven in production use

| ID | Change | Evidence | Modules touched | Level | Status | Dead fact |
|---|---|---|---|---|---|---|
| **L-001** | **Replace modes with explicit editing sessions.** Mesh is canonical; BMesh is opened, edited and flushed explicitly, with no implicit sync on a mode switch. | 178/320 modelling ops gated by mode; `mode_set` dispatches by operator name; stale `Mesh` in edit mode; conversion cost never removed (S01 [03](s01-modeling/03-trace.md) §5.1, §5.13; [04](s01-modeling/04-why.md) Themes 1–2) | `editors/object/object_modes.cc`, `object_edit.cc`, `editors/mesh/editmesh_utils.cc`, `bmesh/intern/bmesh_mesh_convert.cc` | L1 | proposed | DF1 |
| **L-002** | **Selection-as-scope → explicit element sets.** Every edit takes indices or an attribute mask; selection becomes an optional, plain attribute. | 56 "remove" cards; `loop_select` exec already index-driven; `.select_*` already boolean attributes (S01 03 §2; 04 §3) | `editors/mesh/editmesh_select*.cc`, bmop slot inputs | L1 | proposed | DF1 |
| **L-003** | **Return results, not statuses.** Every edit returns a diff (created / deleted / changed) plus validity checks. | Operators end at `DEG_id_tag_update` + redraw; `EDBM_op_finish` only checks for errors (03 §5.12); 03c X2 "operators return only status" · **P01:** 4 of 21 region-borrowed operators returned FINISHED with real arguments and changed nothing measurable ([probe](probes/p01-context-override.md)) | `windowmanager` operator return path, `editmesh_utils.cc`, bmop output slots | L2 | proposed | DF4 |
| **L-004** | **Hidden context defaults → explicit parameters; machine-readable preconditions** in place of polls that encode button location. | Cursor, view axis, tool settings and local view read inside exec; heuristic wrong for 50%; poll ≠ need (03 §5.5–5.6) · **P01:** 0/23 region-gated operators pass poll headless, 21/23 pass once any (never-drawn) region is supplied; loop/ring/path pick then work from indices alone ([probe](probes/p01-context-override.md)) | `editors/*` polls and execs, `screen_ops.cc` | L2 | proposed | DF2 |
| **L-005** | **Expose the bmop slot schema as a generated, typed command vocabulary** (83 bmops) for agent topology edits. | Printf-style `EDBM_op_init` format strings parsed into typed slots (`bmesh_opdefines.cc`) (03 §5.7; 04 Theme 6) | `bmesh/intern/bmesh_opdefines.cc`, `bmesh_operators.cc` | L1 | proposed | DF2, DF3 |
| **L-006** | **Declarative-first artefact.** The modifier / GN recipe is the primary output, stored and diffed as code. | 91% of mesh objects carry modifiers; 68% of geometry ops have twins; nodes-as-code endorsed upstream (02; 03 §3; 03c S04) | `modifiers/`, `nodes/`, `nodebpy` | L1 | proposed | DF3 |
| **L-007** | **Converge duplicated cores on Mesh-native `geometry::`**, following upstream (e.g. the two bevels). | `BM_mesh_bevel` and `geometry::mesh_bevel` coexist; node tools round-trip BMesh↔Mesh (03 §5.9) | `bmesh/tools/`, `geometry/intern/` | L1 | proposed | DF3 |
| **L-008** | **Differential transactions and branching** from Euler-operator inverses, replacing snapshot undo; agent calls always transactional. | Full BMesh→Mesh copy per undo step; Python calls push no undo by default (03 §5.4, §5.11; 04 Themes 3, 6) · **P01:** 5 sculpt gesture operators segfault in their undo push in a windowless session ([probe](probes/p01-context-override.md)) | `editors/mesh/editmesh_undo.cc`, `bmesh/intern/bmesh_core.cc` | L1 | proposed | DF1 |
| **L-009** | **Placement tools re-specified as data:** knife → cut path or plane; retopo → target loops; brush → field or 3D path. No mouse shims. | 27 gui-event ops, 14 with no twin; node tools already capture mouse/region as RNA props (03 §5.3, §5.14) | `editmesh_knife.cc`, polybuild, `paint_stroke.cc`, `node_group_operator.cc` | L1 | proposed | DF1, DF4 |
| **L-010** | **Machine QA gates** replace eye checks: quad ratio, manifold, doubles, normals, applied scale, naming; plus an isomorphism compare. | Studio checks are mostly visual; 94.5% quads shows the rules are real; `mesh_comparison` exists (01 §5; 02; 04 §3) | new, on `blenkernel` mesh queries | L1 | proposed | DF4 |
| **L-011** | **Headless boot profile:** empty, windowless, deterministic; no default cube, and no CLI-only settings. | 03c X2 (bpy module boots the default cube, CLI flags without API); transform needs only window+screen from `startup.blend` (03 §1.1) · **P01:** the same 5 crashes show edit code assuming a windowed session ([probe](probes/p01-context-override.md)) | `source/creator/`, `windowmanager/intern/wm_init_exit.cc` | L1 | proposed | DF1 |
