"""Spec checks for demo 003 (Charge first slice: battery-factory bay), written BEFORE the build.

Runs inside Blender via tools/live/bl.py. Thresholds from docs/showcase/03-charge.md section 5.
Layers 3 (fresh rebuild) and 4 (renders) are separate scripts.
"""

import math
import statistics

import bmesh
import bpy
from mathutils.bvhtree import BVHTree

sc = bpy.context.scene
checks = []
frame0 = sc.frame_current


def check(layer, name, value, ok):
    checks.append({"layer": layer, "check": name, "value": value, "pass": bool(ok)})


sc.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
KIT = [o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO-")
       and not o.hide_render and o.name != "GEO-battery_cells"]


def eval_bm(o):
    me = o.evaluated_get(deps).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.transform(o.matrix_world)
    o.evaluated_get(deps).to_mesh_clear()
    return bm


def parts(bm):
    seen, out = set(), []
    for f in bm.faces:
        if f.index in seen:
            continue
        stack, comp = [f], []
        seen.add(f.index)
        while stack:
            c = stack.pop()
            comp.append(c)
            for e in c.edges:
                for nf in e.link_faces:
                    if nf.index not in seen:
                        seen.add(nf.index)
                        stack.append(nf)
        out.append(comp)
    return out


def signed_volume(faces):
    vol = 0.0
    for f in faces:
        vs = [l.vert.co for l in f.loops]
        for i in range(1, len(vs) - 1):
            vol += vs[0].dot(vs[i].cross(vs[i + 1])) / 6.0
    return vol


# Layer 1: validity per kit part (each object, evaluated with its modifier stack)
bad = {}
for o in KIT:
    bm = eval_bm(o)
    bm.faces.ensure_lookup_table()
    nm = sum(1 for e in bm.edges if not e.is_manifold)
    deg = sum(1 for f in bm.faces if f.calc_area() < 1e-9)
    loose = sum(1 for v in bm.verts if not v.link_edges)
    inward = sum(1 for p in parts(bm) if signed_volume(p) <= 0)
    if nm or deg or loose or inward:
        bad[o.name] = [nm, deg, inward, loose]
    bm.free()
check(1, "kit parts: non-manifold / degenerate / inward / loose", bad or f"0 in {len(KIT)} parts", not bad)

# Layer 1: boolean result has no self-intersecting faces
wall = bpy.data.objects.get("GEO-wall_back")
if wall:
    bm = eval_bm(wall)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    pairs = [(a, b) for a, b in tree.overlap(tree) if a < b
             and not set(v.index for v in bm.faces[a].verts) & set(v.index for v in bm.faces[b].verts)]
    check(1, "boolean wall: self-intersecting face pairs", len(pairs), len(pairs) == 0)
    bm.free()

# Layer 2: bay bounding box from the shell parts
shell = [o for o in KIT if o.name.startswith(("GEO-floor", "GEO-wall", "GEO-ceiling"))]
xs, ys, zs = [], [], []
for o in shell:
    for c in o.evaluated_get(deps).bound_box:
        w = o.matrix_world @ __import__("mathutils").Vector(c)
        xs.append(w.x), ys.append(w.y), zs.append(w.z)
dims = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
ok = all(abs(d - t) <= 0.02 * t for d, t in zip(dims, (20, 12, 6)))
check(2, "bay bounding box 20 x 12 x 6 m +-2%", " x ".join(f"{d:.2f}" for d in dims), ok)

# Layer 2: racks = shelf parts grouped by (x, side); 2 rows x 8, pitch 2.0 m +- 1 cm
rack = bpy.data.objects.get("GEO-rack")
centres = set()
if rack:
    bm = eval_bm(rack)
    for p in parts(bm):
        vs = [v.co for f in p for v in f.verts]
        dx = max(v.x for v in vs) - min(v.x for v in vs)
        dz = max(v.z for v in vs) - min(v.z for v in vs)
        if dx > 1.5 and dz < 0.1:  # a shelf board
            cx = sum(v.x for v in vs) / len(vs)
            cy = sum(v.y for v in vs) / len(vs)
            centres.add((round(cx, 2), 1 if cy > 0 else -1))
    bm.free()
