# S01 Modeling — Pass 4: Why

- **Date:** 2026-10-07 · **Pilot:** S01 Modeling · **Previous:** [03c — Inventory: the "why" layer](../03c-inventory-why.md)
- **Question:** Why is Blender's modeling stack built the way it is? What did the developers decide, what did they reject, what debt is left, and where is it heading?
- **Method:** I opened the five S01 rows from 03c and added primary sources: design tasks on projects.blender.org (read as raw JSON through the Gitea API, `/api/v1/repos/blender/blender/issues/<n>`, because the HTML pages return 403 to fetchers), code.blender.org posts, devtalk threads, the local developer docs, release notes 2.81→5.3 and a few source files.
- **Path prefixes used below:**
  - `DD` = `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender-developer-docs/docs`
  - `SRC` = `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender/source/blender`
- **Correction to 03c:** 03c summarised Winter of Quality 2026 as "mesh attribute storage migration still unfinished". The post actually says the migration was *completed*: "Completed the transition to the 'Attribute Storage' format for mesh attributes". What is still unfinished is the split storage described in Theme 1.

---

## 1. Sources

"opened" means I read the content in this pass. "listing" means I only saw it referenced or in search results.

| Item | URL/path | Year | opened? | One-line insight |
|---|---|---|---|---|
| Mesh Struct of Arrays Refactor #95965 (H. Goudey) | https://projects.blender.org/blender/blender/issues/95965 | 2022–23 | opened (body + 8 comments) | Moved from array-of-structs to SoA because SoA is "the established best practice"; closed Apr 2023 ("this task is done!"). Forward compatibility was broken on purpose, all at once in 4.0 |
| Proposal for fast high poly mesh editing #74186 (C. Barton) | https://projects.blender.org/blender/blender/issues/74186 | 2020–24 | opened (body + 32 comments) | Since 2.8 every edit builds an evaluated Mesh from the BMesh. Fix was to skip or delay that build. Closed 2024 with parts never done |
| Edit-Mesh Performance Overview #88021 (C. Barton) | https://projects.blender.org/blender/blender/issues/88021 | 2021–25 | opened | Profiling a single-vertex move: 30–50% of the time goes to drawing/GPU upload, 15–40% to the copy-on-write update, which is "redundant" in edit mode |
| Winter of Quality 2026 | https://code.blender.org/2026/02/winter-of-quality-2026/ | 2026 | opened | Attribute Storage migration done. Redo added for edge/vertex slide. Node tools now register one operator per tool |
| Node Tools Overview #101778 (H. Goudey) | https://projects.blender.org/blender/blender/issues/101778 | 2022–24 | opened | "The node group itself is the operator asset". Considered done only when any edit-mode operator can be built from nodes, which is not expected soon |
| Node Tools blog (D. Felinto) | https://code.blender.org/2023/10/node-tools/ | 2023 | opened | Tools without Python. No modal support. "Modeling operations have not being a priority yet" |
| Sculpt Brush Refactor #118145 (H. Goudey) | https://projects.blender.org/blender/blender/issues/118145 | 2024 | opened | A per-vertex macro switched between Mesh, BMesh and grids inside hot loops. Rewritten as array-based code, one implementation per data type |
| This Summer's Sculpt Mode Refactor (H. Goudey) | https://code.blender.org/2024/11/this-summers-sculpt-mode-refactor/ | 2024 | opened | PBVH had been a "catch-all storage". Sculpt mode enters 5× faster, brushes run 8× faster. Dyntopo and multires still bottlenecks |
| bf-committers "Sculpt Work" (J. Eagar) | https://archive.blender.org/lists/bf-committers/2020-October/050704.html | 2020 | opened | BMesh was never meant for high-res sculpting. Dyntopo was nearly removed |
| Design Session: Essentials Assets (devtalk) | https://devtalk.blender.org/t/2025-04-24-design-session-essentials-assets/40166 | 2025 | opened | Array is the first modifier ported to a GN asset. Rule: full feature parity, "mostly 'Single Value' inputs" |
| GN Workshop Sept 2026 | https://code.blender.org/2026/10/geometry-nodes-workshop-september-2026/ | 2026 | opened | Modal node tools are a work-in-progress PR. `nodebpy` converts node trees to Python and back. Construct Mesh node builds explicit topology |
| Dev docs: Mesh | `DD/features/objects/mesh/mesh.md:1-155` | living | opened | Two structures by design: Mesh for many elements, BMesh for small topology edits |
| Dev docs: BMesh | `DD/features/objects/mesh/bmesh.md:1-483` | living | opened | Radial-edge B-rep. Eulers guarantee valid output. Three API layers. Holes in faces deferred |
| Dev docs: Mesh comparison | `DD/features/objects/mesh/mesh_comparison.md:1-222` | living | opened | Tests compare meshes by isomorphism, not by index: a ready-made way to check geometry without looking at the viewport |
| Dev docs: Attributes | `DD/features/objects/attributes.md:1-157` | living | opened | Unique names, generic types, `for_write` const-correctness. "`BMesh` isn't supported yet" |
| Dev docs: Implicit sharing | `DD/features/core/implicit_sharing.md:1-25` | living | opened | Copy-on-write by user count: read-only when shared, mutable with one user |
| Dev docs: Undo | `DD/features/core/undo.md:1-92` | living (WIP) | opened | One stack holding several step types. "Fully relative". Undo pushes are driven by the operator system |
| Dev docs: Operators | `DD/features/interface/operators.md:1-271` | living | opened | Operator is the controller in MVC. Redo panel is generated from operator properties. Operators act on UI context |
| Dev docs: HIG Paradigms | `DD/features/interface/human_interface_guidelines/paradigms.md:1-93` | living | opened | Select→Operate, Operate→Settings, Non-modal. "Blender is for Artists … not a coders API!" |
| Dev docs: Transform | `DD/features/objects/transform.md:1-190` | old (paths stale) | opened | One generic engine over `TransData`. Modal loop with cancel rollback, undo pushed at the end |
| Dev docs: Mesh paint | `DD/features/sculpt_paint/mesh_paint.md:1-47` | living | opened | Sculpt has three storage backends (Mesh / BMesh for dyntopo / SubdivCCG grids). Paint BVH used for raycasts and partial redraws |
| Proposal: Everything Nodes | `DD/features/nodes/proposals/everything_nodes.md:1-116` | ~2019 | opened | Functions without side effects. "Function users" apply the side effects. Separate frontends and backends |
| Proposal: Breaking up the Modifier Stack | `DD/features/nodes/proposals/break_modifier_stack.md:1-61` | ~2020 | opened | Modifiers mix four concepts (Function, With Binding, Simulation, Final Output). Not all should become nodes |
| Proposal: Node Tools prototype | `DD/features/nodes/proposals/node_tools.md:1-66` | 2021 | opened | Ship tools together with node-group assets. Open question: how to package Python inside assets |
| Proposal: Mesh type requirements | `DD/features/nodes/proposals/mesh_type_requirements.md:1-90` | ~2020 | opened | Named attributes, auto-interpolation between domains, derived "intrinsic" attributes kept read-only |
| Release notes: SoA migration | `DD/release_notes/3.4/python_api.md:36-60`, `3.6/python_api.md:41-62`, `4.0/python_api.md:59-85`, `4.1` | 2022–24 | opened | Selection, hidden state, material index, edges, corners, seams, sharpness, creases and mask all moved to generic attributes |
| Release notes: edit-mode exit performance | `DD/release_notes/3.1/modeling.md:3-10`, `3.6/modeling.md:55-61` | 2022–23 | opened | BMesh→Mesh conversion was parallelised rather than removed |
| Release notes: node tools | `DD/release_notes/4.0/geometry_nodes.md:3-28`, `4.2/geometry_nodes.md:43-56`, `5.1/geometry_nodes.md:49-53`, `5.2/geometry_nodes.md:167-169` | 2023–26 | opened | Selection, 3D cursor, mouse, viewport and active-element inputs added. One idname per tool. Inputs remembered and settable from Python |
| Release notes: GN modifiers (Array etc.) | `DD/release_notes/5.0/modeling.md:5-44`, `4.1/modeling.md:5-27`, `4.2/modeling.md:10-13` | 2024–25 | opened | Auto Smooth became a modifier asset in 4.1. Six GN-based modifiers in 5.0. "The legacy array modifier is still available for now" |
| Release notes: sculpt | `DD/release_notes/4.3/sculpt.md:107-117`, `5.0/sculpt.md:36-38`, `5.2/sculpt.md:10-15`, `5.3/sculpt.md:14-15` | 2024–26 | opened | Refactor results. Undo data compressed. Voxel remesh now interpolates attributes. Multires shows attributes |
| Release notes: remesh (2.81) | `DD/release_notes/2.81/sculpt.md:66-79` | 2019 | opened | Voxel remesh is "an alternative to dynamic topology without the performance cost". QuadriFlow is slow but gives higher-quality topology |
| Source: `editmesh_undo.cc` | `SRC/editors/mesh/editmesh_undo.cc:53-100, 931-990` | current | opened | Edit-mode undo converts BMesh→Mesh on every step and deduplicates with `BLI_array_store` (chunking plus RLE for booleans) |
| Source: `ed_undo.cc` redo | `SRC/editors/undo/ed_undo.cc:651-700` | current | opened | "Adjust Last Operation" works by undo-pop then re-exec (`ED_undo_pop_op`) |
| Source: `mesh_wrapper.cc` | `SRC/blenkernel/intern/mesh_wrapper.cc:8-20` | current | opened | Implements the "lazy" answer to #74186: the evaluated mesh can wrap BMEditMesh until a caller needs arrays |
| Source: `DNA_mesh_types.h` | `SRC/makesdna/DNA_mesh_types.h:181-190` | current | opened | `AttributeStorage` for generic attributes sits next to `CustomData` for "non-generic layer data": two storages still exist |
| Source: knife / loopcut operator types | `SRC/editors/mesh/editmesh_knife.cc:4649-4664`, `editmesh_loopcut.cc:721-742` | current | opened | Knife has `invoke` and `modal` but **no `exec`**. Loop cut has `exec` |
| Edit-data attributes proposal #97452 | https://projects.blender.org/blender/blender/issues/97452 | 2022 | listing | How selection and hidden state should (not) propagate through nodes |
| GPU mesh drawing performance #87835 | https://projects.blender.org/blender/blender/issues/87835 | 2021 | listing | The largest bottleneck named in #88021 |
| Node Tools feedback thread | https://devtalk.blender.org/t/node-tools-feedback/31388 | 2023 | listing | User feedback on 4.0 node tools |
| Sculpt module meetings (2022–23) | https://devtalk.blender.org/t/2023-04-25-sculpt-texture-paint-module-meeting/29142 | 2023 | listing | Dyntopo and multires rework "in limbo" (quoted second-hand in search results, not verified) |

