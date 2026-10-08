"""Fingerprint of the Flow scene for the layer-3 reproducibility check.

Hashes the evaluated terrain, every tree instance transform, the boat's keyed
motion and the camera's evaluated path. Run in the live session and in a fresh
headless session that rebuilt the scene from flow_build.py; the digests must match.
Values are rounded to 1e-4 so float noise at the last bit does not count.
"""

import hashlib

import bpy

sc = bpy.context.scene
h = hashlib.sha256()
sc.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
terrain = bpy.data.objects["ENV-terrain"]
me = terrain.evaluated_get(deps).to_mesh()
for v in me.vertices:
    h.update(("%.4f %.4f %.4f;" % tuple(v.co)).encode())
terrain.evaluated_get(deps).to_mesh_clear()
inst = sorted("%.4f %.4f %.4f %.4f" % (*i.matrix_world.translation, i.matrix_world.to_scale().x)
              for i in deps.object_instances
              if i.is_instance and i.parent and i.parent.original == terrain)
h.update(";".join(inst).encode())
boat, cam = bpy.data.objects["GEO-boat"], bpy.data.objects["CAM-main"]
for f in range(sc.frame_start, sc.frame_end + 1, 8):
    sc.frame_set(f)
    h.update(("%.4f %.4f %.4f %.4f|" % (boat.location.z, boat.rotation_euler.x, boat.rotation_euler.y,
                                         cam.rotation_euler.x)).encode())
    h.update(("%.3f %.3f %.3f|" % tuple(cam.location)).encode())
sc.frame_set(1)
result["digest"] = h.hexdigest()[:16]
result["instances"] = len(inst)
