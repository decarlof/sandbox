#!/usr/bin/env python
"""
Flat field vertical stripe motion analysis.

Analyzes vertical motion of horizontal stripes in flat field images at two timescales:
1. Fast motion: frame-to-frame shifts within each 10-image set (1 second timescale)
2. Slow motion: drift of averaged stripe position across sets (8 hour timescale)

Usage:
    python analyze_stripe_motion.py /path/to/flat/images

Output:
    - Console summary statistics
    - stripe_motion_results.npz  (numerical results)
    - stripe_motion_slow.png     (slow drift plot)
    - stripe_motion_fast.png     (fast motion statistics plot)
"""

import os
import sys
import glob
import numpy as np
from skimage import io
from scipy.signal import correlate

# --- Configuration ---
IMAGES_PER_SET = 10
ACQUISITION_INTERVAL = 60  # seconds between sets
EXPOSURE_TIME = 0.1        # seconds per frame
FILE_PREFIX = "flat_2x_2bin3.45um_momo20keV_"


def load_image(filepath):
    """Load a single TIFF image and return as float64 array."""
    img = io.imread(filepath).astype(np.float64)
    return img


def compute_vertical_profile(img):
    """
    Compute the vertical profile by averaging along the horizontal axis.
    Returns a 1D array of length = image height.
    """
    return np.mean(img, axis=1)


def compute_vertical_shift(profile_ref, profile_target):
    """
    Compute the vertical shift (in pixels) of profile_target relative to profile_ref
    using cross-correlation with sub-pixel interpolation.

    Returns:
        shift: float, vertical shift in pixels (positive = moved down)
    """
    n = len(profile_ref)

    # Normalize profiles (zero mean, unit variance)
    ref = profile_ref - np.mean(profile_ref)
    ref_std = np.std(ref)
    if ref_std > 0:
        ref = ref / ref_std

    tgt = profile_target - np.mean(profile_target)
    tgt_std = np.std(tgt)
    if tgt_std > 0:
        tgt = tgt / tgt_std

    # Cross-correlation
    cc = correlate(tgt, ref, mode='full')
    mid = len(cc) // 2

    # Search within +/- 50 pixels
    search_range = min(50, mid)
    cc_region = cc[mid - search_range: mid + search_range + 1]

    # Integer peak
    peak_idx = np.argmax(cc_region)
    peak_pos = peak_idx - search_range  # shift relative to zero-lag

    # Sub-pixel refinement using parabolic interpolation
    if 0 < peak_idx < len(cc_region) - 1:
        y0 = cc_region[peak_idx - 1]
        y1 = cc_region[peak_idx]
        y2 = cc_region[peak_idx + 1]
        denom = 2.0 * (2.0 * y1 - y0 - y2)
        if abs(denom) > 1e-12:
            sub_pixel = (y0 - y2) / denom
        else:
            sub_pixel = 0.0
        shift = peak_pos + sub_pixel
    else:
        shift = float(peak_pos)

    return shift


