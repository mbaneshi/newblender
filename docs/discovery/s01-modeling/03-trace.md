# S01 Pass 3 — Trace: where modelling operators are gated, and what they really call

- **Date:** 2026-10-07 · **Blender:** 5.2.2 (`v5.2.2`, source at `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender`)
- **Input:** `~/newblender-data/registry/s01_modelling_ops.json` (320 modelling operators: runtime registry dump + static scan + headless poll result + a heuristic gate label)
- **Output data:** `~/newblender-data/registry/s01_trace.json` (all 320 operators: corrected gate, poll function, exec/modal facts, undo flag, twin status)
- **Paths:** all `file:line` references are relative to `source/blender/` unless they start with `scripts/` or `tests/`.

**How this was checked**

1. **Gates for all 320 are read, not guessed.** I re-scanned the source for every operator's `wmOperatorType` definition, including the 20 `TRANSFORM_OT_*` operators and 18 macros that the first scan missed. I then read the body of each of the **70 distinct poll functions** (and the helpers they call), plus the `poll()` of the 16 Python operators.
2. **The ~70 key operators were traced by hand.** For each one I read the poll → exec / invoke / modal → the core call. The table only shows "exec w/o window = yes (verified)" when the code shows that the region is null-checked or not used.
3. **The other ~250 operators:** "exec without a window" is *inferred* from two facts: the poll needs no area/region, and an `exec` callback exists. These rows are labelled inferred in the JSON (`gate` ≠ `gui-*`), not verified one by one.
4. **The poll results agree with the reading.** No operator I gated as `gui-*` passed the headless poll. The 15 non-GUI operators that failed it all need data that the factory cube lacks (attributes, face sets, modifiers, shape keys, dyntopo).

---

## 0. Summary numbers (all 320 operators)

| Measure | Value |
|---|---|
| **Corrected gate** (strongest blocker) | **mode 178** · data 69 · gui-event 27 · gui-region 23 · window 16 · none 5 · selection 2 |
| Pass the poll in `blender -b` once the right mode/data is set | **270 / 320 (84%)** (none + data + mode + selection + window) |
| Need a real GUI | **50 (16%)**: 23 need an area/region, 27 need an event stream (no `exec`, or blocked under `G.background`) |
| Heuristic labels that were wrong or vague | **160 / 320 (50%)**, mostly `other` → mode/data/window; see §1.2 |
| **Modal** operators | **66**: 48 with a C `modal` callback + 18 macros. The registry said 28; the scan had missed all of `transform.*` and every macro. |
| Modal **and** have `exec` | **51 of 66**, so the modal part is optional for most of them |
| **No `exec` at all** (invoke/modal only) | **26**. The registry said 19: it missed 7 macros and Python ops, and it mis-flagged 2 light-linking ops and `mode_set_with_submode`, which do have exec. |
| `UNDO` flag | 299 / 320. The 21 without it: `object.mode_set` (flag `0` on purpose), `mesh.duplicate` (no flags at all; its macro carries undo), 14 sculpt ops that push their own sculpt undo (`editors/sculpt_paint/mesh/sculpt.cc:5516`), plus a few transform-copy / UI ops |
| **Declarative twin** (modifier or GN node) | exact **55** · approx **70** · none **59** · n/a (selection/state/stack management) 136 |
| Of the **184 operators that change geometry** | **30% exact, 38% approx, 32% no twin** |

---

## 1. Corrected gate classification

### 1.1 Gate definitions (as used in `s01_trace.json`)

| Gate | Meaning | Poll functions (examples, read) |
|---|---|---|
| none | No condition | `material_slot_select` / `deselect` (no poll), `object.select_camera`, `object.subdivision_set`, `mesh.primitive_torus_add` |
| data | Data exists and is editable; no mode required | `ED_operator_scene_editable` `screen/screen_ops.cc:218`, `ED_operator_object_active_editable` `:590`, `object_join_poll` `editors/object/object_add.cc:5436`, `edit_modifier_poll_generic` `editors/object/object_modifier.cc:1527`, `object_remesh_poll` `editors/object/object_remesh.cc:78`, `object_mode_set_poll` `editors/object/object_edit.cc:2041` |
| mode | An object interaction mode is required, sometimes plus data | `ED_operator_editmesh` `screen/screen_ops.cc:663` (edit object + `BMEditMesh`), `sculpt_mode_poll` `editors/sculpt_paint/mesh/sculpt.cc:3883`, `ED_operator_objectmode` `screen_ops.cc:242`, `objects_selectable_poll` `editors/object/object_select.cc:360`, `shade_poll` `editors/object/object_edit.cc:1737` (not edit/sculpt), `modifier_apply_poll` `object_modifier.cc:1960` (not edit mode) |
| selection | A mesh select-mode is required | `edbm_vert_or_edge_select_mode_poll` `editors/mesh/editmesh_select.cc:78`, `edbm_select_ungrouped_poll` `:6018` |
| **window** (new label) | Only `CTX_wm_window` + `CTX_wm_screen`. This is met in `-b`, because `startup.blend` brings a window; every one of these passed the headless poll. | `ED_operator_active_screen_and_scene` `screen_ops.cc:147`, `ED_operator_screenactive` `:136` (all of `transform.translate/rotate/resize/mirror/tosphere/push_pull/trackball`) |
| gui-region | Needs an area/region/space (View3D, Image editor, Properties) | `ED_operator_editmesh_region_view3d` `screen_ops.cc:677`, `EDBM_view3d_poll` `editors/mesh/editmesh_utils.cc:1857`, `sculpt_mode_poll_view3d` `sculpt.cc:3889`, `paint_brush_tool_poll` `editors/sculpt_paint/paint_stroke.cc:1719` (looks up the tool via `brush_tool_get(area, region)` `:1705`), `ED_operator_uvedit_space_image` `screen_ops.cc:785` |
| gui-event | No `exec` callback; or the poll explicitly refuses `G.background` | knife, polybuild, rip, `transform.bend`, `sculpt.expand`, `cloth_filter`, `object.select_grouped` (`object_select.cc:1088`: "uses popup menus which won't work in background mode") |

