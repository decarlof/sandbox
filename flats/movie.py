#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

folder = Path("/Users/decarlo/Downloads/data")
files = sorted(folder.glob("flat_1min_*.tif"))
if not files:
    raise SystemExit("No files found matching flat_1min_*.tif")

# Load all frames (OK for modest number of images; if huge, we can stream instead)
frames = [tiff.imread(f) for f in files]

# Robust display scaling using percentiles from the first frame
vmin, vmax = np.percentile(frames[0], (1, 99))

fig, ax = plt.subplots(figsize=(7, 7))
im = ax.imshow(frames[0], cmap="gray", vmin=vmin, vmax=vmax, animated=True)
title = ax.set_title(files[0].name)
ax.axis("off")

def update(i):
    im.set_array(frames[i])
    title.set_text(f"{i+1}/{len(frames)}  {files[i].name}")
    return im, title

# interval in ms (1000 ms = 1 frame/sec). Adjust as desired.
ani = FuncAnimation(fig, update, frames=len(frames), interval=150, blit=False, repeat=True)

plt.show()

# Optional: save an mp4 (requires ffmpeg installed)
# ani.save("flat_1min_movie.mp4", dpi=150, fps=10)
