# Blender showcase: 20 works people made

Compiled 2026-10-07. This is a list of 20 works made mostly by hand in Blender. They cover the whole range of the tool rather than 20 short films: feature films, open movies, indie VFX, blockbuster VFX, 2D-in-3D Grease Pencil, a TV series, immersive motion graphics, Geometry Nodes art, scientific visualisation, architectural visualisation, product rendering at scale, hard-surface work, character sculpting, a game and fluid simulation. Most date from 2019 to 2026, and each has at least one primary or reputable trade source.

Each item has its own plan file, named `NN-slug.md` in this folder.

**Built so far (first slices, live in Blender 5.2):**

| # | Slice | Checks | Blind quality (agent vs. studio) | Report |
|---|---|---|---|---|
| 01 | Flow: flooded-forest boat shot, 4K | 11/11, plus layers 3–4 pass | 1.00 vs. 3.75 | [002-flow](../demos/002-flow/report.md) |
| 03 | Charge: battery-factory bay | 11/11 live; UV-stretch and firefly fails await owner rulings | 2.33 vs. 4.50 | [003-charge](../demos/003-charge/report.md) |

**How sources are marked:**

- **verified** means the page was fetched or returned by search during this research, and it supports the facts stated.
- **unverified** means the link or fact comes from memory or from a search snippet I couldn't fetch. Check it before you rely on it.

**Pipeline stages:** S01 Modeling · S02 UV & texturing · S03 Shading · S04 Geometry Nodes · S05 Rigging · S06 Layout · S07 Animation · S08 Simulation & FX · S09 Lighting & rendering · S10 Compositing · S11 Editing · S12 Grease Pencil

## Summary

| # | Title | Creator | Year | Category | Stages |
|---|---|---|---|---|---|
| 01 | Flow | Gints Zilbalodis / Dream Well Studio (+ co-producers) | 2024 | Feature film (Oscar 2025) | S01 S04 S05 S06 S07 S08 S09 |
| 02 | Sprite Fright | Blender Studio (dir. Matthew Luhn, co-dir. Hjalti Hjálmarsson) | 2021 | Open movie: stylised character animation | S01 S02 S03 S04 S05 S07 S08 S09 |
| 03 | Charge | Blender Studio (dir. Hjalti Hjálmarsson) | 2022 | Open movie: photoreal action | S01 S02 S03 S04 S05 S07 S08 S09 S10 |
| 04 | Singularity | Blender Studio (dir. Andy Goralczyk) | 2026 | Open movie: painterly NPR | S03 S04 S06 S07 S09 S10 |
| 05 | Dynamo Dream | Ian Hubert | 2021– | Indie sci-fi VFX short series | S01 S02 S03 S06 S08 S09 S10 S11 |
| 06 | RRR (Blender VFX shots) | Makuta Visual Effects | 2022 | Blockbuster feature VFX | S01 S03 S04 S08 S09 |
| 07 | Unicorn Wars | Alberto Vázquez (dir.); Blender pipeline by ADV Studios | 2022 | 2D-in-3D animated feature | S06 S07 S09 S12 |
| 08 | Blender 4.0 splash illustration | Gaku Tada | 2023 | NPR watercolour illustration | S01 S03 S09 S12 |
| 09 | Il Baracchino | Megadrago (Nicolò Cuccì, Salvo Di Paola) / Lucky Red | 2025 | TV series (adult animation) | S04 S05 S07 S09 S11 S12 |
| 10 | Sinking Feeling | Blue Zoo Animation Studio | 2021 | Studio short / charity campaign | S05 S06 S07 S09 |
| 11 | Nashville International Airport Grand Lobby | Gentilhomme | 2023 | Immersive motion graphics / large-format LED | S03 S04 S09 S10 |
| 12 | Procedural Still Life (Blender 2.93 splash) | Erindale Woodford | 2021 | Geometry Nodes procedural art | S01 S03 S04 S09 |
| 13 | Molecular Nodes | Brady Johnston | 2022– | Scientific visualisation tool | S03 S04 S07 S09 |
| 14 | The Junk Shop (Blender 2.81 splash) | Alex Treviño | 2019 | Stylised environment / community landmark | S01 S02 S03 S06 S09 |
| 15 | Park Lipence | Polygoniq | 2021 | Architectural visualisation / landscape | S01 S03 S04 S06 S09 |
| 16 | Internet-scale product visualisation | LiveLink Technology | 2014–2022 | Product rendering at scale | S02 S03 S09 |
| 17 | Bismuth Security Mech | Kevin Skok | 2019 | Hard-surface / mechanical | S01 S02 S03 S08 S09 |
| 18 | Amber Bust | RoseRedTiger | 2020 | Character sculpting | S01 S03 S09 |
| 19 | DOGWALK | Blender Studio | 2025 | Game development (Blender + Godot) | S01 S02 S03 S05 S07 |
| 20 | FLIP Fluids 2021 Customer Reel | FLIP Fluids devs (Ryan & Dennis) + community artists | 2022 | Fluid simulation showcase | S08 S09 S10 |

