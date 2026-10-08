"""Demo 001: build a game-ready chair live, one step per call.

Sent through tools/live/bl.py with STEP set, e.g.
    python3 bl.py -e "STEP=1; exec(open('chair_build.py').read())"

Agent-native on purpose: geometry is created as data (bmesh into Mesh), never
through Edit Mode, selection or operators; detail is a declared modifier
recipe (Mirror, Bevel) that stays live and editable. Checks live in
tools/live/checks/chair_checks.py and were written before this file.
"""

import bmesh
import bpy

P = "GEO-chair"


def box(name, size, center, taper_bottom=1.0):
    """A closed box mesh object with UVs, built as data. Object transform stays identity."""
    bm = bmesh.new()
    bm.loops.layers.uv.new("UVMap")  # calc_uvs only fills an existing layer
    bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
    for v in bm.verts:
        k = taper_bottom if v.co.z < 0 else 1.0
        v.co.x = v.co.x * size[0] * k + center[0]
        v.co.y = v.co.y * size[1] * k + center[1]
        v.co.z = v.co.z * size[2] + center[2]
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    old = bpy.data.objects.get(name)
    if old:
        bpy.data.objects.remove(old)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


def mirror(ob, x=True, y=False):
    m = ob.modifiers.new("Mirror", "MIRROR")
    m.use_axis = (x, y, False)
    return m


def frame_view():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                region = next(r for r in area.regions if r.type == "WINDOW")
                with bpy.context.temp_override(window=win, area=area, region=region):
                    bpy.ops.view3d.view_all(center=False)


def shading(kind):
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                area.spaces[0].shading.type = kind


if STEP == 0:  # clean slate: empty scene, metric units
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)
    bpy.context.scene.unit_settings.system = "METRIC"
    result["objects"] = len(bpy.data.objects)

elif STEP == 1:  # seat: 44 x 42 x 4 cm slab, top at 45 cm
    seat = box(f"{P}_seat", (0.44, 0.42, 0.04), (0.0, 0.0, 0.43))
    frame_view()
    result["made"] = seat.name

elif STEP == 2:  # one tapered leg, mirrored on X and Y -> four legs
    leg = box(f"{P}_legs", (0.036, 0.036, 0.42), (0.19, 0.18, 0.21), taper_bottom=0.75)
    mirror(leg, x=True, y=True)
    frame_view()
    result["made"] = leg.name

elif STEP == 3:  # back posts (mirrored) and backrest panel
    post = box(f"{P}_back_posts", (0.036, 0.036, 0.46), (0.19, -0.18, 0.68))
    mirror(post, x=True)
    box(f"{P}_backrest", (0.40, 0.025, 0.16), (0.0, -0.18, 0.80))
    box(f"{P}_back_rail", (0.40, 0.025, 0.04), (0.0, -0.18, 0.58))
    frame_view()
    result["made"] = [o.name for o in bpy.data.objects]

elif STEP == 4:  # declared detail: rounded edges on every part, still live
    for ob in bpy.data.objects:
        if ob.type == "MESH" and "Bevel" not in ob.modifiers:
            b = ob.modifiers.new("Bevel", "BEVEL")
            b.width = 0.004
            b.segments = 2
            b.limit_method = "ANGLE"
    result["bevelled"] = len(bpy.data.objects)

elif STEP == 5:  # material, light, camera, look
    mat = bpy.data.materials.get("MAT-chair_wood") or bpy.data.materials.new("MAT-chair_wood")
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    # Base colour is linear: a dark, saturated value reads as walnut after view transform.
    bsdf.inputs["Base Color"].default_value = (0.13, 0.05, 0.018, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.45
    for ob in bpy.data.objects:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(mat)
    light = bpy.data.objects.get("LGT-key")
    if not light:
        light = bpy.data.objects.new("LGT-key", bpy.data.lights.new("LGT-key", "AREA"))
        bpy.context.scene.collection.objects.link(light)
    light.data.energy = 150
    light.data.size = 1.5
    light.location = (1.2, 1.4, 1.8)
    light.rotation_euler = (0.75, 0.0, 2.4)
    cam = bpy.data.objects.get("CAM-main")
    if not cam:
        cam = bpy.data.objects.new("CAM-main", bpy.data.cameras.new("CAM-main"))
        bpy.context.scene.collection.objects.link(cam)
    # Front three-quarter view (the seat faces +Y; the back is at -Y).
    cam.location = (1.35, 1.6, 1.05)
    cam.rotation_euler = (1.2, 0.0, 2.43)
    bpy.context.scene.camera = cam
    shading("MATERIAL")
    frame_view()
    result["look"] = "material preview"
