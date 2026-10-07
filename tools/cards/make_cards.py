"""Generate capability cards (one YAML per operator) from the S01 trace data.

    python3 make_cards.py s01_trace.json OUT_DIR

Each card has a source row (from Pass 3), a human row (workflow-script steps that
use it, from STEPS below), and a proposed verdict. Verdicts come from RULES
applied in order, unless OVERRIDES says otherwise. Every verdict is a proposal;
`contested: true` marks the ones that need the owner's judgement.

Verdicts:
  remove  - ceremony: exists to serve a human session (selection, mode, menus)
  declare - best expressed as a declared outcome (modifier / node) that exists today
  free    - real logic trapped behind UI context; make it a plain typed function
  keep    - already fine for an agent, modulo explicit parameters
"""

import re
import sys
from pathlib import Path

import yaml

SRC_ROOT = "~/agent-native-lab-data/sources/blender/projects.blender.org/blender/blender/"

# Workflow-script rows (docs/discovery/s01-modeling/01-workflow-script.md) per operator.
STEPS = {
    "object.mode_set": [12], "object.editmode_toggle": [12], "mesh.select_mode": [12],
    "mesh.extrude_region": [13, 48], "mesh.extrude_region_move": [13, 48], "mesh.extrude_context_move": [13],
    "mesh.inset": [13, 32], "mesh.loopcut": [13], "mesh.loopcut_slide": [13], "mesh.knife_tool": [13],
    "mesh.loop_select": [14], "mesh.edgering_select": [14], "mesh.select_linked": [14],
    "mesh.select_linked_pick": [14], "mesh.shortest_path_pick": [14], "mesh.shortest_path_select": [14],
    "object.modifier_add": [17, 18, 19, 20, 21, 22, 23, 24, 33, 46, 51],
    "mesh.mark_sharp": [21], "object.modifier_apply": [30, 63], "mesh.bevel": [33, 35],
    "transform.edge_crease": [33], "object.voxel_remesh": [37], "sculpt.brush_stroke": [36, 38, 39, 40],
    "sculpt.dynamic_topology_toggle": [38], "transform.translate": [27, 44, 48],
    "transform.rotate": [27], "transform.resize": [48],
    "mesh.polybuild_face_at_cursor_move": [45], "mesh.polybuild_split_at_cursor_move": [45],
    "mesh.polybuild_dissolve_at_cursor": [45], "mesh.polybuild_transform_at_cursor_move": [45],
    "mesh.symmetrize": [46], "object.quadriflow_remesh": [50], "object.multires_subdivide": [51],
    "object.multires_reshape": [51], "object.shape_key_add": [26, 52], "mesh.mark_seam": [54],
    "mesh.remove_doubles": [59], "mesh.normals_make_consistent": [60], "object.shade_smooth": [61],
    "object.transform_apply": [62], "mesh.select_non_manifold": [69], "object.origin_set": [27, 68],
    "mesh.separate": [25, 40], "object.join": [25], "mesh.subdivide": [48],
    "object.convert": [63], "mesh.delete": [67],
}

# Hand verdicts where the rule is not enough. (verdict, why, contested)
OVERRIDES = {
    "sculpt.brush_stroke": ("free", "The stroke is the creative act. Its agent form could be a declared "
        "displacement/deformation field or a replayable 3D path. Whether an agent should sculpt by "
        "strokes at all is a taste question (gray zone G1).", True),
    "mesh.polybuild_face_at_cursor_move": ("free", "Manual retopology by cursor. Input must become data "
        "(target loops/patches). Whether machine retopo is acceptable for final topology is the "
        "owner's call (workflow row 50).", True),
    "object.quadriflow_remesh": ("free", "Exec already runs headless as a blocking job; no node twin. "
        "Make it a plain function and a node. Quality of auto-retopo vs human retopo is contested "
        "(row 50).", True),
    "mesh.knife_tool": ("free", "Invoke/modal only, no exec. Re-specify the input as data: a cut path "
        "(polyline in object space) or cutting plane(s); the core BM_face_split_edgenet already exists.", False),
    "object.mode_set": ("remove", "A human session switch that dispatches another operator by name. "
        "An agent should name the representation it edits (Mesh vs BMesh) explicitly, and flush is a "
        "call, not a mode.", False),
    "object.editmode_toggle": ("remove", "Same as mode_set.", False),
    "object.modifier_add": ("keep", "This is the declarative layer itself. Keep, with typed arguments "
        "and no menu.", False),
    "object.modifier_apply": ("keep", "Bakes a declared step into data; the agent equivalent of "
        "'commit'. Keep.", False),
    "object.modifier_move_to_index": ("keep", "Stack ordering is part of the recipe.", False),
    "object.shade_auto_smooth": ("declare", "Already just adds the Smooth by Angle node-group modifier.", False),
    "transform.translate": ("free", "Exec is already window-free (area may be null). Remove the modal "
        "veneer and hidden pivot/orientation defaults; make it a pure transform with explicit space "
        "and pivot.", False),
    "mesh.loop_select": ("remove", "Selection as a means of scoping. Replace with an explicit "
        "edge-loop query returning element indices (exec is already index-driven).", False),
}

