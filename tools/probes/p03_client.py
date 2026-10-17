"""Probe P03 supervisor and checks for tools/probes/p03_serve.py.

Run: python3 tools/probes/p03_client.py OUT.json
Starts a Blender worker, drives it over TCP, kills it with a real crashing operator, starts a fresh worker
and restores the last checkpoint. Records pass/fail per check and latency statistics.
"""
import json
import os
import socket
import statistics
import subprocess
import sys
import tempfile
import time

BLENDER = "/Applications/Blender.app/Contents/MacOS/Blender"
WORKER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "p03_serve.py")
out_path = sys.argv[1]
res = {"checks": {}}


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class Worker:
    def __init__(self):
        self.port = free_port()
        self.proc = subprocess.Popen(
            [BLENDER, "-b", "--factory-startup", "--disable-autoexec", "--python", WORKER, "-c", "p03_serve", str(self.port), "30"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.sock = None
        t0 = time.time()
        while time.time() - t0 < 30:
            try:
                self.sock = socket.create_connection(("127.0.0.1", self.port), timeout=30)
                break
            except OSError:
                if self.proc.poll() is not None:
                    raise RuntimeError(f"worker exited early rc={self.proc.returncode}")
                time.sleep(0.1)
        if self.sock is None:
            raise RuntimeError("worker did not open its port")
        self.startup_s = round(time.time() - t0, 2)
        self.f = self.sock.makefile("rwb")
        self.n = 0

    def call(self, method, **params):
        self.n += 1
        t = time.perf_counter()
        self.f.write((json.dumps({"id": self.n, "method": method, "params": params}) + "\n").encode())
        self.f.flush()
        line = self.f.readline()
        if not line:
            raise ConnectionError("worker closed the connection")
        reply = json.loads(line)
        reply["rtt_ms"] = round((time.perf_counter() - t) * 1000, 3)
        return reply


def check(name, ok, **detail):
    res["checks"][name] = {"pass": bool(ok), **detail}
    print(("PASS " if ok else "FAIL ") + name, detail if not ok else "")


w = Worker()
res["startup_s"] = w.startup_s
check("1 ping", w.call("ping")["result"] == "pong", startup_s=w.startup_s)

rtts = [w.call("ping")["rtt_ms"] for _ in range(300)]
res["ping_rtt_ms"] = {"median": statistics.median(rtts), "p95": sorted(rtts)[int(0.95 * len(rtts))], "max": max(rtts)}
check("1b loop latency", True, **res["ping_rtt_ms"])

q0 = w.call("scene.query")["result"]
r = w.call("op.run", op="mesh.primitive_uv_sphere_add")
q1 = w.call("scene.query")["result"]
check("2 operator in loop", r["ok"] and q1["fingerprint"]["objects"] == q0["fingerprint"]["objects"] + 1,
      status=r.get("result", {}).get("status"), objects=[q0["fingerprint"]["objects"], q1["fingerprint"]["objects"]])

w.call("undo.push", message="after sphere")
before = w.call("scene.query")["result"]["fingerprint"]
w.call("op.run", op="mesh.primitive_cube_add")
w.call("undo.push", message="after cube")
mid = w.call("scene.query")["result"]["fingerprint"]
w.call("undo.undo")
after = w.call("scene.query")["result"]["fingerprint"]
check("3 undo in loop", mid != before and after == before, before=before, mid=mid, after=after)

ck = os.path.join(tempfile.mkdtemp(), "p03_ck.blend")
ckfp = w.call("checkpoint", path=ck)["result"]
w.call("op.run", op="mesh.primitive_cube_add")
rest = w.call("restore", path=ck)["result"]
check("4 checkpoint and restore in loop", rest == ckfp, checkpoint=ckfp, restored=rest)

for _ in range(20):
    w.call("op.run", op="mesh.primitive_cube_add")
    w.call("scene.query")
fin = w.call("scene.query")["result"]["fingerprint"]
check("5 repeated requests stay consistent", fin["objects"] == ckfp["objects"] + 20, objects=fin["objects"])

bad = w.call("op.run", op="mesh.no_such_operator")
check("6 bad request returns error, loop survives", (not bad["ok"]) and w.call("ping")["result"] == "pong", error=bad.get("error"))

rest_ok = w.call("restore", path=ck)["result"] == ckfp
crashed = False
try:
    w.call("crash.sculpt_box")
except (ConnectionError, OSError):
    crashed = True
rc = None
try:
    rc = w.proc.wait(timeout=15)
except subprocess.TimeoutExpired:
    w.proc.kill()
check("7 real crash is detected by the client", crashed and rc not in (0, None), returncode=rc, restored_before_crash=rest_ok)

w2 = Worker()
rest2 = w2.call("restore", path=ck)["result"]
check("8 fresh worker restores checkpoint after crash", rest2 == ckfp, checkpoint=ckfp, restored=rest2, startup_s=w2.startup_s)
bye = w2.call("shutdown")
rc2 = w2.proc.wait(timeout=15)
check("9 clean shutdown", bye["ok"] and rc2 == 0, returncode=rc2)

res["all_pass"] = all(c["pass"] for c in res["checks"].values())
json.dump(res, open(out_path, "w"), indent=1)
print("ALL PASS" if res["all_pass"] else "SOME FAILED")
