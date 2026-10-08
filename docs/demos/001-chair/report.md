# Demo 001: chair — check report

Built live in Blender 5.2.2 via the Blender Lab bridge. 12/12 checks pass; 9 loose parts.

| Result | Layer | Check | Measured |
|---|---|---|---|
| PASS | 1 | manifold edges | 0 non-manifold |
| PASS | 1 | no loose vertices | 0 |
| PASS | 1 | no degenerate faces | 0 |
| PASS | 1 | normals point outward (every part) | 0 inward of 9 |
| PASS | 2 | face budget < 5000 | 486 |
| PASS | 2 | rests on the floor (min z = 0) | 0.0 |
| PASS | 2 | exactly 4 legs touch the floor | 4 |
| PASS | 2 | seat top 44-46 cm | 45.0 cm |
| PASS | 2 | scale applied | all 1.0 |
| PASS | 2 | Studio naming GEO-chair_* | ok |
| PASS | 2 | UVs on every mesh | ok |
| PASS | 2 | material assigned | ok |

First run: 11/12 — UVs missing on all meshes (bmesh calc_uvs needs an existing UV layer); fixed and rebuilt.
Layer 5 (look), from the camera render: first render read as pale pink and showed the back; colour and camera fixed.
