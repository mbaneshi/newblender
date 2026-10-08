"""Demo 003: first slice of "Charge" (docs/showcase/03-charge.md), built live.

A 20 x 12 x 6 m battery-factory bay from a modular kit (data + declared Bevel,
Array, Mirror, Boolean), 2 x 8 steel racks with 768 flickering battery cells,
pillars, pipes, a slatted ceiling throwing light shafts through haze, CC0 Poly
Haven PBR textures, and an FX beat at frame 48: muzzle flash, analytic GN sparks
and a volumetric smoke puff. Sent through tools/live/bl.py with STEP set.
Checks (written first): tools/live/checks/charge_checks.py.
"""

import math
import os

import bmesh
import bpy
from mathutils import Vector

sc = bpy.context.scene
TEX = os.path.expanduser("~/newblender-data/assets/polyhaven")
FLOOR_TOP = 0.1
FX_ORIGIN = Vector((7.4, 0.0, 1.35))
FX_FRAME = 48


def link(ob, coll=None):
    (coll or sc.collection).objects.link(ob)
    return ob


def box(bm, size, center):
    for v in bmesh.ops.create_cube(bm, size=1.0)["verts"]:
        v.co = Vector((v.co.x * size[0] + center[0], v.co.y * size[1] + center[1], v.co.z * size[2] + center[2]))


def tube_x(bm, radius, length, center, segments=16):
    verts = bmesh.ops.create_cone(bm, cap_ends=True, segments=segments, radius1=radius,
                                  radius2=radius, depth=length)["verts"]
    bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"))
    bmesh.ops.translate(bm, verts=verts, vec=center)


