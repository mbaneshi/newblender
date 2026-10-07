"""Census of what a real .blend file actually contains.

Run headless, never executing embedded scripts or drivers:
    Blender --factory-startup --disable-autoexec -b FILE.blend --python census.py -- OUT.json

Counts what professionals actually used: object types, mesh topology (tri/quad/
ngon), modifier stacks (live vs. how deep), Geometry Nodes usage, UVs, vertex
groups, shape keys, sculpt data (multires), linking and overrides, node types.
Reads data only; changes nothing and saves nothing.
"""

import json
import sys
from collections import Counter

import bpy


def mesh_stats(me):
    sizes = Counter()
    for p in me.polygons:
        n = p.loop_total
        sizes["tri" if n == 3 else "quad" if n == 4 else "ngon"] += 1
    return {
        "verts": len(me.vertices),
        "faces": len(me.polygons),
        "tri": sizes["tri"], "quad": sizes["quad"], "ngon": sizes["ngon"],
        "uv_layers": len(me.uv_layers),
        "color_attributes": len(me.color_attributes),
        "attributes": sorted(a.name for a in me.attributes if not a.name.startswith(".")),
        "shape_keys": len(me.shape_keys.key_blocks) if me.shape_keys else 0,
        "materials": len(me.materials),
        "linked": me.library is not None,
    }


def node_group_stats(ng):
    return {
        "type": ng.bl_idname,
        "nodes": len(ng.nodes),
        "node_types": Counter(n.bl_idname for n in ng.nodes),
        "is_asset": ng.asset_data is not None,
        "linked": ng.library is not None,
    }


def main(out_path):
    objects = bpy.data.objects
    obj_types = Counter(o.type for o in objects)
    modifier_types = Counter()
    stack_depths = Counter()
    gn_groups = Counter()
    constraint_types = Counter()
    modifiers_render_off = 0
    instancers = 0
    for o in objects:
        stack_depths[len(o.modifiers)] += 1
        for m in o.modifiers:
            modifier_types[m.type] += 1
            if not m.show_render:
                modifiers_render_off += 1
            if m.type == "NODES" and m.node_group:
                gn_groups[m.node_group.name] += 1
            if m.type == "MULTIRES":
                modifier_types["MULTIRES_levels_" + str(m.total_levels)] += 1
        for c in o.constraints:
            constraint_types[c.type] += 1
        if o.instance_type != "NONE":
            instancers += 1

    meshes = {me.name: mesh_stats(me) for me in bpy.data.meshes}
    topo = Counter()
    for s in meshes.values():
        for k in ("tri", "quad", "ngon", "verts", "faces"):
            topo[k] += s[k]

    node_groups = {ng.name: node_group_stats(ng) for ng in bpy.data.node_groups}
    gn_node_types = Counter()
    for s in node_groups.values():
        if s["type"] == "GeometryNodeTree":
            gn_node_types.update(s["node_types"])

    data = {
        "file": bpy.data.filepath,
        "version_saved": list(bpy.data.version),
        "scenes": len(bpy.data.scenes),
        "render_engine": bpy.context.scene.render.engine,
        "objects": len(objects),
        "object_types": obj_types,
        "instancers": instancers,
        "collections": len(bpy.data.collections),
        "libraries": [lib.filepath for lib in bpy.data.libraries],
        "linked_ids": sum(1 for idb in bpy.data.objects if idb.library),
        "overrides": sum(1 for o in objects if o.override_library),
        "meshes": len(meshes),
        "topology_total": topo,
        "meshes_with_ngons": sum(1 for s in meshes.values() if s["ngon"]),
        "meshes_with_uvs": sum(1 for s in meshes.values() if s["uv_layers"]),
        "meshes_with_shape_keys": sum(1 for s in meshes.values() if s["shape_keys"]),
        "modifier_types": modifier_types,
        "modifier_stack_depths": {str(k): v for k, v in sorted(stack_depths.items())},
        "modifiers_render_off": modifiers_render_off,
        "geometry_node_groups_on_modifiers": gn_groups,
        "node_groups_by_type": Counter(s["type"] for s in node_groups.values()),
        "gn_node_types_top": dict(gn_node_types.most_common(40)),
        "vertex_groups_total": sum(len(o.vertex_groups) for o in objects if o.type == "MESH"),
        "constraint_types": constraint_types,
        "materials": len(bpy.data.materials),
        "images": len(bpy.data.images),
        "actions": len(bpy.data.actions),
        "armatures": len(bpy.data.armatures),
        "texts": len(bpy.data.texts),
        "per_mesh": meshes,
    }
    with open(out_path, "w") as f:
        json.dump(data, f, indent=1, default=dict)
    print(f"census: {len(objects)} objects, {len(meshes)} meshes -> {out_path}")


argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
main(argv[0] if argv else "census.json")
