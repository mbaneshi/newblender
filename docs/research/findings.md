# Findings and current thinking

Two kinds of statement live here, kept apart on purpose:

- **Results:** measured facts, each with its evidence level and source.
- **Positions:** what we currently think the results mean. Each position states its confidence and what would change our mind.

A position may be wrong. A result should only be wrong if the measurement was.

## Results

### The source: S01 Modeling (evidence L1, Blender 5.2.2)

| Result | Value | Source |
|---|---|---|
| Operators registered | 2,498 (2,210 C++, 288 Python) | registry dump |
| Operators failing a headless poll in every mode (factory scene) | 1,605 (64%) | registry dump |
| Modelling operators that pass a headless poll given the right mode and data | 270 of 320 (84%) | [trace](../discovery/s01-modeling/03-trace.md) |
| …that truly need a GUI | 50 (16%): 23 need a region, 27 need an event stream | trace |
| Modelling operators gated by *mode alone* | 178 of 320 | trace |
| Modal operators that also have a non-interactive `exec` | 51 of 66 | trace |
| Geometry-changing operators with a declarative twin (a modifier or GN node) | 125 of 184 (68%) | trace |
| Poll checks that describe *where the button lives*, not what the function needs | the name heuristic was wrong for 50% | trace |

### Runtime probes (evidence L2)

| Result | Value | Source |
|---|---|---|
| Region-gated modelling operators passing poll headless | 0 / 23 | [P01](../discovery/probes/p01-context-override.md) |
| …passing poll once any region is borrowed (never drawn, no view data) | 21 / 23 | P01 |
| …that then did their job, verified by fingerprint | 5 | P01 |
| …that returned FINISHED with real arguments but changed nothing | 4 (shear, brush stroke, rip, rip-move) | P01 |
| …that crashed Blender (segfault in sculpt undo) | 5 | P01 |

### Real production files (evidence L1, 78 free files)

| Result | Value |
|---|---|
| Mesh objects carrying modifiers (asset files) | 91% |
| Quad faces | 94.5% (ngons 0.1%) |
| Median mesh size | 111 vertices |
| Geometry Nodes modifiers | 836 in asset files, 8,423 in shot files |

**Caveat:** the sample is stylised animated film, so hard-surface work is under-represented.

### What the agent can build today (live demos)

| Demo | Correctness | Blind quality (agent / studio) | Self score |
|---|---|---|---|
| 001 Chair | 12/12 | not scored | n/a |
| 002 Flow slice | 11/11, plus layers 3–4 pass | **1.00** / 3.75 | 2.5 |
| 003 Charge slice | 11/11 live; 2 layer-4 fails open | **2.33** / 4.50 | 2.5 |

Across the blind session: mean quality was 1.67 for the agent against 4.00 for the studio, and the owner guessed the source correctly 83% of the time.

## Positions

### P1. The GUI is mostly a wrapper, not the substance (confidence: high)

84% of modelling operators run headless once mode and data are right, and 68% of geometry operations already have a declarative twin. Most of Blender's "human-ness" sits at the edges: modes, selection-as-scope, modal drag loops, polls tied to UI location, and statuses instead of results. The core algorithms are shared by the operator and the modifier.

- **Implication:** newblender is more likely a **re-layering** of existing cores (BMesh, `geometry::`, modifiers, Geometry Nodes) than a rewrite.
- **What would change our mind:** if other stages (rigging, animation, simulation) show their logic is fused into the interaction code rather than wrapped by it.

**Update 2026-10-08 (P01):** runtime evidence agrees for the selection-picking operators. Their exec runs from element indices, and the region exists only to satisfy the poll. It also shows the wrapper is not always thin: five sculpt operators crash without a window, because their undo path assumes one.

### P2. Declarative-first is how professionals already work (confidence: high)

91% of mesh objects carry live modifiers. The authored artefact is a *recipe*, not a final mesh. An agent that declares outcomes (ledger L-006) is not imposing a new paradigm; it is matching existing practice.

### P3. Technical correctness is cheap; quality is the real gap (confidence: high, from one session)

Both film slices passed every structural check, yet scored 1.0 and 2.33 blind against 3.75–4.5 for studio work. The agent can make *valid* scenes. It cannot yet make *good* ones.

- **Implication:** the bottleneck for agent-made production work is not the API. It is art direction, lighting contrast, detail density and characters.
- **What would change our mind:** a blind session where checks-passing agent work regularly scores ≥ 3.

### P4. The agent's own judgement of quality cannot be trusted (confidence: medium, n = 2 slices)

Self scores were 2.5 and 2.5, against blind scores of 1.0 and 2.33. On the Flow slice the agent overrated itself by 1.5 points.

- **Implication:** the R6 rule stands. The vision check is a warning, never a gate, and the quality number must come from blind rating.
- **To firm this up:** more sessions and more items.

### P5. Where the agent struggled, the engine's human shape was often the cause (confidence: medium)

In the demos, several fixes came from things a human sees instantly but an agent sees only by rendering:

- a camera inside a tree
- haze that turned the frame black
- smoke invisible in one renderer

That is DF4 in practice: results are visible only by drawing them. Ledger entries **L-003 (return diffs, not statuses)** and **L-010 (machine QA gates)** target exactly this.

### P6. Upstream will not carry this; a fork or extraction is the likely path (confidence: medium)

The Blender Foundation's public stance ("made by humans for humans") and the absence of any agent-native fork point there. The reuse vs. rewrite question (RFC Q4) stays open until more stages have data.

### P7. Blender's statuses are not trustworthy for an agent (confidence: medium-high, new)

In P01, 4 operators reported FINISHED with real arguments and did nothing, and 5 crashed the process with no error to read. An agent driving stock Blender must verify every call independently, which is exactly what the demos did with fingerprints and checks.

- **Implication:** L-003 (return a diff, not a status) is not a nicety. Without it, every agent integration re-implements verification by itself.

## What surprised us

- **How much already runs headless.** The common belief that Blender "needs the GUI" is mostly about polls, not real dependencies.
- **Bevel's modal loop re-runs the whole operation on every mouse move.** The interactive layer is pure ceremony around a pure function.
- **Hidden required inputs fool the prober too.** Our own probe got CANCELLED from `loop_select` until we found the hidden index property. A tool built for agents would have said what it needed.
- **Fixing a scene was easy; judging it wasn't.** The hardest part of the demos was knowing whether a render was good.
