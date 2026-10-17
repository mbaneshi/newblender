# Roadmap

What comes next, in order of when we expect to do it. Nothing here is a commitment to write engine code: the process stays RFC → discovery → spec → plan, and the spec needs the owner's approval.

## Now: turn L1 claims into L2 evidence

Most ledger entries are documented and traced (L1) but not yet reproduced at runtime (L2). These are the cheap probes from the [S01 brief §8](../discovery/s01-modeling/05-brief.md#8-open-questions-and-next-probes). Results go into the [log](log.md).

| Probe | Question | Ledger |
|---|---|---|
| **Undo** | Do scripted operator calls really push no undo step? | L-008 |
| ~~**Context override**~~ | **Done, 2026-10-08:** [P01](../discovery/probes/p01-context-override.md). The poll passes 21/23 with a borrowed region; 5 operators did the job, 4 failed silently and 5 crashed. Follow-ups: a drawn-region baseline, and gesture point lists. | L-004, L-011 |
| **Twin parity** | Do "exact" declarative twins give identical meshes? Tested with an isomorphism compare. | L-006, L-010 |
| **Stroke replay** | Can a sculpt brush stroke be replayed headless? | L-009 |

## Next: owner rulings and a second blind session

- **Owner rulings on the two open Charge checks:**
  - Should UV stretch be weighted by area?
  - Should known emitters be masked out of the firefly count?
- **Quality iteration.** Rebuild the Charge slice aiming at the levers the blind session pointed to (lighting contrast, emissive cells, smoke in EEVEE). Then run a second blind session with more items, to test P3 and P4 in [findings](findings.md).
- **"Today" slices.** Build one of the three works predicted *Today* (procedural still life, Molecular Nodes or product viz at scale). This calibrates the readiness predictions against outcomes, as R7 asks.

## Then: the second pipeline stage

- **Apply the S01 retrospective first:**
  - read poll bodies (not names)
  - record the operator id for each workflow step
  - name a counter-corpus up front (hard-surface / archviz)
  - split the trace pass across parallel agents
- **Candidate stages:**
  - **S04 Geometry Nodes**, which is closest to the declarative core
  - **S05 Rigging**, which is likely the most human-shaped, and so the best test of [P1](findings.md#p1-the-gui-is-mostly-a-wrapper-not-the-substance-confidence-high)

## Later: towards a spec

- Once enough stages have data, decide [RFC 0001](../rfc/0001-newblender.md) Q4 (reuse vs. rewrite) and Q5 (relationship to upstream).
- Write the newblender spec: the agent-native shape across stages, starting from the [S01 proposal](../discovery/s01-modeling/05-brief.md#6-the-agent-native-shape-for-modelling-proposal-interpretation).
- [RFC 0002](../rfc/0002-research-publication.md): decide whether and how to publish the discovery work as a research series.

## Horizon notes: what the stack opens (north star, 2026-10-17)

The north star ([RFC 0001 R8](../rfc/0001-newblender.md), [RFC 0004](../rfc/0004-platform-stack-and-scope.md)) is a Rust kernel (native and WASM), Supabase as the data layer, a Svelte front end and a native agent harness. While we do lab work we keep it in the back of our minds. These are **hypotheses from reasoning about how the tools work, not tested for 3D**; each is a candidate star check, not a plan.

| Choice | What it may open | Gap it answers (evidence) |
|---|---|---|
| Supabase: Postgres, auth, storage, realtime, row-level security | Append-only event log with branches as rows; snapshot and render storage; change streaming to agents and viewers; risk classes (R0 to R4) enforced as row-level policy | Linear truncating undo ([04](../discovery/04-ai-wiring-seams.md) §5); no change stream; extension permissions are displayed, never enforced |
| Rust server and kernel | One kernel native and in WASM; headless by construction; command registry and JSON Schema from one source; WASM sandbox for agent code | GUI-coupled operators (P01: 0 of 23 pass poll headless); drifting tool vocabularies across the Craft apps |

**Look-ahead habits (cheap; they shape format, never scope):**

1. Log probe results as event records (actor, model, input, output, previous hash), the nexus envelope. JSON lines today, a table later.
2. Write tool contracts as JSON Schema first; they map to Rust types later.
3. Keep Blender behind a backend interface so the worker can be swapped.
4. Keep this list with an evidence level per item, like the ledger.

**Guards.** Each lab step must answer its own question first; look-ahead only decides naming and format. Anything that costs real effort gets its own issue. Treat Supabase and Rust as hypotheses until the T0 spike; unverified costs include the hosted-service dependency, row-level-security complexity and realtime limits at scene-sized payloads.

## Parked (gray zones)

- **G1:** fine-tuning models to act like a human in 3D, or to judge art the way a human would.
- **G2:** a self-learning lab that improves from its own runs.
