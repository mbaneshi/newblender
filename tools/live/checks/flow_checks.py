"""Spec checks for demo 002 (Flow first slice: flooded forest), written BEFORE the build.

Runs inside Blender through tools/live/bl.py. Reads evaluated data only, except
for frame changes, which are restored afterwards. Thresholds come from
docs/showcase/01-flow.md section 5. One stated deviation: the terrain is an open
heightfield, so boundary edges are expected; "non-manifold" here means edges
shared by more than two faces.

Independence from the builder: the builder keys the boat from the nearest ocean
vertex; this checker measures the waterline by ray-casting the evaluated ocean
surface, a different method.
"""

import math
import statistics

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
from mathutils.bvhtree import BVHTree

sc = bpy.context.scene
deps = bpy.context.evaluated_depsgraph_get()
checks = []
frame0 = sc.frame_current


def check(layer, name, value, ok):
    checks.append({"layer": layer, "check": name, "value": value, "pass": bool(ok)})


terrain = bpy.data.objects.get("ENV-terrain")
ocean = bpy.data.objects.get("ENV-flood")
boat = bpy.data.objects.get("GEO-boat")
cam = sc.camera
W = sc.get("water_level")

# Layer 1: validity of the evaluated terrain
sc.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
tev = terrain.evaluated_get(deps)
tme = tev.to_mesh()
edge_faces = {}
for p in tme.polygons:
    for ek in p.edge_keys:
        edge_faces[ek] = edge_faces.get(ek, 0) + 1
over = sum(1 for n in edge_faces.values() if n > 2)
degenerate = sum(1 for p in tme.polygons if p.area < 1e-8)
down = sum(1 for p in tme.polygons if p.normal.z <= 0)
check(1, "terrain: edges shared by >2 faces", over, over == 0)
check(1, "terrain: degenerate faces", degenerate, degenerate == 0)
check(1, "terrain: faces pointing down", down, down == 0)

# Layer 2: submerged fraction at frame 1 (area-weighted, by face centre)
mw = terrain.matrix_world
area_total = sum(p.area for p in tme.polygons)
area_under = sum(p.area for p in tme.polygons if (mw @ p.center).z < W)
frac = area_under / area_total
check(2, "terrain area below water line", f"{frac * 100:.1f}%", 0.35 <= frac <= 0.50)
tev.to_mesh_clear()

# Layer 2: vegetation instances (origin above water, count in frustum at frame 120)
sc.frame_set(120)
deps = bpy.context.evaluated_depsgraph_get()
under, in_view, total = 0, 0, 0
for inst in deps.object_instances:
    if not inst.is_instance or inst.parent is None or inst.parent.original != terrain:
        continue
    total += 1
    loc = inst.matrix_world.translation
    if loc.z < W:
        under += 1
    v = world_to_camera_view(sc, cam, loc)
    if 0 <= v.x <= 1 and 0 <= v.y <= 1 and v.z > 0:
        in_view += 1
check(2, "tree instances with origin below water", f"{under} of {total}", under == 0)
check(2, "tree instances in camera frustum (frame 120)", in_view, 2000 <= in_view <= 20000)

# Layer 1 + 2: ocean evaluates every frame; boat waterline measured by ray cast
errors, gaps, frames = 0, [], range(sc.frame_start, sc.frame_end + 1)
for f in frames:
    sc.frame_set(f)
    deps = bpy.context.evaluated_depsgraph_get()
    try:
        oev = ocean.evaluated_get(deps)
        ome = oev.to_mesh()
        if len(ome.vertices) == 0:
            errors += 1
            continue
        ome.transform(ocean.matrix_world)
        bvh = BVHTree.FromPolygons([v.co for v in ome.vertices], [p.vertices for p in ome.polygons])
        o = boat.matrix_world.translation
        hit, *_ = bvh.ray_cast(Vector((o.x, o.y, o.z + 50)), Vector((0, 0, -1)))
        oev.to_mesh_clear()
        if hit is None:
            errors += 1
            continue
        gaps.append(abs(o.z - hit.z))
    except Exception:
        errors += 1
n = len(frames)
check(1, "ocean evaluates on every frame", f"{n - errors} of {n}", errors == 0)
worst = max(gaps) if gaps else float("inf")
check(2, "boat waterline gap, worst frame", f"{worst * 100:.1f} cm", worst <= 0.05)

# Layer 2: camera handheld noise = evaluated rotation minus the keyframe path
act = cam.animation_data.action if cam.animation_data else None
devs = []
fcs = []
if act:
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                fcs += [fc for fc in bag.fcurves if fc.data_path == "rotation_euler"]
    fcs = fcs or [fc for fc in getattr(act, "fcurves", []) if fc.data_path == "rotation_euler"]
for fc in fcs:
    k = fc.keyframe_points
    if len(k) < 2:
        continue
    (f0, v0), (f1, v1) = k[0].co, k[-1].co
    series = []
    for f in frames:
        base = v0 + (v1 - v0) * (f - f0) / (f1 - f0)
        series.append(math.degrees(fc.evaluate(f) - base))
    devs.append(series)
if devs:
    rms = math.sqrt(statistics.fmean([d * d for s in devs for d in s]))
    s0 = [d - statistics.fmean(devs[0]) for d in devs[0]]
    crossings = sum(1 for a, b in zip(s0, s0[1:]) if a * b < 0)
    hz = crossings / 2 / (n / sc.render.fps)
    check(2, "camera jitter RMS", f"{rms:.2f} deg", 0.3 <= rms <= 1.5)
    check(2, "camera jitter frequency", f"{hz:.2f} Hz", 0.5 <= hz <= 2.0)
else:
    check(2, "camera jitter RMS", "no rotation keys", False)

# Layer 2: naming
prefixes = ("GEO-", "ENV-", "CAM-", "LGT-")
bad = [o.name for o in bpy.data.objects if not o.name.startswith(prefixes)]
check(2, "naming prefixes GEO-/ENV-/CAM-/LGT-", bad or "100%", not bad)

sc.frame_set(frame0)
result["checks"] = checks
result["passed"] = sum(c["pass"] for c in checks)
result["total"] = len(checks)
