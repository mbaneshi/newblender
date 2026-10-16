"""Probe P02-4: cost of per-mutation checkpoints and in-session undo steps.

Run: Blender -b --factory-startup --disable-autoexec --python tools/probes/p02_snapshot_cost.py -- OUT.json
Scenes: S (default cube), M (200 subdivided UV spheres), L (1 grid object, ~4M vertices).
Per scene it measures: save_as_mainfile(copy=True) time + file size (uncompressed and compressed),
ed.undo_push() time, and a restore check (mutate, ed.undo(), compare vertex-sum fingerprint).
"""
import json
import os
import sys
import tempfile
import time

import bpy

out = sys.argv[sys.argv.index("--") + 1]
tmp = tempfile.mkdtemp()
res = {}


def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def build(kind):
    clear()
    if kind == "S":
        bpy.ops.mesh.primitive_cube_add()
    elif kind == "M":
        for i in range(200):
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=(i % 20, i // 20, 0))
    elif kind == "L":
        bpy.ops.mesh.primitive_grid_add(x_subdivisions=2000, y_subdivisions=2000)


def fingerprint():
    s = 0.0
    n = 0
    for o in bpy.data.objects:
        if o.type == "MESH":
            n += len(o.data.vertices)
            s += sum(v.co.z for v in o.data.vertices[:2000])
    return {"verts": n, "zsum_first2000": round(s, 6)}


def timed(fn):
    t = time.perf_counter()
    r = fn()
    return round((time.perf_counter() - t) * 1000, 2), r


for kind in ("S", "M", "L"):
    build(kind)
    r = {"fingerprint": fingerprint()}
    for comp in (False, True):
        path = os.path.join(tmp, f"{kind}_{int(comp)}.blend")
        ms, _ = timed(lambda: bpy.ops.wm.save_as_mainfile(filepath=path, copy=True, compress=comp))
        r[f"save_copy_ms_compress{int(comp)}"] = ms
        r[f"size_mb_compress{int(comp)}"] = round(os.path.getsize(path) / 1e6, 2)
    ms, _ = timed(lambda: bpy.ops.ed.undo_push(message="p02"))
    r["undo_push_ms"] = ms
    # restore check
    before = fingerprint()
    obj = next(o for o in bpy.data.objects if o.type == "MESH")
    for v in obj.data.vertices[:50]:
        v.co.z += 1.0
    bpy.ops.ed.undo_push(message="p02-mutate")
    mutated = fingerprint()
    try:
        ms, _ = timed(lambda: bpy.ops.ed.undo())
        r["undo_ms"] = ms
        r["restored_equals_before"] = fingerprint() == before
        r["mutation_visible_before_undo"] = mutated != before
    except Exception as e:  # noqa: BLE001
        r["undo_error"] = f"{type(e).__name__}: {str(e)[:160]}"
    # reload-from-snapshot cost
    path = os.path.join(tmp, f"{kind}_0.blend")
    ms, _ = timed(lambda: bpy.ops.wm.open_mainfile(filepath=path))
    r["open_snapshot_ms"] = ms
    res[kind] = r

json.dump(res, open(out, "w"), indent=1)
