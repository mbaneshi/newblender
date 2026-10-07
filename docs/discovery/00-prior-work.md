# Discovery 00 — What earlier work already found (and what it assumed)

- **Date:** 2026-10-07 · **Feeds:** RFC 0001 R2 ("build on prior discussions, don't restart")
- **Method:** a read-only agent reviewed agent-native-lab (ANL) issues and files, mytodo issues and sessions, and the ChatGPT transcript `~/mytodo-data/chatgpt/2026-10-04-blender-mcp-eval/transcript.md`. Paths are relative to `~/agent-native-lab` unless noted.

## A. Human lens: how professionals work

- **Studio pipeline** (transcript ~2618–2720): Editorial/Previz → Concept → Asset Creation (Model/Shade/Rig) → Shot Assembly → Animation → Lighting → Render → Review.
- **Studio asset pipeline:** task layers with an owner per data element, ending in a "Published Asset". A production artifact = Intent + Source + Task layers + Dependencies + State + Validation + Review + Version + Publish, not a single `.blend`.
- **Studio modelling flow:** Reference → Setup → Blocking → Modifiers → Topology → UV → Handover. Each stage serves the next, so an agent needs "downstream awareness".
- **Human-to-Artifact decomposition** (ANL#7): per stage, what the human sees / knows / decides / manipulates / verifies, and what Blender changes underneath. "Human UI is a baseline, not a specification."
- **Sources** (ANL#18, `knowledge/blender/sources/SOURCES.md`, 139 tiered sources):
  - Studio Tools/Pipeline docs, rated the richest agent-readable account of pro work.
  - `blender-studio-tools` (asset_pipeline, blender_kitsu, CloudRig).
  - About 25 Studio trainings (Scripting for Artists, Fundamentals, Geometry Nodes from Scratch).
  - Production files: Sprite Fright, Wing It!, the Vault. Kitsu and Watchtower for production state.
- **Human UI summary:** `knowledge/blender/MASTERY.md` §1 covers the HIG paradigms (select → operate, non-modal), modes, active vs selected, keymaps and redo.

## B. Source lens: modules and architecture

- **Chain** (transcript ~2347): DNA → RNA → Data → Operators → Depsgraph → Nodes → Evaluation → Render.
- **Four interfaces:** Human, Python, Internal, AI. The depsgraph is a ready-made "causal dependency model"; Geometry Nodes are Blender's own move toward declarative authoring.
- **Proposed stack** (~2960–3020): semantic 3D model → Blender IR/DSL → RNA/BMesh/Nodes → core.
- **`knowledge/blender/MASTERY.md`:** 4 layers, 143 path:line citations against v5.2.2. Covers operators (~2000 types; redo = undo + re-exec), ID data-blocks, RNA/DNA, original vs evaluated depsgraph, GeometrySet/fields, BMesh vs Mesh, undo.
  - Its conclusion: prefer declarative layers; operators are a UI contract, not a function API; verify through evaluated state.
- **No full module inventory existed before** [Discovery 01](01-source-module-map.md).
- **Pinned source:** v5.2.2 `d13f752`, searchable with `bun _tools/search-sources.ts`.

## C. Methods and status

| Method | Where | Status |
|---|---|---|
| Phase ladder: observe → map → expose → compose → benchmark → missing primitives → extend → modify core | ANL#4, #23 (W0–W7), #14 | Only W0 (sources) done |
| End-goal hypotheses | ANL#22 → `vision/blender/END-GOAL.md` | Not written |
| Knowledge map: 4 tiers, executable knowledge, failures → knowledge | ANL#5 | Tiering applied; map not written |
| Four-layer trace + golden table | ANL#7; `lab/blender/golden-table.md` | Done for 5 tasks; sculpt/UV/rig and real Info-log sessions not done |
| Operability baseline, T6 animation | ANL#32, #35 | Closed. Data/RNA won as control surface; official MCP saw 2/6 and 0/5 of the needed state |
| Primitives v0: apply / inspect / render / checkpoint / verify, JSON-only | ANL#37; `lab/blender/operability/2026-10-06-primitives-decision.md` | Closed |
| Agent experiment A1 | ANL#43 | Closed |
| Benchmarks A–F, MCP bake-off, community atlas | ANL#3, #20, #21, #19 | Not started |

## D. Parallel efforts already touched

- **storytold / ArtCraft spike** (mytodo#358; `~/mytodo/docs/sessions/2026-10-06-storytold-spike/`).
  - Result: FilmCraft produced byte-identical MP4s, but the project can't be reopened after an OTIO import (mytodo#365).
  - Decisions: FilmCraft sits next to Resolve; EffectCraft is a candidate; PhotoCraft gets one batch spike; ArtCraft no.
- **"Model supplies data, reviewed code executes" pattern across engines:** fusion_kit v0, Chrome engines v0, mytodo Blender `loop`.
- **Blender agent projects inventoried** (ANL#6, #16): mcp-blender, BlendRelay, LL3M, blender-open-mcp, Blender Agent Studio. Patterns to borrow: BlenderProc, AYON, Sverchok.

## E. Prior claims resting on the dead facts (RFC R1): re-examine, don't inherit

| Dead fact | Prior claims built on it |
|---|---|
| 1. Human is the operator / viewport is the core loop | MASTERY's "F9 handle" for the human; golden table measured against human steps; transcript architecture starts at "HUMAN → Intent"; `vision/PRINCIPLES.md` #21 ("human creative judgment remains…"); ANL#45 treats human review hours as the main cost |
| 2. Humans write code | "No model-generated runtime Python": templates and dispatcher are human-reviewed trusted code (ANL#37, fusion_kit, loop.py); W1 = lessons for a human learner |
| 3. Tiny imperative steps | Transcript's `move_to()` / `align()` one-call ops; ANL#2's many small per-task agents. The trace itself argues the opposite: declare outcomes. |
| 4. The human eye verifies | "Validate = visual inspection"; ANL#14 Phase 7. The operability work already moved the gate to evaluated state, with render comparison as a warning only. |

**Keep vs drop:**

- **Keep:**
  - The *evidence* (traces, operability results, source corpus).
  - The *methods* (four-layer trace, tiered sources).
  - The safety lesson behind "no model-generated code": the retrofit MCPs run LLM code "without any guards".
- **Drop:** using the human path as the yardstick for *what newblender should be*. Human steps stay a baseline for measurement only.
