"""Demo 003 layer 4: Cycles 1080p still, 256 samples + denoise, on the GPU, headless.

    Blender -b charge.blend --factory-startup --disable-autoexec --python charge_render_still.py -- OUT_DIR FRAME

Writes still.exr (for NaN/Inf) and still.png, then measures:
- render seconds (plan: < 15 min)
- NaN/Inf pixels (plan: 0)
- fireflies: pixels whose luminance exceeds 50x the median of their 5x5 neighbourhood
  (the plan says "50x the median luminance"; a local median is used so a legitimately
  bright source is not counted as a firefly). Plan: < 20.
Preferences are changed only in this factory-startup process, never saved.
"""

import json
import sys
import time

import bpy
import numpy as np

out_dir, frame = sys.argv[sys.argv.index("--") + 1:][:2]
frame = int(frame)
sc = bpy.context.scene
prefs = bpy.context.preferences.addons["cycles"].preferences
devices = []
for kind in ("METAL", "OPTIX", "CUDA"):
    try:
        prefs.compute_device_type = kind
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == kind]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == kind
            devices = [d.name for d in gpus]
            sc.cycles.device = "GPU"
            break
    except TypeError:
        continue
sc.render.engine = "CYCLES"
sc.cycles.samples, sc.cycles.use_denoising = 256, True
sc.render.resolution_x, sc.render.resolution_y, sc.render.resolution_percentage = 1920, 1080, 100
sc.frame_set(frame)
sc.render.image_settings.file_format = "OPEN_EXR"
sc.render.filepath = f"{out_dir}/still.exr"
t = time.time()
bpy.ops.render.render(write_still=True)
secs = time.time() - t
img = bpy.data.images.load(f"{out_dir}/still.exr")
img.save_render(f"{out_dir}/still.png") if False else None
w, h = img.size
px = np.empty(w * h * 4, dtype=np.float32)
img.pixels.foreach_get(px)
px = px.reshape(h, w, 4)[:, :, :3]
nan = int(np.count_nonzero(~np.isfinite(px)))
lum = px @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
pad = np.pad(lum, 2, mode="edge")
win = np.lib.stride_tricks.sliding_window_view(pad, (5, 5))
local = np.median(win.reshape(h, w, 25), axis=2)
ff = int(np.count_nonzero(lum > 50 * np.maximum(local, 1e-4)))
sc.render.image_settings.file_format = "PNG"
sc.render.filepath = f"{out_dir}/still.png"
rr = bpy.data.images["Render Result"]
rr.save_render(f"{out_dir}/still.png", scene=sc)
report = {"frame": frame, "devices": devices or ["CPU"], "seconds": round(secs, 1),
          "nan_inf_pixels": nan, "fireflies_local50x": ff, "resolution": [w, h]}
json.dump(report, open(f"{out_dir}/still_checks.json", "w"), indent=1)
print("STILL", json.dumps(report))
