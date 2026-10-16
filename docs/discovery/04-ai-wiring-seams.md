# Discovery 04 — AI wiring seams in the Blender engine

- **Date:** 2026-10-17 · **Feeds:** RFC 0003 (harness architecture), ledger L-012 to L-015, evidence on L-003 / L-004 / L-008
- **Source tree:** `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender` at `d13f752e` (v5.2.2). Paths below are under `source/blender/`.
- **Method:** static reading by an exploration pass on 2026-10-11, then an independent re-read on 2026-10-17. Eight anchors were spot-checked by hand for this note (listed in §7). Blender was not built and no probe was re-run, so everything here is L1 (documented and traced in source) unless marked otherwise.
- **Scope:** observation and wiring points where an agent can see and drive the engine. It changes no behaviour.

## 1. What a seam is

A seam is a place in the code where an agent can be attached without a large surgery. We rank each by the engine change it needs and by the risk of breaking existing behaviour.

| # | Seam | Python-only today? | C++ work (estimate) | Risk |
|---|---|---|---|---|
| 1 | Operator observation | Partly (no attribution, no old values) | patch-sized, under about 500 lines | Low |
| 2 | Main-thread command queue | Yes, via `bpy.app.timers`; headless behaviour unproven | patch-sized (`--command` handler) | Low to medium |
| 3 | Change stream | Yes, coarse (`depsgraph_update_post`) | patch-sized for attribution; project-sized for old values | Medium |
| 4 | Branchable undo | No | project-sized | Medium to high |
| 5 | Declarative geometry | Yes via Geometry Nodes API | small; cheapness of scratch copies unproven | Medium |

Effort sizes are judgement from reading anchor code. No prototype backs them.

## 2. Seam 1 — Operator observation

- **Hook.** `wm_operator_finished` (`windowmanager/intern/wm_event_system.cc:1282`) is the common success sink for exec, invoke, Python and modal paths. Call sites: `:1419`, `:1741`, `:2725`. It sees the operator, the undo decision and whether a redo entry registered.
- **Not the hook.** `WM_operator_poll` (`:1113`) is called from many places, including UI redraw and greying-out, so an observer there would fire many times per frame. This corrects the 2026-10-11 note.
- **Already in the tree.** `WM_operator_pystring_ex` (`windowmanager/intern/wm_operators.cc:264`) renders an operator call as replayable Python. `RPT_OPERATOR` reports appear under `G_DEBUG_WM`. The in-session redo list is capped at 32 entries (`windowmanager/intern/wm.cc:252`).
- **Schema.** `bpy.ops.x.get_rna_type()` (`python/intern/bpy_operator_function.cc:707-713`) gives the operator schema from Python. `blenkernel/intern/idprop_serialize.cc` serializes IDProperties and is **not** an operator-schema dumper (correction to the 2026-10-11 note).
- **Gap.** No old property values, no operator-level handler event, no transaction concept. Unchecked: whether C++-to-C++ operator calls bypass `wm_operator_finished`.

## 3. Seam 2 — Main-thread command queue

- **Python.** `bpy.app.timers` wraps `BLI_timer_register` (`python/intern/bpy_app_timers.cc:90`). The Python API is single-threaded, so an agent bridge must marshal every call onto the main thread.
- **Headless.** A CLI `CommandHandler` exists (`blenkernel/BKE_blender_cli_command.hh:26`). Whether `BLI_timer_execute` fires in a pure `-b` session is **unproven**; in `-b --python` the script owns the thread. Design for a `--command` handler or a script-owned loop until a Phase 0 test settles it.
- **Contract worth copying.** CADCraft marshals each call through an atomic QUEUED / STARTED / CANCELLED state so a timeout can report `not-run` (safe to resend) or `may-have-run` (inspect first). Blender's timer queue has the same shape.

## 4. Seam 3 — Change stream

- **Python.** `depsgraph_update_post` fires after `DEG_evaluate_on_refresh` (`blenkernel/intern/scene.cc:2776-2786`), with per-ID flags such as `is_updated_geometry` exposed by `makesrna/intern/rna_depsgraph.cc`.
- **Per-ID change masks.** `ID.recalc_up_to_undo_push` and `ID.recalc_after_undo_push` (`makesdna/DNA_ID.h:441-452`) record the change category per ID between undo pushes.
- **Granularity.** "Which ID, which category". No old values, no operator attribution, no field-level diff anywhere in the tree. A callback that mutates the scene forces a second evaluation pass.
- **Identity.** `ID.session_uid` is stable within a session. Whether it survives save and load is ambiguous and needs a one-line test. No persistent UUID and no element-level ids exist. `ID.deep_hash` is populated only for packed linked data-blocks.

