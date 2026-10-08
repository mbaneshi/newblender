"""Probe P01: can context overrides make region-gated modelling operators run headless?

Ledger L-004 / L-011 and S01 brief §8. The trace (pass 3) found 23 modelling
operators whose poll demands a GUI region (gate: gui-region). This probe checks,
in a windowless background session, for each of them:

  A. poll() with the plain background context
  B. poll() under bpy.context.temp_override(screen, area, region) borrowed from a
     screen stored in the factory startup file (no window exists in -b)
  C. if B passes: the exec result (EXEC_DEFAULT), or the exception it raises

Each operator runs in its own Blender process, so a crash is recorded rather than
ending the probe. Run:
  python3 tools/probes/p01_context_override.py OUT.json            # driver
(the driver calls Blender -b --factory-startup --disable-autoexec with `-- OP ROW.json`)
"""

import json
import subprocess
import sys
import traceback

BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"

OPS = [
    "mesh.edgering_select", "mesh.loop_select", "mesh.knife_project", "mesh.primitive_cube_add_gizmo",
    "mesh.rip_edge", "mesh.rip_edge_move", "mesh.shortest_path_pick",
    "sculpt.brush_stroke", "sculpt.face_set_line_gesture", "sculpt.face_set_polyline_gesture",
    "sculpt.face_set_box_gesture", "sculpt.project_line_gesture", "sculpt.face_set_lasso_gesture",
    "sculpt.set_pivot_position", "sculpt.trim_line_gesture", "sculpt.trim_box_gesture",
    "sculpt.trim_lasso_gesture", "sculpt.trim_polyline_gesture",
    "transform.delete_orientation", "transform.create_orientation", "transform.shear",
    "transform.select_orientation", "transform.seq_slide",
]
MODE = {"mesh": "EDIT", "sculpt": "SCULPT", "transform": "OBJECT"}
SPACE = {"transform.seq_slide": ("Video Editing", "SEQUENCE_EDITOR")}

# Non-default arguments for operators whose defaults are a no-op, so "nothing changed"
# means the call failed silently rather than that it was asked to do nothing.
_STROKE = [{"name": "", "location": (0.0, 0.0, 1.0 - 0.01 * i), "mouse": (0.0, 0.0), "mouse_event": (0.0, 0.0),
            "is_start": i == 0, "pressure": 1.0, "size": 50.0, "time": float(i),
            "x_tilt": 0.0, "y_tilt": 0.0} for i in range(8)]
PARAMS = {
    "transform.shear": {"angle": 0.5},
    "transform.create_orientation": {"name": "Probe", "use": True},
    "mesh.primitive_cube_add_gizmo": {"matrix": ((2, 0, 0, 0), (0, 2, 0, 0), (0, 0, 2, 0), (0, 0, 0, 1))},
    "sculpt.brush_stroke": {"stroke": _STROKE},
    # Index-driven exec (pass 3 claim): the hidden index properties default to -1, which cancels.
    "mesh.loop_select": {"object_index": 0, "edge_index": 0},
    "mesh.edgering_select": {"object_index": 0, "edge_index": 0},
    "mesh.shortest_path_pick": {"index": 40},
}



def op(name):
    mod, fn = name.split(".")
    return getattr(getattr(bpy.ops, mod), fn)


def borrowed(name):
    screen_name, space = SPACE.get(name, ("Layout", "VIEW_3D"))
    screen = bpy.data.screens.get(screen_name)
    if screen is None:
        return None
    area = next((a for a in screen.areas if a.type == space), None)
    if area is None:
        return None
    region = next((r for r in area.regions if r.type == "WINDOW"), None)
    return {"screen": screen, "area": area, "region": region}


