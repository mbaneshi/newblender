"""Aggregate per-file census JSON into one modelling-focused summary.

    python3 aggregate.py CENSUS_DIR OUT.json

Files are split into two groups so linked data isn't counted twice:
  assets - files that author data (asset libraries, props, chars, demos)
  shots  - assembly files (shot/splash masters) that mostly link assets in
Mesh topology counts only meshes local to their file.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path

SHOT = re.compile(r"(anim(\.[ABC])?|lighting)\.blend|splash", re.I)


def main(census_dir, out_path):
    groups = {"assets": [], "shots": []}
    for p in sorted(Path(census_dir).glob("*.json")):
        d = json.load(open(p))
        groups["shots" if SHOT.search(d["file"]) else "assets"].append(d)

    summary = {}
    for name, files in groups.items():
        topo, mods, depth, objs, gn_nodes, ngtypes, cons = (Counter() for _ in range(7))
        local_meshes = with_ngon = with_uv = with_sk = 0
        per_mesh_verts = []
        libs = linked = overrides = 0
        for d in files:
            objs.update(d["object_types"])
            mods.update({k: v for k, v in d["modifier_types"].items() if not k.startswith("MULTIRES_levels")})
            for k, v in d["modifier_stack_depths"].items():
                depth[int(k)] += v
            gn_nodes.update(d["gn_node_types_top"])
            ngtypes.update(d["node_groups_by_type"])
            cons.update(d["constraint_types"])
            libs += len(d["libraries"])
            linked += d["linked_ids"]
            overrides += d["overrides"]
            for m in d["per_mesh"].values():
                if m["linked"]:
                    continue
                local_meshes += 1
                for k in ("tri", "quad", "ngon", "verts", "faces"):
                    topo[k] += m[k]
                with_ngon += bool(m["ngon"])
                with_uv += bool(m["uv_layers"])
                with_sk += bool(m["shape_keys"])
                per_mesh_verts.append(m["verts"])
        faces = topo["faces"] or 1
        mesh_objs = objs.get("MESH", 0) or 1
        objs_with_mods = sum(v for k, v in depth.items() if k > 0)
        per_mesh_verts.sort()
        summary[name] = {
            "files": len(files),
            "object_types": dict(objs.most_common()),
            "local_meshes": local_meshes,
            "faces": topo["faces"], "verts": topo["verts"],
            "face_mix_pct": {k: round(100 * topo[k] / faces, 1) for k in ("quad", "tri", "ngon")},
            "meshes_with_ngons_pct": round(100 * with_ngon / max(local_meshes, 1), 1),
            "meshes_with_uvs_pct": round(100 * with_uv / max(local_meshes, 1), 1),
            "meshes_with_shape_keys": with_sk,
            "median_mesh_verts": per_mesh_verts[len(per_mesh_verts) // 2] if per_mesh_verts else 0,
            "modifier_types": dict(mods.most_common()),
            "modifiers_total": sum(mods.values()),
            "objects_with_modifiers_pct_of_mesh_objs": round(100 * objs_with_mods / mesh_objs, 1),
            "stack_depth_hist": dict(sorted(depth.items())),
            "node_groups_by_type": dict(ngtypes),
            "gn_node_types_top": dict(gn_nodes.most_common(30)),
            "constraint_types": dict(cons.most_common(15)),
            "libraries_refs": libs, "linked_objects": linked, "overrides": overrides,
        }
    json.dump(summary, open(out_path, "w"), indent=1)
    print(json.dumps(summary, indent=1))


main(sys.argv[1], sys.argv[2])
