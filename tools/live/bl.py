"""Send Python to a live Blender session through the Blender Lab MCP add-on socket.

    python3 bl.py FILE.py        # run a file
    python3 bl.py - < code.py    # run stdin
    python3 bl.py -e "result['n'] = len(bpy.data.objects)"

The code runs on Blender's main thread with `bpy` available; put return values
into the `result` dict. Requires the add-on (lab/blender_mcp, id "mcp") enabled
and its server started; it listens on 127.0.0.1:9876 by default.
"""

import json
import socket
import sys

HOST, PORT = "127.0.0.1", 9876


def send(code, strict_json=False, timeout=120.0):
    request = json.dumps({"type": "execute", "code": code, "strict_json": strict_json}) + "\0"
    with socket.create_connection((HOST, PORT), timeout=timeout) as sock:
        sock.sendall(request.encode("utf-8"))
        buf = bytearray()
        while not buf.endswith(b"\0"):
            chunk = sock.recv(65536)
            if not chunk:
                break
            buf.extend(chunk)
    return json.loads(buf.rstrip(b"\0").decode("utf-8"))


def main(argv):
    if not argv:
        sys.exit(__doc__)
    if argv[0] == "-e":
        code = argv[1]
    elif argv[0] == "-":
        code = sys.stdin.read()
    else:
        code = open(argv[0]).read()
    response = send("import bpy\n" + code)
    print(json.dumps(response, indent=1, default=str))
    sys.exit(0 if response.get("status") == "ok" else 1)


main(sys.argv[1:])
