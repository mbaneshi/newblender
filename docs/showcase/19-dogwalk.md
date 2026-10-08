# 19 — DOGWALK: how an agent could make it

| | |
|---|---|
| **Original** | Blender Studio, 2025, game development (Blender → glTF → Godot) · [blender.org](https://blender.org/projects/dogwalk/) |
| **Agent-readiness today** | **Partial.** The Blender side of a game pipeline (set dressing, GN level tools, collision proxies, naming, glTF export) is data plus declared GN and runs headless today. Character modelling, rigging and animation are the human-heavy parts, and the gameplay half lives in Godot, which is outside Blender and this bridge entirely. |
| **Difficulty** | **4.** A polished small game is a team-months project; the original took a studio team about four months. |
| **First slice** | One playable-ready "set layer": a snowy clearing generated from a closed curve with GN, set-dressed with linked trees and boulders from the DOGWALK splash file, auto-generated collision proxies named for Godot, exported to glTF and re-imported to prove the round trip, all visible in the live window. |

## 1. What the original actually is

- **A finished game:** a short, cosy winter game. You play Chocomel, a big dog, helping the kid Pinda find decorations for a snowman. Released 11 July 2025, free on blender.org and Steam.
- **Built in about four months** as Blender Studio's R&D project, with "Blender as the DCC hub, Godot as the game engine, and glTF as the exchange format" (Khronos summary).
- **Assets:** two rigged characters, rigged props, a library of instanceable set dressing, and levels assembled in Blender.
- **Open project:** the production bundle (asset library, source code, lessons) is for Blender Studio subscribers; the game itself is free.
- **What the local splash file shows** (`blender-4.5-splash.blend`, the DOGWALK scene, inspected headless while writing this):
  - 512 objects, 289 meshes, 5 armatures, 52 actions, 43 materials, 73 images (2K–4K PNG atlases);
  - rigs: `RIG-Chocomel` 318 bones, `RIG-Pinda` 215, `RIG-Snowman` 35;
  - modifiers dominated by game prep: Weighted Normal 62, Geometry Nodes 58, **Triangulate 56**, Armature 28;
  - GN groups such as `GN-collision_primitive`, `GN-ground_curve_to_mesh`, `GN-pond`, `GN-generate_paper_cutout_tree`;
  - per-asset collections `…-geometry`, `…-collision` (`COL-*` objects), `…-leash` (`HLP-leash_point` Empties);
  - Chocomel is a low-poly kit of parts (e.g. legs 292 faces each, ears 152).

## 2. How the humans made it

| Stage | Technique | Fact / interpretation |
|---|---|---|
| S01 Modeling | Game-ready, low-poly stylised assets; triangulated with weighted normals for export. | Fact from the splash file's modifier counts |
| S02 UV & texturing | Texture atlases (bark/foliage atlases with `UVMap` + `UV2`). | Fact (file) |
| S03 Shading | Stylised real-time materials (a "paper" look: `SH-paper-default`). | Fact (file); how they map to Godot shaders is not public in what I read |
| S04 Geometry Nodes | Creek, pond and paths from curve inputs with UV-mapped output; grass and reeds scattered with GN then turned into editable objects by a custom "Visual Geometry to Objects" operator; snow patches from closed curves. | Fact (Studio blog "Assembling the world") |
| S05 Rigging / S07 Animation | Character rigs with hooks for fur and skirts (`chocomel-rigging-furhooks`); actions such as `ANI-pinda.walk`, `ACTN-chocomel-wake_up`. | Fact (file) |
| S06 Layout / levels | Levels built in Blender: Set (SE) collections made of Set Layers (SL), linked library assets (LI), characters (CH), props (PR). Each exported asset becomes a Node3D in Godot, so collision types differ per asset. Custom tools on top of the glTF exporter keep the linking hierarchy and de-duplicate textures. | Fact (Studio blog, Khronos) |
| Godot | Gameplay code, physics, camera, UI, build. | Fact that it exists; details out of scope here |

## 3. How I would make it: the agent-native plan

The split is the key fact: **Blender (and this agent) covers content: levels, set dressing, collision, export, and lightweight animation. Godot covers the game.** An agent can also write GDScript, but that is a separate toolchain and Godot is not installed on this machine.

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S06 Level as data | A level is a JSON layout: closed curves for ground and snow patches, a path curve, and a list of `{asset, transform}` placements. The agent writes it; Blender builds it. | — | live bridge / headless |
| S04 Terrain | GN recipe: closed curve → filled, subdivided ground mesh with noise height and a UV, like `GN-ground_curve_to_mesh`. Snow patches the same way. | — | GN as code ([L-006](../discovery/ledger.md)) |
| S04 Scatter | GN Distribute Points on Faces with density masks (away from the path) instancing linked library assets; realise to objects for export. | Trees, boulders, bushes from the DOGWALK splash file (CC-BY per Blender splash licensing, confirm) or CC0 [Quaternius](https://quaternius.com/) / [Kenney](https://kenney.nl/) packs | GN, `bpy.data.libraries.load(link=True)` |
| Collision | Per asset: a convex hull or capsule proxy generated from the evaluated mesh (GN Convex Hull, or bounding cylinder), named `COL-*`, in a `-collision` collection; Godot import hints via name suffixes (`-col`, `-colonly`) or glTF extras. | — | GN / bmesh |
| S01/S02 props | New simple props as data (a snowman from spheres, a sledge from boxes) with UVs written per loop, Triangulate + Weighted Normal like the studio's. | — | bmesh + modifiers |
| S05/S07 | **Reuse existing rigs;** procedural animation only (a dog-tail wag driver, a camera path). New character animation stays human. | Chocomel / Pinda rigs from the splash file | drivers, keyframes as data |
| Export | glTF per set layer (`export_scene.gltf`, active collection), textures de-duplicated by hash; a manifest JSON listing nodes, collision shapes and materials for Godot. | — | headless glTF exporter |
| Godot (out of Blender) | Import the glTF, add a CharacterBody3D controller, follow camera, pickup logic. | Godot 4 (would need installing) | GDScript, `godot --headless` |

**Build order**

1. Write the set-layer spec and checks (section 5).
2. Link 5 library assets from the splash file into the live session.
3. Build ground and snow patches from curves (GN); scatter assets; carve the path.
4. Generate collision proxies; name and collect them.
5. Export glTF; re-import into an empty scene to check the round trip.
6. (Later) Godot: import, walk a capsule around, confirm collisions.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Linking assets, GN curve-to-ground tools, scatter, collision proxies, naming: all data and declared nodes.
  - **glTF export headless:** measured while writing this file, `export_scene.gltf` on the `CH-Chocomel` collection of the splash scene (rig, meshes, actions) finished in **11.75 s** and wrote a **34 MB GLB** with Blender 5.2.2 in background mode.
- **Painful today:**
  - **Export is scoped by "active collection" or selection,** not by an explicit list of objects ([L-002](../discovery/ledger.md), [L-004](../discovery/ledger.md)). The studio needed custom tools to keep the link hierarchy and dedupe textures; that is the same gap.
  - **Realising GN instances into editable objects** needed a custom operator in the original ("Visual Geometry to Objects"); stock Blender has `object.duplicates_make_real`, which is selection-scoped.
  - **Exports return a status, not a manifest** of what was written ([L-003](../discovery/ledger.md)); the agent must re-import to know.
  - **Weight painting and retopology for new characters** are brush- and placement-driven (no twin: [L-009](../discovery/ledger.md)).
- **Not feasible today in this setup:**
  - **Gameplay, physics and builds:** Godot, not Blender. Godot is not installed locally; nothing here tests it.
  - **Character animation with performance** (Chocomel's weight, Pinda's walk): keyframes are data, but good animation is human.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every exported mesh: non-manifold edges outside open borders, degenerate faces, NaN positions | 0 / 0 / 0 |
| 1 Validity | Collision proxies are closed and convex (convex-hull vertex count = proxy vertex count) | 100% of `COL-*` |
| 2 Spec | Triangle budget for the set layer | ≤ 60,000 tris total; no single asset > 5,000 |
| 2 Spec | Naming: `GEO-*`, `COL-*`, `LI-*`, collections `SL-*`; every `GEO-*` with ≥ 1 `COL-*` | 100% compliant; 0 assets without collision |
| 2 Spec | Path clearance: no instance or collider inside 1.2 m of the walk path curve | 0 violations |
| 2 Spec | Texture budget: unique images after dedupe; max size | ≤ 12 images; ≤ 2048² each |
| 3 Reference | **glTF round trip:** re-import the GLB into an empty scene | same object count, triangle count, material count and bone count (± 0) as the source |
| 3 Reference | Rebuilding from the same layout JSON | identical object names and transforms (max diff < 1e-6) |
| 4 Downstream | Walkability: raycast a 0.5 m grid down onto ground + colliders along the path | ≥ 99% of path samples hit ground within ± 0.3 m of curve height; slope ≤ 35° |
| 4 Downstream | Export size / time for the set layer | GLB ≤ 50 MB; export ≤ 30 s headless |
| 4 Downstream | (When Godot is available) `godot --headless` import with zero errors; a capsule walked along the path never falls through | 0 import errors; 0 fall-throughs in 3 runs |
| 5 Appearance (warning) | Vision model on 4 game-camera renders vs the brief ("cosy snowy clearing, birch trees, clear walk path") | warn on mismatch |
| 6 Taste (owner) | Does it feel cosy and readable as a game space? Is the path inviting? | owner judgement |

## 6. Where the human is still needed

- **Game design:** what is fun, pacing, what the player does. None of this is in Blender.
- **Character design, rigging polish and animation performance:** Chocomel's heavy, playful dog movement is animation craft.
- **Art direction of the "paper" look** and level composition: where the eye goes, where the snowman stands.
- **Playtesting:** only people can say the game is cosy.

## 7. Effort

- **First slice (live demo, ~1 day):** in the live window, a flat curve outline appears and becomes a gently bumpy snowy ground (GN, visible in Solid then Material Preview). Birch trees, boulders and bushes linked from the DOGWALK splash file pop in along the edges, avoiding a winding path. Wireframe collision capsules and hulls appear around each asset. A glTF export runs; the GLB is re-imported into a second scene and shown side by side, with the round-trip numbers and check report in the Text Editor. A game-camera render closes the day.
- **Full reproduction:** content side (3 levels, ~40 set-dressing assets reused, collision, export tooling): ~1–2 agent-weeks. New characters, rigs and animation: human-led, weeks. Godot gameplay and builds: ~2–4 agent-weeks plus heavy human playtesting. Compute is small (real-time game; renders only for review).

## 8. Risks and unknowns

- **Licensing of the splash-file assets** for reuse in a derived game: Blender splash files are CC-BY (I believe; not verified for this file). The full DOGWALK production bundle is subscriber-only and must not be redistributed.
- **Godot import conventions** (name suffixes vs glTF extras for collision) need checking against the Godot version used; not verified here.
- **GN scatter realised to objects** can explode object counts and export times.
- **The first-slice round trip tests Blender against itself,** not against Godot; downstream fitness is only partly proven until Godot runs.
- **A 34 MB GLB for one character** suggests texture sizes need budgeting for web or mobile targets.

## 9. Sources

- [blender.org: DOGWALK — Open Game by Blender Studio](https://blender.org/projects/dogwalk/) (verified: release 11 July 2025, Blender + Godot pipeline, subscriber production bundle)
- [Khronos: Project DogWalk — stress-testing Blender to Godot interoperability with glTF](https://www.khronos.org/news/permalink/project-dogwalk-stress-testing-blender-to-godot-interoperability-with-gltf) (verified: four months, glTF as exchange)
- [Blender Studio blog: DOGWALK — Assembling the world](https://studio.blender.org/blog/dogwalk-assembling-the-world/) (verified: CH/PR/LI/SE/SL prefixes, set layers → Node3D, GN creek/pond/paths/snow, "Visual Geometry to Objects")
- [GamingOnLinux: DOGWALK out now](https://www.gamingonlinux.com/2025/07/dogwalk-is-a-free-casual-game-from-the-blender-studio-out-now) (via index)
- [Godot docs: Exporting 3D scenes](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/exporting_3d_scenes.html) (listed, not fetched)
- [00-index.md § 19](00-index.md), [Transformation ledger](../discovery/ledger.md), [RFC 0001 § R6](../rfc/0001-newblender.md)
- Local: `~/newblender-data/downloads/blender-4.5-splash.blend` (counts and export timing measured headless on Blender 5.2.2 while writing this file); bridge `tools/live/bl.py`
