# Discovery 03 — Source inventory per pipeline stage (index)

- **Date:** 2026-10-07 · **Feeds:** RFC 0001 R4 (virtual production from free sources)
- **Slices:**
  - [03a — Local corpus](03a-inventory-local.md): Studio docs, manual, developer docs, source modules, UI panels. All free and already on disk.
  - [03b — Free real files, assets, trainings](03b-inventory-real-files.md): demo, splash and benchmark scenes, free rigs, partly free courses.
  - [03c — The "why" layer](03c-inventory-why.md): design posts, forum threads, proposals, talks.

## Coverage at a glance

Ratings: **●** strong, **◐** usable, **○** thin.

| Stage | Human lens (Studio / manual / training) | Real files to dissect | Internal (dev docs + source) | Why (design threads) | Note |
|---|---|---|---|---|---|
| S01 Modeling | ● | ● base meshes, Cube Diorama, sculpt demos | ● | ● | Best-covered stage |
| S02 UV & texturing | ◐ manual only, no Studio page | ◐ UDIM Monster, Poly Haven | ○ no dev-docs page | ◐ | Weakest internal docs |
| S03 Shading | ● | ● 5.x shading demos | ● | ◐ | |
| S04 Geometry Nodes | ● | ● official demo corpus (4.2–5.2), node tools | ● | ● | Most declarative stage |
| S05 Rigging | ● CloudRig docs | ● 22 free Studio rigs | ● | ◐ | |
| S06 Layout & assembly | ◐ Studio layout page is a stub | ● 5 production splash scenes + a real Sprite Fright shot | ● | ● overrides redesign | |
| S07 Animation | ● | ◐ Ellie pose library, free rigs | ● | ● layered actions | |
| S08 Simulation & FX | ◐ | ● sim-node demos | ○ solver internals undocumented | ● | |
| S09 Lighting & rendering | ◐ Studio rendering page is a stub | ● benchmark + Cycles/EEVEE demos | ● | ◐ | |
| S10 Compositing | ○ | ◐ Tears of Steel plates | ○ | ◐ | Thinnest stage |
| S11 Editing (VSE) | ◐ | ◐ 5.x storyboard demo, film masters | ◐ | ● | Low staffing upstream |
| S12 Grease Pencil | ● GP Fundamentals fully free | ● GP demos, Gaku splash | ● | ● | |
| X1 Pipeline | ● naming, TD guide, project-tools | ● studio-tools, Flamenco code | ◐ | — | |
| X2 Python & extensions | ● | — | ● | ● | |
| X3 Core architecture | ◐ | — | ● | ● | |

## What we can and can't get

- **Can, free:**
  - every document and line of source
  - the official demo/splash/benchmark scenes (5.x splashes come from Studio productions: Gold, House of Chores, DOGWALK, Singularity)
  - one real Sprite Fright shot file
  - 22 production rigs
  - the official Geometry Nodes demo corpus
  - the Studio pipeline code
- **Can't, without a subscription:** full film repositories (Wing It!, Singularity) and most video trainings.
- **Free substitute for a full film:** the 5.x splash scenes are final, assembled production frames. Taken with the Sprite Fright shot and the Studio pipeline docs, they approximate a production end to end.

## Corrections and caveats

- "Realistic Character Workflow" doesn't exist as a Studio course (404). It is "Stylized Character Workflow" (about half free).
- File contents are not yet inspected. "Free" means listed for download, not opened.
- Design-thread items marked "listing" were not opened. Re-open before quoting.
