# 16 — Internet-scale product visualisation: how an agent could make it

| | |
|---|---|
| **Original** | LiveLink Technology (Jamie Robert Brown, Head of Content), 2014–2022, product rendering / e-commerce at scale · [Blender Conference 2022 talk](https://conference.blender.org/2022/presentations/1337/) |
| **Agent-readiness today** | **Today.** The Blender half of this work is already a Python batch job: load a template, swap an image, set a variant, render, write a file. Nothing in it needs Edit Mode, selection or a mouse. The hard parts are service engineering (latency, queueing, colour accuracy), not human-shaped Blender. |
| **Difficulty** | **3** for a production service (many product templates, ~10 s latency, colour-managed output, a million images). The Blender core alone is a 1–2. |
| **First slice** | A "customise your mug" pipeline: one parametric mug template plus 12 user designs gives 12 × 3 colourway × 2 camera = 72 renders, made headless in a batch, each with a JSON sidecar and checks, and a contact sheet that appears in the live Blender window. |

## 1. What the original actually is

- **A render-on-demand system, not a picture.** Shoppers customise a product (upload a photo, pick a frame) and get a photoreal preview back in as little as about ten seconds.
- **Product range** (from the talk abstract): canvases, wooden frames, corkboards, mugs, water bottles, laser-etched glass, fully printed apparel.
- **Clients:** Walmart, ASDA, Costco, Jessops.
- **Output:** "around a million images", starting on Blender 2.74, over eight years.
- **What is not public:** the talk abstract gives no detail on the farm, the queue, the per-image render settings or the template format. Anything below about *how* they did it is **interpretation**, marked as such.

Deliverables, then, are three things: (a) a library of product templates (one per SKU family), (b) a variant engine that maps an order (image + options) onto a template, and (c) a render service with a latency budget.

## 2. How the humans made it

| Stage | What it needs | Fact or interpretation |
|---|---|---|
| S01 Modeling | One accurate model per product family (mug, bottle, frame profiles). Real dimensions matter, because a print area in mm must map to the model. | Products listed in the abstract are fact; the modelling method is interpretation. |
| S02 UV & texturing | **Print-area UVs.** The user's image must land on a known UV island (mug wrap, canvas front, frame inset) without stretch. The abstract names "decal and print placement" in the index entry. | Interpretation from the product types. |
| S03 Shading | Physically based materials: glazed ceramic, glass with etch masks, canvas weave, fabric. Image-texture slots are the variable inputs. | Interpretation. |
| S09 Lighting & rendering | Automated Cycles rendering, fixed lighting rigs and cameras per product, driven by Python. | Index entry (Techniques); "ten seconds" is from the talk abstract. |

The human labour concentrates in building and tuning each **template** once. After that, the per-image work is the machine's. This is why the item is the most automation-native one in the showcase: the original team had already made Blender into infrastructure.

## 3. How I would make it: the agent-native plan

| Stage | Agent approach | Inputs (free) | Tooling |
|---|---|---|---|
| S01 Modeling | **Parametric template as data.** A mug is a lathe profile (list of (r, z) points) turned into a mesh with `bmesh.ops.spin`, plus a handle swept along a curve. Dimensions come from a spec dict (height 95 mm, Ø 82 mm). Smoothness is a declared Subdivision modifier ([L-006](../discovery/ledger.md)). | Real catalogue dimensions for a standard 11 oz mug | live bridge `tools/live/bl.py` for authoring; headless `blender -b` for the batch |
| S02 UV & texturing | **Print area as a named UV island.** The wrap band gets its own UV map `UV-print` (cylindrical unwrap computed analytically from the lathe angle, not via `uv.unwrap`, which needs edit mode and selection: [L-001](../discovery/ledger.md), [L-002](../discovery/ledger.md)). The design image is a single Image Texture node on that map. | User designs: CC0 images from Poly Haven / public-domain art | bmesh UV layer written per loop |
| S03 Shading | Principled BSDF glaze; design mixed over the base colour by a print-mask attribute; colourways are a small parameter table (body, inner, handle). | Poly Haven HDRIs (CC0) | Shader nodes built as data |
| S09 Lighting & render | One studio rig per product (HDRI + softbox area lights + shadow catcher plane); 2 cameras (hero ¾, front). Render with Cycles at low samples + OpenImageDenoise, or EEVEE for previews. | — | headless Cycles/EEVEE, one `.blend` template opened per worker |
| Batch | **Order → render job.** A JSON order `{sku, design, colourway, camera}` becomes: open template (or reuse a warm process), set image path, set three colour values, set camera, render, write PNG + sidecar JSON (inputs, hashes, timings, checks). | — | a Python driver outside Blender spawning N warm `blender -b` workers |

**Build order**

1. Write the spec and checks first (section 5), as `checks/mug_checks.py` next to the chair checks.
2. Build the mug template live through the bridge: lathe body, handle, `UV-print` map, materials, studio rig, 2 cameras. Save as `mug_template.blend`.
3. Write `batch_render.py`: reads `orders.jsonl`, keeps one Blender process warm per worker, applies each order, renders, writes sidecars. No operators except `render.render`.
4. Run 72 orders headless. Measure time per image.
5. Run the checks over every output; build a contact sheet (a tiled image) and show it in the live window's Image Editor via the bridge.
6. Scale step (not day one): a second template (water bottle) to prove the template contract generalises; then a queue (one job file per order) and warm workers to approach the 10 s target.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:** everything in the first slice. Geometry as data (proven by the chair demo, `~/newblender-data/demos/001-chair/report.md`), material and image swaps via RNA, camera switches, `render.render(write_still=True)` headless. Measured while writing this file on Blender 5.2.2 (M-series Mac, factory scene, 512 × 512): **EEVEE 0.29 s, Cycles 64 spp GPU 0.60 s** per frame. A real product at 1024 px with glass will be slower, but the ten-second budget is within reach without a farm.
- **Painful today:**
  - **Startup cost.** A cold `blender -b` boots the default scene and add-ons before loading the template ([L-011](../discovery/ledger.md)). At 10 s latency this overhead matters, so workers must stay warm and receive jobs over a socket (exactly what the bridge already does for one interactive session).
  - **No result object.** `render.render` returns `{'FINISHED'}`, not the image or the stats; the driver must read the file back and time it itself ([L-003](../discovery/ledger.md)).
  - **UV unwrap is an edit-mode operator.** For print areas we sidestep it by computing UVs analytically; for arbitrary products (apparel) a headless, selection-free unwrap is needed ([L-001](../discovery/ledger.md), [L-002](../discovery/ledger.md)).
- **Not feasible today:** nothing in the Blender core. Out of scope for a day: colour-proof matching to a physical print (needs a calibrated photo of the real product), and apparel with cloth drape per size, which pushes into S08.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Template mesh manifold, no loose verts, no degenerate faces, normals outward | 0 / 0 / 0 / 0 |
| 1 Validity | Every render file exists, decodes, and has the requested size | 72 / 72, exactly 1024 × 1024 |
| 2 Spec | Mug dimensions from the evaluated mesh | height 95 ± 1 mm, outer Ø 82 ± 1 mm |
| 2 Spec | `UV-print` island bounds and stretch | inside [0,1]²; area-weighted UV/3D ratio varies < 2% across the band |
| 2 Spec | Every order produced exactly one image + one sidecar with matching input hash | 72 / 72 |
| 2 Spec | Latency per image (warm worker, Cycles, 1024 px) | median ≤ 10 s, p95 ≤ 15 s |
| 3 Reference | **Print placement:** render a calibration design (a grid with 4 coloured corner markers) and locate the markers in the output | each marker within 4 px of its predicted projected position |
| 3 Reference | Determinism: the same order rendered twice | per-pixel mean abs diff < 0.5 / 255 (Cycles seed fixed) |
| 4 Downstream | Web delivery: sRGB PNG/JPEG, correct colour-space tag, size | file ≤ 400 KB at 1024 px JPEG q85; colour space = sRGB |
| 4 Downstream | Colourway fidelity: sample the body colour in a flat lit patch | ΔE2000 ≤ 3 against the spec colour under the reference rig |
| 5 Appearance (warning) | Vision model compares each render with the brief ("design wrapped on the mug, handle visible, no clipping, no black frames") | warn if any image is flagged |
| 6 Taste (owner) | Owner reviews the contact sheet: lighting mood, angle, whether it sells the product | owner yes/no on the 2 camera presets, before scaling |

## 6. Where the human is still needed

- **The look of the template.** Choosing the lighting mood, the camera angles and how "premium" the ceramic reads is art direction, done once per product family. After that, the agent can hold it constant across a million images.
- **Colour sign-off against the physical product.** Only someone with the real mug in hand can say the preview matches. The agent can measure ΔE against a target, but the target comes from a human (or a calibrated photo).
- **Business rules:** which variants exist, what counts as an acceptable preview, what happens with bad uploads (low resolution, transparency).

## 7. Effort

- **First slice (live demo, ~1 day):**
  - Morning: the mug template appears in the live Blender window, built step by step through the bridge (body, handle, studio rig). The viewport switches to Material Preview so the owner sees the ceramic and a placeholder design.
  - Afternoon: a headless batch renders 72 images in the background (~1–3 minutes total at the measured speeds). The checks run, then a 9 × 8 contact sheet and a check report (`report.md`, like the chair's) open in the live window's Image Editor. `snap.py` captures the screen for the record.
- **Full reproduction:** ~10 product templates at ~3–5 agent-hours each, a queue + warm-worker service (~2–3 agent-days), colour calibration with the owner (~1 human-day per product family). Compute: at ~5 s per Cycles image, a million images is ~1,400 GPU-hours, spread over years of real orders.

## 8. Risks and unknowns

- **We have no access to LiveLink's actual system;** the plan reproduces the result, not their architecture.
- **Glass and etched glass are slow and noisy** in Cycles; the 10 s target may need EEVEE or pre-baked lighting for those SKUs.
- **Warm-worker memory leaks** over thousands of renders in one process are untested; workers may need recycling every N jobs.
- **Untrusted uploads:** user images must be validated and decoded outside Blender before they are loaded.
- **GPU nondeterminism** may break the strict determinism threshold; fall back to a perceptual tolerance if so.

## 9. Sources

- [Blender Conference 2022: Internet-scale product visualization and customization](https://conference.blender.org/2022/presentations/1337/) (verified: a million images since 2.74, product list, clients via the index)
- [00-index.md § 16](00-index.md)
- [RFC 0001 § R6 Verification model](../rfc/0001-newblender.md)
- [Transformation ledger L-001…L-011](../discovery/ledger.md)
- Live bridge and chair demo: `tools/live/bl.py`, `tools/live/demos/chair_build.py`, `tools/live/checks/chair_checks.py`, `~/newblender-data/demos/001-chair/report.md`
- Render timings: headless probe on Blender 5.2.2 LTS, run while writing this file (factory scene, 512 px).
- [Poly Haven](https://polyhaven.com/) (CC0 HDRIs and textures)