Rule: gate = the strongest blocker (gui-event > gui-region > window > selection > mode > data > none). A macro takes the strongest gate among its sub-operators. Macro polls are `nullptr` (`windowmanager/intern/wm_operator_type.cc:516`), and `wm_macro_exec` checks each step.

### 1.2 Heuristic → corrected (count)

| Heuristic → Corrected | n | What the reading found |
|---|---|---|
| mode → mode | 136 | Correct |
| other → mode | 35 | `objects_selectable_poll`, `shade_poll`, `modifier_apply_poll`, `object_convert_poll` and others all encode a mode |
| other → data | 35 | Modifier/shaderfx/customdata/UV polls |
| other → window | 15 | All the `transform.*` operators. The scan saw no poll because they use `ot->idname = OP_TRANSLATION` constants (`editors/transform/transform_ops.cc:59`) |
| gui → gui-region | 18 | Correct, now more precise |
| gui → gui-event | 14 | Invoke-only (polybuild, rip, knife, …) |
| other/python → gui-event | 11 | Macros wrapping invoke-only steps (`rip_move`, `polybuild_*_move`), `object.add_modifier_menu` |
| mode → gui-region | 1 | **`sculpt.brush_stroke`**. The poll name says "mode", but `paint_brush_tool_poll` needs area + region |
| mode → gui-event | 2 | `sculpt.cloth_filter`, `sculpt.expand` (no exec) |
| gui → data | 2 | `light_linking_*_select`: the exec is a template (`light_linking_select_exec<…>`), and the poll is `ED_operator_object_active` |
| none → data | 1 | `mode_set_with_submode` copies `OBJECT_OT_mode_set` (`object_edit.cc:2178`), so it inherits its poll |
| gui → window | 1 | `transform.transform` |

### 1.3 Gate × twin (all 320)

| Gate | exact | approx | none | n/a | total |
|---|---|---|---|---|---|
| none | 1 | 1 | 0 | 3 | 5 |
| data | 10 | 3 | 3 | 53 | 69 |
| mode | 38 | 42 | 38 | 60 | 178 |
| selection | 0 | 0 | 0 | 2 | 2 |
| window | 5 | 11 | 0 | 0 | 16 |
| gui-region | 1 | 10 | 4 | 8 | 23 |
| gui-event | 0 | 3 | **14** | 10 | 27 |

Of the 27 gui-event operators, 14 have no twin at all. These are the "pure human hand" tools: knife, polybuild ×9 (incl. macros), rip ×4, `dupli_extrude_cursor`.

---

## 2. Corrected table — the ~70 key modelling operators

Legend for flags: R=REGISTER U=UNDO B=BLOCKING G=GRAB_CURSOR D=DEPENDS_ON_CURSOR I=INTERNAL M=MACRO.
In the context column, `view3d?` means the operator reads `CTX_wm_view3d` but accepts null. Nearly every edit-mesh exec passes it to `BKE_view_layer_array_from_objects_in_edit_mode_unique_data` purely as a local-view filter for multi-object edit. Context reads are the direct `CTX_*` calls in poll + exec (+ one helper level), extracted automatically and spot-checked.

