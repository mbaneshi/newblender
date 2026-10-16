"""Probe P02-2/3: session_uid across save/load, compare_geometry reachability, poll message.

Run: Blender -b --factory-startup --disable-autoexec --python tools/probes/p02_identity_api.py -- OUT.json [PHASE]
PHASE 'save' (default) builds a scene, records session_uids, saves TMP.blend, then reopens it in the
same process. PHASE 'reopen:<file>:<prev.json>' opens a saved file in a NEW process and compares.
"""
import json
import sys
import tempfile

import bpy

args = sys.argv[sys.argv.index("--") + 1:]
out = args[0]
phase = args[1] if len(args) > 1 else "save"
res = {}


def uids():
    return {
        "objects": {o.name: o.session_uid for o in bpy.data.objects},
        "meshes": {m.name: m.session_uid for m in bpy.data.meshes},
        "materials": {m.name: m.session_uid for m in bpy.data.materials},
    }


if phase == "save":
    mat = bpy.data.materials.new("M")
    bpy.ops.mesh.primitive_uv_sphere_add()
    bpy.context.object.data.materials.append(mat)
    before = uids()
    path = tempfile.gettempdir() + "/p02_ident.blend"
    bpy.ops.wm.save_as_mainfile(filepath=path)
    after_save = uids()
    bpy.ops.wm.open_mainfile(filepath=path)
    after_reopen_same_process = uids()
    res.update(before=before, after_save=after_save, after_reopen_same_process=after_reopen_same_process,
               saved_path=path, same_after_save=before == after_save,
               same_after_reopen_same_process=before == after_reopen_same_process)
else:
    _, path, prev = phase.split(":", 2)
    bpy.ops.wm.open_mainfile(filepath=path)
    now = uids()
    prev = json.load(open(prev))
    res.update(now=now, prev_before=prev["before"], same_in_new_process=now == prev["before"])

# compare_geometry reachability: Mesh.unit_test_compare
bpy.ops.wm.read_factory_settings(use_empty=True)
a = bpy.data.meshes.new("A"); b = bpy.data.meshes.new("B"); c = bpy.data.meshes.new("C")
verts = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
a.from_pydata(verts, [], [(0, 1, 2, 3)])
b.from_pydata(verts, [], [(0, 1, 2, 3)])
c.from_pydata([(0, 0, 0), (1, 0, 0), (1, 1, 0.5), (0, 1, 0)], [], [(0, 1, 2, 3)])
res["compare_has_attr"] = hasattr(a, "unit_test_compare")
res["compare_identical"] = a.unit_test_compare(mesh=b, threshold=0.0001)
res["compare_moved_vertex"] = a.unit_test_compare(mesh=c, threshold=0.0001)

# poll message: bool from .poll(), message only in the RuntimeError from a call
op = bpy.ops.mesh.loop_select
res["poll_return_type"] = type(op.poll()).__name__
res["poll_value_headless"] = op.poll()
try:
    op()
    res["call_error"] = None
except Exception as e:  # noqa: BLE001
    res["call_error"] = f"{type(e).__name__}: {e}"
res["get_rna_type_props"] = sorted(p.identifier for p in op.get_rna_type().properties)[:8]

json.dump(res, open(out, "w"), indent=1)