def fingerprint():
    """Hash of the active mesh's vertex positions and object matrix, plus counts. Edit-mode safe."""
    import hashlib
    obj = bpy.context.view_layer.objects.active
    if obj.mode == "EDIT":
        obj.update_from_editmode()
    me = obj.data
    co = [0.0] * (len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    mat = [round(v, 5) for row in obj.matrix_world for v in row]
    h = hashlib.sha1(repr(([round(c, 5) for c in co], mat)).encode()).hexdigest()[:12]
    slot = bpy.context.scene.transform_orientation_slots[0]
    orient = slot.custom_orientation.name if slot.custom_orientation else slot.type
    sel = sum(e.select for e in me.edges)
    return f"{len(me.vertices)}v/{len(me.polygons)}f/{h}/sel{sel}/objs{len(bpy.data.objects)}/orient:{orient}"


def set_mode(mode):
    obj = bpy.context.view_layer.objects.active
    if obj.mode != mode:
        bpy.ops.object.mode_set(mode=mode)


def setup():
    # Scene: the factory cube, subdivided so sculpt and edge-loop operators have topology.
    cube = bpy.data.objects["Cube"]
    bpy.context.view_layer.objects.active = cube
    cube.select_set(True)
    mod = cube.modifiers.new("sub", "SUBSURF")
    mod.levels = 2
    bpy.ops.object.modifier_apply(modifier="sub")

    global env
    env = {
        "blender": bpy.app.version_string,
        "background": bpy.app.background,
        "windows": len(bpy.context.window_manager.windows),
        "screens": [s.name for s in bpy.data.screens],
    }
    lay = borrowed("mesh.loop_select")
    env["borrowed_view3d_region_data"] = None if lay is None else repr(lay["region"].data)

def probe(name, row_path):
    row = {"op": name, "env": env}
    try:
        set_mode(MODE[name.split(".")[0]])
        if name.startswith("mesh."):
            # Loop/ring selection starts from nothing selected so a pick is visible; the rest act on all.
            bpy.ops.mesh.select_all(action="DESELECT" if name in ("mesh.loop_select", "mesh.edgering_select", "mesh.shortest_path_pick") else "SELECT")
            if name == "mesh.shortest_path_pick":  # a path needs an active start vertex
                import bmesh
                bm = bmesh.from_edit_mesh(bpy.context.object.data)
                bm.verts.ensure_lookup_table()
                bm.verts[0].select = True
                bm.select_history.add(bm.verts[0])
                bmesh.update_edit_mesh(bpy.context.object.data)
        row["poll_plain"] = op(name).poll()
        ctx = borrowed(name)
        row["override_available"] = ctx is not None
        if ctx is not None:
            with bpy.context.temp_override(**ctx):
                row["poll_override"] = op(name).poll()
                if row["poll_override"]:
                    try:
                        before = fingerprint()
                        row["args"] = sorted(PARAMS.get(name, {}))
                        row["exec"] = sorted(op(name)("EXEC_DEFAULT", **PARAMS.get(name, {})))
                        row["changed"] = fingerprint() != before
                    except Exception as e:  # noqa: BLE001 - the probe records whatever fails
                        row["exec"] = f"{type(e).__name__}: {str(e).strip().splitlines()[-1][:200]}"
    except Exception as e:  # noqa: BLE001
        row["error"] = f"{type(e).__name__}: {str(e).strip()[:200]}"
        row["trace"] = traceback.format_exc().splitlines()[-1][:200]
    with open(row_path, "w") as f:
        json.dump(row, f)


def crash_frame():
    """First Blender frame after the signal trampoline in Blender's crash log."""
    import os
    import re
    path = os.path.join(tempfile_dir(), "blender.crash.txt")
    if not os.path.exists(path):
        return ""
    frames = [l for l in open(path) if re.match(r"^\d+\s", l)]
    after = frames[[i for i, l in enumerate(frames) if "_sigtramp" in l][0] + 1:] if any("_sigtramp" in l for l in frames) else frames
    sym = after[0].split()[3] if after else ""
    demangled = subprocess.run(["c++filt", sym], capture_output=True, text=True).stdout.strip()
    return demangled.split("(")[0][:160]


def tempfile_dir():
    import tempfile
    return tempfile.gettempdir()


def driver(out_path):
    import os
    import tempfile
    rows = []
    for name in OPS:
        row_path = os.path.join(tempfile.mkdtemp(), "row.json")
        p = subprocess.run([BLENDER, "-b", "--factory-startup", "--disable-autoexec", "--python", __file__,
                            "--", name, row_path], capture_output=True, text=True, timeout=120)
        if os.path.exists(row_path):
            row = json.load(open(row_path))
        else:
            row = {"op": name, "crash": f"exit {p.returncode}", "crash_frame": crash_frame()}
        rows.append(row)
        print(name.ljust(34), row.get("poll_plain"), row.get("poll_override"), row.get("exec", row.get("crash", "")),
              row.get("changed", ""), row.get("crash_frame", ""), flush=True)
    env = next((r.pop("env") for r in rows if "env" in r), {})
    for r in rows:
        r.pop("env", None)
    with open(out_path, "w") as f:
        json.dump({"env": env, "rows": rows}, f, indent=1)
    print(f"[p01] {len(rows)} operators → {out_path}")


if __name__ == "__main__":
    if "--" in sys.argv:
        import bpy  # noqa: F401 - inside Blender
        globals()["bpy"] = bpy
        name, row_path = sys.argv[sys.argv.index("--") + 1:][:2]
        setup()
        probe(name, row_path)
    else:
        driver(sys.argv[1])
