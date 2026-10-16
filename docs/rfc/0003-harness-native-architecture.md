# RFC 0003 — Harness-native architecture: a Claude-Code-grade harness for a 3D scene

- **Status:** Open (recommendation drafted, nothing decided)
- **Opened:** 2026-10-17
- **Author:** mbaneshi (with Claude Code)
- **Drives:** [#3](https://github.com/mbaneshi/newblender/issues/3)
- **Depends on:** [RFC 0001](0001-newblender.md), [RFC 0002](0002-research-publication.md)
- **Evidence:** [`docs/research/2026-10-17-agent-harness-for-creative-suites.md`](../research/2026-10-17-agent-harness-for-creative-suites.md) (six parallel research notes; sourcing caveats are listed there and apply here)
- **Sibling:** [RFC 0004](0004-platform-stack-and-scope.md) (which platform stack hosts the harness)
- **Discussion:** _not posted; the repo is public, so the owner decides when_

## 1. Question

What does it take for an AI agent to be a first-class citizen of a 3D application the way Claude Code is a first-class citizen of a code repository, and where in Blender (or beside it) do we build that?

An MCP server is only a socket. The harness is the working environment around the model: the loop, addressable queries, diffs, checkpoints and branches, verification, permissions, memory and plan layers, subagents. Claude Code leans on four properties of a repo (text addressability, diffs, git undo, tests as oracle). A scene has none of them by default.

**Framing (owner decision, 2026-10-17).** The mission stays [RFC 0001](0001-newblender.md): redesign the engine so an agent is its primary user. The out-of-process harness in this RFC is a **measuring instrument**, not the destination. Its job is to produce runtime evidence (ledger L2) for engine changes cheaply. Whether the final product is a redesigned Blender engine or a standalone platform ([RFC 0004](0004-platform-stack-and-scope.md)) is **decided after probes H1 and H2**. Until then RFC 0004 is parked.

## 2. Verified current state (2026-10-17)

| Fact | Source |
|---|---|
| All five recorded C++ seams exist at `d13f752e` (v5.2.2). The better operator hook is `wm_operator_finished` (`wm_event_system.cc:1282`), not `WM_operator_poll` (`:1113`). | research §Source |
| `idprop_serialize.cc` serializes IDProperties; it is not an operator-schema dumper. Schemas come free from `bpy.ops.x.get_rna_type()`. | research §Source |
| Timer queue (`bpy.app.timers`) and change stream (`depsgraph_update_post`) are already reachable from Python. | research §Source |
| Undo is linear and truncates redo on every push (`undo_system.cc:547-553`). In `-b` mode `ed.undo()` fails until `ed.undo_push()` is called (measured on 5.2.2). | research §Source, platform note |
| Probe P01: of 23 region-gated operators, 4 returned `FINISHED` with no change and 5 sculpt operators segfaulted. P01 was not re-run for this RFC. | `docs/discovery/probes/p01-context-override.md` |
| Every Blender agent integration found is an unauthenticated "execute arbitrary Python" socket (ahujasid/blender-mcp; Blender Lab MCP says it runs LLM code "without any guards"). | prior-art note |
| CADCraft, PhotoCraft and FilmCraft have a good command registry and timeout contract; none has branching, a change stream, risk classes or automatic verification. | teardown note |
| Foundation, 2026-05-01: "No generative AI functionality is currently available or planned." Upstream acceptance of anything agent-native is unlikely near-term. | platform + prior-art notes |
| Extension `[permissions]` are displayed, not enforced (Python side searched only). | platform note |

## 3. Mapping: repo-harness property to scene equivalent

| Repo-harness property | Scene equivalent | Verdict |
|---|---|---|
| Loop, context management, memory files, skills, plan mode, subagents, MCP | Same, over scene queries and edits | Transfers |
| Hooks (PreToolUse, PostToolUse, Stop) | Op interception, auto-verify, Stop gated on verifier | Transfers, but enforcement needs process isolation |
| Grep/Read addressing | Layered ids `(type, name, library)`, `session_uid`, custom-property UUID | Needs substitute |
| Diff as review unit | Depsgraph updates plus RNA snapshot comparison | Needs substitute (no field-level diff in-tree) |
| git checkpoints and worktrees | Per-mutation `.blend` snapshots; branch = new worker process from a snapshot | Needs substitute |
| Tests as oracle | Scene assertions, reference checks, separate-context VLM judge | Needs substitute for the checkable part |
| Risk and permission classes | External table keyed by `(idname, properties)`, enforced by an OS sandbox | Needs substitute |
| "Looks right" as a cheap oracle | None | No substitute: human approval is a first-class gate |

## 4. Options

| Option | What | Gains | Costs and risks |
|---|---|---|---|
| **A** | Out-of-process Python harness; headless Blender workers | Fastest; no rebase burden; query, coarse change stream, file checkpoints, risk table, verification all feasible | No operator attribution or old values, no in-memory branching; P01 crashes and silent no-ops; API breaks per major version |
| **B** | Small C++ patch queue (each under ~500 lines): operator tap at `wm_operator_finished`, ring buffer plus Python accessor, expose poll message and `compare_geometry`, `--command agent-serve` | Closes observation gaps without changing behaviour; most upstream-friendly | Needs a custom build; AI-contribution policy applies to upstream PRs |
| **C** | Long-lived renamed fork: branchable undo, structured operator results, context-free operators | Only route to engine-level agent citizenship | Project-sized work in entangled code; permanent rebase cost; must be renamed |
| **D** | New Rust engine (ArtCraft-style) | Cleanest harness | Abandons Blender's features; see RFC 0004 for a scoped variant |

Size estimates (patch-sized versus project-sized) come from static reading only; no prototype backs them.

## 5. Recommendation (draft)

**Option A now, Option B queued behind probe evidence, Option C deferred.** "newblender" stays an internal codename; a public fork must be renamed.

Architecture sketch:

- A harness process owns the loop, memory, policy and MCP front end; one headless Blender worker per session (`--command` handler or script-owned loop, always `--disable-autoexec`).
- A CADCraft-style `Backend` trait serves the same method names from a headless `bpy` session or a live UI add-on. Calls carry `not-run` / `may-have-run` semantics; only a read-only allowlist is auto-retried.
- Intent-level meta-tools, not one tool per operator: `scene_query`, `op_describe`, `scene_edit`, `scene_diff`, `checkpoint` / `restore` / `branch`, `verify`, `render_preview`, notes and plan. Raw `run_python` sits behind a default-deny gate and is also the comparison arm in H1.
- Policy follows mytodo's R0 to R4 scale with "spend" read as compute and render cost. A test fails when a registered operator idname is unclassified.
- Verification is the Stop gate: deterministic assertions, then reference checks, then a rubric VLM judge in a separate context, then human approval for taste.

## 6. Probe plan (cheapest informative first)

Costs are the report's arithmetic on assumed token shapes (Sonnet 5.5: USD 2 / 10 per million tokens, cache reads 0.10; reference episode about USD 0.51 cached, 2.60 uncached). They are not measurements.

| Step | Question | Cost |
|---|---|---|
| Phase 0 (done 2026-10-17, see P02) | Do timers fire in pure `-b`? Does `session_uid` survive save/load? Are `compare_geometry` and the poll message reachable from Python? Cost of `save_as_mainfile(copy=True)` on a real scene? Re-run P01's three unaccounted operators with a GUI baseline. | USD 0 |
| H1 | Structured tools versus raw `run_python` on 20 verifiable tasks (BlenderGym-style start/goal pairs) | about USD 34 |
| H2 | Does snapshot and rollback change agent outcomes? (No direct evidence in the literature.) | about USD 22 |
| H3 | Deterministic checks versus VLM judge, with an injected-fault set | about USD 42 |
| Opus slice | One top-model run | about USD 25 |
| Reserve | A silent cache failure multiplies spend about fivefold | about USD 77 |

Each probe is accountable to the [transformation ledger](../discovery/ledger.md): a result that does not move an entry is not worth its spend.

| Probe | Ledger entries it feeds | What a good result means | Needs C++ to confirm? |
|---|---|---|---|
| Phase 0 (done, [P02](../discovery/probes/p02-phase0-premises.md)) | L-013, L-014 | Premises measured; the timer-driven queue is rejected for headless workers | no |
| H1 structured tools versus raw `run_python` | L-003, L-004 | Typed results and explicit parameters beat exec-only at equal spend | the typed result record (L-012) does |
| H2 snapshot and rollback | L-008 | Cheap rollback lifts agent pass rate, which justifies the branchable-undo work | file snapshots only show the value, not the in-memory implementation |
| H3 deterministic checks versus VLM judge | L-010 | A machine QA gate catches what the VLM catches, at lower cost | no |

Entries L-012 (operator-finished tap) and L-014 (attributed change stream) can only be confirmed with Option B patches (Phase B); the harness can show the need, not the implementation.

## 7. Open questions for the owner

- [x] Q1 — Approve "A now, B behind evidence, C deferred" as the working direction? **Yes, as an instrument for the engine mission; final goal decided after H1/H2 (owner, 2026-10-17).**
- [x] Q2 — Start Phase 0 (no API spend) now, together with Phase A (seams doc, ledger L-012 to L-015)? **Done: Phase A in PR #6, Phase 0 in PR #8.**
- [ ] Q3 — Is the human approval gate for taste a first-class product feature (recommended) or a fallback?
- [ ] Q4 — Licensing posture: keep the harness out-of-process and GPL-clean, or commit now to an in-process add-on? (Out-of-process IPC against GPL Blender has no official statement; this is not legal advice.)
- [ ] Q5 — Upstream strategy: submit only behaviour-neutral observation patches, keep the rest in a renamed fork?
- [ ] Q6 — Spend cap for the first probe round (draft: about USD 60 of the 200)?

## 8. Corrections to earlier assumptions

| Earlier assumption | Now |
|---|---|
| Hook `WM_operator_poll` | Hook `wm_operator_finished`; poll is called for UI state many times per frame |
| `idprop_serialize.cc` exports schemas | It does not; use `get_rna_type()` |
| Queue and change stream need C++ | Reachable from Python; C++ is for attribution, old values and granularity |
| `FINISHED` means it worked | 4 of 23 returned `FINISHED` with no change (P01) |
| Python edits are undoable | `bpy.ops` pushes no undo by default; `-b` disables it until `ed.undo_push()` |
| Undo can be a checkpoint tree | It is linear and truncates; branching must be built outside it |
| A timer-driven queue drains agent commands | Timers never fired in four `-b` variants (P02); own the loop in a `register_cli_command` + `-c` callback. Long-running loop inside it not yet tested |
| `session_uid` is a stable id | It changes on every save and load (P02); use `(type, name, library)` plus an add-on-written UUID property |

## 9. Unverified claims

Carried over from the report, not repeated in full: line anchors and size estimates are static reading only; P01 not re-run; several paper numbers come from abstracts or small-model summaries; the Foundation's "no generative AI planned" statement sits beside a first-party Lab MCP server and the notes do not reconcile them; Foundation policy v3 and any CLA were not retrieved; star counts disagree across sources.
