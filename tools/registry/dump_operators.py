"""Dump Blender's full operator registry as JSON.

Run headless, with no user config and no embedded scripts:
    Blender --factory-startup --disable-autoexec -b --python dump_operators.py -- OUT.json

For every registered operator: idname, category, label, description, bl_options
(REGISTER, UNDO, BLOCKING, GRAB_CURSOR, INTERNAL, ...), whether it is defined in
Python, and its properties with types. Poll/modal facts are not exposed to Python;
scan_source.py recovers them from the C++ source.
"""

import json
import sys

import bpy


def prop_info(p):
    info = {"id": p.identifier, "type": p.type}
    if p.type in {"INT", "FLOAT"}:
        info["array"] = getattr(p, "array_length", 0) or 0
    if p.type == "ENUM":
        info["items"] = [i.identifier for i in p.enum_items][:40]
    if p.is_hidden or p.is_skip_save:
        info["hidden"] = True
    return info


def safe_poll(op):
    try:
        return bool(op.poll())
    except Exception:
        return None


def main(out_path):
    ops = []
    for category in dir(bpy.ops):
        if category.startswith("_"):
            continue
        module = getattr(bpy.ops, category)
        for name in dir(module):
            if name.startswith("_"):
                continue
            op = getattr(module, name)
            try:
                rna = op.get_rna_type()
            except (KeyError, AttributeError):
                continue
            ops.append({
                "id": f"{category}.{name}",
                "idname": op.idname(),
                "category": category,
                "label": rna.name,
                "description": rna.description,
                "options": sorted(op.bl_options),
                "python": getattr(bpy.types, op.idname(), None) is not None,
                # Coarse signal: poll headless in the factory scene (default cube
                # active) per mode. An op that fails in every mode is gated by
                # something else, usually a window/area/region; scan_source.py
                # gives the static reason.
                "poll_headless": {},
                "props": [prop_info(p) for p in rna.properties if p.identifier != "rna_type"],
            })
    by_id = {o["id"]: o for o in ops}
    for mode in ("OBJECT", "EDIT", "SCULPT"):
        bpy.ops.object.mode_set(mode=mode)
        for op_id, o in by_id.items():
            category, name = op_id.split(".", 1)
            o["poll_headless"][mode] = safe_poll(getattr(getattr(bpy.ops, category), name))
    bpy.ops.object.mode_set(mode="OBJECT")
    ops.sort(key=lambda o: o["id"])
    data = {"blender": bpy.app.version_string, "count": len(ops), "operators": ops}
    with open(out_path, "w") as f:
        json.dump(data, f, indent=1)
    print(f"dumped {len(ops)} operators to {out_path}")


argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
main(argv[0] if argv else "operators.json")
