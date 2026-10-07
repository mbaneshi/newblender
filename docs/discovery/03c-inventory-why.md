# Inventory C — The "why" layer: design threads, posts, talks

- **Date:** 2026-10-07 · **Index:** [03 — Inventory](03-inventory.md)
- **Method:** web research by an agent.
  - **opened** = the agent fetched and read the page.
  - **listing** = seen in a reliable search result or index, not opened.
  - YouTube talk URLs were not verified; the BCON (Blender Conference) entries link to conference.blender.org pages.
  - Re-open before quoting anything.

## S01 Modeling
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Mesh struct-of-arrays refactor #95965 | https://developer.blender.org/T95965 | 2022 | listing | Mesh data moves from fixed C structs to generic named attributes; any tool can address them uniformly |
| Fast high-poly mesh editing #74186 | https://developer.blender.org/T74186 | 2020 | listing | Edit mode keeps two meshes (BMesh + Mesh); conversion is the main performance tax |
| Edit-mesh performance overview #88021 | https://developer.blender.org/T88021 | 2021 | listing | Conversion on every update, later made lazy; still structural debt |
| 4.0 GN release notes: node tools | https://developer.blender.org/docs/release_notes/4.0/geometry_nodes/ | 2023 | listing | Node groups act as operators; selection, face sets and the 3D cursor become node inputs |
| Winter of Quality 2026 | https://code.blender.org/2026/02/winter-of-quality-2026/ | 2026 | opened | Mesh attribute storage migration reported "Completed". *Corrected 2026-10-07 by S01 Pass 4:* Mesh still keeps `AttributeStorage` alongside `CustomData`, and BMesh uses `CustomData` only. |

## S02 UV & texturing
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Layered Textures Design (Brecht Van Lommel) | https://code.blender.org/?p=9303 | 2022 | opened | One texture data-block, edited as layer stack or node graph; blur/filter nodes force baking |
| Layered Textures feedback | https://devtalk.blender.org/t/layered-textures-design-feedback/23092 | 2022 | listing | Users want Substance parity, UDIMs, multi-channel paint; the design stalled |
| Layered/procedural textures #68894 | https://projects.blender.org/blender/blender/issues/68894 | 2019+ | listing | Long-running split of textures from shaders |
| SLIM UV unwrapping | https://devtalk.blender.org/t/slim-uv-unwrapping/32192 | 2023 | listing | Unwrap method can't be chosen beforehand; settings exist only after the operator runs (redo panel) |
| Winter of Quality 2026 | https://code.blender.org/2026/02/winter-of-quality-2026/ | 2026 | opened | Texture paint only now gets global undo |

## S03 Shading & materials
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| EEVEE's Future | https://code.blender.org/2021/06/eevees-future/ | 2021 | listing | C++ rewrite; engine-agnostic shader codegen |
| USD Hydra / MaterialX #100569 | https://developer.blender.org/T100569 | 2022 | listing | Only a subset of Cycles nodes maps to MaterialX: the edge of portability |
| Procedural texture nodes as USD | https://devtalk.blender.org/t/exporting-procedural-texture-nodes-as-usd/31513 | 2023 | listing | No standard interchange for procedural nodes |
| Layered Textures Design | https://code.blender.org/?p=9303 | 2022 | opened | Texture vs shader nodes overlap; when to use which is unclear |

## S04 Geometry Nodes / procedural
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Declarative Systems in GN (Jacques Lucke) | https://code.blender.org/2025/05/declarative-systems-in-geometry-nodes/ | 2025 | opened | Describe behaviour (emitters, forces), not steps; less cognitive load |
| Bundles and Closures | https://code.blender.org/2025/08/bundles-and-closures/ | 2025 | opened | Functions as node inputs; trees can no longer be debugged left-to-right |
| GN Workshop Sept 2026 | https://code.blender.org/2026/10/geometry-nodes-workshop-september-2026/ | 2026 | opened | `nodebpy`: node trees as readable Python for review; modal node tools, dynamic sockets, C++ auto-layout planned |
| GN Workshop Sept 2025 | https://code.blender.org/2025/10/geometry-nodes-workshop-september-2025/ | 2025 | opened | Each node tool registers its own operator; groups compute default inputs |
| Volume Grids in GN | https://code.blender.org/2025/10/volume-grids-in-geometry-nodes/ | 2025 | opened | Grids are data, fields are functions; the separation keeps evaluation composable |
| BCON22 "GN development process" | https://conference.blender.org/2022/presentations/1709/ | 2022 | listing | How the project began and pivoted |

