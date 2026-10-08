"""Demo 002: the first slice of "Flow" (docs/showcase/01-flow.md), built live.

A 10-second flooded-forest shot: displaced terrain, an Ocean-modifier flood whose
level is chosen to submerge a declared share of the land, GN-scattered trees only
above the water, a boat that rides the waves, and a camera with declared
handheld noise. Sent through tools/live/bl.py with STEP set:
    python3 bl.py -e "STEP=1; exec(open('flow_build.py').read())"

Agent-native: geometry as data, detail as declared modifiers/GN, every rule a
named number. Checks: tools/live/checks/flow_checks.py (written first).
"""

import math
import random

import bmesh
import bpy
from mathutils import Euler, Vector
from mathutils.kdtree import KDTree

sc = bpy.context.scene
SEED = 7
SUBMERGED = 0.42       # target share of terrain area under water
TREE_MARGIN = 0.6      # trees only this far above the mean water level (m)
BOAT_HINT = Vector((-10.0, -20.0))


def link(ob, coll=None):
    (coll or sc.collection).objects.link(ob)
    return ob


def mesh_object(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return bpy.data.objects.new(name, me)


def material(name, color, rough=0.6):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    return m


def box(bm, size, center, taper_bottom=1.0):
    geom = bmesh.ops.create_cube(bm, size=1.0)["verts"]
    for v in geom:
        k = taper_bottom if v.co.z < 0 else 1.0
        v.co = Vector((v.co.x * size[0] * k + center[0], v.co.y * size[1] * k + center[1],
                       v.co.z * size[2] + center[2]))


def fcurves_of(ob):
    act = ob.animation_data.action
    try:
        from bpy_extras import anim_utils
        return anim_utils.action_get_channelbag_for_slot(act, ob.animation_data.action_slot).fcurves
    except Exception:
        return act.fcurves


def view3d_spaces():
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                yield area.spaces[0]


def look_from(loc, target):
    return (target - loc).to_track_quat("-Z", "Y").to_euler()


def sock(node, name, out=False):
    socks = node.outputs if out else node.inputs
    cands = [s for s in socks if s.name == name and getattr(s, "enabled", True)]
    return cands[0]


if STEP == 0:  # clean slate
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob)
    for coll in (bpy.data.meshes, bpy.data.materials, bpy.data.node_groups, bpy.data.textures,
                 bpy.data.collections, bpy.data.cameras, bpy.data.lights, bpy.data.actions):
        for d in list(coll):
            coll.remove(d)
    sc.unit_settings.system = "METRIC"
    sc.render.fps = 24
    sc.frame_start, sc.frame_end = 1, 240
    sc.frame_set(1)
    result["objects"] = len(bpy.data.objects)

