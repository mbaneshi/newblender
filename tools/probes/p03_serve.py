"""Probe P03 worker: a JSON-lines TCP serve loop inside a Blender `-c` command callback.

Run (the --python script registers the command; it must come before -c):
  Blender -b --factory-startup --disable-autoexec --python tools/probes/p03_serve.py -c p03_serve PORT [IDLE_S]
Protocol: one JSON object per line. Request {"id", "method", "params"}; reply {"id", "ok", "result"|"error", "ms"}.
The loop runs on Blender's main thread and needs no event loop, so no timers are used.
"""
import hashlib
import json
import socket
import time

import bpy


def objects():
    out = []
    for o in bpy.data.objects:
        row = {"name": o.name, "type": o.type, "session_uid": o.session_uid}
        if o.type == "MESH":
            row["verts"] = len(o.data.vertices)
        out.append(row)
    return out


def fingerprint():
    h = hashlib.sha1()
    for o in sorted(bpy.data.objects, key=lambda o: o.name):
        h.update(o.name.encode())
        h.update(repr([round(v, 5) for row in o.matrix_world for v in row]).encode())
        if o.type == "MESH":
            co = [0.0] * (len(o.data.vertices) * 3)
            o.data.vertices.foreach_get("co", co)
            h.update(repr([round(c, 5) for c in co]).encode())
    return {"objects": len(bpy.data.objects), "hash": h.hexdigest()[:12]}


def op(name):
    mod, fn = name.split(".")
    return getattr(getattr(bpy.ops, mod), fn)


def m_ping(p):
    return "pong"


def m_scene_query(p):
    return {"objects": objects(), "fingerprint": fingerprint()}


def m_op_run(p):
    before = fingerprint()
    res = sorted(op(p["op"])("EXEC_DEFAULT", **p.get("args", {})))
    after = fingerprint()
    return {"status": res, "changed": before != after, "before": before, "after": after}


def m_undo_push(p):
    bpy.ops.ed.undo_push(message=p.get("message", "p03"))
    return fingerprint()


def m_undo_undo(p):
    bpy.ops.ed.undo()
    return fingerprint()


def m_checkpoint(p):
    bpy.ops.wm.save_as_mainfile(filepath=p["path"], copy=True)
    return fingerprint()


def m_restore(p):
    bpy.ops.wm.open_mainfile(filepath=p["path"])
    return fingerprint()


def m_crash_sculpt_box(p):
    """A real P01 crasher: sculpt.face_set_box_gesture under a borrowed region segfaults in its undo push."""
    bpy.ops.object.mode_set(mode="SCULPT")
    screen = bpy.data.screens["Layout"]
    area = next(a for a in screen.areas if a.type == "VIEW_3D")
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(screen=screen, area=area, region=region):
        return sorted(bpy.ops.sculpt.face_set_box_gesture("EXEC_DEFAULT"))


METHODS = {
    "ping": m_ping, "scene.query": m_scene_query, "op.run": m_op_run, "undo.push": m_undo_push,
    "undo.undo": m_undo_undo, "checkpoint": m_checkpoint, "restore": m_restore,
    "crash.sculpt_box": m_crash_sculpt_box,
}


def serve(argv):
    port = int(argv[0])
    idle = float(argv[1]) if len(argv) > 1 else 60.0
    srv = socket.socket()
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", port))
    srv.listen(1)
    srv.settimeout(idle)
    conn, _ = srv.accept()
    conn.settimeout(idle)
    f = conn.makefile("rwb")
    for line in f:
        req = json.loads(line)
        t = time.perf_counter()
        try:
            if req["method"] == "shutdown":
                f.write((json.dumps({"id": req["id"], "ok": True, "result": "bye"}) + "\n").encode())
                f.flush()
                return 0
            result = METHODS[req["method"]](req.get("params", {}))
            reply = {"id": req["id"], "ok": True, "result": result}
        except Exception as e:  # noqa: BLE001 - report any bpy failure to the client
            reply = {"id": req["id"], "ok": False, "error": f"{type(e).__name__}: {str(e).strip().splitlines()[-1][:200]}"}
        reply["ms"] = round((time.perf_counter() - t) * 1000, 3)
        f.write((json.dumps(reply) + "\n").encode())
        f.flush()
    return 0


bpy.utils.register_cli_command("p03_serve", serve)
