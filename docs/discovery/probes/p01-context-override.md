# Probe P01: do region-gated modelling operators really need a GUI?

- **Date:** 2026-10-08 · **Blender:** 5.2.2 LTS, background mode (`-b --factory-startup --disable-autoexec`)
- **Question:** the [S01 trace](../s01-modeling/03-trace.md) found 23 modelling operators whose poll demands a GUI region (`gate: gui-region`). Is that a real dependency, or does the poll only encode where the button lives (ledger [L-004](../ledger.md))?
- **Script:** [`tools/probes/p01_context_override.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p01_context_override.py). Each operator runs in its own Blender process, so a crash is recorded instead of ending the run. Raw data: `~/newblender-data/probes/p01.json` (local only).
- **Evidence level reached:** L2 (reproduced at runtime).

## Method

Scene: the factory cube, subdivided twice (98 vertices). For each operator:

1. **Plain poll.** Call `poll()` in the windowless background context.
2. **Borrowed context.** Take the 3D View area and region from the *Layout* screen stored in the startup file, and call `poll()` again under `bpy.context.temp_override(screen=…, area=…, region=…)`. That region has never been drawn: its view data (`region.data`) is `None`.
3. **Exec.** If the poll passes, call the operator with `EXEC_DEFAULT`, and compare a fingerprint before and after: vertex positions, object matrix, selection, object count and transform orientation.

Operators whose default arguments do nothing were given real ones: a shear angle, an orientation name, a cube matrix, an 8-point brush stroke, and edge or vertex indices for the picking operators. That way "nothing changed" means the call failed, not that it was asked to do nothing.

## Result

| Outcome | Count | Operators |
|---|---|---|
| **Plain poll passes headless** | **0 / 23** | (confirms the trace) |
| **Poll passes once *any* region is supplied** | **21 / 23** | all except `transform.delete_orientation` (needs an existing custom orientation: a data precondition) and `transform.seq_slide` (no sequencer area in the startup screens) |
| **Ran and did the job,** verified by the fingerprint | **5** | `mesh.loop_select`, `mesh.edgering_select`, `mesh.shortest_path_pick` (all given element indices), `mesh.primitive_cube_add_gizmo`, `transform.create_orientation` |
| **Returned FINISHED, but nothing measurable changed** | **4** | `transform.shear` (angle 0.5), `sculpt.brush_stroke` (8-point stroke), `mesh.rip_edge`, `mesh.rip_edge_move` |
| FINISHED; the effect is outside what the fingerprint measures | 2 | `sculpt.set_pivot_position`, `transform.select_orientation` |
| CANCELLED: the gesture needs a path or points the probe did not supply | 6 | `sculpt.face_set_polyline_gesture`, `face_set_lasso_gesture`, `trim_lasso_gesture`, `trim_polyline_gesture` and similar |
| Error from a data precondition | 1 | `mesh.knife_project` (needs a second object with wire edges) |
| **Segmentation fault** (Blender crashes) | **5** | `sculpt.face_set_line_gesture`, `face_set_box_gesture`, `project_line_gesture`, `trim_line_gesture`, `trim_box_gesture`, all inside sculpt **undo** (`undo::push_begin_ex`, `undo::geometry_begin_ex`) |

## What it means

1. **Polls check where the button lives, not what the code needs.** (Ledger L-004, now at L2.)
   - The three picking operators run correctly with a region whose view data is `None`. The region only satisfies the poll; the exec never touches it.
   - `loop_select`'s exec reads `object_index` and `edge_index`, as the trace said. Both are hidden properties that default to −1, which cancels the call.
   - In our first run the probe forgot the indices and got CANCELLED. That briefly looked like evidence against the trace; reading the exec body showed the missing input.
   - **Lesson:** a hidden required input is the same anti-pattern seen from the agent's side.
2. **A status is not a result.** (Ledger L-003, new runtime evidence.)
   - Four operators reported FINISHED with real arguments and changed nothing measurable.
   - The likely cause is that they need view data that a borrowed, never-drawn region does not have. Shear, rip and brush strokes all project through the view.
   - The operator gives no sign of this. Only the fingerprint shows it. An agent trusting `{'FINISHED'}` would believe it had sheared the object.
3. **Some code assumes a window exists, and crashes without one.** (Ledger L-008 and L-011.)
   - Five sculpt gesture operators crash Blender in their undo push. Sculpt undo assumes the windowed undo system is set up, and in a background session it isn't.
   - That's not a poll problem, but a hard dependency on the interactive session buried in the edit path.
   - For an agent this is the worst case: no error to read, just a dead process.

## Limits

- **No GUI baseline.** The same calls were not repeated in a windowed session to confirm that, there, they change the scene. "Did nothing headless" is measured, but "works in the GUI" is assumed from normal use.
- **The six CANCELLED gesture operators** were not given point lists, so this probe says nothing about them yet.
- **Single-object scene.** Multi-object editing was not probed.

## Next

- Repeat the four silent no-ops with a *drawn* region (one windowed session) to tell "needs view data" apart from "broken headless".
- Give the polyline and lasso gestures explicit point lists.
- Probe P02, undo: do scripted calls push undo steps, and does sculpt undo exist at all in `-b`?