elif STEP == 1:  # terrain: a grid plus two declared noise displacements
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=200, y_segments=200, size=60.0)
    terrain = link(mesh_object("ENV-terrain", bm))
    for name, scale, strength, depth in (("hills", 28.0, 46.0, 2), ("detail", 5.0, 2.2, 3)):
        tex = bpy.data.textures.new(f"TEX-{name}", "CLOUDS")
        tex.noise_scale, tex.noise_depth = scale, depth
        d = terrain.modifiers.new(f"Displace {name}", "DISPLACE")
        d.texture, d.strength, d.texture_coords = tex, strength, "GLOBAL"
    deps = bpy.context.evaluated_depsgraph_get()
    me = terrain.evaluated_get(deps).to_mesh()
    faces = sorted((p.center.z, p.area) for p in me.polygons)
    total, acc, W = sum(a for _, a in faces), 0.0, None
    for z, a in faces:  # area-weighted percentile = declared submerged share
        acc += a
        if acc >= SUBMERGED * total:
            W = z
            break
    zs = [v.co.z for v in me.vertices]
    terrain.evaluated_get(deps).to_mesh_clear()
    sc["water_level"] = W
    # Height-graded material: sand near water, grass, forest floor, rock on top.
    mat = material("MAT-terrain", (0.3, 0.35, 0.2), 0.9)
    nt = mat.node_tree
    geo = nt.nodes.new("ShaderNodeNewGeometry")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    rng = nt.nodes.new("ShaderNodeMapRange")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    rng.inputs["From Min"].default_value, rng.inputs["From Max"].default_value = W - 2, max(zs)
    nt.links.new(geo.outputs["Position"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], rng.inputs["Value"])
    nt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.08, (0.42, 0.36, 0.24, 1)
    el[1].position, el[1].color = 0.95, (0.48, 0.47, 0.44, 1)
    for pos, col in ((0.16, (0.17, 0.24, 0.07, 1)), (0.55, (0.08, 0.15, 0.05, 1))):
        e = el.new(pos)
        e.color = col
    nt.links.new(ramp.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    terrain.data.materials.append(mat)
    for s in view3d_spaces():
        s.region_3d.view_location = Vector((0, 0, W))
        s.region_3d.view_distance = 150
        s.region_3d.view_rotation = Euler((1.05, 0, 0.6)).to_quaternion()
    result["water_level_m"] = round(W, 2)
    result["height_range_m"] = [round(min(zs), 1), round(max(zs), 1)]

elif STEP == 2:  # the flood: Ocean modifier at the computed level, time keyed
    W = sc["water_level"]
    ocean = link(bpy.data.objects.new("ENV-flood", bpy.data.meshes.new("ENV-flood")))
    ocean.location.z = W
    m = ocean.modifiers.new("Ocean", "OCEAN")
    m.geometry_mode = "GENERATE"
    m.spatial_size, m.size, m.resolution = 140, 1.0, 20
    m.viewport_resolution = 20
    m.wave_scale, m.choppiness, m.wind_velocity = 0.55, 0.9, 9.0
    m.random_seed, m.use_normals = SEED, True
    m.time = 1.0
    m.keyframe_insert("time", frame=1)
    m.time = 11.0
    m.keyframe_insert("time", frame=240)
    for fc in fcurves_of(ocean):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
    water = material("MAT-water", (0.03, 0.09, 0.1), 0.06)
    ocean.data.materials.append(water)
    deps = bpy.context.evaluated_depsgraph_get()
    oe = ocean.evaluated_get(deps)
    xs = [v.co.x for v in oe.to_mesh().vertices]
    n = len(xs)
    oe.to_mesh_clear()
    result["ocean_verts"] = n
    result["ocean_extent_m"] = round(max(xs) - min(xs), 1)

elif STEP == 3:  # tree library + GN scatter only above water, on gentle slopes
    W = sc["water_level"]
    lib = bpy.data.collections.new("ENV-tree_library")
    sc.collection.children.link(lib)
    lib.hide_render, lib.hide_viewport = True, True
    bark = material("MAT-bark", (0.12, 0.08, 0.05), 0.8)
    leaves = [material("MAT-leaves_a", (0.06, 0.16, 0.04), 0.7),
              material("MAT-leaves_b", (0.11, 0.2, 0.05), 0.7),
              material("MAT-leaves_c", (0.05, 0.12, 0.06), 0.7)]
    for i, (h, r, kind) in enumerate(((6.0, 1.8, "round"), (8.5, 1.4, "cone"), (5.0, 2.2, "round"))):
        bm = bmesh.new()
        box(bm, (0.35, 0.35, h * 0.5), (0, 0, h * 0.25), taper_bottom=1.3)
        if kind == "round":
            g = bmesh.ops.create_icosphere(bm, subdivisions=2, radius=r)["verts"]
            for v in g:
                v.co.z = v.co.z * 1.1 + h * 0.7
        else:
            for j, (zz, rr) in enumerate(((0.35, 1.0), (0.6, 0.75), (0.82, 0.45))):
                g = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=r * rr,
                                          radius2=0.0, depth=h * 0.35)["verts"]
                for v in g:
                    v.co.z += h * zz
        ob = mesh_object(f"GEO-tree_{'abc'[i]}", bm)
        ob.data.materials.append(bark)
        ob.data.materials.append(leaves[i])
        for p in ob.data.polygons:  # canopy faces get the leaf material
            p.material_index = 1 if p.center.z > h * 0.5 or kind == "cone" and p.center.z > h * 0.3 else 0
        link(ob, lib)
    ng = bpy.data.node_groups.new("GN-forest_scatter", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N = ng.nodes.new
    gin, gout = N("NodeGroupInput"), N("NodeGroupOutput")
    pos, nrm = N("GeometryNodeInputPosition"), N("GeometryNodeInputNormal")
    sp, sn = N("ShaderNodeSeparateXYZ"), N("ShaderNodeSeparateXYZ")
    above, flat, both = N("FunctionNodeCompare"), N("FunctionNodeCompare"), N("FunctionNodeBooleanMath")
    above.operation, flat.operation, both.operation = "GREATER_THAN", "GREATER_THAN", "AND"
    sock(above, "B").default_value = W + TREE_MARGIN
    sock(flat, "B").default_value = 0.72
    dist = N("GeometryNodeDistributePointsOnFaces")
    dist.distribute_method = "POISSON"
    sock(dist, "Distance Min").default_value = 0.5
    sock(dist, "Density Max").default_value = 5.0
    sock(dist, "Seed").default_value = SEED
    coll = N("GeometryNodeCollectionInfo")
    coll.inputs["Collection"].default_value = lib
    sock(coll, "Separate Children").default_value = True
    sock(coll, "Reset Children").default_value = True
    pick = N("FunctionNodeRandomValue")
    pick.data_type = "INT"
    sock(pick, "Min").default_value, sock(pick, "Max").default_value = 0, 2
    scale = N("FunctionNodeRandomValue")
    scale.data_type = "FLOAT"
    sock(scale, "Min").default_value, sock(scale, "Max").default_value = 0.7, 1.35
    yaw = N("FunctionNodeRandomValue")
    yaw.data_type = "FLOAT"
    sock(yaw, "Min").default_value, sock(yaw, "Max").default_value = 0.0, 6.283
    cxyz, rot = N("ShaderNodeCombineXYZ"), N("FunctionNodeEulerToRotation")
    iop, join = N("GeometryNodeInstanceOnPoints"), N("GeometryNodeJoinGeometry")
    L = ng.links.new
    L(pos.outputs["Position"], sp.inputs[0])
    L(nrm.outputs["Normal"], sn.inputs[0])
    L(sock(sp, "Z", True), sock(above, "A"))
    L(sock(sn, "Z", True), sock(flat, "A"))
    L(above.outputs[0], both.inputs[0])
    L(flat.outputs[0], both.inputs[1])
    L(gin.outputs[0], dist.inputs["Mesh"])
    L(both.outputs[0], dist.inputs["Selection"])
    L(dist.outputs["Points"], iop.inputs["Points"])
    # Second filter on each point's own height: a point can land on a low corner of a high face.
    ppos, psep, pabove = N("GeometryNodeInputPosition"), N("ShaderNodeSeparateXYZ"), N("FunctionNodeCompare")
    pabove.operation = "GREATER_THAN"
    sock(pabove, "B").default_value = W + TREE_MARGIN
    L(ppos.outputs["Position"], psep.inputs[0])
    L(sock(psep, "Z", True), sock(pabove, "A"))
    L(pabove.outputs[0], iop.inputs["Selection"])
    L(coll.outputs[0], iop.inputs["Instance"])
    sock(iop, "Pick Instance").default_value = True
    L(sock(pick, "Value", True), iop.inputs["Instance Index"])
    L(sock(yaw, "Value", True), cxyz.inputs["Z"])
    L(cxyz.outputs[0], rot.inputs[0])
    L(rot.outputs[0], iop.inputs["Rotation"])
    L(sock(scale, "Value", True), iop.inputs["Scale"])
    L(gin.outputs[0], join.inputs[0])
    L(iop.outputs[0], join.inputs[0])
    L(join.outputs[0], gout.inputs[0])
    terrain = bpy.data.objects["ENV-terrain"]
    terrain.modifiers.new("Forest", "NODES").node_group = ng
    deps = bpy.context.evaluated_depsgraph_get()
    result["tree_instances"] = sum(1 for i in deps.object_instances
                                   if i.is_instance and i.parent and i.parent.original == terrain)

elif STEP == 4:  # boat as data, placed in deep water, keyed to ride the waves
    W = sc["water_level"]
    terrain = bpy.data.objects["ENV-terrain"]
    deps = bpy.context.evaluated_depsgraph_get()
    tme = terrain.evaluated_get(deps).to_mesh()
    deep = [v.co.copy() for v in tme.vertices if v.co.z < W - 2.0]
    # Open water: the deep point farthest from any land (sampled), so the boat can be seen.
    land = KDTree(len(tme.vertices))
    n_land = 0
    for v in tme.vertices:
        if v.co.z > W:
            land.insert(v.co.copy(), n_land)
            n_land += 1
    land.balance()
    spot = max(deep[::7], key=lambda c: land.find(Vector((c.x, c.y, W)))[2] - 0.05 * c.xy.length)
    result["boat_to_land_m"] = round(land.find(Vector((spot.x, spot.y, W)))[2], 1)
    terrain.evaluated_get(deps).to_mesh_clear()
    bm = bmesh.new()
    box(bm, (1.3, 3.4, 0.7), (0, 0, 0.1), taper_bottom=0.45)      # hull, waterline at origin
    box(bm, (1.1, 1.2, 0.35), (0, -0.4, 0.6))                     # cabin
    box(bm, (0.08, 0.08, 3.6), (0, 0.5, 2.25))                    # mast
    sail = [bm.verts.new(c) for c in ((0, 0.55, 0.9), (0, 0.55, 3.9), (0, 1.9, 0.9))]
    bm.faces.new(sail)
    boat = link(mesh_object("GEO-boat", bm))
    boat.data.materials.append(material("MAT-boat", (0.55, 0.53, 0.5), 0.5))
    boat.location = (spot.x, spot.y, W)
    boat.rotation_euler.z = 0.6
    ocean = bpy.data.objects["ENV-flood"]
    probes = ((0, 0), (0, 1.5), (0, -1.5), (0.6, 0), (-0.6, 0))
    for f in range(sc.frame_start, sc.frame_end + 1):
        sc.frame_set(f)
        deps = bpy.context.evaluated_depsgraph_get()
        oe = ocean.evaluated_get(deps)
        ome = oe.to_mesh()
        kd = KDTree(len(ome.vertices))
        for i, v in enumerate(ome.vertices):
            kd.insert(ocean.matrix_world @ v.co, i)
        kd.balance()
        rz = Euler((0, 0, boat.rotation_euler.z)).to_matrix()
        h = []
        for px, py in probes:
            p = Vector((spot.x, spot.y, W)) + rz @ Vector((px, py, 0))
            co, _, _ = kd.find(p)
            h.append(co.z)
        oe.to_mesh_clear()
        boat.location.z = h[0]
        boat.rotation_euler.x = math.atan2(h[1] - h[2], 3.0)
        boat.rotation_euler.y = -math.atan2(h[3] - h[4], 1.2)
        boat.keyframe_insert("location", index=2, frame=f)
        boat.keyframe_insert("rotation_euler", frame=f)
    sc.frame_set(1)
    sc["boat_xy"] = [spot.x, spot.y]
    result["boat_at"] = [round(spot.x, 1), round(spot.y, 1)]

elif STEP == 5:  # camera glides past the boat; handheld = declared noise
    bx, by = sc["boat_xy"]
    W = sc["water_level"]
    target = Vector((bx, by, W + 1.0))
    from mathutils.bvhtree import BVHTree
    deps = bpy.context.evaluated_depsgraph_get()
    terrain = bpy.data.objects["ENV-terrain"]
    tme = terrain.evaluated_get(deps).to_mesh()
    tbvh = BVHTree.FromPolygons([v.co.copy() for v in tme.vertices], [p.vertices[:] for p in tme.polygons])
    terrain.evaluated_get(deps).to_mesh_clear()
    trees, tree_z, nt = KDTree(20000), [], 0
    for i in deps.object_instances:
        if i.is_instance and i.parent and i.parent.original == terrain:
            loc = i.matrix_world.translation
            trees.insert(Vector((loc.x, loc.y, 0)), nt)
            tree_z.append(loc.z)
            nt += 1
    trees.balance()
    TREE_TOP = 12.0  # tallest tree incl. random scale (8.5 m x 1.35)

    def ground(x, y):
        hit, *_ = tbvh.ray_cast(Vector((x, y, 60)), Vector((0, 0, -1)))
        return hit.z if hit else W - 5

    def blocked(q, canopy):  # inside some tree's canopy cylinder?
        return any(q.z < tree_z[i] + TREE_TOP for _, i, _ in trees.find_range(Vector((q.x, q.y, 0)), canopy))

    def ok(p, canopy):  # clear of trees and terrain, sight line to the boat clear
        if blocked(p, canopy + 1.0):
            return False
        d = target - p
        if tbvh.ray_cast(p, d.normalized(), d.length)[0] is not None:
            return False
        return not any(blocked(p + d * (t / 20), canopy) for t in range(1, 20))

    best, level = None, None
    for canopy, lo, hi in ((3.0, 0.6, 1.4), (2.5, 0.5, 1.6), (2.0, 0.4, 1.8)):
        cands = []
        for k in range(72):
            a = k * math.tau / 72
            for r in (18, 22, 26, 30):
                x, y = target.x + math.cos(a) * r, target.y + math.sin(a) * r
                p = Vector((x, y, max(W + 4.5, ground(x, y) + TREE_TOP + 1.5)))
                if ok(p, canopy):
                    cands.append((a, r, p))
        pairs = [(c1, c2) for c1 in cands for c2 in cands
                 if lo < (c2[0] - c1[0]) % math.tau < hi and abs(c1[1] - c2[1]) <= 4]
        if pairs:  # prefer low cameras (closest to the water) at ~22 m
            best = min(pairs, key=lambda pr: pr[0][2].z + pr[1][2].z + abs(pr[0][1] - 22) + abs(pr[1][1] - 22))
            level = {"canopy_radius_m": canopy}
            break
    result["camera_rule_level"] = level
    result["camera_candidates"] = len(cands)
    cam = link(bpy.data.objects.new("CAM-main", bpy.data.cameras.new("CAM-main")))
    cam.data.lens = 26
    sc.camera = cam
    for f, c in ((1, best[0]), (240, best[1])):
        cam.location = c[2]
        cam.rotation_euler = look_from(cam.location, target)
        cam.keyframe_insert("location", frame=f)
        cam.keyframe_insert("rotation_euler", frame=f)
    for fc in fcurves_of(cam):
        for k in fc.keyframe_points:
            k.interpolation = "LINEAR"
        if fc.data_path == "rotation_euler":
            n = fc.modifiers.new("NOISE")
            n.strength, n.scale, n.phase = 0.06, 22.0, 3.0 + fc.array_index * 11
    for s in view3d_spaces():
        s.region_3d.view_perspective = "CAMERA"
    result["camera"] = "keyed + noise"

elif STEP == 6:  # light, haze, render settings, scene-lit viewport
    sun = link(bpy.data.objects.new("LGT-sun", bpy.data.lights.new("LGT-sun", "SUN")))
    sun.data.energy, sun.data.angle = 3.5, math.radians(3)
    sun.data.color = (1.0, 0.86, 0.68)
    sun.rotation_euler = (math.radians(62), 0, math.radians(-35))
    world = sc.world or bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes["Background"].inputs["Color"].default_value = (0.42, 0.55, 0.68, 1)
    nt.nodes["Background"].inputs["Strength"].default_value = 0.9
    # Haze as a bounded volume: a world volume in EEVEE absorbs the infinitely far sky (all black).
    bm = bmesh.new()
    box(bm, (170, 170, 46), (0, 0, 8))
    haze = link(mesh_object("ENV-haze", bm))
    hm = bpy.data.materials.new("MAT-haze")
    hm.use_nodes = True
    hn = hm.node_tree
    hn.nodes.remove(hn.nodes["Principled BSDF"])
    vol = hn.nodes.new("ShaderNodeVolumeScatter")
    vol.inputs["Density"].default_value = 0.006
    vol.inputs["Color"].default_value = (0.82, 0.88, 0.95, 1)
    hn.links.new(vol.outputs[0], hn.nodes["Material Output"].inputs["Volume"])
    haze.data.materials.append(hm)
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 3840, 2160
    sc.eevee.taa_render_samples = 32
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = bpy.path.abspath("//frames/") if bpy.data.filepath else "/tmp/flow_frames/"
    for s in view3d_spaces():
        s.shading.type = "MATERIAL"
        s.shading.use_scene_lights = True
        s.shading.use_scene_world = True
    result["look"] = "sun + haze, EEVEE 4K"
