# RFC 0004 — Platform stack and scope: a Rust + Supabase + Svelte system inspired by Blender

- **Status:** Open, adopted as the final goal by [RFC 0001 R8](0001-newblender.md) (owner, 2026-10-17). Scope tier, viewer technology and budget are still open (§7).
- **Opened:** 2026-10-17
- **Author:** mbaneshi (with Claude Code)
- **Drives:** [#3](https://github.com/mbaneshi/newblender/issues/3)
- **Depends on:** [RFC 0003](0003-harness-native-architecture.md), [RFC 0001](0001-newblender.md)
- **Evidence:** [`docs/research/2026-10-17-agent-harness-for-creative-suites.md`](../research/2026-10-17-agent-harness-for-creative-suites.md); calibration from the owner's own `nexus-platform-ir` repository
- **Discussion:** _not posted_

## 0. History

Parked earlier on 2026-10-17 ("decide after probes H1 and H2"), then adopted as the final goal the same day (RFC 0001 R8). The owner's argument: a Supabase data layer, a Rust/WASM backend and a web-based Blender-class editor, with a native agentic harness, is a giant leap over retrofitting agents onto desktop Blender. The honest cost remains in §3: T2 is roughly 150 to 250 working days.

**Consequence for the plan.** Probes H1 to H3 (RFC 0003) now measure what the new kernel must provide and de-risk the control plane. They are no longer a gate on whether the platform is built.

## 1. Question

If, instead of patching Blender, we build something in the style of `nexus-platform-ir` (Rust core, Supabase for auth, storage and persistence, Svelte front end) that is inspired by Blender, how much money, calendar time and human effort does it take, and what is the cheapest scope worth building?

## 2. Calibration: what nexus-platform-ir cost (measured 2026-10-17)

| Measure | Value |
|---|---|
| First commit | 2026-04-10 |
| Commits | 1,657 |
| Distinct commit days | 48 |
| Rust / Svelte / TypeScript lines (tracked files) | about 39.5k / 14.1k / 80.6k (TypeScript may include tests and generated code; not inspected) |
| RFCs | 44 files in its RFC directory |

Reading: a 2D CAD with an agent contract took roughly 50 AI-assisted working days of the owner's time over about six months of calendar time. That measures velocity, not feature completeness, and no completeness audit was done here. We assume 3D geometry costs 2 to 3 times the 2D effort.

## 3. Scope tiers

Days are focused, AI-assisted, solo, and cumulative. They are estimates, not measurements.

| Tier | What you get | Days | Main risk |
|---|---|---|---|
| **T0** | Headless agent-native scene kernel in Rust: scene graph, one command registry, event log, snapshots and branches, query and diff, verification, risk classes, MCP, Supabase persistence, glTF import/export | 25 to 40 | Low: the nexus pattern in 3D |
| **T1** | T0 plus a Svelte web viewer (orbit, select, transform gizmos, PBR preview via Rust-to-WASM with wgpu, or three.js) | 55 to 95 | Medium: the WASM and GPU plumbing |
| **T2** | T1 plus mesh edit mode (extrude, bevel, loop cut), modifiers, materials, USD, undo across all of it | 150 to 250 | High: the Blender-like core |
| **T3** | Animation, rigging, sculpt, simulation, path-traced renderer | person-years | Out of scope |

## 4. Money

| Item | Estimate |
|---|---|
| Supabase Pro | about USD 25 per month (from memory; verify current pricing) |
| Domain, CI, misc. | about USD 25 per month, so about USD 50 per month during build |
| Anthropic API | USD 200 credit covers the first probes (RFC 0003 §6); a real eval campaign may need USD 300 to 800 more |
| Labor | The real cost: days times the owner's own rate. T0 plus T1 is about 3 to 5 calendar months at nexus pace |

## 5. Architecture options

| Option | What | Notes |
|---|---|---|
| **S1: control plane with Blender workers** | Rust + Supabase + Svelte hold the registry, event log, branches, verification, permissions and UI; Blender runs as a headless worker behind a backend trait | Cheapest; this is RFC 0003 option A with the nexus stack; Blender supplies mesh tools and rendering |
| **S2: control plane plus native kernel** | S1, then a native Rust scene kernel replaces the worker for the subset that matters | Only if probes show Blender workers are the bottleneck |
| **S3: standalone product** | T0 plus T1 as an independent application | Highest effort; no Blender dependency or GPL surface |

Reuse notes from the research: nexus forbids GPL dependencies (`MASTER_BRIEF.md:154`), so nexus shares patterns with newblender, never code. The Craft apps (CADCraft, PhotoCraft, FilmCraft, craft-libs) are MIT OR Apache-2.0 and their code can be ported with attribution; `artcraft-services` (fair-source) and `artcraftx` (no license file) are study-only.

## 6. Recommendation (draft)

With the platform as the destination, build **S1 at T0**: a Rust + Supabase + Svelte control plane that treats Blender as a swappable headless worker. It is the harness from RFC 0003 and gives the nexus-style stack at the lowest cost. Decide on T1 after the Phase 0 spike and probes H1 and H2. Revisit S2 or S3 only with probe evidence.

## 7. Open questions for the owner

- [ ] Q1 — Is S1 at T0 the right first target, or do you want T0 plus T1 as a standalone product (S3)?
- [ ] Q2 — Web viewer: Rust-to-WASM with wgpu, or three.js first? (Neither verified; a 3 to 5 day spike would settle it.)
- [ ] Q3 — What does Supabase hold: only auth, assets and the event log, or also realtime collaboration state?
- [ ] Q4 — What daily rate or opportunity cost do you want to attach to the labor line?
- [ ] Q5 — Calendar budget: how many months, and how many working days per week?

## 8. Unverified

Maturity of Rust 3D and mesh-editing crates, wgpu in WASM inside Svelte, Supabase limits and current pricing, and the completeness of nexus-platform-ir. All tier estimates are judgement scaled from the nexus calibration, not measured. A Phase 0 spike (3 to 5 days) should replace these with measurements before any commitment.