def find_image_files(image_dir):
    """
    Find and sort all flat field TIFF files in the directory.
    Returns sorted list of file paths.
    """
    pattern = os.path.join(image_dir, f"{FILE_PREFIX}*.tif")
    files = sorted(glob.glob(pattern))
    if not files:
        # Try .tiff extension
        pattern = os.path.join(image_dir, f"{FILE_PREFIX}*.tiff")
        files = sorted(glob.glob(pattern))
    return files


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_stripe_motion.py /path/to/flat/images")
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
        print("ERROR: No files found. Check directory and file prefix.")
        sys.exit(1)

    n_sets = n_files // IMAGES_PER_SET
    remainder = n_files % IMAGES_PER_SET
    print(f"Number of complete sets: {n_sets} ({IMAGES_PER_SET} images each)")
    if remainder > 0:
        print(f"WARNING: {remainder} extra images will be ignored.")

    # --- Load first image to get dimensions ---
    test_img = load_image(files[0])
    img_height, img_width = test_img.shape[:2]
    print(f"Image dimensions: {img_width} x {img_height} pixels")
    print()

    # =============================================
    # STEP 1: Compute vertical profiles for all sets
    # =============================================
    print("=" * 60)
    print("STEP 1: Computing vertical profiles for all sets")
    print("=" * 60)

    # Storage for per-set results
    set_avg_profiles = []          # averaged profile for each set
    fast_shifts_all = []           # list of arrays, each with 9 frame-to-frame shifts
    fast_shifts_from_first = []    # list of arrays, each with 10 shifts relative to first frame

    for s in range(n_sets):
        start_idx = s * IMAGES_PER_SET
        set_files = files[start_idx: start_idx + IMAGES_PER_SET]

        # Load all images in this set and compute vertical profiles
        profiles = []
        for f in set_files:
            img = load_image(f)
            prof = compute_vertical_profile(img)
            profiles.append(prof)

        profiles = np.array(profiles)  # shape: (10, height)

        # Average profile for this set (for slow motion analysis)
        avg_prof = np.mean(profiles, axis=0)
        set_avg_profiles.append(avg_prof)

        # Fast motion: shifts relative to first frame in the set
        shifts_from_first = np.zeros(IMAGES_PER_SET)
        for i in range(1, IMAGES_PER_SET):
            shifts_from_first[i] = compute_vertical_shift(profiles[0], profiles[i])
        fast_shifts_from_first.append(shifts_from_first)

        # Fast motion: frame-to-frame shifts
        frame_shifts = np.zeros(IMAGES_PER_SET - 1)
        for i in range(IMAGES_PER_SET - 1):
            frame_shifts[i] = compute_vertical_shift(profiles[i], profiles[i + 1])
        fast_shifts_all.append(frame_shifts)

        if (s + 1) % 50 == 0 or s == 0 or s == n_sets - 1:
            print(f"  Set {s:4d}/{n_sets}: "
                  f"files {os.path.basename(set_files[0])} - "
                  f"{os.path.basename(set_files[-1])} | "
                  f"fast range: {shifts_from_first.max() - shifts_from_first.min():.3f} px")

    set_avg_profiles = np.array(set_avg_profiles)  # shape: (n_sets, height)
    fast_shifts_from_first = np.array(fast_shifts_from_first)  # shape: (n_sets, 10)
    fast_shifts_all = np.array(fast_shifts_all)  # shape: (n_sets, 9)

    print()

    # =============================================
    # STEP 2: Slow motion analysis
    # =============================================
    print("=" * 60)
    print("STEP 2: Slow motion analysis (set-to-set over 8 hours)")
    print("=" * 60)

    # Compute shift of each set's average profile relative to the first set
    slow_shifts = np.zeros(n_sets)
    for s in range(1, n_sets):
        slow_shifts[s] = compute_vertical_shift(set_avg_profiles[0], set_avg_profiles[s])

    # Time axis in minutes
    time_minutes = np.arange(n_sets) * ACQUISITION_INTERVAL / 60.0
    time_hours = time_minutes / 60.0

    print(f"  Total slow drift range: {slow_shifts.max() - slow_shifts.min():.3f} pixels")
    print(f"  Slow drift max:         {slow_shifts.max():.3f} pixels")
    print(f"  Slow drift min:         {slow_shifts.min():.3f} pixels")
    print(f"  Slow drift mean:        {np.mean(slow_shifts):.3f} pixels")
    print(f"  Slow drift std:         {np.std(slow_shifts):.3f} pixels")

    # Linear trend
    coeffs = np.polyfit(time_minutes, slow_shifts, 1)
    trend_slope = coeffs[0]  # pixels per minute
    print(f"  Linear trend:           {trend_slope:.5f} pixels/min "
          f"({trend_slope * 60:.4f} pixels/hour)")

    # Detrended slow shifts
    slow_trend = np.polyval(coeffs, time_minutes)
    slow_detrended = slow_shifts - slow_trend
    print(f"  Detrended std:          {np.std(slow_detrended):.3f} pixels")
    print()

    # =============================================
    # STEP 3: Fast motion analysis
    # =============================================
    print("=" * 60)
    print("STEP 3: Fast motion analysis (within 1-second sets)")
    print("=" * 60)

    # Frame-to-frame statistics
    all_frame_shifts = fast_shifts_all.flatten()
    print(f"  Frame-to-frame shifts (0.1 s interval):")
    print(f"    Mean:  {np.mean(all_frame_shifts):.4f} pixels")
    print(f"    Std:   {np.std(all_frame_shifts):.4f} pixels")
    print(f"    Min:   {np.min(all_frame_shifts):.4f} pixels")
    print(f"    Max:   {np.max(all_frame_shifts):.4f} pixels")
    print(f"    |Max|: {np.max(np.abs(all_frame_shifts)):.4f} pixels")

    # Range within each set (max - min of shifts from first frame)
    fast_ranges = np.ptp(fast_shifts_from_first, axis=1)
    print(f"  Within-set range (over 1 s):")
    print(f"    Mean range: {np.mean(fast_ranges):.4f} pixels")
    print(f"    Std range:  {np.std(fast_ranges):.4f} pixels")
    print(f"    Min range:  {np.min(fast_ranges):.4f} pixels")
    print(f"    Max range:  {np.max(fast_ranges):.4f} pixels")
    print()

    # =============================================
    # STEP 4: Summary
    # =============================================
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Image directory:       {image_dir}")
    print(f"  Total files:           {n_files}")
    print(f"  Complete sets:         {n_sets}")
    print(f"  Image size:            {img_width} x {img_height}")
    print(f"  Duration:              {time_hours[-1]:.1f} hours")
    print()
    print(f"  SLOW MOTION (set-to-set, {ACQUISITION_INTERVAL}s interval):")
    print(f"    Total drift range:   {slow_shifts.max() - slow_shifts.min():.3f} pixels")
    print(f"    Linear trend:        {trend_slope * 60:.4f} pixels/hour")
    print(f"    Detrended std:       {np.std(slow_detrended):.3f} pixels")
    print()
    print(f"  FAST MOTION (within 1s sets, 0.1s interval):")
    print(f"    Frame-to-frame std:  {np.std(all_frame_shifts):.4f} pixels")
    print(f"    Mean within-set range: {np.mean(fast_ranges):.4f} pixels")
    print()

    # =============================================
    # STEP 5: Save results
    # =============================================
    out_npz = os.path.join(image_dir, "stripe_motion_results.npz")
    np.savez(out_npz,
             time_minutes=time_minutes,
             time_hours=time_hours,
             slow_shifts=slow_shifts,
             slow_trend=slow_trend,
             slow_detrended=slow_detrended,
             trend_coeffs=coeffs,
             fast_shifts_from_first=fast_shifts_from_first,
             fast_shifts_frame_to_frame=fast_shifts_all,
             fast_ranges=fast_ranges,
             )
    print(f"Numerical results saved to: {out_npz}")

    # =============================================
    # STEP 6: Generate plots (optional, skip if matplotlib not available)
    # =============================================
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        # --- Slow motion plot ---
        fig, axes = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

        axes[0].plot(time_hours, slow_shifts, 'b-', linewidth=0.5, alpha=0.7)
        axes[0].plot(time_hours, slow_trend, 'r-', linewidth=2,
                     label=f'Linear trend: {trend_slope * 60:.4f} px/hr')
        axes[0].set_ylabel('Vertical shift (pixels)')
        axes[0].set_title('Slow vertical stripe drift (relative to first set)')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].plot(time_hours, slow_detrended, 'g-', linewidth=0.5, alpha=0.7)
        axes[1].set_ylabel('Detrended shift (pixels)')
        axes[1].set_title(f'Detrended slow drift (std = {np.std(slow_detrended):.3f} px)')
        axes[1].grid(True, alpha=0.3)

        axes[2].plot(time_hours, fast_ranges, 'orange', linewidth=0.5, alpha=0.7)
        axes[2].set_ylabel('Within-set range (pixels)')
        axes[2].set_xlabel('Time (hours)')
        axes[2].set_title(f'Fast motion range per set (mean = {np.mean(fast_ranges):.4f} px)')
        axes[2].grid(True, alpha=0.3)

        plt.tight_layout()
        slow_plot = os.path.join(image_dir, "stripe_motion_slow.png")
        plt.savefig(slow_plot, dpi=150)
        plt.close()
        print(f"Slow motion plot saved to: {slow_plot}")

        # --- Fast motion plot ---
        fig, axes = plt.subplots(2, 1, figsize=(12, 7))

        axes[0].hist(all_frame_shifts, bins=100, edgecolor='black', alpha=0.7)
        axes[0].set_xlabel('Frame-to-frame shift (pixels)')
        axes[0].set_ylabel('Count')
        axes[0].set_title(f'Frame-to-frame vertical shifts (0.1 s interval)\n'
                          f'mean={np.mean(all_frame_shifts):.4f}, '
                          f'std={np.std(all_frame_shifts):.4f} px')
        axes[0].axvline(0, color='r', linestyle='--', alpha=0.5)
        axes[0].grid(True, alpha=0.3)

        # Show a few example sets
        n_example = min(5, n_sets)
        frame_times = np.arange(IMAGES_PER_SET) * EXPOSURE_TIME
        for s in range(n_example):
            axes[1].plot(frame_times, fast_shifts_from_first[s],
                         'o-', markersize=3, label=f'Set {s}')
        axes[1].set_xlabel('Time within set (s)')
        axes[1].set_ylabel('Shift from first frame (pixels)')
        axes[1].set_title('Example fast motion traces (first 5 sets)')
        axes[1].legend(fontsize=8)
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()
        fast_plot = os.path.join(image_dir, "stripe_motion_fast.png")
        plt.savefig(fast_plot, dpi=150)
        plt.close()
        print(f"Fast motion plot saved to: {fast_plot}")

    except ImportError:
        print("matplotlib not available. Skipping plot generation.")

    print("\nDone.")


if __name__ == "__main__":
    main()

