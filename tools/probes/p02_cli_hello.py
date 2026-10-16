"""Probe P02-5b: register a CLI command from a --python script, then run it with -c.

Run: Blender -b --factory-startup --disable-autoexec --python tools/probes/p02_cli_hello.py -c p02_hello --foo bar
Expected: prints P02_CMD_RAN with argv ['--foo', 'bar'], exit code 0. The command id must pass str.isidentifier
(so 'p02-hello' is rejected). The --python script must come BEFORE -c on the command line.
"""
import bpy


def cmd(argv):
    print("P02_CMD_RAN argv=", argv, "bg=", bpy.app.background)
    return 0


bpy.utils.register_cli_command("p02_hello", cmd)