rows = {s: sorted(x for x, side in centres if side == s) for s in (1, -1)}
gaps = [b - a for r in rows.values() for a, b in zip(r, r[1:])]
counts = [len(rows[1]), len(rows[-1])]
check(2, "racks: 2 rows x 8", counts, counts == [8, 8])
check(2, "rack pitch 2.0 m +- 1 cm", f"{min(gaps):.3f}-{max(gaps):.3f}" if gaps else "none",
      bool(gaps) and all(abs(g - 2.0) <= 0.01 for g in gaps))

# Layer 2: face budget of the whole bay, evaluated, instances included
faces = 0
for inst in deps.object_instances:
    ob = inst.object
    if ob.type == "MESH" and not ob.original.hide_render:
        faces += len(ob.data.polygons)
check(2, "face budget <= 1.5 M", f"{faces:,}", faces <= 1_500_000)


# Layer 2: PBR sanity, sampling textures where inputs are linked
def upstream_image(sock):
    """First image texture upstream, plus the product of MULTIPLY-by-constant math nodes on the way."""
    seen, stack = set(), [(sock, 1.0)]
    while stack:
        s, k = stack.pop()
        for l in s.links:
            n = l.from_node
            if n.type == "TEX_IMAGE" and n.image:
                return n.image, k
            if n.name in seen:
                continue
            seen.add(n.name)
            if n.type == "MATH" and n.operation == "MULTIPLY" and not n.inputs[1].is_linked:
                stack.append((n.inputs[0], k * n.inputs[1].default_value))
            else:
                stack += [(i, k) for i in n.inputs if i.is_linked]
    return None, 1.0


def mean_value(sock, lum=False):
    if not sock.is_linked:
        v = sock.default_value
        if hasattr(v, "__len__"):
            return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2] if lum else v[0]
        return v
    img, k = upstream_image(sock)
    if img is None:
        return None
    px = list(img.pixels[::4 * 97])  # every 97th pixel, red channel
    pg = list(img.pixels[1::4 * 97])
    pb = list(img.pixels[2::4 * 97])
    if lum:
        return k * statistics.fmean(0.2126 * r + 0.7152 * g + 0.0722 * b for r, g, b in zip(px, pg, pb))
    return k * statistics.fmean(px)


pbr_bad = {}
for m in bpy.data.materials:
    if not m.use_nodes or not m.users:
        continue
    b = m.node_tree.nodes.get("Principled BSDF")
    if b is None or m.name.startswith("MAT-fx") or m.name in ("MAT-cell", "MAT-haze"):
        continue
    metal, rough = mean_value(b.inputs["Metallic"]), mean_value(b.inputs["Roughness"])
    lumv = mean_value(b.inputs["Base Color"], lum=True)
    if metal is not None and metal >= 0.5:
        if rough is None or not 0.15 <= rough <= 0.7:
            pbr_bad[m.name] = f"metal, roughness {rough}"
    elif lumv is None or not 0.03 <= lumv <= 0.9:
        pbr_bad[m.name] = f"dielectric, luminance {lumv}"
check(2, "PBR sanity (metal roughness 0.15-0.7; dielectric luminance 0.03-0.9)", pbr_bad or "all ok", not pbr_bad)


# Layer 2: FX timing from the keyed controls
def keyed_frames(datablock, path, threshold):
    frames = []
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        if eval("datablock." + path) > threshold:
            frames.append(f)
    return frames


flash = bpy.data.materials.get("MAT-fx_flash")
smoke = bpy.data.materials.get("MAT-fx_smoke")
ff = keyed_frames(flash.node_tree.nodes["Emission"].inputs["Strength"], "default_value", 0.5) if flash else []
sf = keyed_frames(smoke.node_tree.nodes["density_scale"].outputs[0], "default_value", 0.01) if smoke else []
check(2, "muzzle flash visible frames (2-3)", ff, 2 <= len(ff) <= 3)
check(2, "smoke lifetime 24-48 frames", len(sf), 24 <= len(sf) <= 48)

# Layer 2: applied scale and naming
scaled = [o.name for o in bpy.data.objects if any(abs(s - 1) > 1e-6 for s in o.scale)]
check(2, "scale applied", scaled or "all 1.0", not scaled)
names = [o.name for o in bpy.data.objects if not o.name.startswith(("GEO-", "FX-", "LGT-", "CAM-"))]
check(2, "naming GEO-/FX-/LGT-/CAM-", names or "100%", not names)

sc.frame_set(frame0)
result["checks"] = checks
result["passed"] = sum(c["pass"] for c in checks)
result["total"] = len(checks)