---

## 2. Themes

### Theme 1 — Two meshes on purpose: SoA `Mesh` for scale, `BMesh` for local topology edits

**Decided.** Blender keeps two mesh representations. `Mesh` "focuses on performance with many elements". `BMesh` is the "edit mode data structure that prioritizes implementation of small topology-changing operations" (`DD/features/objects/mesh/mesh.md:5-10`). `Mesh` went fully struct-of-arrays between 3.4 and 4.0:
- Positions are `float3`.
- Edges are `int2` (`.edge_verts`).
- Faces are just `OffsetIndices`.
- Corners are split into `.corner_vert` and `.corner_edge`.
- Every flag became a named boolean attribute: `.select_*`, `.hide_*`, `sharp_face`, `.uv_seam`, `material_index`, …

Sources: [#95965](https://projects.blender.org/blender/blender/issues/95965); `DD/release_notes/3.6/python_api.md:41-62`.

**Why.** #95965 lists the benefits: less memory touched in hot loops, SIMD, generic algorithms, and easy hand-off to the GPU and to exporters. It closes with: "it's the **established best practice**". The doc stresses that topology is stored "top-down" only. Reverse maps (corner→face, etc.) "can always be recreated" (`mesh.md:46-54`). The `bke::mesh` namespace deliberately takes raw arrays instead of `Mesh`, "to make it clear what data algorithms use and output" (`mesh.md:147-155`).

**Rejected.**
- *Packing selection and hidden into one flag array* (suggested by Campbell Barton). Hans Goudey refused: it "would negate the benefits for code simplicity". With one array per attribute, "any algorithm written for an array of booleans … can be reused" ([comment](https://projects.blender.org/blender/blender/issues/95965#issuecomment-150181)).
- *Converting to the old format on every save, indefinitely.* This would have been "convoluted" and would lose whether a layer exists. They went with a one-time forward-compatibility break in 4.0 instead: "we also need to be realistic and not try to maintain forward compatibility forever" ([comment](https://projects.blender.org/blender/blender/issues/95965#issuecomment-150183)).
- On the BMesh side, *holes in faces* were deferred to stabilise the first merge (`DD/features/objects/mesh/bmesh.md:469-477`).

**Debt.**
- (a) BMesh still uses legacy `CustomData`. The attribute docs say the C++ attribute API is preferred but "`BMesh` isn't supported yet" (`DD/features/objects/attributes.md:36-37`).
- (b) Even after the Attribute Storage migration that WoQ 2026 calls complete, `Mesh` still carries both `AttributeStorage attribute_storage` and four `CustomData` blocks "for non-generic layer data" such as deform weights (`SRC/makesdna/DNA_mesh_types.h:181-190`).
- (c) Freestyle tags became attributes on BMesh in 5.0, but "`Mesh` is not yet affected" (`DD/release_notes/5.0/modeling.md:48-54`). The migration happens one domain at a time, and the two structures drift apart while it is under way.

**Quotes.**
- "Switching to a struct of arrays format can provide significant performance improvements and code simplification." — [#95965](https://projects.blender.org/blender/blender/issues/95965)
- "It's hard to overstate how much this can simplify existing code." — [#95965 comment](https://projects.blender.org/blender/blender/issues/95965#issuecomment-150181)
- "Completed the transition to the 'Attribute Storage' format for mesh attributes." — [WoQ 2026](https://code.blender.org/2026/02/winter-of-quality-2026/)

### Theme 2 — Edit mode costs a conversion, and that cost has been reduced but not removed

**Decided.** Edit mode works on a BMesh. Everything outside edit mode (evaluation, modifiers, drawing, undo, file I/O) wants a `Mesh`. 2.7x drew the edit-mesh directly. In 2.8 it was "convenient to always create this mesh", but "this adds significant overhead, especially when making interactive mesh edits" ([#74186](https://projects.blender.org/blender/blender/issues/74186)). The fixes chosen were incremental:
- Lazy wrapping: `Mesh` wraps a `BMEditMesh` (`ME_WRAPPER_TYPE_BMESH`), "postponing the converting until it's needed or avoiding conversion entirely" (`SRC/blenkernel/intern/mesh_wrapper.cc:8-17`).
- Parallel BMesh→Mesh conversion on exit (`DD/release_notes/3.6/modeling.md:55-61`).
- Multithreaded bounds (`3.1/modeling.md:8-10`).

**Why.** The profile in [#88021](https://projects.blender.org/blender/blender/issues/88021), measured by moving one vertex on a 1.5M-quad mesh, found GPU drawing (30–50%) and the copy-on-write update (15–40%) dominate. Tessellation and normals take about 10–15% each. Brecht agreed on lazy init with a double-checked lock rather than freeing after each use, because "if we free it everytime that might happen a lot and become a performance problem in itself" ([comment](https://projects.blender.org/blender/blender/issues/74186#issuecomment-353495)).

**Rejected or not done.**
- "BMesh Support in the Modifier Stack", i.e. passing BMesh between modifiers. Still a stage-2 idea.
- "Partial geometry updates" were noted as hard because of connected normals, custom normals and UV tangents.
- Undo storing only tagged objects in multi-object edit mode was never implemented.
- #74186 was closed in 2024 with "some of these suggestions have not been implemented" ([comment](https://projects.blender.org/blender/blender/issues/74186#issuecomment-1101723)).

**Debt.** The two-structure model is permanent architecture, not a phase that is ending. Every edit-mode feature has to pay or dodge the BMesh↔Mesh conversion, and the copy-on-write update in edit mode was called "redundant" in 2021.

**Quotes.**
- "Copy-on-write updates in edit-mode is redundant and as far as I can see, should be skipped entirely." — [#88021](https://projects.blender.org/blender/blender/issues/88021)
- "Blender 2.7x supported edit-mesh without the creation of an 'evaluation mesh'." — [#74186](https://projects.blender.org/blender/blender/issues/74186)

### Theme 3 — Operators, redo and undo: "Operate → Settings" is undo-pop plus re-execute

**Decided.**
- An operator is the MVC controller. It reads UI context ("operators will act on what the user is focusing on"), pushes undo when it finishes, and its RNA properties automatically produce the *Adjust Last Operation* panel (`DD/features/interface/operators.md:3-64`).
- HIG: Select → Operate, then Operate → Settings, "to prevent annoying popups forcing you to decide settings before you even know how they'd look like" (`DD/features/interface/human_interface_guidelines/paradigms.md:53-71`).
- Redo is implemented as `ED_undo_pop_op` followed by re-running `exec` with edited properties (`SRC/editors/undo/ed_undo.cc:651-700`).
- Edit-mode undo stores a whole `Mesh` per step, converted from BMesh with `BM_mesh_bm_to_me` and deduplicated by `BLI_array_store`. Booleans (selection, hidden state) are RLE-encoded because they lack "enough *uniqueness* to efficiently de-duplicate" (`SRC/editors/mesh/editmesh_undo.cc:65-100, 931-990`).
- The undo stack is "fully relative": reaching step *n* means walking through every step in between (`DD/features/core/undo.md:24-26, 46-48`).

**Why.** The design serves artists, not programmers: "Blender is a tool allowing artists to create content, and not a coders API!" (`paradigms.md:86-93`). Snapshot undo with deduplication is simple and cannot get out of sync with a tool's own logic. Implicit sharing later made undo cheaper ("Faster undo due to implicit sharing", `DD/release_notes/4.2/core.md:3-5`; bind data in 5.0 `modeling.md:42-44`).

**Rejected.** Operators that pop up their settings before running (HIG, above). Also differential, command-style undo for meshes: mesh undo is stateful, while sculpt undo is differential (`undo.md:28-36`).

**Debt.**
- Redo coverage is uneven. WoQ 2026 had to add "Redo support for Edge & Vertex slide, Extend Vertices & Loop Selection". Vertex Slide only became adjustable in 5.1 (`DD/release_notes/5.1/modeling.md:40-41`).
- Some modal tools have no `exec` at all. `MESH_OT_knife_tool` only defines `invoke`/`modal`/`cancel` (`SRC/editors/mesh/editmesh_knife.cc:4649-4664`), so it cannot be replayed or driven headlessly. Loop cut *does* have `exec` (`editmesh_loopcut.cc:721-742`).
- The docs warn that `bContext` "has the tendency to spread throughout the code like cancer" (`operators.md:209-221`). That is the coupling that makes operators hard to call outside the UI.
- Sections on modal operators, macros and most `OPTYPE_*` flags in the docs are still empty ("TODO", `operators.md:131-189`).

**Quotes.**
- "The UI 'broadcasts' the data it wants operators to act on via context." — `operators.md:60-61`
- "Operators should just use high-level API functions of well defined modules. These should be unit tested…" — `operators.md:204-206`

### Theme 4 — Modal tools and the transform engine: generic data, mouse loop, rollback

**Decided.**
- Transform is one engine over abstract `TransData` units for every data type. Constraints and numeric input are written once (`DD/features/objects/transform.md:1-15`).
- The main loop polls events and recomputes from the saved mouse position. On cancel it rolls back from the saved `TransData` and pushes undo at the end (`transform.md:102-119`).
- The HIG allows only two kinds of persistent mode: per-object editing modes and "sticky" transform. Everything else should be temporary, including the knife, which should keep accepting points only "when the user actively does something" (`paradigms.md:34-51`).
- Snapping and navigation during transform were extended in 4.0 (base point **B**, Alt-navigate, `DD/release_notes/4.0/modeling.md:11-38`).

**Why.** Modal tools give continuous visual feedback in the viewport. The operator system suspends undo and autosave while a modal runs: "no auto-saves or undo pushes are performed" (`operators.md:128-129`).

**Rejected.** "Transparent" pass-through modal operators are discouraged: "it's generally better to avoid such 'transparent' modal operators" (`operators.md:126-128`).

**Debt.**
- The transform doc still points at `source/blender/include/transform.h`, a path that no longer exists, so it predates the current code.
- A modal tool's *intermediate* state (knife cut lines, loop-cut preview) lives only inside the operator's custom data. It is neither in RNA properties nor undoable.

**Quote.** "Blender's transformation engine is based on the principle of generality." — `transform.md:3`

### Theme 5 — Modifiers → Geometry Nodes, and node groups becoming operators ("Everything Nodes")

**Decided.**
- *Everything Nodes* started from "functions" that have no side effects and whose dependencies are knowable without executing them. "Function users" are the places where side effects happen (`DD/features/nodes/proposals/everything_nodes.md:17-52`).
- The modifier stack was explicitly broken into four kinds: Function, With Binding, Simulation, Final Output. Only Function modifiers port "comparatively straight forward[ly]" to nodes (`DD/features/nodes/proposals/break_modifier_stack.md:18-61`).
- In practice:
  - Auto Smooth → modifier node-group asset (4.1, `DD/release_notes/4.1/modeling.md:5-27`).
  - Pin-to-bottom (4.2).
  - Six GN modifiers incl. **Array** (5.0, `DD/release_notes/5.0/modeling.md:5-34`).
- Node tools (4.0): "The node group itself is the operator asset". New input nodes give access to selection, 3D cursor, face sets, mouse position, viewport transform and the active element ([#101778](https://projects.blender.org/blender/blender/issues/101778); `DD/release_notes/4.0/geometry_nodes.md:3-28`, `4.2/geometry_nodes.md:43-56`). Later steps:
  - 5.1 registers "a separate operator type … for every node tool" with a custom idname (`5.1/geometry_nodes.md:49-53`).
  - 5.2 remembers node tool inputs and makes them settable from Python (`5.2/geometry_nodes.md:167-169`).
- Modal node tools are now "a work-in-progress PR" ([GN Workshop Sept 2026](https://code.blender.org/2026/10/geometry-nodes-workshop-september-2026/)).

**Why.**
- "It is very hard to find a place for all tools and their combinations in an ordinary user interface" (`everything_nodes.md:3-11`).
- Artists should be able to make tools "without having to code" (`everything_nodes.md:62-66`).
- Asset creators should ship their tools together with their node groups (`DD/features/nodes/proposals/node_tools.md:5-16`).

**Rejected or limited.**
- *Nested primitives within primitives* in the mesh type: "much harder to grasp" (`mesh_type_requirements.md:34-44`).
- Turning *binding* and *simulation* modifiers into nodes ("nor should they", `break_modifier_stack.md:33-41`).
- Removing the legacy Array: "The legacy array modifier is still available for now" (`5.0/modeling.md:10-11`), because "full feature parity with original modifier" is the rule ([Essentials design session](https://devtalk.blender.org/t/2025-04-24-design-session-essentials-assets/40166)). Some behaviour cannot be reproduced yet, e.g. Mirror clipping "prevents vertex movement—impossible to replicate currently" (same thread).

**Debt.**
- Built-in edit-mode tools are still C++ BMesh operators. The node-tool parity goal ("any existing edit mode operator could be implemented with nodes") is "realistically … not … achieved any time soon" (#101778).
- Node tools ran with "modeling operations have not being a priority yet" ([node tools blog](https://code.blender.org/2023/10/node-tools/)).
- Legacy and GN modifiers live side by side.
- Node tools from before 5.1 "must be opened and saved with 5.1" (`5.1/geometry_nodes.md:53`).

**Quotes.**
- "It must not have side effects." — `everything_nodes.md:40`
- "The project is 'completely finished' when any existing edit mode operator could be implemented with nodes" — [#101778](https://projects.blender.org/blender/blender/issues/101778)

### Theme 6 — BMesh's layered API: Euler operators, bmops, tools (and who may touch selection)

**Decided.** There are three layers (`DD/features/objects/mesh/bmesh.md:218-467`):
1. **Euler operators**, each with a logical inverse. Together they cover "any non-manifold modelling operation", take time proportional to local detail, and guarantee "fully valid" output.
2. **BMesh operators (bmops)** with typed, named, optional *slots* that chain into each other. They have private flag layers and "should *never* touch header flags (visibility, selection)".
3. **Tools**, the only layer allowed to touch selection and other user-visible flags.

**Why.** It replaced the old EditMesh, where a face split "would have taken dozens if not a hundred or more lines" (`bmesh.md:373-378`).

**Rejected.** Two-edged faces are allowed by the data structure but discouraged in a tool's final output: "I am considering removing 2 edged faces from the modelling system altogether" (`bmesh.md:380-396`).

**Debt.** bmops are a second, internal operator system (`bmesh_opdefines.cc`) that is separate from `wmOperator`. Agents, Python (`bmesh.ops`) and C++ tools each reach geometry through a different surface.

**Quote.** "every operator ensures that the data structure that it produces as output is fully valid" — `bmesh.md:261-264`

### Theme 7 — Sculpt: three backends, the PBVH refactor, and dyntopo/multires debt

**Decided.**
- Sculpt data lives in one of three backends: `Mesh`, `BMesh` (dyntopo, "runtime only and not persisted"), or `SubdivCCG` grids (multires) (`DD/features/sculpt_paint/mesh_paint.md:3-19`).
- The 2024 refactor ([#118145](https://projects.blender.org/blender/blender/issues/118145)):
  - removed the per-vertex macro that switched backends at runtime;
  - wrote a separate implementation of each brush for each PBVH type;
  - stripped PBVH down to "only … an acceleration structure";
  - made brushes "a sequence of actions on *arrays*";
  - removed permanent references to mesh data.
- Results: sculpt mode enters about 5× faster and brushes run about 8× faster (`DD/release_notes/4.3/sculpt.md:107-117`).
- Sculpt undo is differential. Its data was compressed in 5.0, and topology-changing sculpt operators now report memory use (`5.0/sculpt.md:36-38`).

**Why.** "Problems with the code have made feature development significantly harder over the years" ([blog](https://code.blender.org/2024/11/this-summers-sculpt-mode-refactor/)). The same SoA, data-oriented philosophy as Theme 1, applied to brushes.

**Rejected.**
- Sharing code by "forc[ing] different data through the same code path" (#118145).
- Removing dyntopo. It was discussed and pushed back by J. Eagar: "I heard talk of removing DynTopo" ([bf-committers 2020](https://archive.blender.org/lists/bf-committers/2020-October/050704.html)).

**Debt.**
- Several #118145 to-dos are still open: removing `SculptSession` region/view state, separate non-leaf node arrays, splitting out "pixels" data.
- The blog lists dyntopo and multires subdivision as remaining bottlenecks.
- BMesh "never intended … for anything like high-res sculpting" (Eagar 2020).
- Multires only began showing generic attributes and textures in 5.3 (`5.3/sculpt.md:14-15`).

**Quotes.**
- "The BVH tree, often referred to as the 'PBVH' was a catch-all storage for any data needed anywhere in sculpt mode." — [blog](https://code.blender.org/2024/11/this-summers-sculpt-mode-refactor/)
- "Unlike most other development projects, this had no effect on the interface." — same

### Theme 8 — Retopology and remeshing: destructive, one-shot operators

**Decided.** Two remeshers were added in 2.81 as one-shot operators (`DD/release_notes/2.81/sculpt.md:66-79`):
- **Voxel Remesh** goes mesh → volume → mesh. It gives even face size and repairs intersections, "as an alternative to dynamic topology without the performance cost of continuous updates".
- **QuadriFlow** produces a quad mesh "with few poles and edge loops following the curvature". It is "relatively slow but generates higher quality".

Later changes made remeshing and topology tools friendlier to attributes and quads:
- Voxel remesh preserves all attributes (4.1) and interpolates them (5.2, `5.2/sculpt.md:10-15`).
- The Manifold boolean solver was added in 4.5 (`DD/release_notes/4.5/modeling.md:29-31`).
- Topology-aware triangle joining (4.4) and Grid Fill that corrects existing geometry (4.5).
- Select Poles (4.4, `4.4/modeling.md:10-16`).
- The default Retopology overlay offset changed from 0.2m to 0.01m in 4.5 (`4.5/modeling.md:32`).

**Why.** Remeshing is a reset step between blocking out a shape and detailing it. It trades continuous cost (dyntopo) for an explicit cost the user pays when they choose to.

**Debt.** QuadriFlow is an external library with crash and hang fixes as recently as 4.4/4.5 (`DD/release_notes/4.4/corrective_releases.md:120`). Neither remesher is a node or a non-destructive step in the stack (the Remesh modifier exists separately in `SRC/modifiers/intern/MOD_remesh.cc`). I found no recent design document for retopology. *Gap: no dedicated design thread opened in this pass.*

---

## 3. Implications for an agent-native engine

Interpretation: these are my readings of the evidence above, not Blender's stated intent.

- **[DF1] human is operator / [DF2] humans write code.** *Interpretation:* Blender's main design premise is "Blender is for Artists … not a coders API!" (`paradigms.md:86-93`). Operators are bound to `bContext`, the knife has no `exec`, and redo is "undo-pop + replay the UI context". The agent layer cannot simply call operators. It needs a context-free layer underneath: the `bke::mesh` raw-array functions (`mesh.md:147-155`), the bmop slot API, and node-tool idnames (5.1+), whose inputs can be set from Python (5.2). These are the closest existing "agent-callable" surfaces.
- **[DF3] tiny imperative steps.** *Interpretation:* BMesh Euler operators (validity guaranteed, each with an inverse, cost proportional to local detail) are already the "tiny imperative step" vocabulary, and bmop slots already chain outputs to inputs. An agent-native modeling API could expose bmops more or less directly, as a typed and logged command stream. Each step's inverse gives a natural differential undo, instead of edit-mode's whole-mesh snapshots.
- **[DF3] tiny imperative steps (vs declarative).** *Interpretation:* Blender is moving *away* from step-by-step modeling toward declarative, side-effect-free functions (Everything Nodes, GN modifiers, node tools). For agents, declarative node graphs are the better *artifact*: reviewable and diffable, as `nodebpy` shows. Imperative steps are the better *interaction*. The engine probably needs both: steps that can be compiled into a node tree.
- **[DF4] viewport + eye verify.** *Interpretation:* `mesh_comparison.md` defines mesh equality up to isomorphism (sorting by attributes, then matching topology). That is a verification method that needs no viewport: an agent can assert "this result is isomorphic to that reference". Pair it with Select Poles–style queries for topology checks, and with `.select_*`/`.hide_*` as plain boolean attributes, so selection can be inspected as data instead of as pixels.
- **[DF4] viewport + eye verify / [DF1].** *Interpretation:* #88021 shows 30–50% of an edit-mode update going to GPU drawing. A headless agent loop that skips drawing (`use_mesh_no_draw` in the benchmark) could edit much faster than a human loop. The Mesh/BMesh duality then becomes a choice of *where the agent lives*:
  - in BMesh, for local topology edits;
  - in SoA `Mesh`, for bulk attribute work and GN.
  Conversion should happen only at verification points.
- **[DF1] human is operator.** *Interpretation:* Operate → Settings (the redo panel) is effectively an "edit the last call's arguments" protocol. Each `wmOperator` already records its idname and RNA properties, which is close to a machine-readable action log. Its gaps (modal tools with no `exec`, uneven redo support, inputs not stored between runs until 5.2) are exactly what an agent-native engine has to fill.
- **[DF2] humans write code.** *Interpretation:* The "full feature parity" rule for GN modifier assets and the long coexistence of legacy and new systems show the cost of not breaking user files. An agent-native fork can only make that trade if it keeps `.blend` compatibility at the SoA `Mesh` level, which is the stable, attribute-generic layer.

---

## 4. Questions for the Trace pass

1. **BMesh↔Mesh conversion.** In `SRC/bmesh/intern/bmesh_mesh_convert.cc`, trace `BM_mesh_bm_to_me` and `BM_mesh_bm_from_me`:
   - Which attributes go through `AttributeStorage` and which through `CustomData`?
   - What does the parallel conversion split on (3.6 note)?
2. **Lazy wrapper.** In `SRC/blenkernel/intern/mesh_wrapper.cc`:
   - Who calls `BKE_mesh_wrapper_ensure_mdata` during an edit-mode transform?
   - Is the "redundant" copy-on-write update from #88021 still there? Look at the depsgraph tag sites in `SRC/editors/transform/transform_convert_mesh.cc` and `DEG_id_tag_update` calls in `SRC/editors/mesh/editmesh_utils.cc` (`EDBM_update`).
3. **Edit-mode undo.** `SRC/editors/mesh/editmesh_undo.cc:931-1090`:
   - How large is one step for a 1M-vert mesh after `BLI_array_store` deduplication?
   - Is there any hook for "only tagged objects" in multi-object edit mode (the #74186 leftover)?
4. **Redo path.** `SRC/editors/undo/ed_undo.cc:651-730` together with `WM_operator_repeat_check` (`SRC/windowmanager/intern/wm_operators.cc`): which mesh operators are excluded from redo, and why? List every `MESH_OT_*` that has `invoke`/`modal` but no `exec`; the knife is the first example.
5. **Node tools as operators.** In `SRC/editors/geometry/node_group_operator.cc:~1400-1800`:
   - How is one `wmOperatorType` registered per tool (5.1)?
   - How are inputs remembered (5.2)?
   - How are Selection, Active Element and Mouse Position fed in?
   - Where would modal support attach (the WIP PR)?
6. **bmop surface.** In `SRC/bmesh/intern/bmesh_opdefines.cc` and `bmesh_operators.cc`:
   - Count the bmops and their slot types.
   - Check how `bmesh.ops` in `SRC/python/bmesh/bmesh_py_ops.cc` exposes them.
   - Could this be the agent's step vocabulary?
7. **Euler kernel.** In `SRC/bmesh/intern/bmesh_core.cc`, confirm the inverse pairs (`bmesh_kernel_split_edge_make_vert` ↔ `bmesh_kernel_join_edge_kill_vert`, etc.) and check whether any differential log of them exists anywhere.
8. **Mesh comparison.** The implementation behind `mesh_comparison.md` is `SRC/blenkernel/intern/geometry_compare.cc` (contains `to_sorted1`/`from_sorted1`). Is it exposed to Python or tests only?
9. **Sculpt.** In `SRC/editors/sculpt_paint/mesh/sculpt_undo.cc` and the `bke::pbvh` tree code:
   - Which #118145 to-dos remain (non-leaf node arrays, `SculptSession` view state)?
   - How do dyntopo's BMesh paths differ from the Mesh paths?
10. **Modifier evaluation.** In `SRC/blenkernel/intern/mesh_data_update.cc` (`mesh_calc_modifiers` / `editbmesh_calc_modifiers`):
    - Where do deform-only modifiers stay on edit-mesh coordinates, and where is BMesh→Mesh forced?
    - How does `MOD_nodes.cc` receive an edit-mode mesh?
11. **Array legacy vs GN.** Compare `SRC/modifiers/intern/MOD_array.cc` with the bundled Array GN asset (find where `release/datafiles/assets` ships modifier node groups). Which features are missing from the asset (merge, caps?) and so keep the legacy one alive?
12. **Remesh.** `SRC/blenkernel/intern/mesh_remesh_voxel.cc` and `SRC/editors/object/object_remesh.cc` (QuadriFlow job):
    - How does attribute interpolation work (5.2)?
    - Is either remesher exposed as a GN node (would make them non-destructive)?
