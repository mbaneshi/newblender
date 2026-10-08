"""Screenshot the live Blender window (what the owner sees) to a PNG.

Sent through tools/live/bl.py. Set SNAP_PATH before the code, e.g.
    python3 bl.py -e "SNAP_PATH='/tmp/x.png'; exec(open('snap.py').read())"
"""

import bpy

win = bpy.context.window_manager.windows[0]
with bpy.context.temp_override(window=win, screen=win.screen, area=win.screen.areas[0]):
    bpy.ops.screen.screenshot(filepath=SNAP_PATH, check_existing=False)
result["snap"] = SNAP_PATH
