# 20 — FLIP Fluids 2021 Customer Reel: how an agent could make it

| | |
|---|---|
| **Original** | FLIP Fluids add-on developers (Ryan and Dennis) + community artists, 2022 (work from April–November 2021), fluid simulation showcase · [BlenderNation](https://www.blendernation.com/2022/02/10/flip-fluids-add-on-2021-customer-reel/) |
| **Agent-readiness today** | **Partial.** Simulation setup and baking are fully scriptable and run headless: a Mantaflow liquid bake ran in a background Blender 5.2.2 process while writing this file. What is not: the shot design (camera, timing, what makes a splash beautiful) and the tuning loop, which is long and judged by eye. The add-on itself is paid, which limits what can be shown without a licence. |
| **Difficulty** | **3** per shot (setup is easy; production quality needs high resolution, whitewater, meshing tuning and hours of bake/render); **4** for a reel of a dozen varied shots. |
| **First slice** | One "pour into a glass" shot with built-in Mantaflow: a glass built as data, a liquid inflow, a resolution sweep baked headless, spray/foam particles on, meshed, and a 48-frame render, with volume and leak checks, shown in the live window. |

## 1. What the original actually is

- **A compilation reel,** not one authored piece: liquid shots by many artists, compiled by the two add-on developers. It is the second yearly reel (the first was 2020).
- **Content:** whitewater (foam, bubbles, spray), viscous fluids, surface tension, meshed liquids rendered in Cycles, plus compositing.
- **Context:** the same add-on supplied detail water in *Flow* (see 01).
- **Numbers:** shot count, resolutions and bake times are not in the source I read. Treat each shot as a typical "hero liquid" shot: seconds long, high resolution, hours of baking.

## 2. How the humans made it

| Stage | Technique | Fact / interpretation |
|---|---|---|
| S08 Simulation & FX | FLIP liquid simulation with the FLIP Fluids add-on; whitewater particles; viscosity; surface tension; meshing of the particle surface. | Fact (index, BlenderNation) |
| S09 Lighting & rendering | Cycles rendering of meshed liquid and whitewater points. | Fact |
| S10 Compositing | Per-shot compositing and the reel edit. | Fact (reel); per-shot detail not public |
| Craft | Choosing domain resolution, emitters, obstacles, timing, camera; iterating bakes until the motion looks right. | Interpretation: standard FX practice |

**Licensing and tooling facts** (verified on fetch from the add-on's GitHub README and Superhive search results):

- The **Blender add-on code is GPL; the FLIP Fluids simulation engine is MIT.**
- It is **sold on Superhive** (formerly Blender Market): $79 for 1 user, $149 for up to 6, $299 for up to 15, including 12 months of support and updates.
- A **free demo add-on** exists; its limits are not stated in the README.
- The source can be **built from GitHub** (C++17, CMake); the README states Blender 4.5 to 5.2 compatibility.

Because the code is GPL, building from source is legal, but buying the add-on funds the developers and gets support. This repo should not redistribute builds. The plan below uses **built-in solvers by default** and treats FLIP Fluids as an optional, owner-bought upgrade.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 Set | Glass, table and pitcher built as data (lathe profiles via `bmesh.ops.spin`, real dimensions), with Solidify for wall thickness. | Real glass dimensions (Ø 75 mm, 120 mm tall) | live bridge `bl.py` |
| S08 Liquid (default) | **Mantaflow FLIP (built in):** domain object with Fluid modifier (`LIQUID`, `cache_type='ALL'`), inflow from the pitcher spout (`FLOW`, `INFLOW`, initial velocity), glass and table as `EFFECTOR` (collision). Spray/foam/bubble particles on. Mesh generation on with upres. Every value is a property, set from a spec dict. | — | headless `blender -b`, `fluid.bake_all` |
| S08 Liquid (alternative) | **Geometry Nodes simulation zone:** a small particle solver (gravity, collision with a signed distance from the glass, simple pressure relaxation) inside a Simulation zone, meshed with Points to Volume → Volume to Mesh. Fully declarative and diffable ([L-006](../discovery/ledger.md)), but not production-grade FLIP. Good for stylised or small-scale liquids. | — | GN simulation zone, `object.simulation_nodes_cache_bake` |
| S08 Liquid (upgrade) | **FLIP Fluids** (owner-licensed): same scene, add-on domain; its properties are also scriptable via Python; whitewater, viscosity and surface tension at production quality. | Superhive licence | add-on, headless bake |
| S08 Wide water | Ocean modifier for open-water backgrounds, baked headless (`object.ocean_bake`). | — | built in |
| S09 Render | Glass + liquid shading (Principled transmission, IOR 1.33 for water), whitewater as point-cloud instances; Cycles with denoising; one camera move as keyframes. | Poly Haven studio HDRI (CC0) | headless Cycles |
| S10 Comp | Compositor: glare on highlights, light grade; output image sequence + MP4. | — | compositor nodes as data |
| Iteration | **Resolution sweep:** bake at 32 → 64 → 128 and stop when the checks stabilise; each bake in its own cache folder with a JSON record (settings, time, disk size, checks). | — | driver script outside Blender |

**Build order**

1. Write the shot spec and checks first: fill level at frame 120, no leaks, volume tolerance, bake budget.
2. Build the set live; frame the camera; owner approves the framing.
3. Bake at resolution 32 headless (seconds), run checks, show the mesh in the live window frame by frame.
4. Raise resolution; add particles and meshing; re-run checks.
5. Render 48 frames (preview EEVEE, final Cycles); composite.
6. (Optional) Re-run the same spec with GN simulation zones and, if licensed, FLIP Fluids; compare.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Every simulation parameter is an RNA property; no GUI is involved in setup.
  - **Headless bake, measured:** a Mantaflow liquid domain (2 m cube, resolution 32, `ALL` cache, mesh on) with a 0.6 m geometry flow, frames 1–24, built entirely as data and baked by `bpy.ops.fluid.bake_all()` under `temp_override` in `blender -b`: **`FINISHED` in 0.71 s**; the evaluated liquid mesh at frame 24 had 23,536 vertices. Blender 5.2.2 also ships the GN `Simulation Input/Output` and `Bake` nodes and `object.simulation_nodes_cache_bake`.
- **Painful today:**
  - **Bake operators run on the *active* object** found through context, not on an explicit domain argument ([L-004](../discovery/ledger.md)); the probe needed `temp_override(active_object=…)`.
  - **Bakes return a status, not a result** (no frame count, timings, particle counts, or warnings), so the agent must read the cache folder and evaluate frames itself ([L-003](../discovery/ledger.md)).
  - **In the GUI, bakes run as background jobs;** through the live bridge a long bake blocks the main thread (the bridge runs code there), so long bakes should go to a separate headless process.
  - **No undo or branching for simulations,** only cache folders; the agent's own folder-per-variant convention fills that gap ([L-008](../discovery/ledger.md)).
- **Not feasible today:** judging whether a splash *looks* right. Fluid motion quality is visual and subtle (layer 5/6). Also, matching FLIP Fluids' whitewater quality with Mantaflow is uncertain; I have not compared them.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every frame's liquid mesh: NaN positions, degenerate faces | 0 / 0 on all frames |
| 1 Validity | Cache completeness: one cache file per frame per enabled layer (data, mesh, particles) | 100% of frames 1–120 |
| 2 Spec | **Leak test:** liquid vertices outside the glass interior (signed distance > 1 mm) once the pour ends, excluding splashes above the rim | ≤ 0.5% of vertices |
| 2 Spec | **Fill level** at frame 120 (median z of top-surface vertices inside the glass) | 70 ± 5 mm above the glass base |
| 2 Spec | **Volume conservation** after the inflow stops (mesh volume, frames 100–120) | drift ≤ 3% |
| 2 Spec | Bake budget at the final resolution | ≤ 30 min wall time; cache ≤ 20 GB |
| 3 Reference | Determinism: bake the same spec twice at resolution 64 | per-frame mesh vertex counts identical, or mean surface distance < 1 voxel |
| 3 Reference | Convergence: fill level and volume at resolution 64 vs 128 | differ by ≤ 5% |
| 4 Downstream | Render: no black or firefly pixels inside the glass region after denoise | 0 pixels > 20× local median luminance |
| 4 Downstream | Whitewater present where expected: spray/foam particle count near impact (frames 40–80) | > 1,000 particles |
| 5 Appearance (warning) | Vision model on 6 sampled frames vs the brief ("water poured from a pitcher fills a glass, splashes on impact, foam at the surface") | warn on mismatch |
| 6 Taste (owner) | Is the motion satisfying? Is timing and camera right for a reel? | owner judgement on the preview before the final render |

## 6. Where the human is still needed

- **Shot design:** choosing the moment, the camera, the lens and the light that make liquid look beautiful. The reel's value is many artists' eyes.
- **Tuning by eye:** viscosity, surface tension, splash scale and timing are adjusted until it "feels" right; numbers alone do not say when a pour looks real.
- **Licensing decision:** whether to buy FLIP Fluids for production quality.
- **Editing a reel:** order, rhythm and music are editorial craft (S11).

## 7. Effort

- **First slice (live demo, ~1 day):** in the live window, a glass and a pitcher appear on a table, with a transparent domain box around them. The resolution-32 bake runs in a headless process; then the live window loads the cache and scrubs the timeline so the owner sees blocky liquid pouring and filling the glass. Resolution 64 and 96 bakes follow, and each step shows smoother water and foam points. The check table (leak %, fill level, volume drift, bake times) appears in the Text Editor; a 48-frame EEVEE preview plays, then a few Cycles frames show the glass-and-water look.
- **Full reproduction (a 12-shot reel):** ~2–4 agent-hours of setup per shot, plus bake compute of ~1–6 hours per hero shot at production resolution and ~1–3 GPU-hours of Cycles rendering per shot. Human direction ~1–2 hours per shot for framing and feel, plus a day of editing.

## 8. Risks and unknowns

- **Mantaflow vs FLIP Fluids quality:** unknown; the reel's look may need the paid add-on.
- **Bake times scale roughly with the cube of resolution;** the 0.71 s probe at resolution 32 tells us little about resolution 256.
- **Demo add-on limits are unknown;** do not plan the first slice around it.
- **Mantaflow's long-term status in Blender** is not checked here; GN simulation zones are where upstream is investing, but they are not yet a FLIP solver.
- **Disk:** high-resolution caches with whitewater reach tens of GB per shot.
- **The bridge blocks during long bakes;** keep heavy bakes out of the live session.

## 9. Sources

- [BlenderNation: FLIP Fluids Add-on 2021 Customer Reel](https://www.blendernation.com/2022/02/10/flip-fluids-add-on-2021-customer-reel/) (verified, via index)
- [GitHub: rlguy/Blender-FLIP-Fluids](https://github.com/rlguy/Blender-FLIP-Fluids) (verified on fetch: addon code GPL, engine MIT, build from source, Blender 4.5–5.2 compatibility, free demo add-on)
- [Superhive: FLIP Fluids](https://superhivemarket.com/products/flipfluids/docs) (prices from search results, not fetched: $79 / $149 / $299)
- [00-index.md § 20](00-index.md) and § 01 (Flow)
- [Transformation ledger](../discovery/ledger.md) (L-003, L-004, L-006, L-008), [RFC 0001 § R6](../rfc/0001-newblender.md)
- Headless Mantaflow probe and operator listing (`fluid.bake_all`, `simulation_nodes_cache_bake`, `ocean_bake`, GN simulation nodes): Blender 5.2.2 LTS, run while writing this file.
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`
