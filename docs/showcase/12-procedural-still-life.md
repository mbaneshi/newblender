# 12 — Procedural Still Life (Blender 2.93 splash): how an agent could make it

| | |
|---|---|
| **Original** | Erindale Woodford, 2021, Geometry Nodes procedural art (Blender 2.93 LTS splash) · [BlenderNation](https://www.blendernation.com/2021/04/15/blender-2-93-lts-splash-screen-revealed/) |
| **Agent-readiness today** | **Today**: everything in the piece is a Geometry Nodes (GN) tree plus procedural shaders and Cycles, and the live bridge can build, evaluate, measure and render all of it now. What it cannot supply is the eye: composition, the sunlit mood, which vessel silhouettes are beautiful. |
| **Difficulty** | 3 (one artist's piece; a faithful-quality version is about two weeks of agent work plus owner direction) |
| **First slice** | One GN "vessel generator" (a profile curve revolved, with lip, foot and fluting as inputs) that fills a workbench with 12 seeded, non-intersecting pots, plus GN stems and flowers in two of them, lit by one warm sun through a window and rendered in Cycles. |

## 1. What the original actually is

- **One still image:** a sunlit potting-shed workbench with ornate vessels and flowers ready for arranging (index entry 12). It shipped as the Blender 2.93 LTS splash.
- **Fact (BlenderNation):** it was made "entirely procedurally using Geometry Nodes" by Erindale Woodford ("nodemancer"), chosen to show off the expanded GN toolset in 2.93.
- **Assets inside the image (interpretation from the picture):** bench and wall, a family of turned vessels, pot rims and feet, stems, leaves and petals, small scattered debris, a window light.
- **Follow-up:** the "Geometry Nodes Flower Shop" (2022, Blender 3.0) built a whole shop from a single node tree ([BlenderNation](https://www.blendernation.com/headers/geometry-nodes-flower-shop/)).
- **The file exists:** blender.org's demo-files page lists "Still Life" by Erindale Woodford under CC-BY, linked to the Blender Cloud gallery. That is a layer-3 reference we can fetch (small file; not downloaded for this note).

## 2. How the humans made it

Stages: **S01 Modeling, S03 Shading, S04 Geometry Nodes, S09 Lighting & rendering.**

- **Fact:** procedural modelling with GN: instancing, curves, distribution (index entry 12; BlenderNation).
- **Fact (version history):** 2.93 GN was the attribute-based system; Fields arrived in 3.0. The 2.93 tree therefore used named attributes passed between nodes, which today's Fields model replaces with function graphs (dev docs `features/nodes/fields.md`: a field is an immutable function graph evaluated in a context).
- **Interpretation:** each vessel family is a parametric recipe (profile + revolve + displacement); flowers are curves with instanced petals; the bench layout is a distribution with collision avoidance. The art is in tuning those parameters and in the light.

**How GN is used in production today (local evidence):**
- S01 census (`docs/discovery/s01-modeling/02-census.md`): 170 GN node groups and 836 GN modifiers across asset files; 8,423 GN modifiers in shot files. The most-used nodes are assembly utilities (Join Geometry, Realize Instances, Object Info), not "modelling from scratch".
- The Blender 4.2 Gold splash ships `assets/nodes/procedural_modeling.blend`: 16 GN trees, 2,798 faces, a Repeat zone, Sample Curve, Instance on Points and heavy Math/Vector Math use (census JSON). The full splash file carries 1,490 GN modifiers and 77 GN trees (e.g. `GN-curve_coral` ×68, `GN-scatter_strokes` ×190).

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free sources) | Tooling |
|---|---|---|---|
| S04 / S01 Vessels | GN group `GN-vessel`: profile from a Bezier built as data (control points = height/radius table) → Curve to Mesh around a circle (revolve); inputs: height, belly, neck, lip roll, foot, flute count, flute depth, seed | Proportions from real pottery reference (owner picks); none downloaded | `tools/live/bl.py`; `bpy.data.node_groups.new` |
| S04 Layout | GN group `GN-bench_scatter`: points on the bench top, Poisson-disk via Distribute Points (min distance = max vessel radius), instance seeded vessel variants, Realize | None | GN Distribute Points on Faces |
| S04 Flowers | GN `GN-stem`: curve with noise + gravity bend, Curve to Mesh; petals instanced along the stem end by Instance on Points with rotation from Align Rotation to Vector | None | GN Repeat zone for petal rings |
| S01 Bench / room | Boxes built as data (chair-demo style), Bevel modifier declared | None | bmesh → Mesh |
| S03 Shading | Glazed ceramic: Principled with coat; colour from a GN-written `glaze` attribute; terracotta: noise + Voronoi; wood bench from ambientCG/Poly Haven textures | [Poly Haven](https://polyhaven.com/textures), [ambientCG](https://ambientcg.com) (CC0) | Shader Attribute node |
| S09 Lighting | One sun through a window cutter, low bounce fill, slight volume for god-rays; camera at 50 mm | Optional Poly Haven HDRI (CC0) for window sky | Cycles, fixed seed |

**Build order:**

1. Write checks first (§5).
2. Bench and back wall as data; camera locked.
3. `GN-vessel` with all inputs exposed; render a contact sheet of 16 seeds for the owner.
4. Owner picks the 3–4 vessel families they like; freeze those seeds as presets.
5. `GN-bench_scatter` places 12 vessels; checker confirms no intersections.
6. `GN-stem` + petals into two vessels.
7. Materials; sun and window; test render at 960 px; full render.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - All GN nodes listed above exist in 5.2.2 and are creatable from Python; group inputs are settable per modifier.
  - Evaluated geometry is readable for checks (`evaluated_get(depsgraph).to_mesh()`), exactly as `tools/live/checks/chair_checks.py` does.
  - Bounding-box and BVH overlap tests (`mathutils.bvhtree.BVHTree.overlap`) between instances.
  - Cycles render to file and screenshots of the owner's viewport.
- **Painful today:**
  - Authoring a 60-node tree as `nodes.new` / `links.new` calls: no text form, no node layout, hard to diff (L-006; `nodebpy` is the upstream direction).
  - GN gives no result summary: instance counts and bounds must be recomputed by the checker (L-003).
  - Real-world placement wants "this pot sits on the bench" as a declared relation; today it is computed positions (L-009 frames placement as data, which is what we do).
  - Iterating looks pushes no undo from Python (L-008); save a versioned file per accepted look.
- **Not feasible today:** nothing mechanical. The infeasible part is knowing which of 1,000 seeds makes the picture sing.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every realised vessel mesh is closed and clean | 0 non-manifold edges (except declared open rims), 0 degenerate faces, 0 loose verts, normals outward |
| 1 Validity | GN trees have no unconnected required inputs and no `NodeUndefined` | 0 (the census found 1,512 undefined nodes in old asset files; ours must have none) |
| 2 Spec | Vessel count and variety | Exactly 12 vessels; ≥ 4 distinct families; height range 8–40 cm |
| 2 Spec | Physical plausibility | Every vessel's lowest point within 1 mm of the bench top; 0 pairwise BVH overlaps between vessels |
| 2 Spec | Budget | Realised scene < 2 M faces; render at 1920 × 1080 < 10 min on the owner's GPU |
| 2 Spec | Determinism of recipe | Same seed → identical vertex hash across two evaluations |
| 3 Reference | Compare with Erindale's CC-BY "Still Life" file (fetch later): vessel count, face counts, light count, camera focal length | Report deltas; not a gate on art, a gate on "same kind of scene" (vessel count within ±50%) |
| 4 Downstream | Render has no fireflies or black holes | < 0.01% pixels > 20× local median; 0 NaN |
| 4 Downstream | UVs exist for textured parts | 100% of bench/wall meshes with a UV layer |
| 5 Appearance (warning) | Vision model compares the render to the 2.93 splash on "sunlit workbench, ornate vessels, flowers" | Warn below 7/10 |
| 6 Taste (owner) | Owner picks vessel families, flower placement, crop | Sign-off on the final frame |

## 6. Where the human is still needed

- **Choosing beautiful silhouettes.** A vessel recipe yields thousands of valid pots; maybe 1 in 20 is lovely. That ratio is the human's.
- **Arrangement.** The "ready for arranging" feeling (a fallen stem, one pot slightly askew) is deliberate imperfection; a scatter with collision avoidance looks tidy and lifeless unless directed.
- **Light.** The warm window shaft and how much it rakes across glaze is the mood of the piece.
- **When to stop.** GN invites endless parameters; the artist knows which ones matter.

## 7. Effort

- **First slice (live demo, ~1 day):** in the owner's Blender window, a plain bench and back wall appear, then a row of 12 different pots grows on the bench as the GN modifier is added. Changing the `seed` input reshuffles every pot's profile and fluting in place; changing `flute_count` on one preset re-carves it live. Two pots sprout curved stems with ring-instanced petals. A Cycles render with a warm raking sun is saved beside a check report (counts, overlaps, validity) in `~/newblender-data/demos/`.
- **Full reproduction:** 40–80 agent-hours for the vessel, flower, debris and layout recipes plus checks; < 5 GPU-hours of render; 10–20 human-hours of art direction (seed picking, arrangement, light).

## 8. Risks and unknowns

- Erindale's actual tree structure is unknown until the CC-BY file is fetched; our recipe may differ in approach even if the picture matches.
- 2.93-era attribute nodes in that file may load as legacy or undefined nodes in 5.2.2 (compare the census `NodeUndefined` open question).
- Vision scoring of "ornate" is weak; expect the owner loop to dominate.

## 9. Sources

- [BlenderNation: Blender 2.93 LTS splash screen revealed](https://www.blendernation.com/2021/04/15/blender-2-93-lts-splash-screen-revealed/) (verified, fetched 2026-10-07)
- [BlenderNation: Geometry Nodes Flower Shop](https://www.blendernation.com/headers/geometry-nodes-flower-shop/) (from index, verified there)
- [blender.org demo files](https://www.blender.org/download/demo-files/): "Still Life", Erindale Woodford, CC-BY (verified listing, 2026-10-07); Simon Thommes CC0 GN demos ("Tree, leaves and grass", "Sample UV Surface")
- Local: `docs/discovery/s01-modeling/02-census.md`; census JSON for `~/newblender-data/extracted/blender-4.2-splash/assets/nodes/procedural_modeling.blend` and `gold-splash_screen.blend` in `~/newblender-data/census/`
- Dev docs: `~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender-developer-docs/docs/features/nodes/fields.md`
- [Ledger L-003, L-006, L-008, L-009](../discovery/ledger.md); [S01 brief](../discovery/s01-modeling/05-brief.md); [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: [`tools/live/bl.py`](../../tools/live/bl.py), [`tools/live/checks/chair_checks.py`](../../tools/live/checks/chair_checks.py)
