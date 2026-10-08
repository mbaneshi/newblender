"""Startup script for a live session: enable the Blender Lab MCP add-on and start its socket.

    Blender --python start_bridge.py

Runs once the window manager exists (via a timer), so operators have a context.
"""

import addon_utils
import bpy

MODULE = "bl_ext.user_default.mcp"


def start():
    addon_utils.enable(MODULE, default_set=True, persistent=True)
    try:
        bpy.ops.blmcp.server_start()
        print("[newblender] bridge started on 127.0.0.1:9876")
    except Exception as ex:  # surfaced in the terminal log
        print("[newblender] bridge failed to start:", ex)
    return None  # run once


bpy.app.timers.register(start, first_interval=1.0)