## S05 Rigging
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Animation 2025: Progress & Planning | https://code.blender.org/2024/02/animation-2025-progress-planning/ | 2024 | opened | "Rig Nodes" prototype keeps shot-specific constraints with the animation |
| Bone Collections (manual) | https://docs.blender.org/manual/en/latest/animation/armatures/bones/bone_collections.html | 2023 | listing | Collections on the Armature; override anchoring by name is fragile |
| Small Teams, Ambitious Projects | https://code.blender.org/2026/09/small-teams-ambitious-projects/ | 2026 | opened | "Rigging at scale" (meta-rigs, pickers) for non-technical users is a 2-year target |
| The Future of Overrides | https://code.blender.org/?p=12380 | 2024 | opened | Library Overrides on linked rigs drifted daily in Studio productions; "99% of cases" don't need the complexity |

## S06 Layout & scene assembly
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| The Future of Overrides | https://code.blender.org/?p=12380 | 2024 | opened | New Override data-block with three rule types (ID remap, RNA-path, filter): property-level and declarative |
| Overrides Workshop | https://code.blender.org/2022/02/overrides-workshop/ | 2022 | listing | Overriding a whole hierarchy to change one control is unworkable |
| Dynamic Overrides #96144 | https://projects.blender.org/blender/blender/issues/96144 | 2022 | listing | Value-only overrides on any data; can't change ID relationships |
| Remote Asset Libraries | https://code.blender.org/2026/07/remote-asset-libraries/ | 2026 | opened | Plain HTTP + JSON listings + .blend files; each asset self-contained |

## S07 Animation
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Layered Animation Workshop 2024 | https://code.blender.org/2025/01/layered-animation-workshop-2024/ | 2025 | opened | MVP blend modes Replace/Combine; keying is rejected with an error when blending is impossible |
| Baklava design page | https://wiki.blender.org/features/animation/animation_system/baklava/ | 2024 | listing | Layers + multi-ID animation: one data-block animates many IDs |
| Animation 2025 | https://code.blender.org/2024/02/animation-2025-progress-planning/ | 2024 | opened | A new Animation data-block replaces Action |
| 4.4 Slotted Actions feedback | https://devtalk.blender.org/t/blender-4-4-slotted-actions-feedback/38906 | 2025 | listing | Actions were a "dumb bag of F-Curves"; slots separate them per target |

## S08 Simulation & FX
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| GN simulation support PR #104924 | https://projects.blender.org/blender/blender/pulls/104924 | 2023 | listing | Simulation zones carry state between frames; baked frames skip evaluation |
| Geometry Nodes Physics | https://code.blender.org/2026/07/geometry-nodes-physics/ | 2026 | opened | One all-purpose solver rejected; a framework for multiple XPBD solvers wrapped as assets |
| GN Workshop Sept 2026 | https://code.blender.org/2026/10/geometry-nodes-workshop-september-2026/ | 2026 | opened | Tags/filters route effectors to solvers; Jolt for rigid bodies |
| Declarative Systems in GN | https://code.blender.org/2025/05/declarative-systems-in-geometry-nodes/ | 2025 | opened | Particle behaviours assembled in modifier-like panels; node editor optional |

## S09 Lighting & rendering
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Cycles Texture Cache | https://code.blender.org/2026/05/cycles-texture-cache/ | 2026 | opened | Cache misses batched, kernels relaunched; no GPU locking |
| EEVEE's Future | https://code.blender.org/2021/06/eevees-future/ | 2021 | listing | Architecture rebuilt so all render passes output efficiently, lighting passes decoupled |
| Light linking #68915 | https://projects.blender.org/blender/blender/issues/68915 | 2019+ | listing | Collections on lights, not shader linking (overrides break it); USD-compatible |
| Cycles X announcement | https://digitalproduction.com/2021/04/26/blender-cycles-x-software/ | 2021 | listing | Dropped OpenCL and features; compatibility traded for architecture |

## S10 Compositing
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Realtime / Viewport Compositor (Omar Emara) | https://code.blender.org/?p=9369 | 2022 | listing | New GPU backend for interactive compositing; started with a subset of nodes |
| Viewport Compositor #99210 | https://developer.blender.org/T99210 | 2022 | listing | Compositor tree applied directly in the viewport |
| Using the Compositor (5.2 manual) | https://docs.blender.org/manual/en/5.2/compositing/usage.html | 2025 | listing | Compositor tree is now a reusable data-block (VSE strips, modifiers) |
| VSE 2026 roadmap | https://devtalk.blender.org/t/video-sequence-editor-vse-2026-roadmap/43206 | 2025 | opened | Compositing and sequencing unify on node groups |