## 5. Seam 4 — Branchable undo (evidence for L-008)

- `BKE_undosys_step_push_with_type` truncates redo on every push (`blenkernel/intern/undo_system.cc:547-553`), so the stack is linear.
- The memfile layer writes each ID as its own chunk set and shares identical chunks with the previous step (`blenloader/intern/writefile.cc:655-700`, `blenloader/intern/undofile.cc:143-158`), so "which IDs changed between two undo steps" is derivable in C++ at byte-chunk granularity, with no field-level information.
- Python `bpy.ops` calls push no undo by default (`windowmanager/intern/wm_event_system.cc:2002-2016`). In `-b` mode `bpy.ops.ed.undo()` fails until `ed.undo_push()` is called (measured on 5.2.2 during the 2026-10-17 research pass).
- **Consequence.** Branching has to be built outside Blender's undo stack in the first phase (file snapshots plus a worker process per branch); a non-truncating in-memory tree is project-sized C++.

## 6. Seam 5 — Declarative geometry

- `execute_geometry_nodes_on_geometry` (`nodes/NOD_geometry_nodes_execute.hh:57-61`) evaluates a node tree on a `GeometrySet`, and is called by the modifier and the node-group tool operator.
- Geometry Nodes is a plausible declarative target for geometry, not a whole-scene format.
- **Unproven:** that evaluating on an implicitly shared scratch copy is cheap. Nobody has opened the implicit-sharing code or measured it.
- `compare_geometry` (`blenkernel/BKE_geometry_compare.hh:39-66`) has the right shape for a machine QA oracle. Whether it is bound to Python is unchecked.

## 7. Anchors spot-checked by hand on 2026-10-17

| Anchor | Result |
|---|---|
| `wm_event_system.cc:1113` `WM_operator_poll` | confirmed |
| `wm_event_system.cc:1282` `wm_operator_finished` | confirmed |
| `wm_operators.cc:264` `WM_operator_pystring_ex` | confirmed (the `_ex` variant; the plain wrapper is nearby) |
| `undo_system.cc:547-553` redo truncation | confirmed |
| `DNA_ID.h:441-452` `recalc_*_undo_push` | confirmed |
| `bpy_app_timers.cc:90` timers register | confirmed |
| `scene.cc:2776-2780` `DEG_evaluate_on_refresh` | confirmed |
| `NOD_geometry_nodes_execute.hh:57-61`, `bpy_operator_function.cc:707-713` | confirmed |

Everything else in §2 to §6 comes from the research pass and was not re-opened for this note.

## 8. Python add-on versus C++

| Capability | Python add-on, no engine change | Needs C++ |
|---|---|---|
| Addressable query | yes | |
| Coarse change stream | yes | |
| File-based checkpoints | yes | |
| Post-hoc verification | yes | |
| Risk table (external, keyed by operator idname) | yes | |
| Operator pre/post attribution and old values | | yes |
| Machine-readable poll reasons | | yes |
| In-memory branchable undo | | yes |
| Crash-proofing windowless edit paths | | yes |

Probe P01 (not re-run for this note) shows where the Python route breaks: of 23 region-gated operators, 4 returned `FINISHED` with no change and 5 sculpt gesture operators segfaulted ([probe](probes/p01-context-override.md)). A harness must verify each call by before/after fingerprint and run each session in a subprocess with crash recovery.

## 9. Open items (feed Phase 0)

- Do timers fire in a pure `-b` session?
- Does `session_uid` survive save and load?
- Is `compare_geometry` bound to Python? Does `bpy.ops.x.poll()` expose the poll message?
- Cost of `save_as_mainfile(copy=True)` on a realistic scene (never measured).
- Do C++-to-C++ operator calls bypass `wm_operator_finished`?
- Is the implicitly shared scratch copy for Geometry Nodes really cheap?
- Blender has no contribution, CLA or security file in-tree; the policy on AI-assisted patches is unverified (the Foundation's published v3 text was not retrieved).
