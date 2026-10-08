# How we work: the newblender research approach

This page describes the method that every other document here follows. The decisions behind each rule live in [RFC 0001](../rfc/0001-newblender.md). This page puts them in one place, in plain terms.

## 1. The question

Blender is a mature, open-source 3D engine built around one assumption: a human sits at the controls with a mouse, a keyboard and a live viewport. Agent integrations today (MCP servers, `bpy` wrappers, add-on bridges) keep that assumption and bolt an AI on top.

**newblender asks the opposite question:** what would the engine look like if an AI agent were its *primary* user? Blender's open source is the raw material for the answer.

The first answer we owe is evidence, not code. "Don't fork without evidence" is a standing caveat from earlier lab work (agent-native-lab #4).

## 2. Principles

1. **Measure before redesigning.** Phase 1 is discovery: understand how the tool is used and how the source behaves before deciding what to change ([R2](../rfc/0001-newblender.md#r2--first-phase-is-discovery-not-building-2026-10-07)).
2. **Challenge old facts, with caution.** Four beliefs behind the retrofit approach are treated as no longer valid ([R1](../rfc/0001-newblender.md#r1--dead-facts-2026-10-07)). Gray zones are parked explicitly instead of being decided by accident.
   - **DF1** "The human operates, the AI helps." Inverted: the agent drives, and the human states intent and judges.
   - **DF2** "Humans write and read the source." Agents now write most code.
   - **DF3** "Agents need tiny imperative steps." Models can declare outcomes in one go.
   - **DF4** "Viewport plus human eye is the core loop." For an agent the loop is declare → evaluate → diff → render → check.
3. **Free sources only.** There is no paid Studio subscription. A *virtual production* is assembled from free docs, trainings, real `.blend` files, source code and design threads, and walked one pipeline stage at a time (S01 Modeling … S12 Grease Pencil) ([R4](../rfc/0001-newblender.md#r4--a-virtual-production-from-free-sources-stage-by-stage-2026-10-07)).
4. **Every claim carries an evidence level.** The levels are L1 documented and traced in source, L2 reproduced at runtime, L3 prototyped, L4 benchmarked, and L5 proven in production. Most of what we know today is L1, and we say so.
5. **Honest scoring.** The builder never grades its own quality. Checks are written before the build, and quality is rated blind ([R7](../rfc/0001-newblender.md#r7--capability-scoring-2026-10-08)).

## 3. Discovery: two lenses, four passes, three layers

**Two tracks run at once** ([R3](../rfc/0001-newblender.md#r3--discovery-runs-both-tracks-at-once-2026-10-07)):

- **Track H (human):** how professionals actually work, stage by stage.
- **Track S (source):** what the code really does, starting from the full operator registry.

They meet on a **capability card**: one YAML file per capability, with a human row, a source row and a verdict.

**Four passes per pipeline stage** ([R5](../rfc/0001-newblender.md#r5--study-method-approved-modelling-pilot-starts-2026-10-07)):

| Pass | Question | Output |
|---|---|---|
| 1. Read | What do professionals do, step by step? | A workflow script with cited steps |
| 2. Dissect | What do real production files actually contain? | A census of free `.blend` files, opened headless and safely (`--factory-startup --disable-autoexec`) |
| 3. Trace | Where in the source is each step gated, and what does it really call? | An internal path map, read from poll and exec bodies |
| 4. Why | Why was it built this way? | Design rationale from developer threads, talks and commits |

**Three distillation layers:**

1. **Cited notes.**
2. **Capability cards.** Each card gets a verdict: *remove* (ceremony), *free* (real logic trapped behind GUI state), *declare* (expressible as a declared outcome) or *keep*. Each verdict is tagged with the dead fact it rests on.
3. **A stage brief,** plus a cross-stage [transformation ledger](../discovery/ledger.md). Every candidate engine change appears there with its evidence level and status.

## 4. Building to learn: live demos

Discovery says what the source *allows*. Demos show what an agent can *actually make* with stock Blender today, and where it hurts.

- **The bridge.** The agent drives a running Blender 5.2 through the official Blender Lab MCP add-on over a local socket (`tools/live/bl.py`). It can also run headless processes for renders and reproducibility checks.
- **The targets.** Each demo is the first slice of a plan from the [showcase](../showcase/00-index.md): 20 real, verified Blender works, each with an agent build plan, a predicted readiness and a predicted difficulty.
- **The sequence.** Plan → write checks → build → verify → report. The checks script is written *before* the build script.

## 5. Verification: six layers of "correct"

From [R6](../rfc/0001-newblender.md#r6--verification-model-how-an-agent-knows-it-was-right-without-a-human-watching-2026-10-07):

| # | Layer | Who judges |
|---|---|---|
| 1 | Validity: is the data well-formed? | machine |
| 2 | Spec conformance: did it build what was asked? | machine, from assertions written before the build |
| 3 | Reference equivalence: is it identical to a known-good result (reproducible fingerprint)? | machine |
| 4 | Downstream fitness: will the next stage work with it (UV stretch, render artefacts, budgets)? | machine |
| 5 | Appearance: does it look like what was meant? | vision model, as a *warning*, never a gate |
| 6 | Taste and intent: is it good? | the human owner |

An agent may call a task done only when layers 1–4 pass.

## 6. Scoring: the five measures

From [R7](../rfc/0001-newblender.md#r7--capability-scoring-2026-10-08). Every agent task reports one row:

| Measure | Meaning |
|---|---|
| **Correctness** | % of pre-written layer 1–4 checks passed, with every open failure listed |
| **Autonomy** | Hands-on human interventions needed, counted separately from approvals |
| **Self-correction** | Problems the agent found and fixed itself vs. problems the owner found later |
| **Cost** | Wall time, iterations, render compute |
| **Quality** | A **blind** rating against real reference frames |

**Rules:**

- Thresholds are never loosened to make a check pass. A threshold that looks wrong goes to the owner as a question, and stays a FAIL until the owner rules.
- Any change the builder makes to a checker is flagged in the report.
- The agent's own look score is kept but labelled "self".

**Blind protocol** (`tools/blind/`):

- Agent renders are mixed with real production frames, all at the same width, metadata stripped and named by random IDs.
- The owner rates each image 1–5 and guesses its source.
- The answer key stays server-side until the owner locks the scores.

## 7. Roles

- **The agent** runs every pass and writes every first draft end to end.
- **The owner:**
  - decides contested verdicts, strategy (reuse vs. rewrite, fork vs. upstream, licensing), gate approvals and anything outward-facing
  - gives the blind quality ratings
  - reviews asynchronously; reviews never block the next stage

## 8. Hygiene

- **Data stays outside the repo,** in `~/newblender-data/`: production files, census output, assets, renders and blind sessions. Reference film frames are used locally for evaluation only and are never published.
- **Documents are the source of truth.** The [public site](https://mbaneshi.github.io/newblender/) is generated from `docs/` on every change.
- **Process:** RFC → discovery → spec → plan. No newblender engine code is written before a spec is approved.