## S11 Editing (VSE)
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| VSE Workshop Aug 2024 | https://code.blender.org/2024/08/vse-workshop-august-2024/ | 2024 | opened | VSE data lives in scenes; a move to a "Movie" ID is undecided |
| VSE 2026 roadmap | https://devtalk.blender.org/t/video-sequence-editor-vse-2026-roadmap/43206 | 2025 | opened | Two part-time developers; image data-blocks vs paths and the audio pipeline still undecided |
| VSE Workshop May 2022 | https://code.blender.org/2022/06/vse-workshop-may-2022-report/ | 2022 | listing | Retiming tools; dedicated sub-editors (colour correction) |
| VSE 2.0: The Big Picture #78986 | https://developer.blender.org/T78986 | 2020 | listing | Early overall vision (not opened) |

## S12 Grease Pencil 2D
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Grease Pencil 3.0 | https://code.blender.org/?p=10860 | 2023 | opened | Full rewrite on CurvesGeometry, built for "10+ years"; Python API break accepted |
| GP integration into GN | https://devtalk.blender.org/t/grease-pencil-integration-into-geometry-nodes/31220 | 2023 | opened | "GP is just a bunch of Curves"; fields per layer; groups flatten |
| GP module meetings 2023 | https://devtalk.blender.org/t/2023-04-03-grease-pencil-module-meeting/28728 | 2023 | listing | Decision trail of the rewrite |

## X2 Python API & extensions
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Logging for Context.temp_override | https://devtalk.blender.org/t/logging-for-context-temp-override-feedback/42991 | 2025 | opened | Operators read hidden context; logging reveals it; some operators still can't be overridden |
| info_gotcha (API docs) | https://docs.blender.org/api/4.3/info_gotcha.html | ongoing | listing | Operators take context, not data, and return only a status; when poll fails, the fix is reading C source |
| Blender as a Python Module | https://docs.blender.org/api/5.3/info_advanced_blender_as_bpy.html | ongoing | opened | Boots with the default cube; no Python threads; some CLI flags have no API |
| Extensions Platform design #106254 | https://projects.blender.org/blender/blender/issues/106254 | 2023 | listing | Wheels, permissions manifest; Python sandboxing rejected as too limiting |
| Headless operator failures #51983 | https://projects.blender.org/blender/blender-addons/issues/51983 | 2017 | listing | No window or GPU context in background mode; many polls fail |
| BCON24 "Pushing vanilla to the edge" | https://conference.blender.org/2024/presentations/1993/ | 2024 | listing | ML inside unmodified Blender via its Python |

## X3 Core architecture
| Item | URL | Year | Status | Insight |
|---|---|---|---|---|
| Depsgraph design docs | https://developer.blender.org/docs/features/core/depsgraph/ | ongoing | opened | Evaluation always on copies; depsgraphs owned per window; "node-everything" still "a long way" off |
| GSoC 2019 Undo Improvements | https://devtalk.blender.org/t/gsoc-2019-undo-improvements/6273 | 2019 | opened | Per-data-block undo rejected (inter-dependencies); memfile undo reloads the scene |
| Global undo speedup (bf-blender-cvs) | https://lists.blender.org/pipermail/bf-blender-cvs/2020-March/137450.html | 2020 | listing | Unchanged IDs and the depsgraph reused across undo steps |
| Depsgraph & overrides design (bf-committers) | https://lists.blender.org/pipermail/bf-committers/2017-November/048900.html | 2017 | listing | 2.8 copy-on-write driven by overrides and multi-state scenes |
| Undo system design (bf-committers) | https://archive.blender.org/lists/bf-committers/2004-November/008313.html | 2004 | listing | Edit-mode and global undo separate; later unified as one linear stack |

## Cross-cutting golden insights (agent's synthesis, to be tested)

1. **Operators are the core obstacle.** They act on hidden context and return only a status. newblender needs pure data-in/data-out functions under every operator.
2. **Blender is already drifting declarative.** Declarative GN systems, closures, GN Physics, dynamic override rules and layered actions all describe *what*, not *how*. Ride that direction rather than fight it.
3. **Generic attributes are the shared data model.** Mesh, Curves, GP3 and point clouds share named struct-of-arrays attributes. One typed attribute schema could be the agent's view of all geometry.
4. **Nodes-as-text is now first-party.** With `nodebpy`, agents author graphs as code and diff them instead of driving the node editor.
5. **Human-only affordances to replace:**
   - settings that exist only after an operator runs (the redo panel)
   - modal, event-driven tools
   - failures surfaced only as error messages
6. **Evaluation and undo are snapshot-based, not transactional.** Agent transactions and branching need a new diff/log layer.
7. **Debt is concentrated where staffing is thin.** VSE (two part-time developers) and library overrides (drift) are candidates for a clean redesign rather than a wrapper.
8. **Headless use is second-class.** The default cube at boot, no Python threads, CLI-only flags. A library use needs an explicit empty, windowless, deterministic boot profile.
