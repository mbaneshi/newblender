# Probe P03: a serve loop inside a `-c` callback, with crash recovery

- **Date:** 2026-10-17 · **Blender:** 5.2.2 LTS, background mode (`-b --factory-startup --disable-autoexec`), macOS arm64 (M4)
- **Question:** [P02](p02-phase0-premises.md) showed timers never fire in `-b`, and that `bpy.utils.register_cli_command` + `-c` runs a callback in background mode. Can a **socket loop inside that callback** drive `bpy` reliably, and can a supervisor recover from a real worker crash?
- **Scripts:** [`p03_serve.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p03_serve.py) (worker), [`p03_client.py`](https://github.com/mbaneshi/newblender/blob/dev/tools/probes/p03_client.py) (supervisor and checks). No API calls.
- **Evidence level reached:** L2 (reproduced at runtime). One run on one machine, synthetic scenes.

## Design

The worker registers `p03_serve` and, when started with `-c p03_serve PORT`, opens a localhost TCP socket and serves JSON lines (`{"id","method","params"}` → `{"id","ok","result"|"error","ms"}`) on Blender's main thread. No event loop and no timers. Methods: `ping`, `scene.query`, `op.run`, `undo.push`, `undo.undo`, `checkpoint` (`save_as_mainfile(copy=True)`), `restore` (`open_mainfile`), `shutdown`, and `crash.sculpt_box`, a real P01 crasher (`sculpt.face_set_box_gesture` under a borrowed region). The supervisor starts the worker, runs the checks, lets the crasher kill it, starts a fresh worker and restores the last checkpoint.

## Results

All ten checks passed on the first run.

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | The loop serves requests with no timers | **Pass** | `ping` answered; worker cold start 3.0 s |
| 1b | Loop latency | **0.07 ms median, 0.10 ms p95, 0.14 ms max** over 300 pings (loopback round trip) | `ping_rtt_ms` |
| 2 | An operator runs inside the loop | **Pass** | `mesh.primitive_uv_sphere_add` → `FINISHED`, objects 3 → 4 |
| 3 | `undo_push` then `ed.undo` restores state inside the loop | **Pass** | scene hash `b2a55d72…` before, `319b2d4c…` after an added cube, `b2a55d72…` after undo |
| 4 | Checkpoint and restore inside the loop | **Pass** | same hash before and after `restore` |
| 5 | 20 more add-and-query cycles stay consistent | **Pass** | object count 4 → 24 exactly |
| 6 | A bad request returns an error and the loop survives | **Pass** | `AttributeError: … mesh.no_such_operator … could not be found`, then `ping` OK |
| 7 | A real crash is detected | **Pass** | `crash.sculpt_box` closed the connection; the process returned **-11 (SIGSEGV)** |
| 8 | A fresh worker restores the checkpoint after the crash | **Pass** | restored hash equals the checkpoint hash; second worker started in 0.5 s |
| 9 | Clean shutdown | **Pass** | `shutdown` acknowledged, exit code 0 |

## What this changes

- **The headless worker model is viable.** A `-c` callback can own the loop. This settles the open item from P02 and the RFC 0003 §5 design. Timers stay out of the headless path.
- **Crash recovery works with a supervisor.** A segfault in a P01 operator kills only the worker; the client sees EOF and a negative return code, and a replacement worker restores the last checkpoint in about half a second. This confirms the "subprocess plus checkpoint" rule P01 implied.
- **Loop overhead is negligible.** 0.07 ms per request is far below any model call; per-request cost is dominated by Blender, not the transport.
- **Operators, undo and file snapshots behave inside the loop as they did in P02's one-shot scripts.**

## Limits

- Check 2 uses an operator that needs no GUI region. Region-gated operators inside the loop were tested only through the crasher; the P01 matrix was not repeated.
- One client, no authentication, no request size limits; this is a probe, not a protocol (PhotoCraft's token and size limits are the pattern to copy).
- No `not-run` / `may-have-run` timeout semantics yet: a call that crashes the worker is detected as a closed connection, but the request-state marker CADCraft uses is not implemented.
- The checkpoint here is a full file save; snapshot cost at scale is in P02. The restore reloads the whole file, so object identity (`session_uid`) changes, as P02 found.
- Cold start was 3.0 s for the first worker and 0.5 s for the second (warm filesystem cache); do not treat either as typical.
- Synthetic scenes, one run, one machine.

## Follow-ups

- Add the request-state marker (queued / started / cancelled) to the worker and test a timeout.
- Repeat the P01 region-gated matrix through the loop.
- With P02 and P03, the headless worker has what H1 needs: query, operators, undo, checkpoint and restore, crash recovery.
