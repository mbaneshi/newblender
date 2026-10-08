# 15 — Park Lipence: how an agent could make it

| | |
|---|---|
| **Original** | Polygoniq, 2021, architectural visualisation / photoreal landscape (Cycles) · [Blender 3D Architect](https://www.blender3darchitect.com/architectural-visualization/park-lipence-in-prague-with-blender-cycles/) |
| **Agent-readiness today** | **Partial**: terrain, paths and park architecture as data, Geometry Nodes (GN) scattering with masks, physical sky and Cycles all work through the live bridge today. The bottleneck is photoreal vegetation: the original used Polygoniq's commercial botaniq library, and free CC0 plant libraries are thin, so the hero trees either need a generator (Sapling, GN tree demo) or a paid library. Photoreal "believability" is also owner taste. |
| **Difficulty** | 4 (a small studio's showcase set; a convincing park section is about two weeks of agent work, mostly vegetation quality and render tuning) |
| **First slice** | A 40 × 40 m park patch: gently rolling terrain built as data, a curving gravel path that masks the scatter, GN-scattered grass clumps, shrubs and 8 generated trees, a simple timber pavilion built with declared modifiers, Blender's physical sky at late afternoon, and an eye-level Cycles render. |

## 1. What the original actually is

- **A set of photoreal stills** of a park near Prague (Lipence is on the city's south-western edge), with "open spaces, vast vegetation, and unique architectural designs" (Blender 3D Architect, fetched 2026-10-07). The number of images and whether it was commissioned or self-initiated are not stated.
- **A vendor showcase:** Polygoniq makes the add-ons used: **botaniq** (vegetation), **materialiq** (materials), **traffiq** (vehicles). The article appeared with a Blender Market discount in August 2021.
- **Deliverables (interpretation):** terrain and lawns, a path network, park buildings/pavilions and furniture, thousands of plant instances at several scales (grass, shrubs, trees), parked or passing vehicles at the edges, a sun-and-sky lighting setup, and colour-graded stills.

## 2. How the humans made it

Stages: **S01 Modeling, S03 Shading, S04 Geometry Nodes, S06 Layout, S09 Lighting & rendering.**

- **Fact:** Cycles rendering; botaniq, materialiq and traffiq libraries (article).
- **Fact (index):** architectural modelling, vegetation scattering, library materials, photoreal Cycles lighting.
- **Interpretation:** the architecture is modelled from plans with standard archviz modelling (extrude, bevel, array); vegetation is scattered by the library's scatter tools (botaniq is built on particle systems / GN scatter with LODs) and art-directed by hand painting density masks; hero trees are placed one by one for composition; lighting is a physical sky or HDRI; post grading in the compositor or an external tool.
- **Local evidence gap:** the S01 census has no archviz corpus yet (brief §8: "add a hard-surface / archviz set"; census next steps name Barcelona Pavilion and Classroom). This file's plan is therefore not grounded in a measured archviz census.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free sources) | Tooling |
|---|---|---|---|
| Site data | Park outline, paths and building footprints from map data; terrain from an elevation model or a declared noise if none | [OpenStreetMap](https://www.openstreetmap.org) (ODbL, not CC0: attribution required); Prague open geodata portals for elevation (*unverified availability*) | Python parse of an OSM extract via `tools/live/bl.py` |
| S01 Terrain | Grid mesh built as data, heights from the DEM or noise; `path_mask` attribute written by distance to path curves | Same | bmesh / GN Set Position + Geometry Proximity |
| S01 Architecture | Pavilion, benches, lamps as data with real dimensions; Bevel/Array/Solidify declared (chair-demo method) | Owner's reference photo or plan | bmesh + declared modifiers |
| S04 Scatter | GN `GN-park_scatter`: Distribute Points on Faces with density = (1 − `path_mask`) × slope falloff × noise; three layers (grass clumps, shrubs, trees) with min-distance per layer; collection instances; camera-distance culling and LOD switch | [Poly Haven models](https://polyhaven.com/models) (CC0 plants, rocks, a few shrubs); [Blender GN demo "Tree, leaves and grass"](https://www.blender.org/download/demo-files/) by Simon Thommes (CC0); [Sapling Tree Gen](https://extensions.blender.org) extension (free) for tree variety | GN |
| S03 Materials | Lawn, gravel, timber, concrete from CC0 PBR sets; leaf translucency in Principled; per-instance hue jitter from GN `Random Value` | [ambientCG](https://ambientcg.com), [Poly Haven textures](https://polyhaven.com/textures) (CC0) | Shader Attribute (instancer) |
| S06 Layout | Cameras at 1.6 m eye height along the path; hero trees placed as data at owner-chosen positions | None | Python |
| S09 Lighting | Sky Texture (physical sun/sky) at a declared date/time/latitude (Prague ≈ 50.0° N), or a CC0 HDRI | [Poly Haven HDRIs](https://polyhaven.com/hdris) (CC0) | Cycles; adaptive sampling; denoise |
| S10 Grade | Compositor: mild filmic/AgX contrast, slight glare | None | Compositor via Python |

**Build order:**

1. Write checks (§5); decide the site (real OSM extract or a declared synthetic plan).
2. Terrain and path curves; `path_mask` attribute; check path width and slope.
3. Pavilion and furniture as data with declared modifiers.
4. Scatter layers one at a time, viewport in solid mode with instance display as bounds to stay interactive.
5. Trees: generate 6–10 variants (Sapling or the GN tree demo), place 8 hero trees as data, scatter background trees.
6. Materials, sky, camera; 25% test render; owner review; final render.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Terrain, paths and buildings as data with declared modifiers and spec checks, as in demo 001 (12/12 checks, `~/newblender-data/demos/001-chair/report.md`).
  - Building and parameterising GN scatter trees from Python; evaluating instance counts and positions for checks.
  - Sky Texture, Cycles settings, compositor nodes and render-to-file from Python; screenshots of the owner's window (`tools/live/snap.py`).
- **Painful today:**
  - Scatter art direction is normally done by **painting** density weights; that is a brush stroke stream (L-009). We replace it with declared masks (distance to path, slope, noise, owner-placed exclusion curves).
  - Hundreds of thousands of instances make the live viewport slow; the right home for final evaluation and render is a headless profile (L-011).
  - GN returns no summary of what it scattered; counts, densities and minimum spacing are recomputed by the checker (L-003).
  - Free photoreal trees: Poly Haven's CC0 plant set is small, Sapling trees read as "generated" up close; this is an asset-supply problem, not an engine one.
- **Not feasible today:**
  - Matching botaniq's hero-tree realism with only CC0 assets. A fair reproduction either buys the library (owner decision) or accepts a lower bar for close-up trees.
  - Traffiq-quality vehicles from CC0 sources at hero distance.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Terrain and architecture meshes clean | 0 non-manifold edges on closed parts; 0 degenerate faces; normals up on terrain (100% faces with normal·Z > 0) |
| 1 Validity | Every instanced collection and texture resolves | 0 missing objects or images |
| 2 Spec | Patch dimensions and terrain | 40 × 40 m ± 0.1 m; max slope < 15° on lawn areas |
| 2 Spec | Paths stay clear | 0 scattered instances with origin inside a path (`path_mask` > 0.5); path width 2.5–3.5 m |
| 2 Spec | Scatter density per layer | Grass ≥ 20 clumps/m² on lawn; shrubs 0.2–0.5 /m² away from paths; exactly 8 hero trees, ≥ 4 m apart |
| 2 Spec | Grounding | Every instance base within 3 cm of terrain surface (raycast) |
| 2 Spec | Architecture | Pavilion footprint and height match the declared plan within 1 cm; scale applied; Studio naming `GEO-park_*` |
| 2 Spec | Budget | 1920 × 1080 Cycles render < 30 min on the owner's GPU; peak memory within GPU VRAM |
| 3 Reference | Sun direction matches the declared date/time/latitude | Sun azimuth and elevation within 1° of an ephemeris calculation |
| 3 Reference | (Later) archviz counter-corpus: compare instance densities and light setup with the CC0 Classroom and CC-BY Barcelona Pavilion demo files | Report deltas; not a gate |
| 4 Downstream | Render health | 0 NaN; fireflies < 0.01% pixels > 20× local median; sky not clipped (< 0.5% pixels > 1.0 after view transform) |
| 4 Downstream | Determinism | Same scene, seed, frame rendered twice: PSNR ≥ 45 dB |
| 5 Appearance (warning) | Vision model compares to the Park Lipence images on "photoreal park, believable vegetation, no CG tells" and lists tells (tiling, repeated trees, floating plants) | Warn below 7/10 or any listed tell |
| 6 Taste (owner) | Owner judges realism, composition and season/mood | Sign-off; notes become mask, density and light parameters |

## 6. Where the human is still needed

- **"Does it look real?"** Photoreal is judged by the eye against lived experience: grass colour variation, how leaves catch the light, the absence of repetition. Machines can flag tells, not sign off realism.
- **Composition of nature.** Where trees frame the building, where an open lawn breathes: archviz is selling a place, and that is a design decision.
- **Asset budget.** Whether to buy a vegetation library (botaniq or similar) is an owner decision with money attached.
- **The architecture itself.** If it represents a real design, the architect's drawings are the source; an agent should not invent a real building.

## 7. Effort

- **First slice (live demo, ~1 day):** in the owner's Blender window, a flat plane rises into gently rolling ground; a gravel path curves through it. Adding the scatter modifier, grass fills the lawn but stops cleanly at the path edges; shrubs and eight trees appear; changing `grass_density` or moving a path control point re-scatters live. A timber pavilion with bevelled beams sits at the path bend. The viewport switches to rendered mode under a late-afternoon physical sky with long shadows. A Cycles still and a check report (density per layer, path clearance, grounding, sun angle) land in `~/newblender-data/demos/`.
- **Full reproduction:** 60–120 agent-hours for site, architecture, scatter system, cameras and checks; 5–20 GPU-hours of final stills; 20–50 human-hours of direction and realism review; plus the cost of a vegetation library if the owner chooses one.

## 8. Risks and unknowns

- The original's exact site, image count and commission status are unknown; the article is short and promotional.
- OSM data is ODbL (attribution and share-alike on the database), not CC0; check before publishing derived renders with the data.
- Free trees may cap realism; this could make the honest result "good archviz, not Polygoniq-level".
- GPU memory with many unique tree meshes; instancing must stay instanced until render (do not Realize Instances on the scatter).
- No archviz census exists yet, so modelling norms for this genre are assumed, not measured.

## 9. Sources

- [Blender 3D Architect: Park Lipence in Prague with Blender Cycles](https://www.blender3darchitect.com/architectural-visualization/park-lipence-in-prague-with-blender-cycles/) (verified, fetched 2026-10-07)
- [blender.org demo files](https://www.blender.org/download/demo-files/): "Tree, leaves and grass" (Simon Thommes, CC0), Classroom (Christophe Seux, CC0), Barcelona Pavilion (eMirage, CC-BY) (verified listing, 2026-10-07)
- CC0 inputs: [Poly Haven](https://polyhaven.com) (HDRIs, textures, models), [ambientCG](https://ambientcg.com); map data [OpenStreetMap](https://www.openstreetmap.org/copyright) (ODbL)
- [S01 brief §8 (archviz corpus gap)](../discovery/s01-modeling/05-brief.md); [S01 census](../discovery/s01-modeling/02-census.md)
- [Ledger L-003, L-009, L-011](../discovery/ledger.md); [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: [`tools/live/bl.py`](../../tools/live/bl.py), [`tools/live/snap.py`](../../tools/live/snap.py), [`tools/live/demos/chair_build.py`](../../tools/live/demos/chair_build.py)