---

## 01 · `01-flow.md` — Flow

- **Creator(s):** Gints Zilbalodis (director). Latvian/French/Belgian co-production, with Dream Well Studio as the Latvian lead (*the studio name is unverified*).
- **Year:** 2024. Won the Oscar for Best Animated Feature at the 97th Academy Awards in 2025.
- **Category:** Feature film
- **What it is:** A dialogue-free animated feature about a cat that survives a world-ending flood with a boat full of other animals. It was made entirely in Blender and rendered in EEVEE, with no render farm.
- **Why it's amazing:** It is the first Oscar-winning feature made fully in free, open-source software, by a team that rarely had more than five people working at once.
- **Techniques:** EEVEE final render, with frames taking 0.5–10 s each in 4K on the director's PC. There was no compositing; grading was done in the shaders. Water combined large waves from Cell Fluids with FLIP Fluids detail, plus a custom water add-on by Mārtiņš Upītis. Also Geometry Nodes, GeoScatter, custom rigs, and long continuous camera moves animated with Animation Layers. Production ran on Blender 2.8 → 3.6.
- **Stages:** S01, S04, S05, S06, S07, S08, S09
- **Scale:** Small team, about 15–20 people in total with 3–5 working at any time. About 5.5 years (2019–2024).
- **Sources:**
  - [Making Flow — blender.org user story](https://www.blender.org/user-stories/making-flow-an-interview-with-director-gints-zilbalodis/) (verified)

## 02 · `02-sprite-fright.md` — Sprite Fright

- **Creator(s):** Blender Studio. Written and directed by Matthew Luhn (ex-Pixar story supervisor) and co-directed by Hjalti Hjálmarsson.
- **Year:** 2021. Premiered on 29 October 2021.
- **Category:** Blender Studio open movie, stylised character animation
- **What it is:** An '80s-inspired horror comedy in which rowdy teenagers trek into a British forest and meet mushroom sprites that turn out to be a force of nature. It is Blender Studio's 13th open movie, and all production files are released under Creative Commons.
- **Why it's amazing:** It is a polished, Pixar-flavoured comedy whose whole production (facial rigs, set dressing, Geometry Nodes moss scattering) is open for anyone to study.
- **Techniques:** Character sculpting, facial rigging, Geometry Nodes environment and moss scattering, set dressing, fire FX, and pipeline and asset-management tooling (a key production goal). Rendered in Cycles.
- **Stages:** S01, S02, S03, S04, S05, S07, S08, S09
- **Scale:** In-house studio team, roughly a year of production.
- **Sources:**
  - [Blender Studio — Sprite Fright](https://studio.blender.org/films/sprite-fright/) (verified)
  - [Announcing Sprite Fright](https://studio.blender.org/blog/announcing-sprite-fright-a-horror-comedy) (verified via search)

## 03 · `03-charge.md` — Charge

- **Creator(s):** Blender Studio. Directed by Hjalti Hjálmarsson, with Andy Goralczyk as art director and Rik Schutte as lead animator.
- **Year:** 2022
- **Category:** Blender Studio open movie, photoreal action
- **What it is:** A 3-minute action short in which an old man in an energy-starved dystopia breaks into a battery factory and is hunted by a security droid. It was inspired by game cinematics and real-time demos, and aimed for realism.
- **Why it's amazing:** It pushed Blender toward a realistic digital human (Einar) and a hard-surface robot in heavy action, and it released the material library and shot files.
- **Techniques:** Layered sculpting for a realistic human (Einar), the new curves hair system, hard-surface modelling of the droid and factory, PBR shading, Geometry Nodes FX for smoke, fire and muzzle flashes, rigging, combat animation, and both Cycles and EEVEE.
- **Stages:** S01, S02, S03, S04, S05, S07, S08, S09, S10
- **Scale:** In-house studio team, about 1 year (it began as "Project Heist").
- **Sources:**
  - [Blender Studio — Charge](https://studio.blender.org/films/charge/) (verified)
  - [befores & afters: how Blender Studio's realistic-human film was made](https://beforesandafters.com/2023/03/13/how-blender-studios-latest-film-with-a-realistic-human-character-was-made/) (unverified, search result only)
  - [Layered sculpting for Einar](https://studio.blender.org/blog/layered-sculpting-for-einar) (unverified, search result only)

## 04 · `04-singularity.md` — Singularity

- **Creator(s):** Blender Studio. Directed by Andy Goralczyk, with Vivien Lulkowski as art director.
- **Year:** 2026 (released May 2026)
- **Category:** Blender Studio open movie, painterly NPR
- **What it is:** A painterly, watercolour-inspired space adventure about a small creature whose home is destroyed by a black hole, set when the universe was young. It is Blender Studio's first 4K HDR film, and its assets are released under CC-BY.
- **Why it's amazing:** It mixes hand-made brushstroke textures with generative, Geometry Nodes-driven effects to get a moving watercolour look in 3D.
- **Techniques:** Brushstroke Tools add-on (painterly strokes), Geometry Nodes procedural crowd and instancing systems, NPR shading, a 4K HDR pipeline, and an in-development build of Blender.
- **Stages:** S03, S04, S06, S07, S09, S10
- **Scale:** In-house studio team (*the duration is unverified*).
- **Sources:**
  - [Blender Studio — Singularity](https://studio.blender.org/films/singularity/) (verified via search)
  - [Digital Production: Blender Singularity lands in 4K HDR (2026-05-15)](https://digitalproduction.com/2026/05/15/blender-singularity-lands-in-4k-hdr/) (verified)

## 05 · `05-dynamo-dream.md` — Dynamo Dream

- **Creator(s):** Ian Hubert, with help from friends
- **Year:** 2021 onward. Episode 1 "Salad Mug" came out in May 2021, followed by "A Single Point in Space", "A Pete Episode" and "Prepare for Execution".
- **Category:** Indie live-action and CG sci-fi VFX series
- **What it is:** A live-action sci-fi series set in a dense cyberpunk city, with nearly every environment built in Blender and composited around actors shot on a tiny budget. Episode 1 alone took about three years of mostly solo work.
- **Why it's amazing:** One artist reached world-building on the scale of a feature film. His "lazy" kitbash, photo-texture and camera-projection tricks became a whole teaching genre.
- **Techniques:** Rapid kitbash modelling, photo-projected textures, camera tracking, green-screen keying and compositing in Blender, Cycles, and editing.
- **Stages:** S01, S02, S03, S06, S08, S09, S10, S11
- **Scale:** Essentially solo, about 3 years for episode 1.
- **Sources:**
  - [BlenderNation: first episode of Ian Hubert's Dynamo Dream is out](https://www.blendernation.com/2021/05/26/first-episode-of-ian-huberts-dynamo-dream-is-out/) (verified via search)
  - [Core77: cityscape VFX split-screen](https://core77.com/posts/100290/A-Bad-Ass-Food-Truck-and-a-Cyberpunk-City-VFX-Split-Screen-Sequence) (unverified, search result only)

## 06 · `06-rrr-makuta-vfx.md` — RRR (Blender VFX by Makuta)

- **Creator(s):** Makuta Visual Effects, Hyderabad (CEO Pete Draper)
- **Year:** 2022 (the studio moved to Blender in November 2019)
- **Category:** Blockbuster feature VFX
- **What it is:** Makuta delivered about 700 shots for S. S. Rajamouli's RRR on Blender 2.83–2.92. These included the palace exteriors in the Komaram Bheem song, the intermission fight environments and crowds, and the military compound and forest scenes.
- **Why it's amazing:** It is one of the largest documented uses of Blender and Cycles on a global box-office hit, from asset building to final render.
- **Techniques:** Asset modelling, LiDAR processing, Geometry Nodes for distribution and material randomisation, volumetrics for explosions and gunfire atmosphere, and Cycles. Some FX stayed in 3ds Max.
- **Stages:** S01, S03, S04, S08, S09
- **Scale:** Large studio team, about 2.5 years.
- **Sources:**
  - [Visual Effects for the Indian blockbuster "RRR" — blender.org user story](https://www.blender.org/user-stories/visual-effects-for-the-indian-blockbuster-rrr/) (verified)

## 07 · `07-unicorn-wars.md` — Unicorn Wars

- **Creator(s):** Alberto Vázquez (writer and director). BlenderNation credits the Blender tools and pipeline to ADV Studios (technical supervisors Christophe Seux and Samuel Bernou). The Spanish-French co-producers are listed on Wikipedia (*names not checked*).
- **Year:** 2022. Won the Goya for Best Animated Film in 2023.
- **Category:** 2D-in-3D animated feature (Grease Pencil)
- **What it is:** An adult war fable ("Bambi meets Apocalypse Now") about teddy-bear soldiers marching into a unicorn forest. Everything except the unicorns was drawn with Grease Pencil inside Blender. The unicorns were animated in 3D and traced to 2D with custom tools.
- **Why it's amazing:** It is a Grease Pencil-centric feature that won a major national film award, made by a relatively small team.
- **Techniques:** Grease Pencil drawing and animation, a background plane manager, GP Tracer (3D to editable 2D lines), an auto-walk tool, and 2D/3D layout.
- **Stages:** S06, S07, S09, S12
- **Scale:** Small-to-mid studio teams (*duration unverified*).
- **Sources:**
  - [BlenderNation: Unicorn Wars, made with Blender](https://www.blendernation.com/2023/01/06/unicorn-wars-made-with-blender-animated-feature-now-in-french-cinemas/) (verified)
  - [Wikipedia: Unicorn Wars](https://en.wikipedia.org/wiki/Unicorn_Wars) (verified via search)

## 08 · `08-gaku-tada-splash.md` — Blender 4.0 splash illustration

- **Creator(s):** Gaku Tada, visual artist and art director
- **Year:** 2023 (Blender 4.0, released 7 Nov 2023)
- **Category:** Stylised NPR / Grease Pencil illustration
- **What it is:** A painterly 3D illustration in Gaku Tada's signature watercolour style, chosen as the Blender 4.0 splash. It is described as mixing Grease Pencil strokes with 3D geometry. *Correction (headless inspection of the published file, 2026-10-07): the distributed splash .blend has no Grease Pencil objects. Outlines are 46 Solidify + Displace inverted hulls, and the trees and vines come from Gaku Tada's Deep Paint GN generators. See [08](08-gaku-tada-splash.md).*
- **Why it's amazing:** Gaku Tada is one of the pioneers of the hybrid Grease Pencil + 3D watercolour look, which makes 3D read as a hand-painted page.
- **Techniques:** Grease Pencil strokes and fills, NPR shading, painterly textures, and EEVEE.
- **Stages:** S01, S03, S09, S12
- **Scale:** Solo (*time unknown*).
- **Sources:**
  - [80.lv: Blender 4.0 to feature Gaku Tada's illustration](https://80.lv/articles/blender-4-0-to-feature-gaku-tada-s-illustration-on-its-splash-screen/) (verified)
  - [BlenderNation: Gaku Tada Grease Pencil reel 2022](https://www.blendernation.com/2022/08/17/gaku-tada-grease-pencil-blender-reel-2022/) (unverified, search result only)

## 09 · `09-il-baracchino.md` — Il Baracchino

- **Creator(s):** Megadrago studio, Palermo (creators and directors Nicolò Cuccì and Salvo Di Paola), produced with Lucky Red. It is an Amazon Prime Video original.
- **Year:** 2025 (Prime Video, 3 June 2025). Presented at Blender Conference 2025.
- **Category:** TV series, adult animated comedy
- **What it is:** Italy's first adult animated series made in Blender: six episodes (about 100 minutes) about an art director trying to save a failing comedy club. It mixes 3D, stop-motion-style puppetry, paper cut-outs and 2D in one look.
- **Why it's amazing:** A team of about 20 shipped a streaming series that fakes stop-motion and paper cut-outs in Blender, using clever rigs instead of brute force.
- **Techniques:** UV Warp modifiers for cut-out animation, Geometry Nodes procedural rigging (Leonardo's mouth), Rigify with bendy bones and shape keys, Grease Pencil storyboards and previz, EEVEE NPR, and the Video Sequence Editor for editorial. Made on Blender 3.6 LTS.
- **Stages:** S04, S05, S07, S09, S11, S12
- **Scale:** About 20 people (*duration unverified*).
- **Sources:**
  - [Creating "Il Baracchino" — blender.org user story](https://www.blender.org/user-stories/creating-il-baracchino-italys-first-adult-animated-series-made-with-blender/) (verified)
  - [Wikipedia: Il Baracchino](https://en.wikipedia.org/wiki/Il_Baracchino) (verified via search)

## 10 · `10-sinking-feeling.md` — Sinking Feeling

- **Creator(s):** Blue Zoo Animation Studio, London, for the charity PAPYRUS UK
- **Year:** 2021 (launched on World Suicide Prevention Day)
- **Category:** Studio short / charity campaign
- **What it is:** An animated short of about 80 seconds about loneliness and peer support, made to promote a youth-suicide-prevention charity. It was Blue Zoo's first full film production in Blender, made with a big remote crew.
- **Why it's amazing:** It is an early proof that a large commercial studio could move about 30 artists (18 animators) onto Blender and get a grainy, illustrated EEVEE look.
- **Techniques:** Character rigs and animation at studio scale, EEVEE stylised rendering with grain, and remote collaboration via Tangent Lab's LoUPE. *(EEVEE and LoUPE are not mentioned in the fetched blender.org story; unverified. See [10](10-sinking-feeling.md).)*
- **Stages:** S05, S06, S07, S09
- **Scale:** About 30 artists, made in paid overtime.
- **Sources:**
  - [BlenderNation: how Blue Zoo used Blender to create Sinking Feeling](https://www.blendernation.com/2021/12/22/how-blue-zoo-animation-studio-used-blender-to-create-sinking-feeling/) (verified via search)
  - [80.lv: using Blender to make a short film for charity](https://80.lv/articles/using-blender-to-make-a-short-film-for-charity) (unverified, search result only)

## 11 · `11-nashville-airport-lobby.md` — Nashville International Airport Grand Lobby content

- **Creator(s):** Gentilhomme, Montreal (CG supervisor Arnaud Mellinger, with Maxime Roux, Miriam Diana Pelletier, Eddie Loukil and Étienne Garon-Vincent)
- **Year:** 2023
- **Category:** Immersive motion graphics / large-format LED installation
- **What it is:** Over 40 minutes of content in 13 segments for two 21 m × 4.5 m LED walls (11,200 × 2,160 px) in Nashville airport's Grand Lobby. The six pure-CGI "capsules" are about distilleries, country music and Broadway neon.
- **Why it's amazing:** It is abstract and figurative motion design at architectural scale, driven by Geometry Nodes and rendered at enormous resolution on a 20-machine farm.
- **Techniques:** Geometry Nodes grid distributions and texture-driven displacement, emissive and refractive Cycles shading, 16/32-bit multipass EXR, scripted rendering and denoising, and assets brought in from Maya and Houdini.
- **Stages:** S03, S04, S09, S10
- **Scale:** Small studio team. Renders took full nights to several days per capsule.
- **Sources:**
  - [Behind the Scenes: Nashville International Airport — blender.org user story](https://www.blender.org/user-stories/behind-the-scenes-nashville-international-airport/) (verified)

## 12 · `12-procedural-still-life.md` — Procedural Still Life (Blender 2.93 splash)

- **Creator(s):** Erindale Woodford
- **Year:** 2021 (Blender 2.93 LTS)
- **Category:** Geometry Nodes procedural art
- **What it is:** A sunlit potting-shed workbench with ornate vessels and flowers ready for arranging, with every element generated by Geometry Nodes. Erindale followed it with a "Geometry Nodes Flower Shop" (2022, Blender 3.0) built in a single node tree.
- **Why it's amazing:** It became the poster image for what Geometry Nodes could do in its first release. Erindale is now a leading Geometry Nodes educator.
- **Techniques:** Procedural modelling with Geometry Nodes (instancing, curves, distribution), procedural shading, and Cycles.
- **Stages:** S01, S03, S04, S09
- **Scale:** Solo (*time unknown*).
- **Sources:**
  - [BlenderNation: Blender 2.93 LTS splash screen revealed](https://www.blendernation.com/2021/04/15/blender-2-93-lts-splash-screen-revealed/) (verified via search)
  - [BlenderNation: Geometry Nodes Flower Shop](https://www.blendernation.com/headers/geometry-nodes-flower-shop/) (verified)

## 13 · `13-molecular-nodes.md` — Molecular Nodes

- **Creator(s):** Brady Johnston, a structural biologist (University of Western Australia when he started it)
- **Year:** 2022 to present. The add-on is on extensions.blender.org and PyPI, and won a NumFOCUS Small Development Grant in 2024.
- **Category:** Scientific visualisation (structural biology)
- **What it is:** An add-on and toolbox that imports PDB, mmCIF and molecular-dynamics data into Blender and builds molecular representations with Geometry Nodes. Scientists use it to make publication-quality renders and animations of proteins.
- **Why it's amazing:** It is a researcher-built tool that turned Blender into serious molecular-graphics software, used in real labs and at conferences.
- **Techniques:** Geometry Nodes (procedural styles such as cartoon, surface and ball-and-stick), attribute-driven shading, keyframed and trajectory animation, and Cycles/EEVEE.
- **Stages:** S03, S04, S07, S09
- **Scale:** Solo-led open-source project with contributors, ongoing since about 2022.
- **Sources:**
  - [GitHub: BradyAJohnston/MolecularNodes](https://github.com/BradyAJohnston/MolecularNodes) (unverified URL, repo named in search)
  - [MDAnalysis: NumFOCUS grant for MolecularNodes](https://www.mdanalysis.org/2024/12/12/sdg_molecularnodes/) (verified via search)
  - [Blender Extensions: Molecular Nodes](https://extensions.blender.org/add-ons/molecularnodes/) (unverified exact URL)

## 14 · `14-the-junk-shop.md` — The Junk Shop (Blender 2.81 splash)

- **Creator(s):** Alex Treviño. Concept art by Anaïs Maamar (verified on blender.org's demo-files page).
- **Year:** 2019
- **Category:** Stylised interior environment / community landmark
- **What it is:** A cluttered, warmly lit junk shop interior full of props and stylised detail. It was the Blender 2.81 splash, and the .blend was released publicly.
- **Why it's amazing:** It's a masterclass in prop density, set dressing and lighting mood. The scene became a standard reference file (believed to be one of the Blender Open Data benchmark scenes, *unverified*).
- **Techniques:** Prop modelling, UV and texture work, layout and set dressing, Cycles lighting.
- **Stages:** S01, S02, S03, S06, S09
- **Scale:** Solo (*time unknown*).
- **Sources:**
  - [BlenderNation: this is the 2.81 splash](https://www.blendernation.com/2019/11/20/this-is-the-2-81-splash/) (verified)
  - [Blender 2.81 manual: splash screen](https://docs.blender.org/manual/en/2.81/interface/splash.html) (verified via search)

## 15 · `15-park-lipence.md` — Park Lipence

- **Creator(s):** Polygoniq, a Czech studio and add-on vendor
- **Year:** 2021
- **Category:** Architectural visualisation / photoreal landscape
- **What it is:** A photoreal exterior visualisation of a park near Prague, with open lawns, dense vegetation and distinctive park architecture, all rendered in Cycles. It also served as a showcase for the studio's vegetation and asset libraries.
- **Why it's amazing:** It is believable large-scale outdoor archviz with vast foliage, made entirely in Blender.
- **Techniques:** Architectural modelling, vegetation scattering (botaniq), library materials (materialiq) and vehicles (traffiq), photoreal Cycles lighting and rendering.
- **Stages:** S01, S03, S04, S06, S09
- **Scale:** Small studio team (*time unknown*).
- **Sources:**
  - [Blender 3D Architect: Park Lipence in Prague with Blender Cycles](https://www.blender3darchitect.com/architectural-visualization/park-lipence-in-prague-with-blender-cycles/) (verified)
- **Note:** This is a vendor showcase. If a later file needs a "purer" archviz example, swap it for an independent artist's archviz piece.

## 16 · `16-livelink-product-viz.md` — Internet-scale product visualisation

- **Creator(s):** LiveLink Technology (UK). Presented at Blender Conference 2022 by Jamie Robert Brown, Head of Content.
- **Year:** 2014–2022 (8 years, starting on Blender 2.74)
- **Category:** Product rendering / e-commerce at scale
- **What it is:** A Blender-based render-on-demand system that shows shoppers photoreal previews of the product they've customised (canvases, frames, mugs, bottles, etched glass, printed apparel) in as little as about ten seconds. Clients include Walmart, ASDA, Costco and Jessops.
- **Why it's amazing:** It has produced about a million product images, which shows Blender as industrial product-rendering infrastructure rather than just a tool for one-off hero shots.
- **Techniques:** Product modelling and UVs set up for decal and print placement, physically based shading, automated Cycles rendering, and Python-driven pipelines.
- **Stages:** S02, S03, S09
- **Scale:** Company team, over 8 years.
- **Sources:**
  - [Blender Conference 2022: Internet-scale product visualization and customization](https://conference.blender.org/2022/presentations/1337/) (verified)

## 17 · `17-bismuth-security-mech.md` — Bismuth Security Mech

- **Creator(s):** Kevin Skok, a hard-surface artist (S4G School for Games, Berlin)
- **Year:** 2019
- **Category:** Hard-surface / mechanical modelling
- **What it is:** A game-ready security mech designed and modelled in Blender for a final thesis, inspired by Ghost in the Shell and grounded in real mechanical references. It was textured in Substance Painter, with decals and simulated cloth covers.
- **Why it's amazing:** It is a textbook example of believable, functional mech design: blockout, then high-poly support loops, then floating details, then a clean bake.
- **Techniques:** Blockout-driven design, support-loop subdivision modelling, floating geometry with Shrinkwrap and vertex groups, high-to-low normal baking, and cloth simulation for ammo covers (Marvelous Designer). Textured externally in Substance Painter.
- **Stages:** S01, S02, S03, S08, S09
- **Scale:** Solo student thesis (*time unknown*).
- **Sources:**
  - [80.lv: 001AGT — tips for mech design in Blender](https://80.lv/articles/001agt-tips-for-mech-design-in-blender) (verified)

## 18 · `18-amber-bust.md` — Amber Bust

- **Creator(s):** RoseRedTiger (Rose)
- **Year:** 2020
- **Category:** Character sculpting (stylised)
- **What it is:** A stylised character bust sculpted, painted and rendered entirely in Blender. It used dynamic topology for flowing hair curls and was painted with sculpt-mode vertex colours, a new feature in the 2.91 alpha.
- **Why it's amazing:** It is a clean, all-Blender sculpt-to-render character with no external texturing app. Everything lives in the sculpt and vertex colours.
- **Techniques:** Snake Hook, Clay Strips, Crease and Smooth brushes, dynamic topology, remesh, mask extract and Solidify, sculpt-mode vertex painting, subsurface scattering in the Principled BSDF, and EEVEE with three-point and HDRI lighting.
- **Stages:** S01, S03, S09
- **Scale:** Solo (*time unknown*).
- **Sources:**
  - [BlenderNation: Behind the Scenes — Amber Bust](https://www.blendernation.com/2020/10/07/behind-the-scenes-amber-bust/) (verified)
- **Alternate if a photoreal sculpt is wanted:** Plea Ruffin's photoreal character renders ([80.lv, 2024](https://80.lv/articles/awesome-photorealistic-character-renders-in-blender), verified), or Charge's Einar (see 03).

## 19 · `19-dogwalk.md` — DOGWALK

- **Creator(s):** Blender Studio
- **Year:** 2025 (released 11 July 2025, free on blender.org and Steam)
- **Category:** Game development (Blender to Godot)
- **What it is:** A short, cosy winter game in which you play Chocomel, a big dog, helping the kid Pinda find decorations for a snowman. All assets and animation were made in Blender and the gameplay runs in Godot, built as an open project.
- **Why it's amazing:** It is a fully open-source game pipeline made in public, and the asset library and source code are available to study.
- **Techniques:** Game-ready modelling, UVs and texturing, stylised real-time materials, rigging and animation exported to Godot.
- **Stages:** S01, S02, S03, S05, S07
- **Scale:** In-house studio team (*duration unverified*).
- **Sources:**
  - [blender.org: DOGWALK — Open Game by Blender Studio](https://blender.org/projects/dogwalk/) (verified)
  - [GamingOnLinux: DOGWALK out now](https://www.gamingonlinux.com/2025/07/dogwalk-is-a-free-casual-game-from-the-blender-studio-out-now) (verified via search)

## 20 · `20-flip-fluids-reel.md` — FLIP Fluids 2021 Customer Reel

- **Creator(s):** FLIP Fluids add-on developers (Ryan and Dennis) and many Blender artists worldwide
- **Year:** 2022 (published; it collects work submitted April–November 2021)
- **Category:** Simulation / FX showcase
- **What it is:** A collaborative reel of liquid-simulation shots made in Blender with the FLIP Fluids add-on, showing whitewater, viscous fluids and surface tension. It is the second of the yearly community reels; the first was in 2020.
- **Why it's amazing:** It shows production-grade liquid FX done inside Blender. The same add-on supplied the detail water in Flow (see 01).
- **Techniques:** FLIP liquid simulation, whitewater particles (foam, bubble, spray), viscosity and surface tension, meshing, Cycles rendering, compositing.
- **Stages:** S08, S09, S10
- **Scale:** Many solo artists' shots compiled by a two-person dev team.
- **Sources:**
  - [BlenderNation: FLIP Fluids Add-on 2021 Customer Reel](https://www.blendernation.com/2022/02/10/flip-fluids-add-on-2021-customer-reel/) (verified)
- **Note:** This is a compilation, not one authored piece. Swap it if a single simulation-led work is needed.

---

## Honourable mentions (verified, not in the 20)

- **Cosmology with Geometry Nodes** — MohammadHossein Jamshidi (2024). HEALPix CMB maps, lensing and spherical harmonics built in Geometry Nodes. [blender.org user story](https://www.blender.org/user-stories/cosmology-with-geometry-nodes/) (verified). A strong alternative for scientific or data visualisation.
- **Rabbids Invasion: Mission to Mars** — Ubisoft Animation Studio with Supamonks (2020–21). A 70-minute TV special that produced the Shot Manager and Mixer add-ons. [blender.org user story](https://www.blender.org/user-stories/blender-and-the-rabbids/) (verified)
- **Spider-Man: Across the Spider-Verse** (2023). Grease Pencil was used for 2D line effects, converted to geometry and sent to Maya. [BlenderNation](https://www.blendernation.com/2023/06/11/blender-used-in-across-the-spiderverse/) (verified)
- **Wolfwalkers** — Cartoon Saloon (2020). [blender.org user story](https://www.blender.org/user-stories/2d-isnt-dead-it-just-became-something-different-using-blender-for-wolfwalkers/) (listed, not fetched)
- **Khara / Evangelion: 3.0+1.0** — the anime studio announced in 2019 that it was switching to Blender. [Anime News Network](https://m.animenewsnetwork.com/news/2019-08-18/khara-to-completely-switch-to-blender-open-source-3d-software-after-evangelion-3.0-1.0/.150173) (verified via search)
- **Hero** — Blender Studio (2018). The Grease Pencil 2.0 showcase directed by Daniel Martínez Lara. [Blender Studio](https://studio.blender.org/films/hero/) (verified via search)
- **Spring** (2019) and **Cosmos Laundromat** (2015) — older Blender Studio open movies, left out in favour of 2021–2026 titles.

---

## How I would make each one (agent-readiness summary)

Each work has a companion file `NN-slug.md` that follows [`_template.md`](_template.md): decomposition, the human pipeline, an agent-native plan, what works today vs. what needs newblender (ledger IDs), a six-layer verification plan (RFC 0001 R6), where the human is still needed, effort, risks and sources.

Readiness: **Today** = the live bridge can do it now · **Partial** = some parts need tooling or a farm · **Taste-bound** = the mechanics work; the hard part is human judgement.

| # | Work | Readiness | Difficulty | First slice (buildable live in about a day) |
|---|---|---|---|---|
| 01 | [Flow](01-flow.md) | Partial | 5 | Flooded-forest shot: GN terrain, Ocean flood, a boat riding sampled waves, EEVEE 4K |
| 02 | [Sprite Fright](02-sprite-fright.md) | Partial | 4 | Mushroom clearing dressed from the film's real library and node groups |
| 03 | [Charge](03-charge.md) | Partial | 5 | Battery-factory bay with a GN muzzle flash, sparks, smoke |
| 04 | [Singularity](04-singularity.md) | Taste-bound | 4 | Painterly ice-shard ring with the Studio's own brushstroke nodes |
| 05 | [Dynamo Dream](05-dynamo-dream.md) | Partial | 4 | Cyberpunk street with camera-projected kitbash; a keyed green-screen plate |
| 06 | [RRR (Makuta VFX)](06-rrr-makuta-vfx.md) | Partial | 5 | Forest gunfire establisher: GN forest, crowd, volumetric haze, comp over a backplate |
| 07 | [Unicorn Wars](07-unicorn-wars.md) | Taste-bound | 5 | Line Art teddy soldier marching past drawn-as-data parallax planes |
| 08 | [Gaku Tada splash](08-gaku-tada-splash.md) | Taste-bound | 2 / 4 | Painterly diorama: GN trees, inverted-hull outlines, toon shading |
| 09 | [Il Baracchino](09-il-baracchino.md) | Partial | 4 | B&W cut-out puppet: UV-Warp face swaps, bendy-bone arm, steps on twos, VSE cut |
| 10 | [Sinking Feeling](10-sinking-feeling.md) | Taste-bound | 3 | Character sinking into mud with procedural GP ripples and a GP face swap |
| 11 | [Nashville airport lobby](11-nashville-airport-lobby.md) | Partial | 4 | Seamless 10 s neon-grid loop framed for the 11,200 × 2,160 wall |
| 12 | [Procedural Still Life](12-procedural-still-life.md) | **Today** | 3 | Parametric vessel generator: 12 seeded pots, stems and petals, window sun |
| 13 | [Molecular Nodes](13-molecular-nodes.md) | **Today** | 2 / 4 | Crambin (PDB 1CRN) from RCSB: 327/327 atoms, two styles, checked secondary structure |
| 14 | [The Junk Shop](14-the-junk-shop.md) | Taste-bound | 4 | Shop corner with ~40 parametric props raycast onto shelves, no overlaps |
| 15 | [Park Lipence](15-park-lipence.md) | Partial | 4 | 40 × 40 m park patch: path-masked GN scatter, timber pavilion, physical sky |
| 16 | [LiveLink product viz](16-livelink-product-viz.md) | **Today** | 3 | Mug template → 72 variant renders headless, with JSON sidecars and checks |
| 17 | [Bismuth mech](17-bismuth-security-mech.md) | Partial | 3 | Hip-actuator module: live Boolean/Bevel stack, low-poly bake, turntable |
| 18 | [Amber bust](18-amber-bust.md) | Taste-bound | 4 | Base-mesh head shaped by Lattice/Displace, GN hair, EEVEE portrait (honestly: a mannequin) |
| 19 | [DOGWALK](19-dogwalk.md) | Partial | 4 | Snowy clearing generated from a curve, dressed with DOGWALK assets, glTF round trip |
| 20 | [FLIP Fluids reel](20-flip-fluids-reel.md) | Partial | 3 / 4 | Pour-into-a-glass with built-in Mantaflow: leak, fill-level and volume checks |

**Tally:**

| Readiness | Count | Items |
|---|---|---|
| Today | 3 | procedural art, data visualisation, product viz at scale |
| Partial | 11 | |
| Taste-bound | 6 | NPR/2D, sculpting, hand-dressed scenes, stylised films |

None of the 20 is out of reach mechanically. The constraints are:

- **Compute:** farm-scale renders.
- **Gated tools** (ledger L-004, L-009): camera tracking needs an open Clip Editor; brush strokes and hand-drawn GP have no data API.
- **Taste.**

### Measured while writing (headless Blender 5.2.2, separate processes, not the live window)

| Measurement | Result |
|---|---|
| EEVEE / Cycles frame, 512 px factory scene | 0.29 s / 0.60 s |
| Normal bake | Runs headless |
| Mantaflow 24-frame bake at resolution 32 | 0.71 s |
| DOGWALK Chocomel glTF export | 11.75 s (34 MB) |
| GP strokes written as data | 200 × 64 points in 0.041 s |
| Line Art bake | Runs headless with an explicit context |
| Clip tracking / solve | Poll fails without a Clip Editor (L-004) |
| GP brush stroke | Poll fails headless (L-009) |
| Blender 5.1 splash | Confirmed as a real Singularity lighting shot: 1,799 GN modifiers, 98% triangles |
