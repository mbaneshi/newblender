"""Join the runtime registry (dump_operators.py) with the source scan (scan_source.py).

    python3 join.py operators.json source_ops.json OUT.json

Adds a heuristic `gate` per operator from its poll function's name and the
headless poll results:
  none   - no poll function at all
  mode   - poll names an edit/object/pose/sculpt mode
  gui    - poll names a window, area, region, space or editor
  data   - poll checks data (active object, editable scene, ...)
  other  - anything else, or poll not found statically
The name rules are a first pass to be corrected by reading the poll bodies.
"""

import json
import re
import sys

GUI = re.compile(r"region|area|space|winactive|screen|view3d|outliner|console|file_brows|"
                 r"_active$|clip_|image_|node_(active|editable)|sequencer_active|text_edit|graphop|nlaop|action_active", re.I)
MODE = re.compile(r"editmesh|editmode|objectmode|posemode|editarmature|sculpt_mode|uvedit|"
                  r"editcurve|editsurf|editfont|editlattice|paint_mode|weight_paint|vertex_paint|texture_paint|editmball", re.I)
DATA = re.compile(r"editable|active_editable|object_active|scene|vertex_group|has_|_exists", re.I)


def gate(poll, headless):
    if poll is None:
        return "other"
    if poll == "(none)":
        return "none"
    if MODE.search(poll) and not re.search(r"view3d|region|space", poll, re.I):
        return "mode"
    if GUI.search(poll):
        return "gui"
    if DATA.search(poll):
        return "data"
    return "other"


def main(reg_path, src_path, out_path):
    reg = json.load(open(reg_path))["operators"]
    src = {o["idname"]: o for o in json.load(open(src_path))["operators"]}
    rows = []
    for o in reg:
        s = src.get(o["idname"])
        poll = None
        if s:
            poll = s["callbacks"].get("poll", "(none)")
        rows.append({
            "id": o["id"], "idname": o["idname"], "category": o["category"], "label": o["label"],
            "python": o["python"], "options": o["options"],
            "file": s["file"] if s else None, "line": s["line"] if s else None,
            "poll": poll,
            "modal": bool(s and "modal" in s["callbacks"]),
            "invoke_only": bool(s and "invoke" in s["callbacks"] and "exec" not in s["callbacks"]),
            "poll_headless": o["poll_headless"],
            "gate": "python" if o["python"] else gate(poll, o["poll_headless"]),
            "n_props": len(o["props"]),
        })
    json.dump({"count": len(rows), "operators": rows}, open(out_path, "w"), indent=1)
    print(f"joined {len(rows)} operators -> {out_path}")


main(*sys.argv[1:4])
