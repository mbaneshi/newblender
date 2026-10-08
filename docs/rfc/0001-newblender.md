# RFC 0001 — newblender: Blender's source, redesigned for AI as the primary user

- **Status:** Brainstorming (open questions being resolved one at a time)
- **Opened:** 2026-10-07
- **Author:** mbaneshi (with Claude Code)
- **Successor:** the spec at `docs/superpowers/specs/` once this RFC resolves

## 1. Framing (the owner's words, condensed)

| | |
|---|---|
| **Good news** | Blender is open source. Code, docs, manual, developer docs, Blender Studio, the community: all on hand (mirrored at `~/agent-native-lab-data/sources/blender/`). |
| **Bad news** | Its whole architecture is built around a human operator. As of August 2026 that is *old school*. |
| **Neither** | Current efforts to retrofit it from *human* to *human + agent* (MCP servers, `bpy` wrappers, Blender Lab MCP, our own lab primitives) don't make sense, because they sit on facts that are no longer valid. |

**Thesis under test:** don't retrofit agents onto a human-shaped tool. Start from what an AI needs from a 3D/creative engine, and use Blender's open source as the raw material.

## 2. Prior evidence (agent-native-lab)

- Four-layer trace / golden table (`agent-native-lab/lab/blender/golden-table.md`, issue #7): 5 tasks, 26 human steps vs 5 declarations, 20 operators vs 0, 93 vs 25 depsgraph evaluations, 9/26 steps unrunnable without GUI context, edit-mode staleness, human defaults leaking (9 channels keyed instead of 1).
- #4 internals as AI substrate (BMesh, depsgraph, Geometry Nodes); #22 end-goal hypotheses; #2 observable scene state.
- Caveat recorded in #4: "don't fork without evidence". This RFC must say how it answers that.

## 3. Open questions

- [x] Q1 — Which "facts" behind the retrofit approach are no longer valid? → R1
- [x] Q2 — What is newblender for in its first phase? → R2 (discovery first)
- [x] Q3 — How do we run discovery? → R3 (both tracks, meeting in capability cards)
- [ ] Q3a — The owner's refinement: anchor discovery in **one complete real production** (an open movie with all its files) and reverse-engineer it end to end, noting internals and human-interface findings along the way. Which production? → No Blender Studio subscription, and none planned. Owner's position: for every aspect there are very good free docs, repos, assets and instructions if we research deeply, and golden insight sits across Studio, the manual, the developer portal and the forum. → R4
- [x] Q3b — Study and distillation method → R5
- [ ] Q4 — Reuse vs rewrite: ~3.25M lines of C++ (Cycles, BMesh, Geometry Nodes, I/O) against the Rust-rewrite pattern (ArtCraft). Deferred until discovery has data.
- [ ] Q5 — Relationship to upstream. Note: the Blender Foundation's May 2026 stance ("made by humans for humans") makes upstreaming unlikely near-term.

### R6 — Verification model: how an agent knows it was right without a human watching (2026-10-07)

**Principle.** The human is not removed; the human's role moves. Instead of watching every step, the human (a) states the intent, (b) judges taste at the end, and (c) periodically calibrates the checkers. Verification is part of the engine, not a layer on top of it.

**Six layers of "correct":**

| # | Layer | Question | How it is checked | Machine |
|---|---|---|---|---|
| 1 | **Validity** | Is the data well-formed? | Manifold, no degenerate faces, consistent normals, no doubles. BMesh operators already guarantee valid output by construction. | full |
| 2 | **Spec conformance** | Did it build what was asked? | The request becomes measurable assertions, written **before** building: dimensions, counts, face budget, symmetry, UVs, naming. | full |
| 3 | **Reference equivalence** | Is it the same as a known-good result? | Mesh isomorphism compare (`mesh_comparison` exists upstream); also how declarative twins are proven equal to their operators. | full |
| 4 | **Downstream fitness** | Will the next stage work with it? | Automated stress tests: extreme rig poses with measured stretch, numeric UV distortion, a render with artefact checks (the Studio does this by hand; workflow row 73). | almost full |
| 5 | **Appearance** | Does it look like what was meant? | Multi-angle renders compared to the reference/brief by a vision model. Research shows these lag humans. | partial: **warning, not gate** |
| 6 | **Taste and intent** | Is it good? | Human judgement (gray zone G1). | no |

**Rule:** an agent may declare a task done only when layers 1–4 pass. Layer 5 raises warnings. Layer 6 is the owner's.

**Mechanisms that make the checks trustworthy:**

1. **Assertions before construction**, so the agent cannot fit the test to its own result.
2. **Builder ≠ checker:** an independent agent or a deterministic tool verifies.
3. **Deterministic headless runs:** the same input gives the same output, so every result is reproducible.
4. **Diffs and transactions:** every step states what it changed and can be reversed, so errors stay small and traceable.
5. **Calibration against the human:** on a sample, machine verdicts are compared with blind human scores (agent-native-lab #47 ledger) to learn where machine checks can be trusted.

**Engine consequences** (already in the ledger):

- **L-003:** return diffs, not statuses.
- **L-004:** explicit inputs and machine-readable preconditions.
- **L-010:** machine QA gates and isomorphism compare.

Stock Blender makes verification hard: results are only visible by drawing them, edit-mode data is stale until mode exit, and scripted calls leave no undo history.

### R7 — Capability scoring (2026-10-08)

**Why.** After three live builds (chair, Flow slice, Charge slice), the scores used so far were mixed:

- **Objective:** pre-written checks.
- **Self-graded:** the agent's own layer-5 "look" score.
- **Predicted:** readiness and difficulty ratings in the showcase plans.

Self-grading is a conflict of interest, and predictions are only worth something when compared with outcomes.

**The score.** Every agent task reports one row with five measures:

| Measure | Definition | Source |
|---|---|---|
| **Correctness** | % of pre-written layer 1–4 checks passed on the final run, plus the failures left open (listed, not hidden) | check scripts |
| **Autonomy** | Hands-on human interventions needed to finish. Counted separately from approvals and topic choice. | session log |
| **Self-correction** | Problems found and fixed before delivery (by checks / by looking) vs. problems the owner finds after delivery | build log, owner review |
| **Cost** | Wall time, agent iterations, render compute | logs |
| **Quality** | **Blind** rating against the real reference (see below). Replaces the agent's self-graded layer-5 score as the quality number. | blind scoring session |

**Rules:**

1. **Checks are written before building** and owned separately from the build. When the builder changes a checker, the change is flagged in the report with the reason.
2. **Thresholds are never loosened to pass.** A threshold that looks wrongly defined is raised as a question for the owner. It stays a FAIL until the owner rules on it.
3. **The agent's own look score is kept, but labelled "self".** It never counts as the quality measure.
4. **Calibration:** across tasks, predicted readiness and difficulty are compared with the measured row, to show how good the agent's planning is.

**Blind scoring:**

- **The pool:** agent renders are mixed with real frames from the reference works, all normalised (same width, metadata stripped, random file names) and served by a local tool under random IDs.
- **The ratings:** the owner gives each item (a) a 1–5 production-quality rating and (b) a guess, agent or studio.
- **The answer key** stays server-side. Scores lock before unblinding.
- **Results:** mean quality for agent vs. studio items, and guess accuracy. Accuracy near 50% would mean the agent's work is indistinguishable from the studio's.
- **Licensing:** reference frames are used locally for evaluation only and are never published.
- **Tool:** `tools/blind/`.
- **First session (`s01-flow-charge`, 2026-10-08):**
  - **Mean quality:** agent 1.67 vs. studio 4.00.
  - **Guess accuracy:** 83%.
  - **By slice:** Flow 1.00 (self score 2.5, so 1.5 too high) and Charge 2.33 (self score 2.5, close). One Charge frame passed as studio work.
  - **Takeaway:** the self score is not a trustworthy quality signal. Rule 3 holds.

## Discovery notes

- [00 — Prior work, and which of its claims rest on dead facts](../discovery/00-prior-work.md)
- [01 — Source module map](../discovery/01-source-module-map.md)
- [02 — Parallel efforts (ArtCraft, Zoo/KCL, papers)](../discovery/02-parallel-efforts.md)
- [03 — Source inventory per stage](../discovery/03-inventory.md), with slices [03a local](../discovery/03a-inventory-local.md), [03b real files](../discovery/03b-inventory-real-files.md), [03c why](../discovery/03c-inventory-why.md)
- **S01 Modeling pilot:** [brief](../discovery/s01-modeling/05-brief.md) · [workflow](../discovery/s01-modeling/01-workflow-script.md) · [census](../discovery/s01-modeling/02-census.md) · [trace](../discovery/s01-modeling/03-trace.md) · [why](../discovery/s01-modeling/04-why.md)
- [Capability cards](../discovery/capabilities/) (320, S01) · [Transformation ledger](../discovery/ledger.md) (L-001 … L-011)
- [Showcase](../showcase/00-index.md): 20 verified Blender works, each with an agent build plan
- **Live demos:**
  - [001 chair](../demos/001-chair/report.md): 12/12 checks
  - [002 Flow slice](../demos/002-flow/report.md): 11/11 checks, blind quality 1.00
  - [003 Charge slice](../demos/003-charge/report.md): 2 open fails awaiting owner rulings, blind quality 2.33

## 4. Resolutions

### R1 — Dead facts (2026-10-07)

This is a lab: its job is to challenge our previous perceptions. All four beliefs below are treated as no longer valid, "and beyond":

1. **The human is the operator, the AI the helper.** Inverted: the agent drives; the human states intent and judges.
2. **Humans write and read the source.** Agents now write most code, so the source can be organised for agents to read, change and regenerate.
3. **Agents need tiny imperative steps.** Models hold the whole scene, reason over the maths directly, and can declare the outcome in one go.
4. **A live viewport plus a human eye is the core loop.** For an agent the loop is declare → evaluate → diff → render → vision check.

**Stance: with caution.** The core idea is valid: we are in a transition and a paradigm shift. Gray zones are explicitly parked for later, not decided:

- **G1** Fine-tuning models so they can act like a human in 3D, or judge and qualify final artifacts the way a human would.
- **G2** A self-learning lab (the system improves from its own runs).

### R2 — First phase is discovery, not building (2026-10-07)

**Who:** the owner and Claude, together, are responsible for turning Blender into newblender: native for AI and agents.
**How:** by taking away what is not necessary and finding how to speed things up. Blender is the *first* lab; more engines follow.
**Method:** reverse-engineer before changing.

1. **Discover through two lenses at once:**
   - *Human lens*: how professionals actually work (Blender Studio training and production docs, the manual, real workflows).
   - *Source lens*: what the code really does (modules in the source tree, how a UI action becomes data and computation).
2. **Then, gradually,** find what needs to change: what to remove, what to keep, what to make declarative or faster.
3. **Look sideways:** parallel endeavours elsewhere (for example a reported effort to rebuild the Adobe suite as an agent-native app in Rust) and our own experiments in mytodo.

Prior discussions of the human way (Studio docs) and source modules exist in issue bodies in agent-native-lab and mytodo; discovery builds on them rather than restarting.

Rejected framings for phase 1: a benchmark-first proof instrument, a usable engine from day one, a from-scratch foundation design.

### R3 — Discovery runs both tracks at once (2026-10-07)

- **Track H (human-led):** walk the Blender Studio pipeline stage by stage and trace each professional step down into the code.
- **Track S (source-led):** audit the source module by module, starting from the full operator registry (~2,000 operators, countable).
- **Meeting point:** a **capability card** per capability. Track H fills the human row, Track S fills the source row, and the verdict is given once both rows exist. Cards are independent, so agents can fill them in parallel.

### R4 — A virtual production from free sources, stage by stage (2026-10-07)

- **No paid film.** There is no Blender Studio subscription, so no single paid film is the anchor. Instead, a **virtual production** is assembled from free material and walked one pipeline stage at a time (S01 Modeling … S12 Grease Pencil, plus cross-cutting X1 pipeline, X2 Python/extensions, X3 core architecture).
- **One dossier per stage**, drawing on four kinds of source:
  - Studio pipeline docs and free trainings (human lens)
  - real free files to take apart (ground truth)
  - developer docs and source modules (internal lens)
  - forum, design threads and talks (the *why*)
- **Step one is an inventory** of those sources per stage: `docs/discovery/03-inventory.md`. Then a study and distillation method is proposed.

### R5 — Study method approved; modelling pilot starts (2026-10-07)

**Four passes per stage:**

1. **Read** → workflow script
2. **Dissect** free real files headless → usage census
3. **Trace** human steps to source → internal path map
4. **Why** → design rationale

**Three distillation layers:**

1. Cited notes
2. Capability cards (verdict: remove / free / declare / keep, tagged with the R1 dead fact)
3. Stage brief, plus a cross-stage transformation ledger

**Order:** S01 Modeling is the pilot; templates are tuned with the owner, then other stages fan out to parallel agents. X3 core runs alongside throughout.

**Roles:**

- **Agent** carries all passes and first drafts end to end.
- **Owner** decides:
  - contested verdicts
  - strategic calls (reuse vs rewrite, fork/extract/upstream, licensing)
  - gate approvals
  - outward actions
  - optional live GUI sessions

  Reviews are asynchronous and never block the next stage.

**Data:** the core set of free files is approved for download. Data lives outside the repo at `~/newblender-data/`. `.blend` files are opened only with `--factory-startup --disable-autoexec`, so embedded scripts never run.
