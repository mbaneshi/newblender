# Research log

A dated record of what was done, in order, with links to the evidence. It is append-only: new entries go at the bottom, and old entries are corrected only by a later entry that says so.

## 2026-10-07: the RFC and the framing

- **Opened [RFC 0001](../rfc/0001-newblender.md),** starting from the owner's framing:
  - **Good:** Blender is open source.
  - **Bad:** its whole architecture assumes a human operator.
  - **Neither:** today's retrofits (MCP servers, `bpy` wrappers) sit on facts that no longer hold.
- **Resolved R1–R5 in one sitting:**
  - the four dead facts (DF1–DF4) and two parked gray zones
  - discovery first
  - two tracks meeting on capability cards
  - a virtual production from free sources
  - the four-pass study method
- **Prior evidence carried in from agent-native-lab:** a golden-table trace of 5 tasks. Humans needed 26 steps where 5 declarations would do, and 9 of the 26 steps could not run without GUI context.

## 2026-10-07: discovery corpus

- **[Discovery 00](../discovery/00-prior-work.md):** which claims in our own earlier work rested on dead facts.
- **[Discovery 01](../discovery/01-source-module-map.md):** a map of the source modules.
- **[Discovery 02](../discovery/02-parallel-efforts.md):** parallel efforts. No confirmed agent-native fork of Blender exists. ArtCraft chose a Rust rewrite. Upstream's "made by humans for humans" stance makes upstreaming unlikely.
- **[Discovery 03](../discovery/03-inventory.md):** an inventory of free sources per pipeline stage. Real production files were downloaded to `~/newblender-data/` (outside the repo).
- **Tools built:**
  - `tools/registry/` dumps all 2,498 operators and scans the C/C++ source
  - `tools/census/` dissects `.blend` files headless

## 2026-10-07: the S01 Modeling pilot

All four passes ran on the first stage, plus the distillation:

- **[Pass 1, workflow script](../discovery/s01-modeling/01-workflow-script.md):** 73 cited professional steps.
- **[Pass 2, census](../discovery/s01-modeling/02-census.md):** 78 free production files.
  - 91% of mesh objects carry modifiers.
  - 94.5% of faces are quads.
  - The median mesh has 111 vertices.
- **[Pass 3, trace](../discovery/s01-modeling/03-trace.md):** 320 modelling operators.
  - 70 poll bodies were read.
  - 178 operators are gated by mode alone.
  - Only 50 (16%) truly need a GUI.
- **[Pass 4, why](../discovery/s01-modeling/04-why.md):** 38 design sources.
- **[320 capability cards](https://github.com/mbaneshi/newblender/tree/dev/docs/discovery/capabilities):** 124 declare, 73 free, 67 keep, 56 remove.
- **[Transformation ledger](../discovery/ledger.md):** L-001 … L-011, all at evidence level L1.
- **[Stage brief](../discovery/s01-modeling/05-brief.md),** with a retrospective. The biggest lesson: a name-based heuristic for "is this operator gated?" was wrong half the time. Pass 3 must read poll bodies.

## 2026-10-07: the showcase

- Picked **[20 real Blender works](../showcase/00-index.md)**, all verified against sources, covering the whole range of the tool: feature films, open movies, VFX, NPR, a TV series, data visualisation, product viz at scale, a game and fluid simulation.
- Wrote an agent build plan for each one: readiness (3 Today, 11 Partial, 6 Taste-bound), difficulty, a first slice and a six-layer verification plan.
- Added [R6](../rfc/0001-newblender.md#r6--verification-model-how-an-agent-knows-it-was-right-without-a-human-watching-2026-10-07), the six-layer verification model.

## 2026-10-07 → 08: live demos

The agent built three first slices live in Blender 5.2.2 through the Blender Lab MCP bridge. Each checks script was written before its build script.

- **[001 Chair](../demos/001-chair/report.md):** a warm-up. 12/12 checks pass.
- **[002 Flow slice](../demos/002-flow/report.md):** a flooded-forest boat shot in the style of *Flow*, rendered in EEVEE at 4K.
  - Checks: 11/11, the reproducible fingerprint is identical across a fresh headless rebuild, and the render budget passes.
  - The agent hit and fixed eight problems along the way, and never loosened a threshold. Examples: a camera inside a tree, and haze that turned the frame black.
- **[003 Charge slice](../demos/003-charge/report.md):** a battery-factory bay in the style of *Charge*.
  - Checks: 11/11 live, and the fingerprint reproduces.
  - Two layer-4 checks fail and are waiting on owner rulings:
    - **UV stretch:** 12.4% of faces are in tolerance by face count, but 94–99% by area.
    - **Fireflies:** 24 against a limit of 20, all of them spark pixels.
  - One checker change was flagged in the report.

## 2026-10-08: capability scoring and the first blind session

- Added [R7](../rfc/0001-newblender.md#r7--capability-scoring-2026-10-08): five measures, written-before-build checks, and blind quality.
- Built `tools/blind/` (4/4 tests). The answer key cannot be read before the owner locks.
- **Session `s01-flow-charge`:** 12 images, 6 agent and 6 studio. The owner rated them blind.
  - **Mean quality:** agent 1.67, studio 4.00.
  - **Source guessing:** 83% correct.
  - **Flow slice:** 1.00 blind against a self score of 2.5. **Charge slice:** 2.33 blind against a self score of 2.5.
  - One Charge frame passed as studio work; one real Flow frame was taken for agent work.

## 2026-10-08: going public

- Set up branch rails: `dev` is the integration branch, and `main` moves by tag only.
- Moved the demo reports into the repo and added a README.
- Made the repo public at [mbaneshi/newblender](https://github.com/mbaneshi/newblender) and launched the [site](https://mbaneshi.github.io/newblender/) (English and Persian), generated from `docs/`.
- Added a newblender card to mbaneshi.ir and released it as v2.3.1. The deploy sat queued until the self-hosted runner came back, then succeeded; the link is live in all three locales. The Docker image-removal failure from the previous deploy is tracked in distributed-computation/mbaneshi-ir-site#42.
- Started this research section: [approach](approach.md), this log, [findings](findings.md) and the [roadmap](roadmap.md).

## 2026-10-08: probe P01, region-gated operators headless

The first runtime probe from the roadmap. Full write-up: [P01](../discovery/probes/p01-context-override.md).

- **Polls:** 0 of the 23 region-gated modelling operators pass their poll headless, and 21 pass once any region is borrowed, even one that has never been drawn.
- **Exec outcomes:**
  - 5 did their job, verified by a before/after fingerprint.
  - 4 returned FINISHED with real arguments and changed nothing.
  - 5 sculpt gesture operators **crashed Blender** in their undo push.
- **Our own mistake:** on the first run, `loop_select` returned CANCELLED. That looked like evidence against the S01 trace, until reading the exec body showed the probe had not passed the hidden `edge_index`. With the index it works. The claim stands, and the episode is logged because it is the same anti-pattern seen from the agent's side.
- **Ledger:** L-003 and L-004 moved from L1 to **L2**. New runtime evidence was added to L-008 and L-011.
