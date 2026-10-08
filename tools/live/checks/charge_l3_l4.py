"""Demo 003 layer-3 fingerprint and layer-4 UV-stretch check (run live or headless).

Fingerprint: evaluated vertex positions of every kit part, cell instance
transforms, and the keyed FX controls. UV stretch: per-face area-distortion
ratio r = (uv_area / uv_total) / (area / area_total) on textured kit parts,
counted as distorted when max(r, 1/r) > 1.15; the plan wants >= 95% of faces within.
"""

import hashlib

import bpy

sc = bpy.context.scene
sc.frame_set(1)
deps = bpy.context.evaluated_depsgraph_get()
h = hashlib.sha256()
kit = sorted((o for o in bpy.data.objects if o.type == "MESH" and o.name.startswith("GEO-")), key=lambda o: o.name)
within = total = 0
per_obj = {}
for o in kit:
    me = o.evaluated_get(deps).to_mesh()
    for v in me.vertices:
        h.update(("%.4f %.4f %.4f;" % tuple(o.matrix_world @ v.co)).encode())
    textured = o.data.materials and any(n.type == "TEX_IMAGE" for m in o.data.materials if m and m.use_nodes
                                        for n in m.node_tree.nodes)
    if textured and me.uv_layers.active and me.polygons:
        uv = me.uv_layers.active.data
        areas, uvas = [], []
        for p in me.polygons:
            pts = [uv[li].uv for li in p.loop_indices]
            a = 0.0
            for i in range(len(pts)):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % len(pts)]
                a += x1 * y2 - x2 * y1
            areas.append(p.area)
            uvas.append(abs(a) / 2)
        ta, tu = sum(areas), sum(uvas)
        ok = 0
        for a, u in zip(areas, uvas):
            if a <= 1e-12:
                continue
            r = (u / tu) / (a / ta) if u > 0 else 0
            ok += 1 if r > 0 and max(r, 1 / r) <= 1.15 else 0
        per_obj[o.name] = round(100 * ok / len(areas), 1)
        within += ok
        total += len(areas)
    o.evaluated_get(deps).to_mesh_clear()
inst = sorted("%.4f %.4f %.4f" % tuple(i.matrix_world.translation) for i in deps.object_instances if i.is_instance)
h.update(";".join(inst).encode())
for f in (47, 48, 49, 50, 60, 75, 90):
    sc.frame_set(f)
    fm = bpy.data.materials["MAT-fx_flash"].node_tree.nodes["Emission"].inputs["Strength"].default_value
    dm = bpy.data.materials["MAT-fx_smoke"].node_tree.nodes["density_scale"].outputs[0].default_value
    h.update(("%.3f %.3f|" % (fm, dm)).encode())
sc.frame_set(1)
result["digest"] = h.hexdigest()[:16]
result["instances"] = len(inst)
result["uv_within_1.15_pct"] = round(100 * within / max(total, 1), 1)
result["uv_by_object_pct"] = per_obj
