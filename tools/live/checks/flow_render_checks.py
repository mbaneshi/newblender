"""Layer-4 checks on the rendered Flow frames (headless; uses Blender's bundled numpy).

    Blender -b --factory-startup --python flow_render_checks.py -- FRAMES_DIR RENDER_LOG OUT.json

- seconds per frame, from Blender's own "Time:" lines in the render log
- fully black pixels per frame (PNG cannot hold NaN, so black stands in for broken pixels)
- flicker: mean luminance change between consecutive frames, as a share of mean luminance.
  The camera moves, so this measures the whole frame, not "static areas": a looser test than the plan's.
"""

import json
import re
import statistics
import sys
from pathlib import Path

import bpy
import numpy as np

frames_dir, log_path, out_path = sys.argv[sys.argv.index("--") + 1:][:3]
times = []
for line in open(log_path, errors="ignore"):
    m = re.search(r"render\s+\| Time: (\d+):(\d+)\.(\d+) \(Saving", line)
    if m:
        mins, secs, frac = m.groups()
        times.append(int(mins) * 60 + int(secs) + int(frac) / 100)
files = sorted(Path(frames_dir).glob("*.png"))
black, lum = [], []
for f in files:
    img = bpy.data.images.load(str(f), check_existing=False)
    w, h = img.size
    px = np.empty(w * h * 4, dtype=np.float32)
    img.pixels.foreach_get(px)
    px = px.reshape(-1, 4)[:, :3]
    black.append(int(np.count_nonzero(px.max(axis=1) <= 0.0)))
    lum.append(float((px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).mean()))
    bpy.data.images.remove(img)
deltas = [abs(b - a) / max(a, 1e-6) for a, b in zip(lum, lum[1:])]
report = {
    "frames": len(files),
    "resolution": [w, h] if files else None,
    "seconds_per_frame": {"n": len(times), "median": statistics.median(times) if times else None,
                          "max": max(times) if times else None, "total_min": round(sum(times) / 60, 1)},
    "black_pixels_max_frame": max(black) if black else None,
    "flicker_max_pct": round(100 * max(deltas), 2) if deltas else None,
    "flicker_mean_pct": round(100 * statistics.fmean(deltas), 3) if deltas else None,
}
json.dump(report, open(out_path, "w"), indent=1)
print("RENDER_CHECKS", json.dumps(report))
