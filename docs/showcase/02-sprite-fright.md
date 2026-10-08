# 02 — Sprite Fright: how an agent could make it

| | |
|---|---|
| **Original** | Blender Studio (written and directed by Matthew Luhn, co-directed by Hjalti Hjálmarsson), 2021, open movie: stylised character animation · [Blender Studio](https://studio.blender.org/films/sprite-fright/) |
| **Agent-readiness today** | **Partial.** Set dressing, GN moss and leaf systems, library linking, lighting from templates, render orchestration and file QA work today. The 11 minutes of comedic character acting, the story and the character design do not. |
| **Difficulty** | 4 (an 11-minute film with about 220 shots and five-plus rigged characters. Less than a feature, but still a studio-year.) |
| **First slice** | A forest-floor "mushroom clearing" set dressed by rules from the **real Sprite Fright library** (fungi, rocks, plants, leaves linked from `lib/env/*.blend`, with the production's own `GE-leaf_system` and `GE-moss.trees` GN groups), lit from `lib/lgt/templates.blend`, and rendered in Cycles through the production camera rig. |

## 1. What the original actually is

- **Film:** about 11 minutes and about 220 shots, which is "a hell of a lot of shots for a film of this length" ([Blender Studio blog, via search](https://studio.blender.org/blog/a-big-short-film-art-director-andy-goralczyk-on-blenders-most-ambitious-movie-yet)).
- **Characters:** five teenagers, the sprites (as a crowd), and creature cast. The local shot library ships `sprite`, `snail`, `spider`, `ladybug` and `butterfly`.
- **Environments:** a British forest, the mushroom grove, and the sprite village.
- **Props:** many hand-made props, including snacks, trash, a thorn staff, dandelions and pine cones.
- **FX:** fire.
- **Output:** a Cycles-rendered film. All production files are released under CC-BY.

**Concrete evidence on this machine.** The released shot `030_0020_A` is in `~/newblender-data/extracted/sprite_fright_030_0020_A/` (1.2 GB). Census numbers come from `~/newblender-data/census/*sprite_fright*`, the same data as [02-census.md](../discovery/s01-modeling/02-census.md).

| File | Engine | Objects | Faces | Linked libraries | Library overrides | Modifiers (of which GN) |
|---|---|---|---|---|---|---|
| `030_0020_A.lighting.blend` | Cycles | 5,170 | 310,400 | 45 | 2,696 | 8,710 (1,216) |
| `030_0020_A.anim.blend` | EEVEE | 5,012 | 305,232 | 42 | 2,696 | 8,626 (1,189) |
| `lib/sets/mushroom_grove` | Cycles | 2,611 | 126,267 | 22 | 71 | 2,149 (259) |
| `lib/sets/sprite_village` | Cycles | 3,173 | 144,217 | 22 | 56 | 2,268 (259) |
| `lib/env/background_forest` | EEVEE | 1,827 | 88,981 | 12 | 0 | 1,457 (75) |
| `lib/char/sprite` | Cycles | 95 | 16,141 | 5 | 0 | 143 (25); 61 actions |

**Reading of the numbers:**

- A single *shot* assembles about 5,000 objects from 45 library files through 2,696 overrides.
- **The pipeline is mostly assembly, not modelling.**
- The top GN groups in the lighting file are `Realize Instances 2.93 Legacy` (510), `store_coordinates` (480) and `Auto Smooth` (65). The sets use `GE-leaf_system`, `GE-moss.trees`, `Variation` and `Scatter Salt`, so procedural dressing is everywhere.

## 2. How the humans made it

**Facts:**

- **Stages:** S01, S02, S03, S04, S05, S07, S08, S09 ([index](00-index.md) §02).
- **Pipeline and asset management** were an explicit production goal: tools to help artists collaborate ([Blender Studio](https://studio.blender.org/films/sprite-fright/), verified).
- **Rendering** moved to Cycles X during production ([production logs, via search](https://studio.blender.org/projects/sprite-fright/production-logs/?page=7)).
- **The shot's readme** says that `.anim` holds the animation, `.FX` files hold simulations, and `.lighting` links animation and FX and "contains the full render setup" (`030_0020_A/readme.txt`).
- **The lib folder** contains `scripts/cloudrig.blend` (the Studio's CloudRig rigging system) and `scripts/rigged_particle_hair.blend`.

**Interpretation:**

- Sprite Fright is a **layered-file assembly pipeline**: assets → sets → anim → lighting, joined by linking and overrides.
- Each layer has a different author. The anim file is split A, B and C (three per-character or per-pass files: 85, 77 and 89 actions).
- This is the shape an agent should copy: *declarative, linkable, per-stage files*, with the agent doing whole layers that are rule-based (set dressing, lighting set-up, render) and the humans doing the acting layer.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs | Tooling |
|---|---|---|---|
| S01 Modeling | Props as data plus declared modifiers (the chair-demo method): mushrooms as revolved profiles with a Subdivision modifier, pine cones as GN spirals. Hero characters stay human-sculpted. | Released Sprite Fright lib (CC-BY) as reference and as reusable assets | `bl.py`, bmesh-as-data, L-006 |
| S02 UV & texturing | Procedural first; UVs only where texture maps are needed. Automatic seams on simple props; check stretch numerically. | Poly Haven CC0 bark and moss | Smart UV by script, then a stretch metric |
| S03 Shading | Reuse the production's shader node libraries (`lib/nodes/shaders.blend`, `textures.blend`) by linking; the agent sets parameters, not graphs. | `lib/nodes/*.blend` | Library linking |
| S04 Geometry Nodes | Set dressing by rules: scatter fungi by moisture (distance to roots or rocks), leaves by slope, moss on the up-facing side of logs. Reuse `GE-leaf_system` and `GE-moss.trees` from the lib. | `lib/env/{fungi,leaves,plants,rocks}.blend` | GN modifier with linked groups |
| S05 Rigging | Generate body rigs from CloudRig or Rigify meta-rigs; the agent runs deformation stress poses (layer 4). Facial rigs need a human rigger. | `lib/scripts/cloudrig.blend` | Rig generation by script |
| S06 Layout | Assemble shot files by linking set, characters and camera rig; create overrides by script; set frame ranges from an edit list. | `lib/cam/camera_rig.blend`; an EDL | `bpy.data.libraries.load`, override API |
| S07 Animation | **Human.** The agent only does secondary motion: wind sway on plants via GN, and crowd cycles for background sprites. | Human-keyed acting | Drivers, GN time |
| S08 Simulation & FX | Fire and smoke: Mantaflow gas domain or GN-driven sprite fire cards, baked headless per shot. | None | `-b` bake |
| S09 Lighting & rendering | Start from `lib/lgt/templates.blend` lighting rigs; set the world, exposure and samples; run Cycles with denoise; render passes for review. | `lib/lgt/templates.blend` | Headless Cycles |

**Build order (for the first slice):**

1. Write `checks/sprite_clearing_checks.py` first (section 5).
2. Set up a clean slate. Link (do not append) the needed collections from `lib/env/fungi.blend`, `rocks.blend`, `plants.blend` and `leaves.blend`, and the camera rig from `lib/cam/camera_rig.blend`. Report the linked-ID count.
3. Build the ground: a 6 × 6 m GN terrain with gentle noise and two root curves.
4. Scatter rocks (a few), then fungi clustered within 0.5 m of rocks and roots, then a leaf litter carpet. Apply `GE-leaf_system` and the moss GN group to logs and rocks.
5. Place the camera rig at a low, child's-eye height (about 30 cm). Use a 35 mm lens and frame the hero mushroom cluster.
6. Link the lighting template, then adjust the sun angle and world strength to the spec.
7. Show progress in the window after each step (`snap.py`). Render a 1920 × 1080 Cycles frame headless.
8. **Reference pass:** open `030_0020_A.lighting.blend` in a headless session, render the same frame size, and compare palette and density statistics against my clearing.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Linking and appending from library files.
  - Applying GN modifiers that reference linked groups.
  - Setting inputs by identifier.
  - Cycles headless rendering.
  - Reading census-style statistics from any `.blend`.
- **Painful today:**
  - **Library overrides by script** are fragile: hierarchies need `override_hierarchy_create` with a context, and many override operations are still operator-shaped (L-004). The 2,696 overrides in one shot show how central this is.
  - **No result diffs:** after linking, I must count IDs before and after to know what came in (L-003).
  - **Version drift:** 2021 files opened in 5.2.2 carry `Realize Instances 2.93 Legacy` groups (510 in the lighting file), and the census flags thousands of `NodeUndefined` nodes ([02-census.md](../discovery/s01-modeling/02-census.md)). This needs a validity pass before reuse.
  - **Placement of a hero prop "just so"** is a human, eye-driven act in Blender. As data it becomes explicit transforms or constraints (L-009).
- **Not feasible today:**
  - Character acting and lip-sync.
  - Facial rig quality (whether a face "reads").
  - Comedic timing.
  - Character and creature design.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Every linked library path resolves; missing-file count | 0 missing |
| 1 Validity | `NodeUndefined` nodes in any GN group used by the slice | 0 |
| 1 Validity | Agent-built meshes: non-manifold, degenerate faces, flipped normals | 0 / 0 / 0 |
| 2 Spec | Clearing footprint | 6 × 6 m ± 5% |
| 2 Spec | Fungi instances within 0.5 m of a rock or root curve | ≥ 80% |
| 2 Spec | Instance interpenetration: fungi pairs with overlapping bounding spheres | ≤ 2% |
| 2 Spec | Floating instances: base more than 1 cm above the ground (raycast) | 0 |
| 2 Spec | Camera height above the ground / focal length | 25–40 cm / 30–40 mm |
| 2 Spec | Naming follows the Studio prefixes (`GEO-`, `ENV-`, `CAM-`) | 100% |
| 3 Reference | Scene scale against the production set: faces in frame relative to `mushroom_grove` | within 0.3×–1.5× of 126k |
| 3 Reference | Rebuild from the recipe in a fresh session: identical instance transforms | identical |
| 4 Downstream | Cycles 1080p render at 128 samples finishes; NaN or black pixels | < 10 min; 0 |
| 4 Downstream | The shot file links (not appends) assets, so library updates propagate: linked-ID ratio | ≥ 90% of dressing IDs linked |
| 5 Appearance (warning) | Hue histogram of my render vs. the `030_0020_A` lighting render (Earth Mover's Distance), plus a vision-model comparison | warning if EMD > 0.15 or vision < 3/5 |
| 6 Taste (owner) | Does it look like the Sprite Fright forest: cosy, slightly spooky, hand-made? | owner's call |

## 6. Where the human is still needed

- **Story and comedy.** Matthew Luhn's horror-comedy beats, the timing of the reveal, and the tonal shift from cute to menacing.
- **Character design and sculpting** of the teens and sprites, including appeal and silhouette.
- **Animation.** Most of the film's labour, and none of it is automatable to Studio quality today.
- **Facial rigging.** The shapes and correctives that make expressions read.
- **Art direction:** hero-prop placement, colour script, what is in focus.
- **Calibrating the checker:** deciding what density and which clustering rules "look like Sprite Fright".

## 7. Effort

- **First slice (live demo, about 1 day):**
  - **On screen:** the owner's Blender window starts empty. A brown, gently uneven forest floor appears, then grey mossy rocks and two twisting roots, then clusters of the actual Sprite Fright mushrooms sprouting around them, then a carpet of leaves.
  - Moss creeps over the tops of the rocks as the GN group is applied.
  - The view drops to a low camera looking into the clearing. Rendered preview shows warm, dappled forest light from the production's template.
  - At the end, a Cycles still sits next to a frame from the real shot `030_0020_A`, with the check report.
- **Full reproduction:**
  - **Agent work:** about 300–600 agent-hours for set dressing of all sets, shot assembly for about 220 shots, lighting set-up and render management.
  - **Render compute:** about 11 min × 24 fps ≈ 16,000 frames × 5–15 min Cycles per frame ≈ 1,300–4,000 GPU-hours.
  - **Human work:** animation is still most of the cost, at roughly 10 animators for many months, plus direction, design and a rigging lead.

## 8. Risks and unknowns

- 2021 assets opened in 5.2.2 may render differently (the EEVEE Legacy anim files, the legacy GN groups). The reference render itself may drift from the released film.
- Library overrides by script may hit operator-only paths, which is the biggest unknown for agent shot assembly.
- The about-220-shots figure comes from a search snippet of a Studio blog; treat it as approximate.
- The thresholds for "cluster near rocks" are my guess at the set-dressing rule; they need owner calibration.

## 9. Sources

- [Blender Studio — Sprite Fright](https://studio.blender.org/films/sprite-fright/) (verified, per index)
- [Announcing Sprite Fright](https://studio.blender.org/blog/announcing-sprite-fright-a-horror-comedy) (verified via search, per index)
- [Blender Studio blog: "A big short film" (Andy Goralczyk)](https://studio.blender.org/blog/a-big-short-film-art-director-andy-goralczyk-on-blenders-most-ambitious-movie-yet) (search snippet: 11 min, about 220 shots; unverified page)
- [Sprite Fright production logs](https://studio.blender.org/projects/sprite-fright/production-logs/?page=7) (search snippet: Cycles X; unverified page)
- Local production files: `~/newblender-data/extracted/sprite_fright_030_0020_A/` (CC-BY, from `download.blender.org/demo/sprite_fright_030_0020_A.zip`) and census JSONs in `~/newblender-data/census/`
- [`docs/discovery/s01-modeling/02-census.md`](../discovery/s01-modeling/02-census.md); [ledger](../discovery/ledger.md) L-003, L-004, L-006, L-009; [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: `tools/live/bl.py`, `tools/live/snap.py`, `tools/live/demos/chair_build.py`
