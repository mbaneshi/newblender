# Discovery 01 — Blender source module map (source lens, first pass)

- **Date:** 2026-10-07 · **Feeds:** RFC 0001 R2 (source lens)
- **Source tree:** `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender` (5.x)
- **Method:** directory survey + line counts (C/C++/GLSL/Py), key call paths read in source. First pass by an exploration agent; line numbers are approximate pointers, re-verify before relying on them.

## 1. Layers by size (~3.25M lines total)

| Group | ~Lines | Share | Main directories |
|---|---|---|---|
| Data model | 1.01M | ~31% | `makesdna` (51k), `makesrna` (199k), `blenkernel` (376k), `blenlib` (194k), `bmesh` (83k), `blenloader` (57k), `imbuf` (40k) |
| Evaluation / computation | 0.40M | ~12% | `depsgraph` (25k), `nodes` (157k), `functions` (13k), `geometry` (44k), `modifiers` (59k), `animrig` (21k), intern solvers (~70k) |
| Rendering | 0.72M | ~22% | `draw` (208k), `gpu` (149k), `intern/cycles` (224k), `freestyle` (85k), `compositor` (35k), `render` (16k) |
| **Human interface** | **0.93M** | **~29%** | `editors` (805k: sculpt_paint 107k, interface 90k, transform 50k, mesh 46k, object 43k, space_view3d 42k, animation 37k), `windowmanager` (62k), `intern/ghost` (59k), `blenfont` (8k), plus `scripts/startup/bl_ui` (2.2 MB of Python UI layout) |
| I/O + Python | 0.15M | ~5% | `io` (61k: usd, alembic, fbx, obj, ply, stl…), `python` (91k: bpy, mathutils, bmesh, gpu) |

**Nuance:** `editors/` mixes real logic (sculpt brushes, mesh/object operators) with UI. The *pure* UI toolkit + windowing (`interface`, `windowmanager`, `ghost`, `space_*`) is closer to **12–15%**. The rest of `editors/` is logic trapped behind operators, which is the interesting part to free, not delete.

## 2. A click's path to data

| Hop | What happens | Key location |
|---|---|---|
| 1. Operator | Registered via `WM_operatortype_append()`; `poll` → `invoke` → `exec` | `windowmanager/intern/wm_operator_type.cc`, `wm_event_system.cc`; ops in `editors/*/…_ops.cc`; Python path `python/intern/bpy_operator_function.cc` → `WM_operator_call_py()` |
| 2. RNA write | `RNA_property_*_set()` then `RNA_property_update()` → per-property update callback + depsgraph tag. Context-free variant exists: `RNA_property_update_main(Main*, Scene*, …)` | `makesrna/intern/rna_access.cc`; bpy setattr in `python/intern/bpy_rna.cc` |
| 3. DNA | Setter writes a plain C struct field | `makesdna/DNA_*_types.h`, mapped in `makesrna/intern/rna_<type>.cc` |
| 4. Depsgraph | Tag `DEG_id_tag_update()`; evaluation is driven by the **window-manager event loop** (`wm_event_do_depsgraph` → `BKE_scene_graph_update_tagged` → `DEG_evaluate_on_refresh`). Headless: `BKE_scene_graph_evaluated_ensure()` | `depsgraph/intern/depsgraph_tag.cc`, `depsgraph_eval.cc`, `blenkernel/intern/scene.cc` |

## 3. The GUI coupling (`bContext`)

- `struct bContext` (`blenkernel/intern/context.cc`) carries window/area/region slots; `CTX_wm_area/region/space_*` return null without a GUI.
- ~**1,909** `ot->poll =` assignments in `editors/`; most common is `ED_operator_editmesh` (120 uses). Shared polls in `editors/screen/screen_ops.cc`.
- ~**1,993** `CTX_wm_(area|region|space_*)` call sites under `editors/`.
- Poll failure → "context is incorrect" (`python/intern/bpy_operator_function.cc`). Workaround today: `Context.temp_override()` (`python/intern/bpy_rna_context.cc`), i.e. faking a GUI for an agent.

## 4. Existing headless entry points

| Mechanism | What | Where |
|---|---|---|
| `WITH_PYTHON_MODULE` | Build `bpy` as an importable Python module | `CMakeLists.txt` (~226); `source/creator/creator.cc`; `PyInit_bpy` in `python/intern/bpy_interface.cc` |
| `WITH_HEADLESS` | Build with no windowing (X11/Wayland/SDL off); selects `GHOST_SystemHeadless` | `CMakeLists.txt` (~375); `windowmanager/CMakeLists.txt`; `intern/ghost/CMakeLists.txt` |
| `-b` / `-c` | Runtime background mode, `G.background = true` | `source/creator/creator_args.cc` |

## 5. First observations for newblender (not decisions)

1. The data model (DNA/RNA) and evaluation (depsgraph, nodes, functions) are already separable from the UI. RNA even has a context-free update path. The agent-facing core likely sits on **RNA + depsgraph + nodes**, not on operators.
2. Operators are where human assumptions concentrate: poll-by-context, modal interaction, "select then act". ~2k context call sites measure the size of that coupling.
3. Evaluation is triggered by the **event loop**, a human-tempo heartbeat. An agent wants explicit "apply these changes → evaluate → give me the diff" transactions.
4. Blender already ships headless builds, so "no GUI" is not the novelty. The novelty is an interface **designed** for agents rather than a GUI with the window removed.
