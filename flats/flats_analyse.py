#!/usr/bin/env python3
from pathlib import Path
import numpy as np
import tifffile as tiff
import matplotlib.pyplot as plt
from skimage.registration import phase_cross_correlation
from scipy.ndimage import gaussian_filter

folder = Path("/Users/decarlo/Downloads/data")
files = sorted(folder.glob("flat_1min_*.tif"))
assert files, "No files found"

def preprocess(img):
    img = img.astype(np.float32)
    # normalize to reduce intensity drift
    img = (img - np.median(img)) / (np.std(img) + 1e-8)
    # band-pass-ish: remove slow background
    low = gaussian_filter(img, sigma=30)
    img = img - low
    # mild denoise
    img = gaussian_filter(img, sigma=1)
    return img

ref = preprocess(tiff.imread(files[0]))

dy = []
dx = []
for f in files:
    img = preprocess(tiff.imread(f))
    shift, error, phasediff = phase_cross_correlation(ref, img, upsample_factor=50)
    # shift is (row_shift, col_shift) = (dy, dx)
    dy.append(shift[0])
    dx.append(shift[1])

dy = np.array(dy)
dx = np.array(dx)

t = np.arange(len(files))  # minutes if 1 frame/min
plt.plot(t, dy, "-o", ms=3)
plt.xlabel("time (min)")
plt.ylabel("vertical shift dy (pixels) relative to first frame")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

print(f"dy range: {dy.min():.3f} .. {dy.max():.3f} pixels")
print(f"dx range: {dx.min():.3f} .. {dx.max():.3f} pixels")
