"""Spec checks for demo 001 (a game-ready chair), written BEFORE the build.

Runs inside Blender (sent through tools/live/bl.py). Reads the evaluated
scene (modifiers applied in the depsgraph, nothing changed) and fills
`result` with one entry per check: layer, name, measured value, pass/fail.

Spec: seat top 44-46 cm; exactly 4 legs touching the floor; < 5,000 faces;
manifold, no loose geometry; outward normals; scale applied; Studio naming
(GEO-...); UVs on every mesh; material assigned.
"""

import bmesh
import bpy

PREFIX = "GEO-chair"
checks = []


def check(layer, name, value, ok):
    checks.append({"layer": layer, "check": name, "value": value, "pass": bool(ok)})


deps = bpy.context.evaluated_depsgraph_get()
objs = [o for o in bpy.data.objects if o.type == "MESH"]

# Evaluated geometry of the whole chair, in world space.
bm = bmesh.new()
for o in objs:
    ev = o.evaluated_get(deps)
    me = ev.to_mesh()
    me.transform(o.matrix_world)
    bm.from_mesh(me)
    ev.to_mesh_clear()
bm.verts.ensure_lookup_table()

# Layer 1 - validity
non_manifold = sum(1 for e in bm.edges if not e.is_manifold)
loose_verts = sum(1 for v in bm.verts if not v.link_edges)
degenerate = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
check(1, "manifold edges", f"{non_manifold} non-manifold", non_manifold == 0)
check(1, "no loose vertices", loose_verts, loose_verts == 0)
check(1, "no degenerate faces", degenerate, degenerate == 0)

# Split into loose parts (connected components).
parts, seen = [], set()
for f in bm.faces:
    if f.index in seen:
        continue
    stack, comp = [f], []
    seen.add(f.index)
    while stack:
        cur = stack.pop()
        comp.append(cur)
        for e in cur.edges:
            for nf in e.link_faces:
                if nf.index not in seen:
                    seen.add(nf.index)
                    stack.append(nf)
    parts.append(comp)


def signed_volume(faces):
    vol = 0.0
    for f in faces:
        vs = [l.vert.co for l in f.loops]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6.0
    return vol


inward = sum(1 for p in parts if signed_volume(p) <= 0)
check(1, "normals point outward (every part)", f"{inward} inward of {len(parts)}", inward == 0)

# Layer 2 - spec conformance
faces = len(bm.faces)
check(2, "face budget < 5000", faces, faces < 5000)
z_min = min(v.co.z for v in bm.verts)
check(2, "rests on the floor (min z = 0)", round(z_min, 4), abs(z_min) < 1e-3)
legs = [p for p in parts if min(v.co.z for f in p for v in f.verts) < 1e-3]
check(2, "exactly 4 legs touch the floor", len(legs), len(legs) == 4)
seat = bpy.data.objects.get(f"{PREFIX}_seat")
if seat:
    sev = seat.evaluated_get(deps)
    top = max((seat.matrix_world @ v.co).z for v in sev.to_mesh().vertices)
    sev.to_mesh_clear()
    check(2, "seat top 44-46 cm", f"{top * 100:.1f} cm", 0.44 <= top <= 0.46)
else:
    check(2, "seat top 44-46 cm", "no seat object", False)
bad_scale = [o.name for o in objs if any(abs(s - 1) > 1e-6 for s in o.scale)]
check(2, "scale applied", bad_scale or "all 1.0", not bad_scale)
bad_names = [o.name for o in objs if not o.name.startswith(PREFIX)]
check(2, "Studio naming GEO-chair_*", bad_names or "ok", not bad_names)
no_uv = [o.name for o in objs if not o.data.uv_layers]
check(2, "UVs on every mesh", no_uv or "ok", not no_uv)
no_mat = [o.name for o in objs if not o.data.materials]
check(2, "material assigned", no_mat or "ok", not no_mat)

bm.free()
result["parts"] = len(parts)
result["checks"] = checks
result["passed"] = sum(c["pass"] for c in checks)
result["total"] = len(checks)
