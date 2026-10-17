# Reframe notes: spatial intelligence, first principles, generative vs programmatic

Date: 2026-10-17. Issue #15. Status: **notes, not a decision.** Nothing here changes an RFC. Claims marked *(from memory)* or *(hypothesis)* are unverified and are inputs to the research, not results of it.

## 1. What triggered this

P02 to P05 (PRs #8, #10, #12, #14) showed that out-of-process control of Blender, crash recovery, a Rust/WASM kernel with a three.js viewer, and picking/sculpt at 1 to 2M triangles are **technically feasible** on an M4 Max. They did not show that any of it makes an AI agent better at 3D work. That is still the unmeasured H2 question.

The owner then challenged the premise behind the harness idea, in three steps:

1. **The Claude Code analogy is only partly true for 3D.** Of the four properties of a code repo (readable text, diffs, undo, tests as oracle), undo and diffs transfer, readable text transfers partly, and the oracle mostly does not: "is this chair good" has no pass or fail. Only the measurable part (leg count, height, overlap, watertightness) can be checked. Taste stays with a human.
2. **Undo is a narrow answer.** The harder problem may be how a model represents and reasons about space.
3. **Start from concepts, and look at other tools.** Map intelligence, art, human and machine onto 3D space and Blender features, and consider that another SDK or engine may fit the mission better.

## 2. Three layers (working model)

| Layer | Question | Examples | Where newblender sits |
|---|---|---|---|
| Understand space | What is here, how do parts relate, what happens if I push it? | World models and spatial-intelligence research *(from memory: World Labs, Google Genie, NVIDIA Cosmos, JEPA work associated with Yann LeCun)* | Not here |
| Simulate and act | Does it fall, collide, fit? | MuJoCo, Isaac Sim, Genesis, Unity, Unreal *(from memory)* | Not here (Blender has some physics, but is not a robotics simulator) |
| Author and edit | Make it, change it, keep it consistent | Blender, CAD, game engines | **Here** |

Consequence: the project is a way for an AI to **author structured 3D**, not a way for it to understand space. Two points in Blender's favour: a scene is explicit, symbolic and inspectable (a grounded structure a language model can read), and robotics and world-model work already uses authoring tools to produce data. The risk: the next leap may happen in the first two layers while we polish the third.

## 3. Concept mapping (first draft)

| Concept | Meaning in a scene | Blender feature |
|---|---|---|
| Understanding | Parts, relations, physical plausibility | Scene graph, constraints, rigid-body and cloth simulation |
| Intelligence | Reaching a goal under constraints, planning steps | Node-based procedural systems, drivers, modifiers |
| Art | Choices no measurement settles: composition, style, mood | Lighting, camera, materials; human taste stays in the loop |
| Human | Intent, taste, correction | Viewport, review, approval |
| Machine | Precise execution, measurement, repetition | Python API, geometry nodes, headless rendering |

## 4. Owner's two additions

### 4.1 Start from math and computer science, not from what exists today

The bridge between the real world and computation, simulation and modelling is mathematics, and computer science rooted in it. Language models can now help build systems from first-principles constraints, so we are not forced to inherit today's tools.

Assessment (agree, with one guard):

- **Where first principles pay off:** the *representation and its invariants*. A scene as a typed structure with checkable properties: transforms as linear algebra, meshes as simplicial or cell complexes (Euler characteristic, manifoldness, watertightness), physics as constrained ODE/PDE problems, intent as constraints and objectives, specifications as properties.
- **A bonus for the oracle problem:** mathematical invariants are exactly the *checkable* part of "tests as oracle" for 3D. Math does not decide taste, but it decides a large share of correctness (does it satisfy its constraints, is it valid geometry, does it match a reference to a tolerance).
- **The guard:** first-principles design is for the interface, the data model and the verifiers. It is not a reason to rewrite numerics (solvers, geometry kernels, rendering) that mature libraries already do. P04 already used the right pattern: a small kernel checked against an independent implementation (matching checksums to about 1e-12).

### 4.2 Generative, programmatic or hybrid: where does it land in a decade

Question: could we build for 3D scenes, virtual reality, simulation and engineering what ChatGPT is for text, a generative model of the artifact itself? Or should we design software so models *operate* it, as an LLM drives ffmpeg for video? Or a mix?

Three paradigms (working definitions):

| Paradigm | The model produces | Strengths | Weaknesses |
|---|---|---|---|
| Generative-native | The artifact itself (splats, voxels, meshes, video, a simulated world) | Plausible appearance, priors, speed on open-ended content | Hard to edit precisely, hard to constrain, hard to verify, weak for tolerances *(hypothesis)* |
| Programmatic | A program, script or tool call that a deterministic system executes (CAD script, geometry nodes, ffmpeg command) | Exact, editable, reproducible, verifiable, diffable | Limited to what the tool can express; the model must know the tool |
| Hybrid | Both: generative proposals and appearance, programmatic structure and verification | Combines priors with control | Interfaces between the two are unsolved *(hypothesis)* |

Observations:

- Text is a model's native token space, so it generates text directly. Code is programmatic. Images are mostly generated directly by a different model family. Video work in practice mixes both: generation for pixels, **ffmpeg for operations**, and the latter has a real, lasting place.
- Open question for 3D: is there a native token space? One candidate is the *scene program* (code or node graph), which would favour the programmatic and hybrid paradigms. This is a hypothesis, not a finding.
- Likely domain split *(hypothesis)*: engineering with tolerances and manufacturing leans programmatic; concept art and appearance tolerate generative; the most valuable products are probably hybrid.
- Our knowledge of 2025 and 2026 work on generative 3D and world models is incomplete (assistant knowledge cutoff June 2026). The research must check current state rather than rely on this note.

## 5. Where to invest time (hypothesis, to be tested by the research)

The aim is value added in the world. The **no-regret** candidates are the parts that matter under all three futures:

| Investment | Why it holds in every future |
|---|---|
| A scene/artifact representation with mathematical invariants | Generative output needs structure to be editable; programmatic output needs it to be executed; hybrids need both |
| Verifiers and oracles for the checkable part, plus a way to bring in a human for taste | Every paradigm needs to know whether the output is acceptable |
| A model-agnostic harness: observe, act, trace, replay, roll back | Works whichever model, generative or programmatic, sits behind it |
| Blender as the lab | A rich, scriptable, open authoring system to test all of the above |

What this note suggests *not* to invest in: training a competing generative model (needs compute and data far beyond a $200 credit), and building a new engine before the layer and paradigm questions are answered.

Open: this reasoning could be wrong if a generative-native system makes authoring tools largely unnecessary for the target use cases. The research should look for that evidence.

## 6. Research to run next (proposal)

1. Spatial reasoning in LLMs and VLMs: benchmarks, results, failure modes.
2. World models and spatial-intelligence systems: what they do, whether one could be the "understand" layer.
3. Robotics simulators and engines versus Blender: what they offer, whether one could be the platform base.
4. Representations that help a model author 3D: scene-graph text, code, procedural recipes, renders, with evidence from CAD and 3D program-synthesis work.
5. Generative versus programmatic versus hybrid across domains (video with ffmpeg, CAD, 3D, simulation): evidence and trajectory.
6. Mathematical foundations: which structures give verifiable invariants for scenes and CAD (geometry kernels, constraint solvers, signed distance fields), and what that implies for a first-principles core.
7. Synthesis: does the north star in RFC 0001 R8 still hold, which layer deserves the effort, and what is the no-regret path.

## 7. Status of related work

- RFC 0001 R8 (north star) and RFC 0003/0004 stand as merged. This note proposes to test them, not to change them.
- No API spend so far. H1 to H3 stay unstarted until the owner sets a budget.
- Open PRs with the probe results: #8, #10, #12, #14.