SELECTION = re.compile(r"(^|_)(select|deselect|hide|reveal)(_|$)|select_|_select$|^mesh\.select|loop_multi_select")
MODE = re.compile(r"mode_set|editmode_toggle|_toggle$")
UI = re.compile(r"_menu$|call_menu|pie|_popup")


def rule(o):
    i = o["id"]
    if UI.search(i):
        return "remove", "UI chrome (menus/popups) with no data effect of its own.", "DF1"
    if MODE.search(i):
        return "remove", "Session mode switch; an agent names representation and state explicitly.", "DF1"
    if SELECTION.search(i):
        return "remove", ("Selection is how a human scopes the next action. For an agent, scope is an "
                          "explicit argument (element indices / attribute mask). Keep the queries, "
                          "drop the stateful selection."), "DF1"
    t = o["twin_status"]
    if t == "exact":
        return "declare", f"Exact declarative twin exists: {o['twin']}.", "DF3"
    if t == "approx":
        return "declare", (f"Approximate twin: {o['twin']}. Declare once result parity is "
                           "verified by mesh-isomorphism test."), "DF3"
    if t == "none":
        if o["gate"] == "gui-event" or not o["has_exec"]:
            return "free", ("No twin and no exec: the input is screen/cursor placement. Re-specify the "
                            "input as data, then expose the core as a typed function."), "DF1"
        return "free", ("No declarative twin; exec works given mode/data. Detach from edit-mode and "
                        "selection state: a typed function over explicit element sets, returning a diff."), "DF3"
    if not o["has_exec"]:
        return "free", "No exec: interactive only. Capture its inputs as properties; make exec pure.", "DF1"
    if o["gate"] in ("gui-region", "gui-event"):
        return "free", "Exec logic is gated by a GUI region it doesn't fundamentally need.", "DF1"
    return "keep", "Usable as a function today, modulo hidden context defaults made explicit.", None


def card(o):
    if o["id"] in OVERRIDES:
        verdict, why, contested = OVERRIDES[o["id"]]
        _, _, df = rule(o)
        source_of_verdict = "hand"
    else:
        verdict, why, df = rule(o)
        contested = False
        source_of_verdict = "rule"
    return {
        "id": o["id"],
        "idname": o["idname"],
        "stage": "S01",
        "human": {"workflow_rows": STEPS.get(o["id"], [])},
        "source": {
            "file": o["file"], "line": o["line"], "kind": o["kind"],
            "poll": o["poll"], "gate": o["gate"],
            "has_exec": o["has_exec"], "modal": o["modal"], "undo": o["undo"],
            "poll_headless": o["poll_headless"],
        },
        "twin": {"status": o["twin_status"], "what": o["twin"]},
        "verdict": {
            "call": verdict, "why": why, "dead_fact": df,
            "contested": contested, "by": source_of_verdict, "evidence": "L1",
        },
    }


def main(trace_path, out_dir):
    ops = yaml.safe_load(open(trace_path))["operators"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    tally = {}
    for o in ops:
        c = card(o)
        (out / f"{o['id']}.yaml").write_text(yaml.safe_dump(c, sort_keys=False, width=100))
        key = (c["verdict"]["call"], c["verdict"]["contested"])
        tally[key] = tally.get(key, 0) + 1
    print(f"wrote {len(ops)} cards to {out}")
    for (v, contested), n in sorted(tally.items()):
        print(f"  {v:8s} {'(contested)' if contested else '':12s} {n}")


main(sys.argv[1], sys.argv[2])
