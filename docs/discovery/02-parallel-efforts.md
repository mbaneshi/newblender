# Discovery 02 — Parallel efforts (sideways lens, first pass)

- **Date:** 2026-10-07 · **Feeds:** RFC 0001 R2 ("look sideways")
- **Method:** web research by a research agent. "Confirmed" = the agent saw a primary source. Links and paper IDs have not yet been re-checked by hand; verify before citing externally.
- **Related own work:** mytodo #358 (closed) already evaluated storytold / ArtCraft (FilmCraft, EffectCraft, PhotoCraft) as an RFC-gated spike.

## The "Adobe suite in Rust" project

**ArtCraft "Crafting Apps"**: GitHub org `storytold`, site getartcraft.com. Seven clean-room Rust apps: PhotoCraft (Photoshop), VectorCraft, FilmCraft, LightCraft, PrintCraft, EffectCraft, DesignCraft. MIT/Apache-2.0. PhotoCraft and PrintCraft are early alpha; the rest are in development. Covered by GIGAZINE on 2026-10-05.

Architecture claims (README): 24 layered crates, engine-first with a thin egui UI, CPU and GPU (wgpu) compositors cross-tested, copy-on-write 256² tiles, and **one registry of 500+ commands that the UI, CLI, JSON control channel and MCP server all call**: "anything you can click, a script or an AI agent can do too." Agents talk to it over an authenticated loopback control channel.

## Landscape

| Name | What | How it's agent-native | Status | Verified |
|---|---|---|---|---|
| ArtCraft Crafting Apps | Adobe CC rewrite in Rust | One command registry shared by every surface | alpha / in dev | confirmed |
| Blender Lab MCP Server | Official MCP add-on (needs 5.1+) | Natural language → bpy; "executes LLM generated code … without any guards" | experimental | confirmed |
| Blender Foundation AI statement (2026-05-01) | "Made by humans for humans. No generative AI functionality is currently available or planned" | Policy only | ongoing | confirmed |
| Zoo Design Studio / KCL / Zookeeper | Code-CAD with its own language and GPU geometry kernel | Code is the source of truth; agent has engine-level inspect/snapshot/debug | shipping | confirmed (secondary) |
| Summer Engine | Godot-compatible game engine | Agent runs inside the engine loop: write → run → read runtime errors → fix | shipping | vendor site |
| bevy_brp / bevy_brp_mcp | MCP over the Bevy Remote Protocol | Agents query and mutate the live ECS, take screenshots | active | confirmed |
| Graphite | Rust/Wasm procedural 2D editor | Declarative node graph, fully nondestructive; not AI-targeted | alpha / RC | confirmed |
| Headless-Blender agent kits (several) | JSON-in/out wrappers around headless Blender | Retrofit | hobby | unconfirmed |
| Adobe Creative Agent (June 2026) | Agent across Adobe apps | Retrofit | shipping | press release |

## Research on agents driving 3D through code

| Paper | Finding about the interface |
|---|---|
| BlenderGym (CVPR 2025) | VLM systems still lag humans on 5 editing tasks; the split of compute between generating and verifying matters |
| LL3M (2025) | Multi-agent plan/retrieve/write/debug/refine; retrieval over the API docs is key; code keeps output editable |
| MeshCoder (2025) | A higher-level part API on top of bpy, trained on 1M shape-code pairs, beats raw bpy |
| 3DCodeBench (May 2026) | Across 12 VLMs, **API mismatch is the main failure mode** |
| 3DHarnessBench (Sep 2026) | Four interface levels (single view → full function calls); richer function-call access helps a lot |
| SceneCraft (ICML 2024) | Scene graph as a blueprint → code → visual critique loop |
| BlenderAlchemy (ECCV 2024), 3D-GPT (2023) | Iterate on renders; fill procedural parameters rather than free-form geometry (from memory, unchecked) |

## Recurring design ideas

1. **One command registry under every surface.** The GUI is one client among several, not the source of truth. Blender's operators are close to this but are tied to UI context.
2. **A headless core plus a first-class observe/verify loop:** renders, structured diffs, errors.
3. **Code or a declarative graph as the scene**, with geometry as compiled output. Editable, diffable, checkable.
4. **API design is the bottleneck, not the model.** The interface should be small, stable, typed and self-describing, not raw bpy.
5. **Rust from-scratch vs retrofit.** New entrants rewrite; incumbents bolt on. Retrofits lack sandboxing and permissions.

## Implications for newblender (observations, not decisions)

- **No confirmed agent-native fork of Blender exists.** The space is open.
- **Upstream is unlikely to take this.** The Blender Foundation's stated position ("made by humans for humans") makes an upstream contribution path unlikely in the near term. This weighs toward a fork or an extraction rather than upstreaming (lab #22's W7 options).
- **Fix the gap PhotoCraft closes.** PhotoCraft's single registry is exactly what Blender lacks: operators exist but are gated by `bContext` (see Discovery 01 §3).
- **Two open questions for the RFC:** ArtCraft chose a *Rust rewrite*. Blender has ~3.25M lines of hard-won C++ (Cycles, BMesh, Geometry Nodes, I/O). When do we reuse that, and when do we rewrite?

## Not confirmed

- Whether Geometry Nodes formally replaces modifiers in 5.x (only node-based tools and node physics in 5.2 are confirmed).
- The 5.2 LTS and 5.3 release dates.
