"""Statically scan Blender's C/C++ source for operator type definitions.

    python3 scan_source.py <blender-source-root> OUT.json

Finds each `ot->idname = "X_OT_y";` and, within the same definition function,
records which callbacks are set (exec / invoke / modal / poll / ui) and the poll
function's name. Static and approximate: polls assigned indirectly or via
macros are reported as found in the text, not resolved.
"""

import json
import re
import sys
from pathlib import Path

IDNAME = re.compile(r'ot->idname\s*=\s*"([A-Z_]+_OT_[a-z0-9_]+)"')
CALLBACK = re.compile(r"ot->(exec|invoke|modal|poll|ui|cancel|check)\s*=\s*([A-Za-z0-9_:]+)")
FUNC_START = re.compile(r"^(?:static\s+)?void\s+([A-Z]+_OT_[a-z0-9_]+|[a-z0-9_]+)\s*\(\s*wmOperatorType\s*\*\s*ot\s*\)", re.M)


def scan_file(path):
    text = path.read_text(errors="ignore")
    starts = [m.start() for m in FUNC_START.finditer(text)]
    found = []
    for i, start in enumerate(starts):
        end = starts[i + 1] if i + 1 < len(starts) else len(text)
        body = text[start:end]
        m = IDNAME.search(body)
        if not m:
            continue
        cbs = {}
        for cb, fn in CALLBACK.findall(body):
            cbs.setdefault(cb, fn)
        line = text.count("\n", 0, start + m.start()) + 1
        found.append({"idname": m.group(1), "file": None, "line": line, "callbacks": cbs})
    return found


def main(root, out):
    root = Path(root)
    ops = []
    for path in sorted((root / "source" / "blender").rglob("*.cc")):
        for op in scan_file(path):
            op["file"] = str(path.relative_to(root))
            ops.append(op)
    with open(out, "w") as f:
        json.dump({"count": len(ops), "operators": ops}, f, indent=1)
    print(f"scanned {len(ops)} C/C++ operator definitions")


main(sys.argv[1], sys.argv[2])
