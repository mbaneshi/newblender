# Probe P02: Phase 0 premises for the harness, headless

- **Date:** 2026-10-17 · **Blender:** 5.2.2 LTS (hash `d13f752e3b9c`), macOS arm64 (M4), background mode (`-b --factory-startup --disable-autoexec`)
- **Feeds:** [RFC 0003 §6](../../rfc/0003-harness-native-architecture.md) Phase 0; ledger L-013, L-014 (once PR #6 lands)
- **Scripts:** [`p02_timers.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p02_timers.py), [`p02_identity_api.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p02_identity_api.py), [`p02_snapshot_cost.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p02_snapshot_cost.py), [`p02_cli_command.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p02_cli_command.py), [`p02_cli_hello.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p02_cli_hello.py). Each ran in its own Blender process. No API calls were made.
- **Evidence level reached:** L2 (reproduced at runtime). One trivial machine, one run each, so treat timings as orders of magnitude, not benchmarks.

## Results

| # | Question | Answer | Evidence |
|---|---|---|---|
| 1 | Do `bpy.app.timers` fire in a pure `-b` session? | **No.** In all four variants (script ends; `time.sleep(1)`; operators incl. a render; a 1 s busy loop) the timer was registered (`is_registered=True`) and never fired. | `p02_timers.py`; the only caller of `BLI_timer_execute` is `wm_event_timers_execute` (`wm_event_system.cc:577`), part of the window-manager event loop, which a `-b --python` run never enters |
| 1b | Is there a headless way to own the loop? | **Yes, partly.** `bpy.utils.register_cli_command(id, fn)` plus `-c id args…` runs `fn(argv)` in background mode and exits with its return code. The id must pass `str.isidentifier`; the `--python` registering script must come before `-c`. | `p02_cli_hello.py` printed `P02_CMD_RAN argv= ['--foo', 'bar'] bg= True`, exit 0. A long-running serve loop inside the callback was **not** tested |
| 2 | Does `ID.session_uid` survive save and load? | **No.** Saving does not change it, but reopening (same process or a new one) assigns new values. | Sphere object 138 before, 176 after reopen in the same process; 165 after reopen in a new process. All uids changed. Zero-user data (the default "Dots Stroke" material) is dropped on save |
| 3a | Is `compare_geometry` reachable from Python? | **Yes, for meshes.** `Mesh.unit_test_compare(mesh=, threshold=)` returns `'Same'` or a mismatch string. | Identical quads returned `Same`; one vertex moved returned `Some values of the point attributes are different`. Binding at `makesrna/intern/rna_mesh_api.cc:372`. The name says unit test, so stability across versions is not guaranteed |
| 3b | Does `poll()` expose a failure message? | **Not from `.poll()`** (returns a plain `bool`). **Yes from a call:** the `RuntimeError` text carries the poll message. | `bpy.ops.mesh.loop_select.poll()` returned `False`; calling it raised `Operator bpy.ops.mesh.loop_select.poll() Expected a view3d region & editmesh`. Source: `bpy_operator_function.cc:290` |
| 3c | Operator schema from Python? | **Yes.** `get_rna_type().properties` lists parameters. | `loop_select`: `delimit_edge_loop, delimit_face_loop, deselect, edge_index, extend, face_index, object_index, …` |
| 4 | Cost of a per-mutation checkpoint | `save_as_mainfile(copy=True)`: **4.6 ms** (8 verts, 0.49 MB), **6.6 ms** (96k verts in 200 spheres, 11 MB), **381 ms** (4.0M-vertex grid, 385 MB uncompressed); compressed: 2.4 / 5.0 / 188 ms for 0.09 / 0.32 / 129 MB. Reopening a snapshot: 3 / 13 / 138 ms. | `p02_snapshot_cost.py`, one run |
| 4b | In-session undo steps | `ed.undo_push()` took 0.3 to 1.1 ms on all three scenes. After a mutation and a second push, `ed.undo()` restored the pre-mutation fingerprint on all three (**true**), in 2 to 7.5 ms. | Same script. The fingerprint covers vertex count and the z-sum of the first 2000 vertices of each mesh, which is narrow |
| 5 | The three P01 operators the research report left unaccounted for | **Resolved without re-running.** P01's table sums to 23: 5 ran and changed state, 4 `FINISHED` with no change, **2 `FINISHED` with an effect outside the fingerprint** (`sculpt.set_pivot_position`, `transform.select_orientation`), 6 `CANCELLED`, **1 data-precondition error** (`mesh.knife_project`), 5 segfaults. The report summed only the five named categories (20). | [P01 report](p01-context-override.md) result table |

## What this changes

- **Timer-driven queues are out for background workers.** ledger L-013 and RFC 0003 §5 assumed `bpy.app.timers` could drain agent commands. For a headless worker, own the loop in a `-c` command callback (or a script) instead. Timers remain the route for a live UI session (documented behaviour; not re-tested here).
- **Cross-session identity needs our own id.** `session_uid` is within-process only. Use a UUID in a custom property written by the harness, plus the `(type, name, library)` triple. This confirms the layered-id design in RFC 0003.
- **A geometry oracle exists for meshes today.** `unit_test_compare` can serve as the "reference equivalence" layer (verification layer 3 in RFC 0001 R6) without C++ changes, with the stability caveat above. Other geometry types were not checked.
- **File snapshots are cheap enough for per-mutation checkpoints up to the tested sizes.** Single-digit milliseconds up to roughly 100k vertices; a 4M-vertex scene costs about 190 to 380 ms per snapshot, so snapshot only on mutation (the Crab finding that most turns change nothing supports this) and consider the compressed variant.
- **The `-b` undo workaround holds.** `ed.undo_push()` followed by `ed.undo()` restores state headless on all three scenes.

## Not done / limits

- The GUI baseline for P01's four silent no-ops needs a windowed session; not attempted.
- No timer test in a windowed session, no long-running loop inside a `-c` callback, no multi-process branch test.
- The snapshot timings measure the write path only; they do not include scene fingerprinting or diffing.
- Scenes were synthetic meshes. Real production files (modifiers, node trees, images, simulation caches) will cost more, and the restore check does not cover sculpt or simulation state.
- Single machine, single run per case.

## Follow-ups

- After PR #6 merges: update L-013 evidence (timers fail in `-b`; `register_cli_command` works) and the seam note §3; add a note to RFC 0003 §5 and §8.
- Phase 0 remainder: loop-in-callback test, windowed timer test, realistic scene sizes.
