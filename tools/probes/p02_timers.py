"""Probe P02-1: do bpy.app.timers fire in a pure background (-b) session?

Run (one variant per Blender process):
  Blender -b --factory-startup --disable-autoexec --python tools/probes/p02_timers.py -- VARIANT OUT.txt
Variants: plain (register, let the script end), sleep (register, time.sleep), ops (register, then
run operators that normally pump events), loop (register, then spin the interpreter).
The timer appends 'FIRED' to OUT.txt; the script appends 'SCRIPT_END' last.
"""
import sys
import time

import bpy

variant, out = sys.argv[sys.argv.index("--") + 1:][:2]


def log(msg):
    with open(out, "a") as f:
        f.write(msg + "\n")


def tick():
    log("FIRED")
    return None


bpy.app.timers.register(tick, first_interval=0.0, persistent=True)
log(f"registered is_registered={bpy.app.timers.is_registered(tick)} variant={variant}")

if variant == "sleep":
    time.sleep(1.0)
elif variant == "ops":
    for name, kw in (("wm.redraw_timer", dict(type="DRAW_WIN_SWAP", iterations=1)), ("render.render", {})):
        try:
            getattr(getattr(bpy.ops, name.split(".")[0]), name.split(".")[1])(**kw)
            log(f"op {name} ok")
        except Exception as e:  # noqa: BLE001
            log(f"op {name} raised {type(e).__name__}: {str(e)[:120]}")
elif variant == "loop":
    t0 = time.time()
    while time.time() - t0 < 1.0:
        pass

log("SCRIPT_END")
