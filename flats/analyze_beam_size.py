#!/usr/bin/env python
"""
Beam vertical size analysis over time.

Loads flat field images and measures the vertical extent of the X-ray beam
in each set by analyzing the vertical intensity profile.

Usage:
    python analyze_beam_size.py /path/to/flat/images

Output:
    - Console summary statistics
    - beam_size_results.npz (numerical results)
    - beam_size.png (plot)
"""

import os
import sys
import re
import glob
import numpy as np
from skimage import io
import matplotlib.pyplot as plt

# --- Configuration ---
IMAGES_PER_SET = 10
ACQUISITION_INTERVAL = 60  # seconds between sets
FILE_PREFIX = "flat_2x_2bin3.45um_momo20keV_"


def extract_file_number(filepath):
    """Extract the numeric index from a flat field filename."""
    basename = os.path.basename(filepath)
    match = re.search(r'_(\d+)\.tiff?$', basename)
    if match:
        return int(match.group(1))
    return -1


def load_image(filepath):
    """Load a single TIFF image and return as float64 array."""
    return io.imread(filepath).astype(np.float64)


def compute_vertical_profile(img):
    """Compute the vertical profile by averaging along the horizontal axis."""
    return np.mean(img, axis=1)


def measure_beam_size(profile, threshold_fraction=0.1):
    """
    Measure the vertical beam size from a 1D vertical profile.

    Returns a dictionary with multiple size metrics:
    - fwhm: full width at half maximum (pixels)
    - fw10: full width at 10% of maximum (pixels)
    - threshold_size: width above threshold_fraction of max (pixels)
    - centroid: intensity-weighted center position (pixels)
    - std: intensity-weighted standard deviation (pixels)
    - edge_top: top edge position (pixels)
    - edge_bottom: bottom edge position (pixels)
    """
    n = len(profile)
    positions = np.arange(n)

    # Subtract baseline (use edges of the profile)
    edge_width = max(10, n // 50)
    baseline = 0.5 * (np.mean(profile[:edge_width]) +
                       np.mean(profile[-edge_width:]))
    prof = profile - baseline
    prof = np.maximum(prof, 0)  # clip negatives

    peak_val = np.max(prof)
    if peak_val <= 0:
        return {
            'fwhm': 0, 'fw10': 0, 'threshold_size': 0,
            'centroid': n / 2, 'std': 0,
            'edge_top': 0, 'edge_bottom': n - 1,
            'peak_intensity': 0, 'integrated_intensity': 0,
        }

    # Normalize
    prof_norm = prof / peak_val

    # --- FWHM ---
    above_half = prof_norm >= 0.5
    above_indices = np.where(above_half)[0]
    if len(above_indices) > 0:
        # Sub-pixel interpolation at edges
        first = above_indices[0]
        last = above_indices[-1]

        # Interpolate left edge
        if first > 0:
            y0, y1 = prof_norm[first - 1], prof_norm[first]
            if y1 != y0:
                left_edge = (first - 1) + (0.5 - y0) / (y1 - y0)
            else:
                left_edge = float(first)
        else:
            left_edge = 0.0

        # Interpolate right edge
        if last < n - 1:
            y0, y1 = prof_norm[last], prof_norm[last + 1]
            if y0 != y1:
                right_edge = last + (0.5 - y0) / (y1 - y0)
            else:
                right_edge = float(last)
        else:
            right_edge = float(n - 1)

        fwhm = right_edge - left_edge
    else:
        fwhm = 0.0

    # --- FW10% ---
    above_10 = prof_norm >= 0.1
    above_10_indices = np.where(above_10)[0]
    if len(above_10_indices) > 0:
        first10 = above_10_indices[0]
        last10 = above_10_indices[-1]

        if first10 > 0:
            y0, y1 = prof_norm[first10 - 1], prof_norm[first10]
            if y1 != y0:
                left10 = (first10 - 1) + (0.1 - y0) / (y1 - y0)
            else:
                left10 = float(first10)
        else:
            left10 = 0.0

        if last10 < n - 1:
            y0, y1 = prof_norm[last10], prof_norm[last10 + 1]
            if y0 != y1:
                right10 = last10 + (0.1 - y0) / (y1 - y0)
            else:
                right10 = float(last10)
        else:
            right10 = float(n - 1)

        fw10 = right10 - left10
    else:
        fw10 = 0.0

    # --- Threshold size ---
    above_thresh = prof_norm >= threshold_fraction
    threshold_size = float(np.sum(above_thresh))

    # --- Centroid and std (intensity-weighted) ---
    total = np.sum(prof)
    if total > 0:
        centroid = np.sum(positions * prof) / total
        variance = np.sum((positions - centroid) ** 2 * prof) / total
        std = np.sqrt(variance)
    else:
        centroid = n / 2.0
        std = 0.0

    # --- Edge positions (10% threshold) ---
    if len(above_10_indices) > 0:
        edge_top = left10 if first10 > 0 else float(above_10_indices[0])
        edge_bottom = right10 if last10 < n - 1 else float(above_10_indices[-1])
    else:
        edge_top = 0.0
        edge_bottom = float(n - 1)

    # --- Intensities ---
    peak_intensity = peak_val + baseline
    integrated_intensity = np.sum(prof)

    return {
        'fwhm': fwhm,
        'fw10': fw10,
        'threshold_size': threshold_size,
        'centroid': centroid,
        'std': std,
        'edge_top': edge_top,
        'edge_bottom': edge_bottom,
        'peak_intensity': peak_intensity,
        'integrated_intensity': integrated_intensity,
    }


def find_image_files(image_dir):
    """Find and sort all flat field TIFF files numerically."""
    pattern = os.path.join(image_dir, f"{FILE_PREFIX}*.tif")
    files = glob.glob(pattern)
    if not files:
        pattern = os.path.join(image_dir, f"{FILE_PREFIX}*.tiff")
        files = glob.glob(pattern)
    files.sort(key=extract_file_number)
    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_beam_size.py /path/to/flat/images")
        sys.exit(1)

    image_dir = sys.argv[1]

    if not os.path.isdir(image_dir):
        print(f"ERROR: Directory not found: {image_dir}")
        sys.exit(1)

    # --- Find files ---
    print(f"Scanning directory: {image_dir}")
    files = find_image_files(image_dir)
    n_files = len(files)
    print(f"Found {n_files} files matching prefix '{FILE_PREFIX}'")

    if n_files == 0:
        print("ERROR: No files found.")
        sys.exit(1)

    n_sets = n_files // IMAGES_PER_SET
    print(f"Number of complete sets: {n_sets}")

    # Get image dimensions
    test_img = load_image(files[0])
    img_height, img_width = test_img.shape[:2]
    pixel_size_um = 3.45  # µm
    print(f"Image dimensions: {img_width} x {img_height} pixels")
    print(f"Pixel size: {pixel_size_um} µm")
    print()

    # =============================================
    # Process all sets
    # =============================================
    print("=" * 60)
    print("Processing sets...")
    print("=" * 60)

    # Storage
    fwhm_arr = np.zeros(n_sets)
    fw10_arr = np.zeros(n_sets)
    centroid_arr = np.zeros(n_sets)
    std_arr = np.zeros(n_sets)
    edge_top_arr = np.zeros(n_sets)
    edge_bottom_arr = np.zeros(n_sets)
    peak_arr = np.zeros(n_sets)
    integrated_arr = np.zeros(n_sets)

    for s in range(n_sets):
        start_idx = s * IMAGES_PER_SET
        set_files = files[start_idx: start_idx + IMAGES_PER_SET]

        # Average all images in the set
        profiles = []
        for f in set_files:
            img = load_image(f)
            prof = compute_vertical_profile(img)
            profiles.append(prof)

        avg_profile = np.mean(profiles, axis=0)

        # Measure beam size
        metrics = measure_beam_size(avg_profile)

        fwhm_arr[s] = metrics['fwhm']
        fw10_arr[s] = metrics['fw10']
        centroid_arr[s] = metrics['centroid']
        std_arr[s] = metrics['std']
        edge_top_arr[s] = metrics['edge_top']
        edge_bottom_arr[s] = metrics['edge_bottom']
        peak_arr[s] = metrics['peak_intensity']
        integrated_arr[s] = metrics['integrated_intensity']

        if (s + 1) % 50 == 0 or s == 0 or s == n_sets - 1:
            print(f"  Set {s:4d}/{n_sets}: FWHM={metrics['fwhm']:.2f} px "
                  f"({metrics['fwhm'] * pixel_size_um:.1f} µm), "
                  f"centroid={metrics['centroid']:.1f} px, "
                  f"peak={metrics['peak_intensity']:.0f}")

    print()

    # Time axis
    time_minutes = np.arange(n_sets) * ACQUISITION_INTERVAL / 60.0
    time_hours = time_minutes / 60.0

    # Convert to µm
    fwhm_um = fwhm_arr * pixel_size_um
    fw10_um = fw10_arr * pixel_size_um
    std_um = std_arr * pixel_size_um

    # =============================================
    # Statistics
    # =============================================
    print("=" * 60)
    print("BEAM VERTICAL SIZE STATISTICS")
    print("=" * 60)

    print(f"\n  FWHM (pixels):")
    print(f"    Mean:   {np.mean(fwhm_arr):.2f}")
    print(f"    Std:    {np.std(fwhm_arr):.2f}")
    print(f"    Min:    {np.min(fwhm_arr):.2f}")
    print(f"    Max:    {np.max(fwhm_arr):.2f}")
    print(f"    Range:  {np.ptp(fwhm_arr):.2f}")

    print(f"\n  FWHM (µm):")
    print(f"    Mean:   {np.mean(fwhm_um):.1f}")
    print(f"    Std:    {np.std(fwhm_um):.1f}")
    print(f"    Min:    {np.min(fwhm_um):.1f}")
    print(f"    Max:    {np.max(fwhm_um):.1f}")
    print(f"    Range:  {np.ptp(fwhm_um):.1f}")

    print(f"\n  FW10% (pixels):")
    print(f"    Mean:   {np.mean(fw10_arr):.2f}")
    print(f"    Std:    {np.std(fw10_arr):.2f}")
    print(f"    Min:    {np.min(fw10_arr):.2f}")
    print(f"    Max:    {np.max(fw10_arr):.2f}")

    print(f"\n  Centroid position (pixels):")
    print(f"    Mean:   {np.mean(centroid_arr):.2f}")
    print(f"    Std:    {np.std(centroid_arr):.2f}")
    print(f"    Range:  {np.ptp(centroid_arr):.2f}")

    print(f"\n  Intensity-weighted std (pixels):")
    print(f"    Mean:   {np.mean(std_arr):.2f}")
    print(f"    Std:    {np.std(std_arr):.2f}")

    print(f"\n  Edge positions (10% threshold, pixels):")
    print(f"    Top edge mean:    {np.mean(edge_top_arr):.2f}")
    print(f"    Bottom edge mean: {np.mean(edge_bottom_arr):.2f}")
    print(f"    Top edge std:     {np.std(edge_top_arr):.2f}")
    print(f"    Bottom edge std:  {np.std(edge_bottom_arr):.2f}")

    print(f"\n  Peak intensity:")
    print(f"    Mean:   {np.mean(peak_arr):.0f}")
    print(f"    Std:    {np.std(peak_arr):.0f}")
    print(f"    Range:  {np.ptp(peak_arr):.0f}")

    print(f"\n  Integrated intensity:")
    print(f"    Mean:   {np.mean(integrated_arr):.0f}")
    print(f"    Std:    {np.std(integrated_arr):.0f}")
    print(f"    Rel. variation: {np.std(integrated_arr) / np.mean(integrated_arr) * 100:.2f}%")

    # Linear trend in FWHM
    fwhm_coeffs = np.polyfit(time_hours, fwhm_arr, 1)
    print(f"\n  FWHM linear trend: {fwhm_coeffs[0]:.3f} px/hr "
          f"({fwhm_coeffs[0] * pixel_size_um:.1f} µm/hr)")
    print()

    # =============================================
    # Save results
    # =============================================
    out_npz = os.path.join(image_dir, "beam_size_results.npz")
    np.savez(out_npz,
             time_minutes=time_minutes,
             time_hours=time_hours,
             fwhm=fwhm_arr,
             fw10=fw10_arr,
             centroid=centroid_arr,
             std=std_arr,
             edge_top=edge_top_arr,
             edge_bottom=edge_bottom_arr,
             peak_intensity=peak_arr,
             integrated_intensity=integrated_arr,
             pixel_size_um=pixel_size_um,
             )
    print(f"Results saved to: {out_npz}")

    # =============================================
    # Plots
    # =============================================
    print("Generating plots...")

    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    fig.suptitle('Beam Vertical Size Analysis — Feb 22, 2026 (00:00–08:03)',
                 fontsize=14, fontweight='bold', y=0.995)

    # (0,0) FWHM over time
    ax = axes[0, 0]
    ax.plot(time_hours, fwhm_arr, 'b-', linewidth=0.5, alpha=0.7)
    fwhm_trend = np.polyval(fwhm_coeffs, time_hours)
    ax.plot(time_hours, fwhm_trend, 'r-', linewidth=2,
            label=f'Trend: {fwhm_coeffs[0]:.3f} px/hr')
    ax.set_ylabel('FWHM (pixels)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Beam vertical FWHM (mean={np.mean(fwhm_arr):.1f} px, '
                 f'{np.mean(fwhm_um):.0f} µm)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (0,1) FWHM in µm
    ax = axes[0, 1]
    ax.plot(time_hours, fwhm_um, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('FWHM (µm)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Beam vertical FWHM in µm')
    ax.grid(True, alpha=0.3)

    # (1,0) Centroid position
    ax = axes[1, 0]
    ax.plot(time_hours, centroid_arr, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('Centroid position (pixels)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Beam centroid (mean={np.mean(centroid_arr):.1f} px, '
                 f'std={np.std(centroid_arr):.2f} px)')
    ax.grid(True, alpha=0.3)

    # (1,1) Edge positions
    ax = axes[1, 1]
    ax.plot(time_hours, edge_top_arr, 'b-', linewidth=0.5, alpha=0.7,
            label='Top edge (10%)')
    ax.plot(time_hours, edge_bottom_arr, 'r-', linewidth=0.5, alpha=0.7,
            label='Bottom edge (10%)')
    ax.set_ylabel('Edge position (pixels)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title('Beam edge positions (10% threshold)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (2,0) Peak intensity
    ax = axes[2, 0]
    ax.plot(time_hours, peak_arr, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('Peak intensity (counts)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Peak intensity (mean={np.mean(peak_arr):.0f})')
    ax.grid(True, alpha=0.3)

    # (2,1) Integrated intensity
    ax = axes[2, 1]
    ax.plot(time_hours, integrated_arr, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('Integrated intensity')
    ax.set_xlabel('Hour of day (starting 00:00)')
    rel_var = np.std(integrated_arr) / np.mean(integrated_arr) * 100
    ax.set_title(f'Integrated intensity (rel. variation={rel_var:.2f}%)')
    ax.grid(True, alpha=0.3)

    # (3,0) FWHM histogram
    ax = axes[3, 0]
    ax.hist(fwhm_arr, bins=50, edgecolor='black', alpha=0.7)
    ax.axvline(np.mean(fwhm_arr), color='r', linestyle='--',
               label=f'Mean: {np.mean(fwhm_arr):.1f} px')
    ax.set_xlabel('FWHM (pixels)')
    ax.set_ylabel('Count')
    ax.set_title('FWHM distribution')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (3,1) Intensity-weighted std over time
    ax = axes[3, 1]
    ax.plot(time_hours, std_arr, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('Intensity-weighted std (pixels)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Beam width (intensity-weighted std, '
                 f'mean={np.mean(std_arr):.1f} px)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    plot_file = os.path.join(image_dir, "beam_size.png")
    plt.savefig(plot_file, dpi=150)
    print(f"Plot saved to: {plot_file}")

    plt.show(block=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
