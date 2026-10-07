# RFC 0002 — Publishing newblender discovery as a research series

- **Status:** Open (proposal received, nothing decided)
- **Opened:** 2026-10-07
- **Author:** mbaneshi (with Claude Code)
- **Depends on:** [RFC 0001](0001-newblender.md), R5 (four-pass study method), the [S01 brief](../discovery/s01-modeling/05-brief.md)
- **Discussion:** _to be linked once the GitHub repo exists_

## 1. Proposal (condensed from an outside review of the S01 brief)

The S01 brief reads as a **research report / lab notebook / mid-run study**, not yet an academic paper. Its data set is what separates it from an opinion piece about "Blender is bad for AI":

- 78 production `.blend` files (~2 GB in the sample, 4.2 GB in `~/newblender-data/` overall)
- 2,498 registered operators; 1,605 context-dependent; 190 needing mouse/keyboard; 138 with no direct invocation; 320 modelling operators
- topology, modifier and Geometry Nodes statistics; a cited professional workflow; developer design threads; source tracing

**Reframe.** The research problem is bigger than Blender:

> Before a professional creative application can become agent-native, we must learn how professionals actually use it, what production artefacts really contain, and which parts of its API still assume a human behind a mouse and keyboard.

Blender becomes the **case study**; the idea is **agent-native creative software**.

### 1.1 Series, not a single paper

- **NEWBLENDER Research — S01: Modeling**
  - *S01 Mid-Run Report*: the current brief, published as-is
  - *S01 Final Report*: after pass 3 (trace) is complete
  - *Paper*: extracted from the final report
- Later stages follow the same shape (S02 Animation, S03 Materials, …).

### 1.2 Candidate titles

- *NEWBLENDER S01: An Empirical Study of Blender Modeling Workflows, Production Artifacts, and Human-Centric APIs*
- **Toward Agent-Native Creative Software: An Empirical Study of Blender's Modeling Workflow and API** (reviewer's preference: Blender is the case study, the thesis is the headline)

### 1.3 Paper skeleton

1. **Abstract.** Problem (creative software is built around human interaction) · question · method (four passes) · results · implication.
2. **Introduction.** Not "I want to rewrite Blender", but *what would need to change before a professional creative application can become agent-native*.
3. **Research questions.**
   - RQ1 What operations make up professional Blender modelling workflows?
   - RQ2 What structures actually occur in production `.blend` files?
   - RQ3 Which modelling operations depend on human UI context?
   - RQ4 Where does the programmatic interface encode assumptions about human interaction?
   - RQ5 Which existing abstractions already suit agentic execution?
   - RQ6 What architectural changes would make modelling more agent-native?
4. **Methodology.** Workflow → production files → operator/API surface → source → design rationale → agent-native principles.
5. **Dataset.** Formal counts and provenance; the stylised-film sampling bias moves into *Threats to Validity*.
6. **Results.** Operator-surface table (total / context-dependent / input-dependent / no direct invocation / modelling).
7. **Production reality.** 91% of sampled mesh objects carry modifiers; Subdivision Surface is 54% of modifiers. Claim: *professional modelling is substantially more procedural and declarative than a naive replay of UI actions suggests.*
8. **Human-centricity.** Knife, context, mouse/keyboard, Edit Mode, undo, operator redo, mesh copying, UI state; formalise the term **human-centric API surface**.
9. **Agent-native design implications.** Human-centric (context-dependent, imperative, stateful, interactive) vs agent-native (context-independent, declarative, inspectable, reversible, composable, verifiable); capability cards as the bridge.

### 1.4 Repository shape

```text
newblender/
├── research/
│   ├── README.md
│   └── S01-modeling/
│       ├── protocol.md  dataset.md  methodology.md
│       ├── mid-run-report.md  final-report.md
│       ├── results/  evidence/  citations.md
├── data/
│   ├── manifests/   # source, licence, hash per file
│   ├── derived/
│   └── statistics/
├── experiments/
├── docs/
└── src/
```

Raw production files stay out of git: **file → manifest → source/licence → hash → derived statistics**. Reproducible without a 2 GB asset dump.

### 1.5 Publication channels

| Channel | Role | Rating |
|---|---|---|
| GitHub repository | Code, data manifests, method, evidence (canonical) | ★★★★★ |
| GitHub Pages | Readable, permanent report site | ★★★★★ |
| Zenodo | Citable release with a DOI | ★★★★★ |
| arXiv | Public technical paper, citing GitHub + Zenodo | ★★★★ |
| Hugging Face Papers/Repo | Only if the AI-agent tooling angle grows | ★★★ |
| ACM / SIGGRAPH / CHI | Peer review, later stage | ★★★★★ (later) |

### 1.6 Intellectual architecture

```text
NEWBLENDER → Agent-Native Software
  ├── S01 Modeling ── workflow · artefacts · API surface · source · rationale
  ├── S02 Animation
  └── S03 Materials
        ↓
  Agent-native design principles → capability model → new Blender architecture
```

## 2. Open questions

- [ ] **Q1 — Publish at all, and when?** Mid-run report now, or wait for the S01 final report? Does going public early cost anything (scooping, locking in claims before pass 3)?
- [ ] **Q2 — Title and thesis.** Blender-centred title or "Toward Agent-Native Creative Software"? The second makes a bigger claim that S01 alone may not carry.
- [ ] **Q3 — Repo restructure.** Adopt `research/S01-modeling/` + `data/manifests/` now, or keep `docs/discovery/` and map it to the paper shape only at publish time? (RFC 0001's link structure depends on the current paths.)
- [ ] **Q4 — Dataset licensing and redistribution.** Per-file licence audit of the 78 files (Blender Studio CC-BY variants vs others). Manifest + hash only, or redistribute derived statistics? Who checks?
- [ ] **Q5 — Evidence standard.** The brief is evidence level L1 (documented and traced, nothing benchmarked). What level must claims reach before a paper: runtime probes (brief §8), replication script, re-run on a second Blender version?
- [ ] **Q6 — Visibility.** Repo is local-only today (no remote). Public from day one, or private until the first release? This also decides where this RFC's Discussion lives.
- [ ] **Q7 — Channels and order.** GitHub → Pages → Zenodo DOI → arXiv as proposed? arXiv needs an endorser for cs.GR/cs.HC; is that available?
- [ ] **Q8 — Authorship and AI disclosure.** How to credit agent-performed passes (R5: the agent carries all passes and first drafts) under arXiv/ACM authorship and AI-use policies.
- [ ] **Q9 — Language.** English canonical paper; Persian report/digests as a companion edition or not?
- [ ] **Q10 — Next concrete step.** The reviewer offers a *paper-ready specification* for S01 (title, abstract, RQs, methodology, dataset protocol, evidence standard, results schema, bibliography) without rewriting current findings. Take it as the first deliverable?

## 3. Resolutions

_None yet._
