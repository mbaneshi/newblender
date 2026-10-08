# 13 — Molecular Nodes: how an agent could make it

| | |
|---|---|
| **Original** | Brady Johnston (+ contributors), 2022–present, scientific visualisation add-on for structural biology · [GitHub](https://github.com/BradyAJohnston/MolecularNodes) · [PyPI](https://pypi.org/project/molecularnodes/) |
| **Agent-readiness today** | **Today**: the input is real, public, machine-readable data (the Protein Data Bank), the representation is Geometry Nodes (GN) driven by attributes, and correctness is checkable against the file itself. This is the most agent-native work in the 20. Taste remains in colour, framing and what to emphasise for a scientific story. |
| **Difficulty** | 2 for renders and animations of a structure with the real add-on; 4 to rebuild the add-on itself (cartoon ribbons, surfaces, trajectories, density maps) |
| **First slice** | Parse crambin (PDB 1CRN, 327 atoms) straight from RCSB, write atoms as a point cloud with `element`, `chain` and `residue` attributes, and build a ball-and-stick plus a CA backbone tube in one GN tree, coloured by element; checks prove every atom and both helices arrived. |

## 1. What the original actually is

- **A tool, not a picture.** An add-on and Python package that imports PDB, mmCIF, molecular-dynamics (MD) trajectories and electron-microscopy (EM) density maps into Blender and styles them with GN (README, fetched 2026-10-07).
- **Distribution:** Blender extension (Get Extensions, Blender ≥ 4.2) and PyPI. PyPI's latest is **520.2.0 (18 Sep 2026), Python ~= 3.13**: the version number tracks the Blender release line (5.2). Licence GPL-3.0. Core dependencies Biotite and MDAnalysis.
- **Styles:** procedural representations such as cartoon, surface, ball-and-stick and spheres (index entry 13); colouring from per-atom attributes.
- **Funding and use:** a 2024 NumFOCUS Small Development Grant via MDAnalysis; used in labs for publication renders and animations.
- **Outputs people make with it:** stills for papers and covers, rotating turntables, MD trajectory playback, morphs between conformations.

## 2. How the humans made it

Stages: **S03 Shading, S04 Geometry Nodes, S07 Animation, S09 Lighting & rendering.**

- **Fact (README/docs):** data parsing is delegated to Biotite and MDAnalysis; Blender receives meshes/point clouds with attributes; GN node groups shipped with the add-on turn atoms into styles.
- **Fact (index):** attribute-driven shading; keyframed and trajectory animation; Cycles/EEVEE.
- **Interpretation:** the human craft was in the *library of node groups* (how a cartoon ribbon is derived from backbone atoms and secondary-structure records) and the import plumbing. A user then picks a style and colours. This is exactly the declarative-first artefact the ledger proposes (L-006): data in, recipe on top, nothing hand-modelled.

## 3. How I would make it: the agent-native plan

Two paths. **Path A** uses the real add-on (what a scientist would do). **Path B** rebuilds the minimum from scratch to prove the pipeline needs no hand work; the first slice is Path B because it needs no extension install and every step is inspectable.

| Stage | Agent approach | Inputs (real data) | Tooling |
|---|---|---|---|
| Data | Fetch PDB/mmCIF from RCSB; parse ATOM/HETATM, HELIX/SHEET, SSBOND records (Path B: a 60-line parser; Path A: Biotite inside the add-on) | [RCSB PDB](https://www.rcsb.org): `https://files.rcsb.org/download/1CRN.pdb` (crambin, 327 atoms, 46 residues, 2 helices, 1 sheet, 3 disulfides); `4HHB` (deoxyhaemoglobin, 4 chains, 4,384 ATOM + 395 HETATM incl. 4 haem groups) | Python inside Blender via `tools/live/bl.py` |
| S01 as data | One mesh of loose vertices (one per atom) with attributes: `element` (int), `b_factor`, `res_id`, `chain_id`, `is_backbone`, `sec_struct` | Same | `mesh.attributes.new(...).data.foreach_set` |
| S04 Style: spheres | Instance on Points (Ico Sphere), scale from a van der Waals radius lookup by `element` (Index Switch / Sample Index on a radii table) | Bondi radii (C 1.70, N 1.55, O 1.52, S 1.80 Å) | GN |
| S04 Style: sticks | Bonds computed by distance (pairs closer than sum of covalent radii + 0.45 Å) written as mesh edges; Mesh to Curve → Curve to Mesh with a thin circle profile | Covalent radii table | Python for bonds (KD-tree), GN for geometry |
| S04 Style: backbone | Filter `is_backbone` CA atoms in residue order → Points to Curves → smooth (Resample, Set Spline Type) → Curve to Mesh; profile width larger where `sec_struct` = helix | HELIX/SHEET records | GN |
| S03 Shading | Colour by element (CPK-like: C grey, N blue, O red, S yellow) via Attribute node; alternative ramp on `b_factor` | None | Shader Attribute |
| S07 Animation | Turntable (one driver), or interpolate positions between two PDB conformations by GN Mix on position; Path A loads MD trajectories | Second conformation from PDB, or an MDAnalysis test trajectory | GN / add-on |
| S09 Render | Cycles, three-point light, soft AO-like ambient; orthographic option for figures | Poly Haven studio HDRI (CC0), optional | Cycles |

**Build order:**

1. Download `1CRN.pdb` (≈ 60 KB). Write the checks (§5) from the file's own header: 327 atoms, 46 CA, 2 helices (residues 7–19, 23–30), sheet 1–4 / 32–35, 3 SSBONDs.
2. Parse and write the point mesh with attributes; run layer-1/2 checks.
3. GN tree `GN-mol_style` with a `style` menu input (spheres / ball-and-stick / backbone).
4. Bonds by KD-tree; check bond-length distribution and the 3 disulfide bonds.
5. Element colours; camera framing the bounding sphere; turntable.
6. Repeat with `4HHB` to show scale (4 chains, haem groups as HETATM).
7. Path A follow-up: install Molecular Nodes from extensions.blender.org in the owner's Blender and render the same structure in its cartoon style as the layer-3 reference.

## 4. What works today vs. what needs newblender

- **Works today with the live bridge:**
  - Network fetch and text parsing inside Blender's Python; writing named attributes in bulk with `foreach_set`.
  - Every GN node in the plan exists in 5.2.2 (Instance on Points, Points to Curves, Curve to Mesh, Sample Index, Index Switch, Menu Switch).
  - `mathutils.kdtree` for bonding; evaluated-geometry checks as in `tools/live/checks/chair_checks.py`.
  - The real add-on tracks Blender versions closely (520.x for 5.2), so Path A is available today.
- **Painful today:**
  - Building a style library as `nodes.new`/`links.new` calls; no text artefact to diff (L-006).
  - GN returns no "what did I build": instance counts and curve lengths must be re-derived from the depsgraph (L-003).
  - Large MD trajectories in an interactive session: memory and frame-change cost; a headless batch profile would be the right home (L-011).
- **Not feasible today (for an agent alone):**
  - Reproducing the add-on's full cartoon algorithm (guide points, peptide-plane orientation, arrow heads for sheets) to its quality in a day. It is a known, specifiable algorithm, just long.
  - Molecular surfaces (solvent-excluded) at research accuracy without a library.

## 5. Verification plan (RFC 0001 R6, six layers)

| Layer | Check | Threshold |
|---|---|---|
| 1 Validity | Point mesh has no NaN coordinates and the declared attributes on the POINT domain | 0 NaN; attributes {element, res_id, chain_id, is_backbone, sec_struct, b_factor} all present |
| 1 Validity | Realised style meshes clean | 0 degenerate faces; 0 non-manifold edges on sphere and tube meshes |
| 2 Spec | Atom count equals the file | 1CRN: exactly 327 points; 4HHB: 4,384 + 395 = 4,779 (or 4,384 + 174 if waters are excluded by spec: 172 HEM + 2 PO4) |
| 2 Spec | Residues and chains | 1CRN: 46 CA atoms, chain set {A}; 4HHB: chains {A, B, C, D} |
| 2 Spec | Secondary structure transferred | Points flagged helix exactly residues 7–19 and 23–30 in 1CRN |
| 2 Spec | Bonds plausible | All bond lengths 0.9–2.1 Å; the 3 SSBOND pairs (3–40, 4–32, 16–26) bonded at 2.00–2.05 Å ± 0.05 |
| 2 Spec | Coordinates preserved | Max abs difference between file coordinates and point positions (Å → scene units at declared scale) < 1e-4 |
| 3 Reference | Same structure through Molecular Nodes (Path A) | Atom count equal; bounding boxes equal within 0.01 Å; centroid within 0.01 Å |
| 4 Downstream | Render readable and colour-correct | Pixel sample on a known oxygen atom maps to the red element colour (hue within ±10°); no fireflies (< 0.01% > 20× local median) |
| 4 Downstream | Turntable loops | Frame 0 and frame N+1 identical (PSNR ≥ 45 dB) |
| 5 Appearance (warning) | Vision model: "is this a small protein with two helices shown as ball-and-stick?" | Warn on "no" |
| 6 Taste (owner) | Colour scheme, which residues to highlight, framing for a figure | Owner sign-off |

## 6. Where the human is still needed

- **The scientific story.** Which residues matter (an active site, a binding pocket, a mutation) and what to hide is a researcher's judgement, not a rendering choice.
- **Honesty of representation.** Smoothing, exaggerated radii and dramatic depth-of-field can mislead; a domain expert decides what is acceptable for a paper.
- **Style.** Journal figure conventions, colour-blind-safe palettes and cover-art drama are taste.
- **Trajectories.** Choosing which frames of a microsecond simulation tell the story.

## 7. Effort

- **First slice (live demo, ~1 day):** the owner's Blender shows an empty scene, then a cloud of 327 dots appears in the shape of crambin. Switching the GN `style` input turns the dots into grey/blue/red/yellow balls joined by sticks, then into a smooth backbone tube that visibly thickens along the two helices. Three yellow sulfur bridges are visible. A turntable plays; a Cycles still and a check report (327/327 atoms, 46/46 residues, helices 7–19 and 23–30, 3/3 disulfides) are saved in `~/newblender-data/demos/`. A second run loads haemoglobin's four chains with the same tree.
- **Full reproduction:** of *renders* using the add-on: a few agent-hours per figure. Of the *add-on itself* (cartoon, surfaces, MD, density, UI): several hundred agent-hours plus a domain expert's review time; render compute is small (minutes per still).

## 8. Risks and unknowns

- The add-on's exact Python scripting API was not verified for this note (docs point to API pages; signatures unconfirmed).
- mmCIF is the PDB's primary format; very large structures are mmCIF-only, so Path B's PDB parser does not scale to ribosomes.
- Extension install needs Blender's online access enabled; that is a one-time owner action.
- Unit scale (Å vs metres) must be declared, or lighting and depth of field behave oddly.

## 9. Sources

- [GitHub: BradyAJohnston/MolecularNodes](https://github.com/BradyAJohnston/MolecularNodes) (verified, README fetched 2026-10-07)
- [PyPI: molecularnodes 520.2.0](https://pypi.org/project/molecularnodes/) (verified, fetched 2026-10-07)
- [Molecular Nodes documentation](https://bradyajohnston.github.io/MolecularNodes/) (verified, fetched)
- [MDAnalysis: NumFOCUS grant for MolecularNodes](https://www.mdanalysis.org/2024/12/12/sdg_molecularnodes/) (from index)
- [RCSB PDB 1CRN](https://www.rcsb.org/structure/1CRN) and [4HHB](https://www.rcsb.org/structure/4HHB): record counts above measured from `files.rcsb.org/download/*.pdb` on 2026-10-07
- [Ledger L-003, L-006, L-011](../discovery/ledger.md); [S01 brief §6](../discovery/s01-modeling/05-brief.md); [RFC 0001 R6](../rfc/0001-newblender.md)
- Live bridge: [`tools/live/bl.py`](../../tools/live/bl.py); chair evidence `~/newblender-data/demos/001-chair/report.md`
