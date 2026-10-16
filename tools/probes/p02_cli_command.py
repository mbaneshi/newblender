"""Probe P02-5: is the CLI-command registration API reachable from Python, and what happens in a -c run?

Run: Blender --factory-startup --disable-autoexec --python tools/probes/p02_cli_command.py -- OUT.json
(registers a command, lists the API; the -c invocation itself is exercised by the second step in the report.)
"""
import json
import sys

import bpy

out = sys.argv[sys.argv.index("--") + 1]
r = {"has_register_cli_command": hasattr(bpy.utils, "register_cli_command"),
     "has_unregister_cli_command": hasattr(bpy.utils, "unregister_cli_command")}
if r["has_register_cli_command"]:
    r["doc"] = (bpy.utils.register_cli_command.__doc__ or "")[:600]
json.dump(r, open(out, "w"), indent=1)