def box_uv(bm, tile=2.0):
    """World-scale box projection as data: each face maps on its dominant axis plane."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][ax]
        for loop in f.loops:
            loop[uv].uv = (loop.vert.co[a] / tile, loop.vert.co[b] / tile)


def mesh_object(name, bm, uv_tile=2.0):
    bm.normal_update()
    box_uv(bm, uv_tile)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def bevel(ob, width=0.008):
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width, b.segments, b.limit_method, b.harden_normals = width, 2, "ANGLE", True
    return b


def array(ob, count, offset):
    a = ob.modifiers.new("Array", "ARRAY")
    a.count, a.use_relative_offset, a.use_constant_offset = count, False, True
    a.constant_offset_displace = offset
    return a


def mirror_y(ob):
    m = ob.modifiers.new("Mirror", "MIRROR")
    m.use_axis = (False, True, False)
    return m


def pbr(name, asset, metallic=None, rough_scale=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]

    def img(kind, color=True):
        for ext in ("jpg", "png"):
            path = f"{TEX}/{asset}/{kind}.{ext}"
            try:
                im = bpy.data.images.load(path, check_existing=True)
            except RuntimeError:
                continue
            if not color:
                im.colorspace_settings.name = "Non-Color"
            n = nt.nodes.new("ShaderNodeTexImage")
            n.image = im
            return n
        return None

    nt.links.new(img("diff").outputs["Color"], b.inputs["Base Color"])
    rough = img("rough", False)
    if rough_scale != 1.0:  # art adjustment: scale the authored roughness
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation, mul.inputs[1].default_value = "MULTIPLY", rough_scale
        nt.links.new(rough.outputs["Color"], mul.inputs[0])
        nt.links.new(mul.outputs[0], b.inputs["Roughness"])
    else:
        nt.links.new(rough.outputs["Color"], b.inputs["Roughness"])
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(img("nor", False).outputs["Color"], nm.inputs["Color"])
    nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    met = img("metal", False)
    if met is not None:
        nt.links.new(met.outputs["Color"], b.inputs["Metallic"])
    elif metallic is not None:
        b.inputs["Metallic"].default_value = metallic
    return m


def channelbag_fcurves(idblock):
    ad = idblock.animation_data
    from bpy_extras import anim_utils
    return anim_utils.action_get_channelbag_for_slot(ad.action, ad.action_slot).fcurves


def key(sock, pairs, interp="LINEAR", path="default_value"):
    for f, v in pairs:
        setattr(sock, path, v)
        sock.keyframe_insert(path, frame=f)


def sock(node, name, out=False):
    socks = node.outputs if out else node.inputs
    return [s for s in socks if s.name == name and getattr(s, "enabled", True)][0]


def view3d_spaces():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                yield area.spaces[0]


if STEP == 0:  # clean slate
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.node_groups, bpy.data.images,
                 bpy.data.collections, bpy.data.cameras, bpy.data.lights, bpy.data.actions, bpy.data.textures):
        for d in list(coll):
            coll.remove(d)
    sc.unit_settings.system = "METRIC"
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, 96
    sc.frame_set(1)
    for s in view3d_spaces():
        s.region_3d.view_perspective = "PERSP"
        s.region_3d.view_location = Vector((0, 0, 2.5))
        s.region_3d.view_distance = 34
        s.region_3d.view_rotation = __import__("mathutils").Euler((1.1, 0, -0.9)).to_quaternion()
    result["objects"] = len(bpy.data.objects)

elif STEP == 1:  # shell: floor, walls (doorway by Boolean), slatted ceiling
    bm = bmesh.new()
    box(bm, (20, 12, FLOOR_TOP), (0, 0, FLOOR_TOP / 2))
    link(mesh_object("GEO-floor", bm))
    bm = bmesh.new()
    box(bm, (0.3, 12, 6), (9.85, 0, 3))
    back = link(mesh_object("GEO-wall_back", bm))
    bm = bmesh.new()
    box(bm, (1.0, 2.6, 3.2), (9.85, -2.5, FLOOR_TOP + 1.6))
    cutter = link(mesh_object("GEO-cutter_door", bm))
    cutter.display_type, cutter.hide_render = "WIRE", True
    bo = back.modifiers.new("Doorway", "BOOLEAN")
    bo.operation, bo.object, bo.solver = "DIFFERENCE", cutter, "EXACT"
    bm = bmesh.new()
    box(bm, (0.3, 12, 6), (-9.85, 0, 3))
    link(mesh_object("GEO-wall_front", bm))
    bm = bmesh.new()
    box(bm, (19.4, 0.3, 6), (0, 5.85, 3))
    mirror_y(link(mesh_object("GEO-wall_sides", bm)))
    bm = bmesh.new()
    box(bm, (0.24, 11.4, 0.35), (-9.45, 0, 5.825))
    slats = link(mesh_object("GEO-ceiling_slats", bm))
    array(slats, 38, (0.51, 0, 0))
    for o in (back, slats):
        bevel(o)
    result["shell"] = [o.name for o in bpy.data.objects]

elif STEP == 2:  # pillars and pipes: one part each, multiplied by declared Array + Mirror
    bm = bmesh.new()
    box(bm, (0.45, 0.45, 5.48), (-6, 4.75, FLOOR_TOP + 2.74))
    pillars = link(mesh_object("GEO-pillars", bm))
    array(pillars, 3, (6, 0, 0))
    mirror_y(pillars)
    bevel(pillars, 0.015)
    bm = bmesh.new()
    tube_x(bm, 0.11, 19.2, (0, 3.4, 5.25))
    pipes = link(mesh_object("GEO-pipes", bm), )
    array(pipes, 3, (0, -0.32, 0))
    mirror_y(pipes)
    result["parts"] = ["GEO-pillars", "GEO-pipes"]

elif STEP == 3:  # one rack as data -> Array x8 at 2.0 m -> Mirror to the other row
    bm = bmesh.new()
    x0, y0 = -7.0, 1.5
    for sx in (-0.87, 0.87):
        for sy in (-0.27, 0.27):
            box(bm, (0.06, 0.06, 2.3), (x0 + sx, y0 + sy, FLOOR_TOP + 1.15))
    for z in (0.35, 0.9, 1.45, 2.0):
        box(bm, (1.8, 0.6, 0.04), (x0, y0, FLOOR_TOP + z))
    rack = link(mesh_object("GEO-rack", bm, uv_tile=1.0))
    array(rack, 8, (2.0, 0, 0))
    mirror_y(rack)
    bevel(rack, 0.004)
    result["rack"] = "8 x 2 declared"

elif STEP == 4:  # 768 battery cells: points as data, cells instanced by GN, per-instance flicker phase
    lib = bpy.data.collections.new("LIB-parts")
    sc.collection.children.link(lib)
    lib.hide_render = lib.hide_viewport = True
    bm = bmesh.new()
    v = bmesh.ops.create_cone(bm, cap_ends=True, segments=12, radius1=0.07, radius2=0.07, depth=0.22)["verts"]
    bmesh.ops.translate(bm, verts=v, vec=(0, 0, 0.11))
    cell = link(mesh_object("GEO-cell", bm, uv_tile=0.3), lib)
    bm = bmesh.new()
    for rack_i in range(8):
        for side in (1, -1):
            for z in (0.35, 0.9, 1.45, 2.0):
                for ix in range(6):
                    for iy in (-0.13, 0.13):
                        bm.verts.new((-7.0 + 2.0 * rack_i - 0.7 + 0.28 * ix, side * (1.5 + iy), FLOOR_TOP + z + 0.02))
    pts = bpy.data.meshes.new("GEO-battery_cells")
    bm.to_mesh(pts)
    bm.free()
    cells = link(bpy.data.objects.new("GEO-battery_cells", pts))
    ng = bpy.data.node_groups.new("GN-battery_cells", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes.new, ng.links.new
    gin, gout = N("NodeGroupInput"), N("NodeGroupOutput")
    m2p, oi, iop = N("GeometryNodeMeshToPoints"), N("GeometryNodeObjectInfo"), N("GeometryNodeInstanceOnPoints")
    oi.inputs["Object"].default_value = cell
    rnd = N("FunctionNodeRandomValue")
    rnd.data_type = "FLOAT"
    store = N("GeometryNodeStoreNamedAttribute")
    store.data_type, store.domain = "FLOAT", "INSTANCE"
    store.inputs["Name"].default_value = "flicker_phase"
    L(gin.outputs[0], m2p.inputs[0])
    L(m2p.outputs[0], iop.inputs["Points"])
    L(sock(oi, "Geometry", True), iop.inputs["Instance"])
    L(iop.outputs[0], store.inputs["Geometry"])
    L(sock(rnd, "Value", True), sock(store, "Value"))
    L(store.outputs[0], gout.inputs[0])
    cells.modifiers.new("Cells", "NODES").node_group = ng
    # Cell material: dark casing + cyan emission, flicker = sin(frame * speed + phase)
    m = bpy.data.materials.new("MAT-cell")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.02, 0.025, 0.03, 1)
    b.inputs["Roughness"].default_value = 0.35
    b.inputs["Emission Color"].default_value = (0.03, 0.55, 1.0, 1)
    attr = nt.nodes.new("ShaderNodeAttribute")
    attr.attribute_type, attr.attribute_name = "INSTANCER", "flicker_phase"
    fr = nt.nodes.new("ShaderNodeValue")
    fr.name = "frame_value"
    drv = fr.outputs[0].driver_add("default_value").driver
    drv.type, drv.expression = "SCRIPTED", "frame"
    ops = []
    for op, val in (("MULTIPLY", 6.283), ("MULTIPLY_ADD", None), ("SINE", None), ("MULTIPLY_ADD", None)):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        ops.append(n)
    ops[0].inputs[1].default_value = 6.283
    nt.links.new(attr.outputs["Fac"], ops[0].inputs[0])
    nt.links.new(fr.outputs[0], ops[1].inputs[0])
    ops[1].inputs[1].default_value = 0.35
    nt.links.new(ops[0].outputs[0], ops[1].inputs[2])
    nt.links.new(ops[1].outputs[0], ops[2].inputs[0])
    nt.links.new(ops[2].outputs[0], ops[3].inputs[0])
    ops[3].inputs[1].default_value, ops[3].inputs[2].default_value = 0.35, 1.0   # 0.65 .. 1.35
    nt.links.new(ops[3].outputs[0], b.inputs["Emission Strength"])
    cell.data.materials.append(m)
    deps = bpy.context.evaluated_depsgraph_get()
    result["cells"] = sum(1 for i in deps.object_instances if i.is_instance and i.parent and i.parent.original == cells)

elif STEP == 5:  # CC0 PBR materials by naming rule
    rules = {
        "GEO-floor": pbr("MAT-concrete_floor", "concrete_floor_worn_001", 0.0),
        "GEO-wall": pbr("MAT-concrete_wall", "concrete_floor_02", 0.0),
        "GEO-rack": pbr("MAT-rack_paint", "blue_metal_plate", 0.0),
        "GEO-pillars": pbr("MAT-steel_plate", "metal_plate"),
        "GEO-pipes": None,
        "GEO-ceiling": pbr("MAT-corrugated", "corrugated_iron", rough_scale=0.9),
    }
    rules["GEO-pipes"] = rules["GEO-pillars"]
    for o in bpy.data.objects:
        if o.type != "MESH" or o.name in ("GEO-cell", "GEO-battery_cells", "GEO-cutter_door"):
            continue
        for prefix, mat in rules.items():
            if o.name.startswith(prefix):
                o.data.materials.clear()
                o.data.materials.append(mat)
    for s in view3d_spaces():
        s.shading.type = "MATERIAL"
    result["materials"] = sorted(m.name for m in bpy.data.materials)

elif STEP == 6:  # light: cold skylight above the slats, warm rim from the doorway, haze
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0.004, 0.005, 0.007, 1)
    sky = link(bpy.data.objects.new("LGT-skylight", bpy.data.lights.new("LGT-skylight", "AREA")))
    sky.data.shape, sky.data.size, sky.data.size_y = "RECTANGLE", 19, 10
    sky.data.energy, sky.data.color = 9000, (0.72, 0.84, 1.0)
    sky.location = (0, 0, 6.5)
    rim = link(bpy.data.objects.new("LGT-door_rim", bpy.data.lights.new("LGT-door_rim", "AREA")))
    rim.data.size, rim.data.energy, rim.data.color = 2.0, 900, (1.0, 0.62, 0.32)
    rim.location = (11.0, -2.5, 1.9)
    rim.rotation_euler = (0, -math.pi / 2, 0)
    bm = bmesh.new()
    box(bm, (19.3, 11.3, 5.6), (0, 0, FLOOR_TOP + 2.85))
    haze = link(mesh_object("FX-haze", bm))
    hm = bpy.data.materials.new("MAT-haze")
    hm.use_nodes = True
    hn = hm.node_tree
    hn.nodes.remove(hn.nodes["Principled BSDF"])
    vol = hn.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Density"].default_value = 0.018
    vol.inputs["Color"].default_value = (0.85, 0.9, 1.0, 1)
    hn.links.new(vol.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
    haze.data.materials.append(hm)
    for s in view3d_spaces():
        s.shading.use_scene_lights = s.shading.use_scene_world = True
    result["light"] = "skylight + rim + haze"

elif STEP == 7:  # FX at frame 48: muzzle flash, sparks (analytic GN), smoke puff
    O = FX_ORIGIN
    # Muzzle flash: three crossed emissive cards + a short cone, emission keyed CONSTANT.
    bm = bmesh.new()
    for ang in (0, 1.047, 2.094):
        c, s_ = math.cos(ang), math.sin(ang)
        quad = [bm.verts.new(O + Vector((-dx, c * dy, s_ * dy))) for dx, dy in ((0, -0.45), (1.35, -0.12), (1.35, 0.12), (0, 0.45))]
        bm.faces.new(quad)
    me = bpy.data.meshes.new("FX-muzzle_flash")
    bm.to_mesh(me)
    bm.free()
    flash = link(bpy.data.objects.new("FX-muzzle_flash", me))
    fm = bpy.data.materials.new("MAT-fx_flash")
    fm.use_nodes = True
    fn = fm.node_tree
    fn.nodes.remove(fn.nodes["Principled BSDF"])
    em = fn.nodes.new("ShaderNodeEmission")
    em.name = "Emission"
    em.inputs["Color"].default_value = (1.0, 0.72, 0.35, 1)
    fn.links.new(em.outputs[0], fn.nodes["Material Output"].inputs["Surface"])
    key(em.inputs["Strength"], ((FX_FRAME - 1, 0.0), (FX_FRAME, 140.0), (FX_FRAME + 1, 70.0), (FX_FRAME + 2, 0.0)))
    for fc in channelbag_fcurves(fn):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"
    flash.data.materials.append(fm)
    fl = link(bpy.data.objects.new("LGT-flash", bpy.data.lights.new("LGT-flash", "POINT")))
    fl.location = O - Vector((0.4, 0, 0))
    fl.data.color, fl.data.shadow_soft_size = (1.0, 0.7, 0.35), 0.1
    key(fl.data, ((FX_FRAME - 1, 0.0), (FX_FRAME, 2500.0), (FX_FRAME + 1, 1200.0), (FX_FRAME + 2, 0.0)), path="energy")
    for fc in channelbag_fcurves(fl.data):
        for k in fc.keyframe_points:
            k.interpolation = "CONSTANT"
    # Sparks: 160 points, p = O + v t + g t^2 / 2, t = (frame - 48) / fps, alive 0 < t < 0.7 s.
    lib = bpy.data.collections["LIB-parts"]
    bm = bmesh.new()
    box(bm, (0.06, 0.008, 0.008), (0, 0, 0))
    shape = link(mesh_object("FX-spark_shape", bm, 0.1), lib)
    sm = bpy.data.materials.new("MAT-fx_spark")
    sm.use_nodes = True
    sn = sm.node_tree
    sn.nodes.remove(sn.nodes["Principled BSDF"])
    se = sn.nodes.new("ShaderNodeEmission")
    se.inputs["Color"].default_value, se.inputs["Strength"].default_value = (1.0, 0.55, 0.2, 1), 40
    sn.links.new(se.outputs[0], sn.nodes["Material Output"].inputs["Surface"])
    shape.data.materials.append(sm)
    ng = bpy.data.node_groups.new("GN-sparks", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes.new, ng.links.new
    gout = N("NodeGroupOutput")
    pts, st = N("GeometryNodePoints"), N("GeometryNodeInputSceneTime")
    sock(pts, "Count").default_value = 160
    tsub, tdiv = N("ShaderNodeMath"), N("ShaderNodeMath")
    tsub.operation, tdiv.operation = "SUBTRACT", "DIVIDE"
    tsub.inputs[1].default_value, tdiv.inputs[1].default_value = FX_FRAME, sc.render.fps
    L(sock(st, "Frame", True), tsub.inputs[0])
    L(tsub.outputs[0], tdiv.inputs[0])
    dirn = N("FunctionNodeRandomValue")
    dirn.data_type = "FLOAT_VECTOR"
    sock(dirn, "Min").default_value, sock(dirn, "Max").default_value = (-1.0, -0.7, -0.1), (-0.3, 0.7, 0.9)
    spd = N("FunctionNodeRandomValue")
    spd.data_type = "FLOAT"
    sock(spd, "Min").default_value, sock(spd, "Max").default_value = 2.5, 7.0
    sock(spd, "Seed").default_value = 3
    norm, vel = N("ShaderNodeVectorMath"), N("ShaderNodeVectorMath")
    norm.operation, vel.operation = "NORMALIZE", "SCALE"
    L(sock(dirn, "Value", True), norm.inputs[0])
    L(norm.outputs[0], vel.inputs[0])
    L(sock(spd, "Value", True), sock(vel, "Scale"))
    vt, t2, gt2, s1, s2 = (N("ShaderNodeVectorMath"), N("ShaderNodeMath"), N("ShaderNodeVectorMath"),
                           N("ShaderNodeVectorMath"), N("ShaderNodeVectorMath"))
    vt.operation, t2.operation, gt2.operation, s1.operation, s2.operation = "SCALE", "MULTIPLY", "SCALE", "ADD", "ADD"
    L(vel.outputs[0], vt.inputs[0])
    L(tdiv.outputs[0], sock(vt, "Scale"))
    L(tdiv.outputs[0], t2.inputs[0])
    L(tdiv.outputs[0], t2.inputs[1])
    gt2.inputs[0].default_value = (0, 0, -4.9)
    L(t2.outputs[0], sock(gt2, "Scale"))
    L(vt.outputs[0], s1.inputs[0])
    L(gt2.outputs[0], s1.inputs[1])
    s2.inputs[1].default_value = tuple(O)
    L(s1.outputs[0], s2.inputs[0])
    L(s2.outputs[0], sock(pts, "Position"))
    gvt, vnow = N("ShaderNodeVectorMath"), N("ShaderNodeVectorMath")
    gvt.operation, vnow.operation = "SCALE", "ADD"
    gvt.inputs[0].default_value = (0, 0, -9.8)
    L(tdiv.outputs[0], sock(gvt, "Scale"))
    L(vel.outputs[0], vnow.inputs[0])
    L(gvt.outputs[0], vnow.inputs[1])
    dead_lo, dead_hi, dead = N("FunctionNodeCompare"), N("FunctionNodeCompare"), N("FunctionNodeBooleanMath")
    dead_lo.operation, dead_hi.operation, dead.operation = "LESS_THAN", "GREATER_THAN", "OR"
    sock(dead_lo, "B").default_value, sock(dead_hi, "B").default_value = 0.0, 0.7
    L(tdiv.outputs[0], sock(dead_lo, "A"))
    L(tdiv.outputs[0], sock(dead_hi, "A"))
    L(dead_lo.outputs[0], dead.inputs[0])
    L(dead_hi.outputs[0], dead.inputs[1])
    delete = N("GeometryNodeDeleteGeometry")
    delete.domain = "POINT"
    L(pts.outputs[0], delete.inputs["Geometry"])
    L(dead.outputs[0], delete.inputs["Selection"])
    align, oi, iop = N("FunctionNodeAlignRotationToVector"), N("GeometryNodeObjectInfo"), N("GeometryNodeInstanceOnPoints")
    L(vnow.outputs[0], sock(align, "Vector"))
    oi.inputs["Object"].default_value = shape
    L(delete.outputs[0], iop.inputs["Points"])
    L(sock(oi, "Geometry", True), iop.inputs["Instance"])
    L(align.outputs[0], iop.inputs["Rotation"])
    L(iop.outputs[0], gout.inputs[0])
    sparks = link(bpy.data.objects.new("FX-sparks", bpy.data.meshes.new("FX-sparks")))
    sparks.modifiers.new("Sparks", "NODES").node_group = ng
    # Smoke: a volume box; density = keyed scale x 4D noise x radial falloff with a keyed radius.
    bm = bmesh.new()
    box(bm, (3.4, 3.4, 3.0), O + Vector((-1.0, 0, 0.6)))
    smoke = link(mesh_object("FX-smoke", bm))
    km = bpy.data.materials.new("MAT-fx_smoke")
    km.use_nodes = True
    kn = km.node_tree
    kn.nodes.remove(kn.nodes["Principled BSDF"])
    vol = kn.nodes.new("ShaderNodeVolumePrincipled")
    vol.inputs["Color"].default_value = (0.3, 0.3, 0.32, 1)
    tc = kn.nodes.new("ShaderNodeTexCoord")
    centre = kn.nodes.new("ShaderNodeVectorMath")
    centre.operation = "DISTANCE"
    centre.inputs[1].default_value = tuple(O + Vector((-0.7, 0, 0.35)))
    kn.links.new(tc.outputs["Object"], centre.inputs[0])
    radius = kn.nodes.new("ShaderNodeValue")
    radius.name = "radius"
    key(radius.outputs[0], ((FX_FRAME - 1, 0.3), (FX_FRAME + 40, 1.7)))
    ratio, fall = kn.nodes.new("ShaderNodeMath"), kn.nodes.new("ShaderNodeMath")
    ratio.operation, fall.operation = "DIVIDE", "SUBTRACT"
    kn.links.new(centre.outputs["Value"], ratio.inputs[0])
    kn.links.new(radius.outputs[0], ratio.inputs[1])
    fall.inputs[0].default_value = 1.0
    fall.use_clamp = True
    kn.links.new(ratio.outputs[0], fall.inputs[1])
    noise = kn.nodes.new("ShaderNodeTexNoise")
    noise.noise_dimensions = "4D"
    noise.inputs["Scale"].default_value, noise.inputs["Detail"].default_value = 2.2, 6
    kn.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    key(noise.inputs["W"], ((FX_FRAME - 1, 0.0), (FX_FRAME + 48, 1.5)))
    dens = kn.nodes.new("ShaderNodeValue")
    dens.name = "density_scale"
    key(dens.outputs[0], ((FX_FRAME - 1, 0.0), (FX_FRAME + 1, 25.0), (FX_FRAME + 27, 9.0), (FX_FRAME + 42, 0.0)))
    m1, m2 = kn.nodes.new("ShaderNodeMath"), kn.nodes.new("ShaderNodeMath")
    m1.operation = m2.operation = "MULTIPLY"
    kn.links.new(noise.outputs["Fac"], m1.inputs[0])
    kn.links.new(fall.outputs[0], m1.inputs[1])
    kn.links.new(m1.outputs[0], m2.inputs[0])
    kn.links.new(dens.outputs[0], m2.inputs[1])
    kn.links.new(m2.outputs[0], vol.inputs["Density"])
    kn.links.new(vol.outputs[0], kn.nodes["Material Output"].inputs["Volume"])
    for fc in channelbag_fcurves(kn):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    smoke.data.materials.append(km)
    result["fx"] = ["FX-muzzle_flash", "LGT-flash", "FX-sparks", "FX-smoke"]

elif STEP == 8:  # camera push-in down the aisle; render settings
    cam = link(bpy.data.objects.new("CAM-main", bpy.data.cameras.new("CAM-main")))
    cam.data.lens = 28
    sc.camera = cam
    target = Vector((8.0, 0.0, 1.45))
    for f, loc in ((1, Vector((-9.0, -0.45, 1.75))), (sc.frame_end, Vector((-3.0, -0.25, 1.6)))):
        cam.location = loc
        cam.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 256
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    for s in view3d_spaces():
        s.region_3d.view_perspective = "CAMERA"
    result["camera"] = "push-in 1-96"