| idname | gate | context read | exec w/o window? | modal (flags) | core call file:line | declarative twin |
|---|---|---|---|---|---|---|
| `object.mode_set` | data | active_object; exec: main, wm_manager, wm_window | **yes, verified** (the registry dump itself calls it under `-b`) | no (flag `0`, no R/U, `object_edit.cc:2165`) | `object_edit.cc:2048` → `mode_set_ex` `editors/object/object_modes.cc:186` → **calls `OBJECT_OT_editmode_toggle` by name** (`:220`) → `editmode_enter_ex` `object_edit.cc:870` → `EDBM_mesh_make` `editors/mesh/editmesh_utils.cc:294` → `BKE_mesh_to_bmesh` `blenkernel/intern/mesh.cc:1576`; exit: `editmode_load_free_ex` `object_edit.cc:635` → `BM_mesh_bm_to_me` `bmesh/intern/bmesh_mesh_convert.cc:1669` | n/a |
| `object.mode_set_with_submode` | data | as above | yes | no (—) | `object_edit.cc:2176` (copy of mode_set) | n/a |
| `mesh.select_all` | mode | edit_object; main, scene, view_layer, view3d? | yes (inferred) | no (RU) | `editmesh_select.cc:2599` → `EDBM_flag_enable_all` `editmesh_utils.cc:484` / `EDBM_select_swap` `editmesh_select.cc:3478` | n/a (node tools: Set Selection) |
| `mesh.select_mode` | mode | edit_object; invoke: tool_settings, space_image | yes | no (RU) | `editmesh_select.cc:1543` → `EDBM_selectmode_toggle_multi` `:3167` | n/a |
| `mesh.select_linked` | mode | edit_object; main, scene, view_layer, view3d? | yes | no (RU) | `editmesh_select.cc:4036` → BMesh walker `BMW_init` | n/a |
| `mesh.select_more` | mode | same | yes | no (RU) | `editmesh_select.cc:4954` → `EDBM_select_more` `editmesh_utils.cc:425` | n/a |
| `mesh.loop_select` | **gui-region** | edit_object, **region_view3d** (poll) | **exec is index-driven** (`edge_index` etc. props) → plausible with `temp_override(region=…)` (inferred) | no (DRU) | exec `editmesh_select.cc:2484` → `edbm_select_loop_or_ring_exec_impl` `:2250` (edge-loop walker); invoke projects the mouse `:2440-2475` | n/a |
| `mesh.select_non_manifold` | selection | edit_object, view3d? | yes | no (RU) | `editmesh_select.cc:5794` (`BM_edge_is_manifold`/`BM_vert_is_manifold` sweep) | n/a |
| `mesh.select_similar` | mode | edit_object, tool_settings | yes | no (RU) | `editmesh_select_similar.cc:1254` | n/a |
| `mesh.extrude_region` | mode | edit_object; main, scene, view_layer, view3d? | yes (inferred) | no (RU) | `editmesh_extrude.cc:430` → `edbm_extrude_mesh` `:358` → `edbm_extrude_ex` `:212` → bmop `"extrude_face_region"` `:231` → `bmo_extrude_face_region_exec` `bmesh/operators/bmo_extrude.cc:319` | **exact**: GN Extrude Mesh |
| `mesh.extrude_region_move` | window | union of sub-ops | yes (`wm_macro_exec` runs each sub-op's exec; inferred) | macro (MRU) | `editors/mesh/mesh_ops.cc:263` = `MESH_OT_extrude_region` + `TRANSFORM_OT_translate` | exact: Extrude Mesh (Offset) |
| `mesh.extrude_faces_indiv` | mode | as extrude_region | yes | no (RU) | `editmesh_extrude.cc:641` → `"extrude_discrete_faces"` `:113` → `bmo_extrude.cc:42` | exact: Extrude Mesh (individual) |
| `mesh.extrude_repeat` | mode | + region_view3d? (null-checked; only gives the view-axis default offset) | yes | no (RU) | `editmesh_extrude.cc:265` → `edbm_extrude_ex` + bmop `"translate"` `:308` → `bmo_utils.cc:85` | approx: Extrude Mesh in a Repeat zone |
| **`mesh.bevel`** | mode | edit_object; exec: main, scene, view_layer, tool_settings, view3d?, area?, region (modal only); invoke: region_view3d | **yes, verified**: region is touched only when `is_modal` (`editmesh_bevel.cc:316-318`); area null-checked (`:440`) | **yes** (BGRU) | exec `editmesh_bevel.cc:489` → `edbm_bevel_calc` `:328` → `EDBM_op_init(…"bevel geom=%hev offset=%f …")` `:363` → `BMO_op_exec` `:391` → `bmo_bevel_exec` `bmesh/operators/bmo_bevel.cc:21` → `BM_mesh_bevel` (call `:65`, def `bmesh/tools/bmesh_bevel.cc:8239`) | **exact ×2**: Bevel modifier (same `BM_mesh_bevel`, `modifiers/intern/MOD_bevel.cc:238`) + **GN Mesh Bevel** (`geometry::mesh_bevel`, `geometry/intern/mesh_bevel.cc:7685`, a separate Mesh-native implementation) |
| `mesh.inset` | mode | same pattern as bevel | yes (same `is_modal` pattern; inferred by symmetry) | yes (BGRU) | `editmesh_inset.cc:327` → `edbm_inset_calc` `:237` → `"inset_region"` `:283` / `"inset_individual"` `:269` → `bmo_inset.cc:669` / `:419` | approx: Extrude Mesh (offset 0) + Scale Elements |
| `mesh.loopcut` | mode | edit_object; exec: region_view3d?, view3d? | **yes, verified**: `loopcut_init` comment says it runs "entirely in the background with `blender -b`" (`editmesh_loopcut.cc:371-373`); needs `object_index` + `edge_index` | yes (BRU) | exec `editmesh_loopcut.cc:522` → `loopcut_init` `:369` → `ringsel_finish` `:158` → `BM_mesh_esubdivide` (call `:188`, def `bmesh/operators/bmo_subdivide.cc:1324`) | none |
| `mesh.loopcut_slide` | mode | — | yes (inferred) | macro (MRU) | `mesh_ops.cc:221` = loopcut + `TRANSFORM_OT_edge_slide` | none |
| `mesh.knife_tool` | **gui-event** | poll: View3D area; invoke: wm_window | **no**: invoke + modal only | yes (BRU) | invoke `editmesh_knife.cc:4579`, modal `:4220` → `knife_make_cuts` `:2205` → `BM_face_split_edgenet` (call `:2163`) | none |
| `mesh.knife_project` | gui-region | region_view3d, scene, selected_objects | no: projects cutters through the view (`em_setup_viewcontext`) | no (BRU) | `editmesh_knife_project.cc:103` → `EDBM_mesh_knife` `editmesh_knife.cc:4751` | none |
| `mesh.subdivide` | mode | edit_object; main, scene, view_layer, view3d? | yes | no (RU) | `editmesh_tools.cc:90` → `BM_mesh_esubdivide` (call `:117`) → `bmo_subdivide_edges_exec` `bmo_subdivide.cc:910` | exact: GN Subdivide Mesh / Subdivision Surface |
| `mesh.unsubdivide` | mode | same | yes | no (RU) | `editmesh_tools.cc:361` → `"unsubdivide"` `:377` → `bmo_unsubdivide.cc:21` | exact: Decimate (Un-Subdivide) |
| `mesh.merge` | mode | same | yes | no (RU); invoke = enum menu `wm_operators.cc:1140` | `editmesh_tools.cc:3491` → `"pointmerge"` `:3484` / `"collapse"` `:3525` → `bmo_removedoubles.cc:463` / `:501` | approx: Merge by Distance |
| `mesh.remove_doubles` | mode | same | yes | no (RU) | `editmesh_tools.cc:3653` → `"find_doubles"` `:3701` + `"weld_verts"` `:3707` → `bmo_removedoubles.cc:923` / `:188` | **exact**: Weld modifier / GN Merge by Distance (`geometry::mesh_merge_by_distance_all`) |
| `mesh.dissolve_verts` | mode | same | yes | no (RU) | `editmesh_tools.cc:6106` → `"dissolve_verts"` `:6128` → `bmo_dissolve.cc:695` | none |
| `mesh.dissolve_edges` | mode | same | yes | no (RU) | `:6172` → `"dissolve_edges"` `:6201` → `bmo_dissolve.cc:455` | none |
| `mesh.dissolve_faces` | mode | same | yes | no (RU) | `:6261` → `"dissolve_faces"` `:6282` → `bmo_dissolve.cc:225` | none |
| `mesh.dissolve_limited` | mode | same | yes | no (RU) | `:6405` → `"dissolve_limit"` `:6463` → `bmo_dissolve.cc:803` | exact: Decimate Planar (`MOD_decimate.cc:192`) |
| `mesh.delete` | mode | same | yes | no (RU); invoke = menu | `:446` → `"delete"` `:466-503` → `bmo_dupe.cc:527` | exact: GN Delete Geometry |
| `mesh.bridge_edge_loops` | mode | same | yes | no (RU) | `:7613` → `"bridge_loops"` `:7527` → `bmo_bridge.cc:577` | none |
| `mesh.fill` | mode | same | yes | no (RU) | `:4678` → `"triangle_fill"` `:4701` → `bmo_triangulate.cc:52` | none |
| `mesh.fill_grid` | mode | same | yes | no (RU) | `:5136` → `"grid_fill"` `:5206` → `bmo_fill_grid.cc:592` | none |
| `mesh.fill_holes` | mode | same | yes | no (RU) | `:5278` → `"holes_fill"` `:5296` → `bmo_fill_holes.cc:18` | none |
| `mesh.edge_face_add` (F) | mode | same | yes | no (RU) | `:922` → `"contextual_create"` `:954` → `bmo_create.cc:24` | none |
| `mesh.spin` | mode | same; invoke reads view for the default axis | yes | no (RU) | `editmesh_extrude_spin.cc:40` → `"spin"` `:74` → `bmo_dupe.cc:547` | approx: Screw modifier |
| `mesh.screw` | mode | same | yes | no (RU) | `editmesh_extrude_screw.cc:38` → `"spin"` `:125` → `bmo_dupe.cc:547` | exact: Screw modifier |
| `mesh.separate` | data (exec handles edit and object mode) | main, scene, view_layer, view3d? | yes | no (U only) | `editmesh_tools.cc:4526` → `mesh_separate_selected` `:4334` → `BM_mesh_bm_to_me` into a new object (`:4259`) | approx: GN Separate Geometry (same object) |
| `object.join` | data | active_object, main | yes | no (RU) | `object_add.cc:5460` → `mesh::join_objects_exec` `editors/mesh/mesh_join.cc:537` | exact: GN Join Geometry |
| `mesh.symmetrize` | mode | edit set | yes | no (RU) | `editmesh_tools.cc:8033` → `"symmetrize"` `:8053` → `bmo_symmetrize.cc:20` | approx: Mirror modifier |
| `mesh.normals_make_consistent` | mode | edit set | yes | no (RU) | `:2666` → `"recalc_face_normals"` `:2689` → `bmo_normals.cc:258` | none |
| `mesh.flip_normals` | mode | edit set | yes | no (RU) | `:2342` → `"reverse_faces"` `:2306` → `bmo_utils.cc:156` | exact: GN Flip Faces |
| `mesh.mark_seam` | mode | edit set | yes | no (RU) | `:1038` sets the `BM_ELEM_SEAM` header flag inline; on save it becomes the `uv_seam` attribute (`bmesh_mesh_convert.cc:1794`) | exact: Store Named Attribute `uv_seam` |
| `mesh.mark_sharp` | mode | edit set | yes | no (RU) | `:1117` toggles `BM_ELEM_SMOOTH`, which becomes `sharp_edge` on save | approx/exact: Set Shade Smooth (edge) / Store `sharp_edge` |
| `mesh.faces_shade_smooth` | mode | edit set | yes | no (RU) | `:3028` → `mesh_set_smooth_faces` `:3012` | exact: GN Set Shade Smooth |
| `object.shade_smooth` | mode (`shade_poll`: not edit/sculpt) | main, scene, view_layer, selected_editable_objects | yes | no (RU) | `object_edit.cc:1651` → `bke::mesh_smooth_set` `blenkernel/intern/mesh.cc:1881` | exact: Set Shade Smooth |
| `object.shade_smooth_by_angle` | mode | same | yes | no (RU) | same exec → `bke::mesh_sharp_edges_set_from_angle` `mesh.cc:1893` | exact: "Smooth by Angle" node group |
| `object.shade_auto_smooth` | mode | same | yes; under `G.background` it blocks to load the asset library (`object_edit.cc:1864-1867`) | no (RU) | `object_edit.cc:1847` → adds a Nodes modifier with the essentials asset `"…/Smooth by Angle"` (`:1862`) | **is itself a twin factory** |
| `object.modifier_add` | data | main, scene; invoke: view3d | yes | no (RU) | `object_modifier.cc:1403` → `ed::object::modifier_add` `:159` → `BKE_modifier_new` `:186` | the declarative layer itself |
| `object.modifier_apply` | mode (not edit mode) | ensure_evaluated_depsgraph, main, scene | yes | no (IRU) | `:2074` → `modifier_apply_exec_ex` `:1991` → `modifier_apply` `:1257` → `modifier_apply_obdata` `:1049` → `create_applied_mesh_for_modifier` `:770` → `BKE_mesh_nomain_to_mesh` (`:1102`) | bakes a twin into data |
| `object.modifier_move_to_index` | data | (modifier name property) | yes | no (IRU) | `:1896` → `modifier_move_to_index` `:493` | n/a (stack order) |
| `object.origin_set` | data | active_object, edit_object, ensure_evaluated_depsgraph, main, scene | yes | no (RU) | `object_transform.cc:1297` → `bke::mesh_translate` `mesh.cc:2045` | approx: Transform Geometry |
| `object.voxel_remesh` | data (not edit, no dyntopo) | active_object, scene | yes | no (RU) | `object_remesh.cc:110` → `BKE_mesh_remesh_voxel` (call `:131`, def `blenkernel/intern/mesh_remesh_voxel.cc:246`, OpenVDB) | **exact**: Remesh modifier Voxel (`MOD_remesh.cc:139`, same core) + GN Mesh to Volume/Volume to Mesh |
| `object.quadriflow_remesh` | data | + wm_manager, wm_window (job) | **yes, verified**: exec without `OP_IS_INVOKE` runs a blocking job (`object_remesh.cc:999-1007`) | no (RU) | `:958` → `BKE_mesh_remesh_quadriflow` `mesh_remesh_voxel.cc:130` (call `object_remesh.cc:875`) | none |
| `sculpt.brush_stroke` | **gui-region** | poll: area + region (tool lookup); invoke: depsgraph, tool_settings, view3d | **partial**: `exec` exists (`sculpt.cc:6148`) and replays a `"stroke"` RNA collection, but the replay loop is keyed on each point's screen-space `"mouse_event"` (`paint_stroke.cc:1652`) and needs a `ViewContext` (`:863`); the stored 3D `"location"` is used unless `override_location` asks for a re-raycast (`:1646`, `:1673`) | yes (B only, no R/U: sculpt undo `sculpt.cc:5516`) | `SculptPaintStroke::exec` → per-brush PBVH node kernels | none |
| `sculpt.mask_filter` | mode | active_object, depsgraph, view3d? (`BKE_base_is_visible` null-safe, `blenkernel/intern/layer.cc:1681`) | yes (inferred) | no (RU) | `sculpt_filter_mask.cc:738` (PBVH node loops) | approx: node-tool fields |
| `sculpt.face_sets_create` | mode | same | yes (inferred) | no (RU) | `sculpt_face_set.cc:415` | approx: node tool Set Face Set |
| `sculpt.mesh_filter` | mode | same + tool_settings; modal: wm_window | yes (exec `:2582`) | yes (BDGRU) | `sculpt_filter_mesh.cc:2582` | approx: Smooth/Displace/Cast modifiers |
| `sculpt.trim_box_gesture` | gui-region | region_view3d; `ViewContext` `sculpt_gesture.cc:64` | partial: exec exists (`sculpt_trim.cc:771`) but takes a **pixel rectangle** | yes (R only; WM box gesture `windowmanager/intern/wm_gesture_ops.cc:194`) | `gesture::init_from_box` `sculpt_gesture.cc:155` → trim boolean (`geometry::boolean` solvers, `sculpt_trim.cc:110`) | approx: Boolean |
| `mesh.primitive_cube_add` | data | main, scene | yes | no (RU) | `editmesh_add.cc:290` → `"create_cube"` `:316` → `bmo_primitive.cc:1617` | exact: GN Cube |
| `mesh.decimate` | mode | edit set | yes | no (RU) | `editmesh_tools.cc:5845` → `BM_mesh_decimate_collapse` `bmesh/tools/bmesh_decimate_collapse.cc:1293` | **exact**: Decimate modifier (same core, `MOD_decimate.cc:177`) |
| `mesh.solidify` | mode | edit set | yes | no (RU) | `:4116` → `"solidify"` `:4135` → `bmo_extrude.cc:836` | exact in result: Solidify modifier (**different implementation**: `MOD_solidify_extrude/nonmanifold`) |
| `mesh.quads_convert_to_tris` | mode | edit set | yes | no (RU) | `:5525` → `"triangulate"` `:5551` → `bmo_triangulate.cc:29` | exact: Triangulate modifier (`BM_mesh_triangulate`) / GN Triangulate (`geometry::mesh_triangulate`) |
| `mesh.vertices_smooth` | mode | edit set | yes | no (RU) | `:2734` → `"smooth_vert"` `:2803` → `bmo_utils.cc:437` | exact in intent: Smooth modifier (different implementation) |
| `mesh.bisect` | mode | + rv3d via `ED_view3d_context_rv3d`: "both can be nullptr, fallbacks values are used" (`editmesh_bisect.cc:236`); default `plane_co` = 3D cursor | **yes, verified** | yes (RU) | `:232` → `"bisect_plane"` `:334` → `bmo_bisect_plane.cc:28` → `BM_mesh_bisect_plane` `bmesh/tools/bmesh_bisect_plane.cc:381` | approx |
| `mesh.duplicate` | mode | edit set | yes | no (**no flags**) | `:2075` → `"duplicate"` `:2097` → `bmo_dupe.cc:370` | exact: Duplicate Elements |
| `mesh.intersect_boolean` | mode | edit set | yes | no (RU) | `editmesh_intersect.cc:342` → `BM_mesh_boolean` `bmesh/tools/bmesh_boolean.cc:425` | exact: Boolean modifier / GN Mesh Boolean |
| `mesh.edge_split` | mode | edit set | yes | no (RU) | `:2009` → `"split_edges"` `:1967` → `bmo_split_edges.cc:18` | exact: Edge Split modifier / GN Split Edges |
| `mesh.wireframe` | mode | edit set | yes | no (RU) | `:7695` → `"wireframe"` `:7723` → `bmo_wireframe.cc:21` → `BM_mesh_wireframe` `bmesh/tools/bmesh_wireframe.cc:146` | exact: Wireframe modifier (same core, `MOD_wireframe.cc:72`) |
| `mesh.poke` | mode | edit set | yes | no (RU) | `:5451` `"poke"` → `bmo_poke.cc:32` | none |
| `mesh.convex_hull` | mode | edit set | yes | no (RU) | `:7917` `"convex_hull"` → `bmo_hull.cc:531` | exact: GN Convex Hull |
| `object.convert` | mode (object mode, via view-layer active object) | ensure_evaluated_depsgraph, selected_editable_bases | yes | no (RU) | `object_add.cc:4600` | n/a (bakes the stack) |
| `transform.translate` | **window** | poll: wm_window, wm_screen; exec: area/region nullable | **yes, verified**: `area == nullptr` → `SPACE_EMPTY` (`editors/transform/transform_generics.cc:240`); Blender's own tests call it in `-b` (`tests/python/bl_animation_keyframing.py:470`) | yes (BRU) | `transform_ops.cc:515` → `transformApply` `editors/transform/transform.cc:2249` | approx: Set Position / Transform Geometry |
| `transform.rotate` / `resize` / `mirror` | window | same | yes (same code path) | yes (BRU) | `transform_ops.cc:972` / `:882` / `:1177`; all `transform_exec` `:515` | approx |
| GN **node tool** (registered per asset, not in the 320) | data (active object + asset trait flags, `editors/geometry/node_group_operator.cc:1106`) | active_object, main, scene, ensure_evaluated_depsgraph; rv3d optional; **mouse/region/cursor are RNA props** (`:970-973`) | yes | no (RU + `OPTYPE_NODE_TOOL`) | exec `:893` → `nodes::execute_geometry_nodes_on_geometry` (call `:992`, def `nodes/intern/geometry_nodes_execute.cc:553`); in edit mode: `EDBM_mesh_load_ex` `:547` → GN → `EDBM_mesh_make_from_mesh` `:667` | is declarative |

---

## 3. Declarative twin table (geometry-changing operators)

"Same core" means the operator and the twin call the same function.

| Edit-mode operator(s) | Twin | Fidelity | Same core? |
|---|---|---|---|
| bevel | Bevel modifier; GN **Mesh Bevel** (new) | exact | modifier: yes (`BM_mesh_bevel`); GN: **no**, Mesh-native `geometry::mesh_bevel` |
| extrude_region/context/faces/edges/verts (+ _move macros) | GN Extrude Mesh | exact | no (the extrude algorithm lives in `nodes/geometry/nodes/node_geo_extrude_mesh.cc`) |
| subdivide | GN Subdivide Mesh / Subdivision Surface | exact | no (`bke::subdiv`) |
| unsubdivide, decimate, dissolve_limited | Decimate modifier (Un-Subdivide / Collapse / Planar) | exact | yes (`BM_mesh_decimate_*`) |
| remove_doubles | Weld modifier; GN Merge by Distance | exact | no (`geometry::mesh_merge_by_distance_*`) |
| quads_convert_to_tris | Triangulate modifier; GN Triangulate | exact | modifier yes (`BM_mesh_triangulate`); GN no |
| intersect_boolean | Boolean modifier; GN Mesh Boolean | exact | partly (Exact/Float/Manifold solvers) |
| edge_split | Edge Split modifier; GN Split Edges | exact | modifier yes (`BM_mesh_edgesplit`) |
| wireframe | Wireframe modifier | exact | yes (`BM_mesh_wireframe`) |
| solidify | Solidify modifier | exact result | no |
| vertices_smooth / _laplacian | Smooth / Laplacian Smooth modifier | exact intent | no |
| screw (spin ≈) | Screw modifier | exact / approx | no |
| voxel_remesh | Remesh modifier (Voxel); Mesh to Volume → Volume to Mesh | exact | modifier yes (`BKE_mesh_remesh_voxel`) |
| delete; duplicate; convex_hull; flip_normals; shade smooth/flat; sort_elements; primitives (except monkey) | Delete Geometry; Duplicate Elements; Convex Hull; Flip Faces; Set Shade Smooth; Sort Elements; Mesh Primitive nodes | exact | no |
| mark_seam / crease / bevel_weight / attribute_set | Store Named Attribute (`uv_seam`, `crease_edge`, `bevel_weight_edge`, …) | exact | n/a: plain attributes on `Mesh` |
| set_sharpness_by_angle, shade_auto_smooth, shade_smooth_by_angle | "Smooth by Angle" essentials node group | exact | `shade_auto_smooth` simply adds it |
| join | Join Geometry (+ Object Info) | exact | no |
| symmetrize, bisect, merge, separate, inset, extrude_repeat, transform.*, normals ops, sculpt filters/trims/face sets | Mirror / Boolean / Merge by Distance / Separate Geometry / Extrude + Scale Elements / Repeat zone / Set Position / Set Mesh Normal / Normal Edit / Weighted Normal / node tools | approx | — |
| **No twin (59)** | dissolve verts/edges/faces/mode/degenerate, fill, fill_grid, fill_holes, bridge_edge_loops, edge_face_add, knife ×2, loopcut (+slide), offset_edge_loops (+slide), rip ×4, polybuild ×9, vert_connect ×4, edge_rotate, edge_collapse, poke, tris_convert_to_quads, beautify_fill, face_split_by_edges, flip_quad_tessellation, subdivide_edgering, space_edge_loops_evenly, symmetry_snap, normals_make_consistent, split, delete_edgeloop, dupli_extrude_cursor, primitive_monkey, shape-key ops ×4, quadriflow_remesh, sculpt brush_stroke / cloth / color filter, edge_slide, vert_slide | — | — |

---

## 4. End-to-end path: `MESH_OT_bevel` (Ctrl+B in Edit Mode)

| # | Hop | Where |
|---|---|---|
| 1 | **Keymap.** `("mesh.bevel", {"type": 'B', "ctrl": True})` in the Edit Mesh keymap | `scripts/presets/keyconfig/keymap_data/blender_default.py:5551` (inside `km_edit_mesh` `:5525`) |
| 2 | **Event → operator.** The keymap handler calls `wm_operator_invoke`; it polls (`WM_operator_poll`), then `op->type->invoke` | `windowmanager/intern/wm_event_system.cc:1643`, invoke call `:1703` (falls back to `exec` when there is no invoke, `:1715`) |
| 3 | **Poll.** `ED_operator_editmesh`: edit object is a mesh with a `BMEditMesh` | `editors/screen/screen_ops.cc:663` |
| 4 | **Invoke.** `edbm_bevel_init(is_modal=true)` snapshots each mesh (`EDBM_redo_state_store`, `editmesh_bevel.cc:316`), installs a region draw callback for the mouse line (`:318`), measures the mouse distance to the projected selection centre (`calculateTransformCenter`, `ED_view3d_pixel_size(rv3d…)`), runs a first `edbm_bevel_calc`, then `WM_event_add_modal_handler` (`:567`) | `editors/mesh/editmesh_bevel.cc:529` |
| 5 | **Modal.** The handler dispatches `ot->modal`. On **every `MOUSEMOVE`** it sets `offset` from the pixel distance, **restores the snapshot** (`EDBM_redo_state_restore` `:358`) and **re-runs the whole BMesh op** (`edbm_bevel_calc` `:743`). Confirm leads to `edbm_bevel_exit` → `OPERATOR_FINISHED` | dispatch `wm_event_system.cc:2690`; `edbm_bevel_modal` `editmesh_bevel.cc:716` |
| 5′ | **Scripted path (no event).** `bpy.ops.mesh.bevel(offset=…)` parses `EXEC_DEFAULT` with undo **off** by default (`python/intern/bpy_operator_function.cc:118`, `:161`) → `WM_operator_call_py` (`:327` → `wm_event_system.cc:2002`) → `wm_operator_call_internal` `:1812` → `wm_operator_exec` `:1374` → `edbm_bevel_exec` `editmesh_bevel.cc:489`: init with `is_modal=false`, then one `edbm_bevel_calc`. **Invoke and modal are skipped entirely.** | as cited |
| 6 | **Operator → BMesh op.** `EDBM_op_init(em, &bmop, op, "bevel geom=%hev offset=%f segments=%i …", BM_ELEM_SELECT, …)`: a printf-style call whose format string is parsed into typed slots | `editmesh_bevel.cc:363` → `EDBM_op_init` `editors/mesh/editmesh_utils.cc:102` → `BMO_op_vinitf` `bmesh/intern/bmesh_operators.cc:1621`; slot schema `bmo_bevel_def` `bmesh/intern/bmesh_opdefines.cc:2413` (83 bmops are defined there) |
| 7 | **Execute.** `BMO_op_exec` ensures tool flags, pushes the op and calls `op->exec` | `bmesh_operators.cc:168` |
| 8 | **Core.** `bmo_bevel_exec` copies slots into parameters → `BM_mesh_bevel` | `bmesh/operators/bmo_bevel.cc:21` → `:65` → `bmesh/tools/bmesh_bevel.cc:8239` |
| 9 | **Selection and finish.** Select `faces.out`; optional auto-merge (`EDBM_automerge_connected`); `EDBM_op_finish` reports BMO errors | `editmesh_bevel.cc:393-418`; `editmesh_utils.cc:120` |
| 10 | **Tag.** `EDBM_update`: `DEG_id_tag_update(&mesh->id, ID_RECALC_GEOMETRY)` + `WM_main_add_notifier(NC_GEOM\|ND_DATA)` + loop-tris / normals recalculation on the BMesh | `editmesh_bevel.cc:427` → `editmesh_utils.cc:1799` (tag `:1803`) |
| 11 | **Undo + register.** `wm_operator_finished` → `ED_undo_push_op` (only if `op_undo_depth == 0`, which is **false for Python calls**, `wm_event_system.cc:2013`). The mesh undo step encodes **a full BMesh→Mesh copy** | `wm_event_system.cc:1282`, push `:1308`; `editors/mesh/editmesh_undo.cc:1173` → `undomesh_from_editmesh` `:931` → `BM_mesh_bm_to_me` `:985` |
| 12 | **Depsgraph.** The event loop evaluates tagged data: `wm_event_do_depsgraph` → `BKE_scene_graph_update_tagged` → object data node `BKE_object_eval_uber_data` → `BKE_object_handle_data_update` → `bke::mesh_data_update` → **edit-mesh branch** `editbmesh_build_data` → `editbmesh_calc_modifiers`. The cage is `BKE_mesh_wrapper_from_editmesh`: the evaluated mesh **wraps the BMesh** and does not convert it | `wm_event_system.cc:488` → `blenkernel/intern/scene.cc:2827` → `depsgraph/intern/builder/deg_builder_nodes.cc:1758` → `blenkernel/intern/object_update.cc:375` → `:179` (call `:204`) → `blenkernel/intern/mesh_data_update.cc:1138` (branch `:1164`) → `:1014` → `:739`; wrapper `:1064` |
| 13 | **Draw.** The notifier and redraw let the human eyeball the result (the GPU path is not traced here) | — |
| 14 | **Flush on mode exit.** `object.mode_set(mode='OBJECT')` → `mode_set_ex` → `OBJECT_OT_editmode_toggle` by name → `editmode_exit_ex` → `editmode_load_free_ex` → `EDBM_mesh_load_ex` → **`BM_mesh_bm_to_me`**, the point where `mesh.data` becomes true again (seam/sharp flags → `uv_seam`/`sharp_edge` attributes) | `object_modes.cc:186`, `:220` → `object_edit.cc:783` → `:635` (call `:662`) → `editmesh_utils.cc:353` → `bmesh/intern/bmesh_mesh_convert.cc:1669` (attrs `:1794`) |

**Contrast: node tool path (no BMesh op):** `run_node_group_exec` loads BMesh → Mesh (`node_group_operator.cc:547`), runs `execute_geometry_nodes_on_geometry` on the SoA Mesh (`:992`), then rebuilds BMesh from the result (`EDBM_mesh_make_from_mesh` `:667`). The declarative route goes through `Mesh`, and BMesh is only the editing cache.

---

## 5. Findings

**[DF1] the human is the operator**

1. **Most operators do not need a window. They need a mode.** 84% pass poll headless given the right mode/data. Mode alone gates 178 of 320 (56%). `object.mode_set` is itself an operator that dispatches *another* operator by name (`object_modes.cc:220`).
   - *Interpretation:* "mode" is a human session concept (a BMesh editing session plus its UI). An agent pays for it as a hidden, stateful precondition rather than as a parameter.
2. **Modal is mostly a veneer.** 51 of 66 modal operators also have `exec`. In bevel, the modal loop just re-runs the full BMesh op from a snapshot on every mouse move (`editmesh_bevel.cc:358`, `:743`).
   - *Interpretation:* the interactive tool is a pure function `f(selection, params)` plus a human-driven slider for `params`. The slider is the only part an agent does not need.
3. **The irreducible human tools are few, and they are about placement.** Of the 27 gui-event operators, 14 have no twin (knife, polybuild, rip, `dupli_extrude_cursor`). Their input is "where the cursor is". *Interpretation:* these need re-specification as data (a cut path, a plane, edge indices), not a headless shim.
4. **Scripted calls skip invoke and undo.** `bpy.ops` defaults to `EXEC_DEFAULT` with `is_undo=false` (`bpy_operator_function.cc:118`). `WM_operator_call_py` bumps `op_undo_depth`, so `wm_operator_finished` pushes no undo step (`wm_event_system.cc:2013`, `:1306`). *Interpretation:* an agent driving operators gets no undo history by default. Undo is a GUI affordance.

**[DF2] humans write the code**

5. **Polls describe where the button lives, not what the function needs.**
   - `loop_select`'s poll demands a `RegionView3D`, yet its exec is index-driven (`editmesh_select.cc:2484`).
   - `transform.*` polls demand a window, yet exec handles `area == nullptr` (`transform_generics.cc:240`).
   - `loopcut`'s exec is explicitly `-b` capable (`editmesh_loopcut.cc:371`).
   - Conversely, `sculpt.brush_stroke`'s poll *name* says mode, but it needs area + region.
   - The name heuristic was wrong or vague for 50% of operators.
   - *Interpretation:* preconditions must be declared machine-readably. They cannot be inferred from names, and not reliably even from polls.
6. **Hidden context inputs are everywhere.**
   - Almost every edit-mesh exec reads `CTX_wm_view3d` (nullable) to filter objects by local view for multi-object edit.
   - Defaults come from UI state: `bisect.plane_co` is the 3D cursor (`editmesh_bisect.cc:259`); `extrude_repeat`'s offset is the view axis (`editmesh_extrude.cc:274-276`); bevel reads `ToolSettings` (custom profile, auto-merge).
   - *Interpretation:* an operator is `f(props, hidden view/cursor/tool state)`. An agent API should make every such input an explicit, logged parameter.
7. **A typed RPC layer already hides inside BMesh.** Operators call 83 BMesh ops through printf-style format strings (`"bevel geom=%hev offset=%f …"`), parsed at runtime into typed slots defined in `bmesh_opdefines.cc`. *Interpretation:* the bmop slot schema is close to a machine-readable command vocabulary. It is hand-written today, but could be generated and exposed.

**[DF3] tiny imperative steps**

8. **68% of geometry-changing operators have a declarative twin:** 55 exact + 70 approx out of 184. The exact twins often share the **same core function**: `BM_mesh_bevel`, `BM_mesh_decimate_*`, `BM_mesh_wireframe`, `BM_mesh_triangulate`, `BM_mesh_edgesplit`, `BKE_mesh_remesh_voxel`. *Interpretation:* imperative vs declarative is a split at the *wrapper* level, not the algorithm level. One core can serve both forms.
9. **Blender 5.2 now has two bevels:** BMesh `BM_mesh_bevel` (`bmesh_bevel.cc`, ~8.2k lines) and Mesh-native `geometry::mesh_bevel` (`geometry/intern/mesh_bevel.cc`, ~7.7k lines, used by GN Mesh Bevel). Node tools also round-trip edit-mode BMesh through `Mesh`. *Interpretation:* upstream is moving algorithms off BMesh onto SoA `Mesh`. That is evidence for putting an agent-native core on `Mesh` + `geometry::` and treating BMesh as an editing cache.
10. **The no-twin gap is "local topology surgery":** dissolve, fill, grid fill, bridge, F-fill, knife, loop cut, rip, connect, slide, poke, tris→quads (59 operators). *Interpretation:* a declarative-first engine would need nodes for exactly these, or would have to keep a typed imperative bmop layer for them.
11. **Undo granularity is coarse.** Each edit-mesh undo step stores a full BMesh→Mesh copy (`editmesh_undo.cc:985`). Fourteen sculpt operators have no `UNDO` flag and push their own sculpt undo. *Interpretation:* there is no per-step inverse at the operator level, even though the BMesh Euler layer could provide one.

**[DF4] the viewport and the eye verify**

12. **Operators return no result, only a status.** The last hop is `DEG_id_tag_update` + a redraw notifier (`editmesh_utils.cc:1803-1804`). `EDBM_op_finish` checks only that the BMO ran without error. The new geometry is only visible by drawing it or by re-reading the mesh. *Interpretation:* an agent needs a returned diff (elements created / deleted / changed) plus validity checks, instead of a status code.
13. **In edit mode the `Mesh` datablock is stale until mode exit.** Evaluation wraps the BMesh (`mesh_data_update.cc:1064`), and only `EDBM_mesh_load_ex` → `BM_mesh_bm_to_me` writes back. *Interpretation:* the "truth" is split across two representations, synced at a human mode switch. An agent loop wants a single source of truth or an explicit flush.
14. **Where a region is truly required, it is for screen-space input** (knife, knife_project, gestures, brush strokes with `"mouse"` points). Node tools show the decoupled pattern: `mouse_position`, `region_size` and `cursor_*` are plain RNA properties (`node_group_operator.cc:970-973`) that `invoke` fills from the event (`:1035-1045`). *Interpretation:* the general fix for gui-region operators is "invoke captures the view into properties; exec is pure". Node tools already do this.

---

## 6. Verified vs inferred

- **Verified by reading code:**
  - all 70 poll bodies;
  - the presence or absence of `exec`/`modal` for all 320 operators (incl. macros and Python);
  - the full bevel path (§4);
  - the headless-safe exec claims for bevel, loopcut, bisect, transform and quadriflow;
  - the twin "same core" claims for bevel, decimate, wireframe, triangulate, edge split and voxel remesh;
  - the Python no-undo default.
- **Inferred:**
  - exec-without-window for the other ~250 operators (from "no GUI poll + has exec");
  - inset (by symmetry with bevel);
  - macro exec in `-b` (from `wm_macro_exec`, not run);
  - `temp_override` viability for gui-region operators;
  - most "approx" twins (I know the node exists; no result was compared);
  - the "exact" result equivalence where implementations differ (solidify, smooth, GN extrude/subdivide/merge).
- **Not traced:** the GPU draw path; the inner algorithms of `BM_mesh_bevel` and the GN nodes; per-transform-type `recalcData`.

## 7. Open questions

1. Does `bpy.context.temp_override(area=…, region=…)` in `-b` make the 23 gui-region operators work, given that `RegionView3D` matrices are never computed without a draw? This needs a runtime probe, one operator per poll family.
2. `sculpt.brush_stroke` exec: stored `location`s are used unless `override_location` is set (`paint_stroke.cc:1646-1680`), but every point still passes through `test_start`/`update` with its `mouse_event` pixel coordinate and a `ViewContext`. Can a stroke be replayed headless with synthetic `mouse_event` values and a `temp_override` region? This needs a runtime probe.
3. "Exact" twins with different implementations (Solidify, Smooth, GN Extrude/Subdivide vs BMesh) need a mesh-isomorphism test (see `04-why.md` [DF4]), ideally added to `~/agent-native-lab/lab/blender/golden-table.md`.
4. GN Mesh Bevel vs `BM_mesh_bevel`: is upstream planning to retire one? Check the 5.x commit history and design tasks.
5. Node tools are registered per asset and do not appear in the registry dump. Enumerate the essentials node tools in 5.2 to see whether any cover the 59 no-twin operators.
6. Confirm at runtime that `bpy.ops` in `-b` produces no undo steps, and that `bpy.ops.x(…, True)` (`is_undo`) does.
7. `object.select_grouped` is the only operator gated on `G.background` itself. Are there others outside the S01 set (grep `G.background` in polls)?
