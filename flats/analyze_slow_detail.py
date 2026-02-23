#!/usr/bin/env python
"""
Detailed slow motion analysis of flat field stripe drift.

Loads results from analyze_stripe_motion.py and produces:
1. Time-segmented statistics (stable vs unstable periods)
2. Rolling standard deviation to identify transition points
3. Low-frequency spectral analysis
4. Autocorrelation analysis

Usage:
    python analyze_slow_detail.py /path/to/flat/images

Requires stripe_motion_results.npz from analyze_stripe_motion.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_slow_detail.py /path/to/flat/images")
        sys.exit(1)

    image_dir = sys.argv[1]
    npz_file = os.path.join(image_dir, "stripe_motion_results.npz")

    if not os.path.isfile(npz_file):
        print(f"ERROR: Results file not found: {npz_file}")
        print("Run analyze_stripe_motion.py first.")
        sys.exit(1)

    # --- Load results ---
    print(f"Loading results from: {npz_file}")
    data = np.load(npz_file)
    time_minutes = data['time_minutes']
    time_hours = data['time_hours']
    slow_shifts = data['slow_shifts']
    slow_detrended = data['slow_detrended']
    fast_ranges = data['fast_ranges']
    trend_coeffs = data['trend_coeffs']

    n_sets = len(slow_shifts)
    dt_min = time_minutes[1] - time_minutes[0] if n_sets > 1 else 1.0

    print(f"Loaded {n_sets} sets, duration {time_hours[-1]:.1f} hours")
    print()

    # =============================================
    # 1. Rolling statistics to find transition point
    # =============================================
    print("=" * 60)
    print("1. ROLLING STATISTICS")
    print("=" * 60)

    window_sizes = [10, 20, 30]  # in sets (= minutes)
    for w in window_sizes:
        if w >= n_sets:
            continue
        rolling_std = np.array([
            np.std(slow_shifts[max(0, i - w):i + 1])
            for i in range(n_sets)
        ])
        rolling_mean = np.array([
            np.mean(slow_shifts[max(0, i - w):i + 1])
            for i in range(n_sets)
        ])

        # Find where rolling std first exceeds 2x the early baseline
        baseline_std = np.mean(rolling_std[:n_sets // 3])
        threshold = 2.0 * baseline_std
        transition_indices = np.where(rolling_std > threshold)[0]

        if len(transition_indices) > 0:
            trans_set = transition_indices[0]
            trans_time = time_hours[trans_set]
        else:
            trans_set = n_sets
            trans_time = time_hours[-1]

        print(f"  Window = {w} min ({w} sets):")
        print(f"    Baseline std (first 1/3):  {baseline_std:.3f} px")
        print(f"    Threshold (2x baseline):   {threshold:.3f} px")
        print(f"    Transition at:             set {trans_set} "
              f"(t = {trans_time:.2f} h)")
        print(f"    Rolling std range:         "
              f"{rolling_std.min():.3f} - {rolling_std.max():.3f} px")
        print()

    # =============================================
    # 2. Segmented analysis
    # =============================================
    print("=" * 60)
    print("2. SEGMENTED ANALYSIS")
    print("=" * 60)

    # Use the 20-set rolling std to find transition
    w = 20
    rolling_std_20 = np.array([
        np.std(slow_shifts[max(0, i - w):i + 1])
        for i in range(n_sets)
    ])
    baseline_std_20 = np.mean(rolling_std_20[:n_sets // 3])
    threshold_20 = 2.0 * baseline_std_20
    transition_indices_20 = np.where(rolling_std_20 > threshold_20)[0]
    if len(transition_indices_20) > 0:
        split_set = transition_indices_20[0]
    else:
        split_set = n_sets

    split_time = time_hours[split_set] if split_set < n_sets else time_hours[-1]

    print(f"  Splitting at set {split_set} (t = {split_time:.2f} h)")
    print()

    # Stable period
    stable = slow_shifts[:split_set]
    stable_time = time_hours[:split_set]
    if len(stable) > 1:
        stable_coeffs = np.polyfit(time_minutes[:split_set], stable, 1)
        stable_trend = stable_coeffs[0] * 60  # px/hr
        stable_detrended = stable - np.polyval(stable_coeffs, time_minutes[:split_set])

        # Set-to-set changes
        stable_diffs = np.diff(stable)

        print(f"  STABLE PERIOD (0 - {split_time:.2f} h, {len(stable)} sets):")
        print(f"    Drift range:       {stable.max() - stable.min():.3f} px")
        print(f"    Mean shift:        {np.mean(stable):.3f} px")
        print(f"    Std:               {np.std(stable):.3f} px")
        print(f"    Linear trend:      {stable_trend:.4f} px/hr")
        print(f"    Detrended std:     {np.std(stable_detrended):.3f} px")
        print(f"    Set-to-set change:")
        print(f"      Mean:            {np.mean(stable_diffs):.4f} px")
        print(f"      Std:             {np.std(stable_diffs):.4f} px")
        print(f"      Max |change|:    {np.max(np.abs(stable_diffs)):.4f} px")
        print()

    # Unstable period
    unstable = slow_shifts[split_set:]
    unstable_time = time_hours[split_set:]
    if len(unstable) > 1:
        unstable_coeffs = np.polyfit(time_minutes[split_set:], unstable, 1)
        unstable_trend = unstable_coeffs[0] * 60  # px/hr
        unstable_detrended = unstable - np.polyval(unstable_coeffs,
                                                    time_minutes[split_set:])
        unstable_diffs = np.diff(unstable)

        print(f"  UNSTABLE PERIOD ({split_time:.2f} - {time_hours[-1]:.1f} h, "
              f"{len(unstable)} sets):")
        print(f"    Drift range:       {unstable.max() - unstable.min():.3f} px")
        print(f"    Mean shift:        {np.mean(unstable):.3f} px")
        print(f"    Std:               {np.std(unstable):.3f} px")
        print(f"    Linear trend:      {unstable_trend:.4f} px/hr")
        print(f"    Detrended std:     {np.std(unstable_detrended):.3f} px")
        print(f"    Set-to-set change:")
        print(f"      Mean:            {np.mean(unstable_diffs):.4f} px")
        print(f"      Std:             {np.std(unstable_diffs):.4f} px")
        print(f"      Max |change|:    {np.max(np.abs(unstable_diffs)):.4f} px")
        print()

    # =============================================
    # 3. Spectral analysis
    # =============================================
    print("=" * 60)
    print("3. SPECTRAL ANALYSIS (slow motion)")
    print("=" * 60)

    # FFT of the full slow shift signal
    n = len(slow_shifts)
    # Remove mean
    signal = slow_shifts - np.mean(slow_shifts)
    # Apply Hanning window to reduce spectral leakage
    window = np.hanning(n)
    signal_windowed = signal * window

    fft_vals = np.fft.rfft(signal_windowed)
    power = np.abs(fft_vals) ** 2
    freqs = np.fft.rfftfreq(n, d=dt_min)  # cycles per minute

    # Convert to periods in minutes
    periods_min = np.zeros_like(freqs)
    periods_min[1:] = 1.0 / freqs[1:]

    # Find dominant frequencies (excluding DC)
    power_no_dc = power.copy()
    power_no_dc[0] = 0

    # Top 10 peaks
    n_peaks = min(10, len(power_no_dc) - 1)
    peak_indices = np.argsort(power_no_dc)[::-1][:n_peaks]

    print(f"  Sampling: 1 sample per {dt_min:.0f} min")
    print(f"  Nyquist frequency: {freqs[-1]:.5f} cycles/min "
          f"(period = {1.0/freqs[-1]:.1f} min)")
    print(f"  Frequency resolution: {freqs[1]:.6f} cycles/min "
          f"(period = {1.0/freqs[1]:.1f} min)")
    print()
    print(f"  Top {n_peaks} spectral peaks:")
    print(f"    {'Rank':>4s}  {'Freq (cyc/min)':>14s}  {'Period (min)':>12s}  "
          f"{'Period (h)':>10s}  {'Power':>12s}")
    for rank, idx in enumerate(peak_indices):
        if idx == 0:
            continue
        f = freqs[idx]
        p_min = periods_min[idx]
        p_hr = p_min / 60.0
        print(f"    {rank + 1:4d}  {f:14.6f}  {p_min:12.1f}  "
              f"{p_hr:10.2f}  {power_no_dc[idx]:12.1f}")
    print()

    # =============================================
    # 4. Autocorrelation
    # =============================================
    print("=" * 60)
    print("4. AUTOCORRELATION ANALYSIS")
    print("=" * 60)

    signal_norm = signal / np.std(signal) if np.std(signal) > 0 else signal
    autocorr = np.correlate(signal_norm, signal_norm, mode='full')
    autocorr = autocorr[n - 1:]  # keep positive lags only
    autocorr = autocorr / autocorr[0]  # normalize

    # Find first zero crossing
    zero_crossings = np.where(np.diff(np.sign(autocorr)))[0]
    if len(zero_crossings) > 0:
        first_zero = zero_crossings[0]
        decorrelation_time = first_zero * dt_min
        print(f"  First zero crossing at lag {first_zero} "
              f"({decorrelation_time:.0f} min = {decorrelation_time / 60:.2f} h)")
    else:
        print(f"  No zero crossing found (signal stays correlated)")

    # Find where autocorrelation drops below 1/e
    e_crossings = np.where(autocorr < 1.0 / np.e)[0]
    if len(e_crossings) > 0:
        e_lag = e_crossings[0]
        e_time = e_lag * dt_min
        print(f"  Drops below 1/e at lag {e_lag} "
              f"({e_time:.0f} min = {e_time / 60:.2f} h)")
    else:
        print(f"  Autocorrelation stays above 1/e")

    # Report autocorrelation at specific lags
    lag_minutes = [1, 2, 5, 10, 20, 30, 60, 120, 180, 240]
    print()
    print(f"  Autocorrelation at specific lags:")
    print(f"    {'Lag (min)':>10s}  {'Lag (sets)':>10s}  {'Autocorr':>10s}")
    for lag_m in lag_minutes:
        lag_sets = int(lag_m / dt_min)
        if lag_sets < n:
            print(f"    {lag_m:10d}  {lag_sets:10d}  {autocorr[lag_sets]:10.4f}")
    print()

    # =============================================
    # 5. Set-to-set change statistics
    # =============================================
    print("=" * 60)
    print("5. SET-TO-SET CHANGES (consecutive 1-minute intervals)")
    print("=" * 60)

    diffs = np.diff(slow_shifts)
    abs_diffs = np.abs(diffs)

    print(f"  Mean change:     {np.mean(diffs):.4f} px/min")
    print(f"  Std change:      {np.std(diffs):.4f} px/min")
    print(f"  Mean |change|:   {np.mean(abs_diffs):.4f} px/min")
    print(f"  Max |change|:    {np.max(abs_diffs):.4f} px/min")
    print()
    print(f"  |Change| percentiles:")
    for p in [50, 75, 90, 95, 99]:
        print(f"    {p:3d}th: {np.percentile(abs_diffs, p):.4f} px/min")
    print()

    # =============================================
    # 6. Save detailed plots
    # =============================================
    fig, axes = plt.subplots(4, 2, figsize=(16, 18))

    # (0,0) Slow shifts with segments
    ax = axes[0, 0]
    if split_set < n_sets:
        ax.axvline(split_time, color='red', linestyle='--', alpha=0.7,
                   label=f'Transition: {split_time:.2f} h')
    ax.plot(time_hours, slow_shifts, 'b-', linewidth=0.5, alpha=0.7)
    ax.set_ylabel('Vertical shift (px)')
    ax.set_title('Slow drift with transition point')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (0,1) Rolling std
    ax = axes[0, 1]
    for w_plot in window_sizes:
        if w_plot >= n_sets:
            continue
        rs = np.array([
            np.std(slow_shifts[max(0, i - w_plot):i + 1])
            for i in range(n_sets)
        ])
        ax.plot(time_hours, rs, linewidth=1, label=f'{w_plot} min window')
    ax.set_ylabel('Rolling std (px)')
    ax.set_title('Rolling standard deviation')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (1,0) Stable period detail
    ax = axes[1, 0]
    if split_set > 1:
        ax.plot(stable_time, stable, 'b-', linewidth=0.5)
        stable_trend_line = np.polyval(stable_coeffs, time_minutes[:split_set])
        ax.plot(stable_time, stable_trend_line, 'r-', linewidth=2,
                label=f'Trend: {stable_trend:.4f} px/hr')
        ax.set_ylabel('Vertical shift (px)')
        ax.set_title(f'Stable period (0 - {split_time:.2f} h)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # (1,1) Unstable period detail
    ax = axes[1, 1]
    if split_set < n_sets and len(unstable) > 1:
        ax.plot(unstable_time, unstable, 'b-', linewidth=0.5)
        unstable_trend_line = np.polyval(unstable_coeffs, time_minutes[split_set:])
        ax.plot(unstable_time, unstable_trend_line, 'r-', linewidth=2,
                label=f'Trend: {unstable_trend:.4f} px/hr')
        ax.set_ylabel('Vertical shift (px)')
        ax.set_title(f'Unstable period ({split_time:.2f} - {time_hours[-1]:.1f} h)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # (2,0) Power spectrum
    ax = axes[2, 0]
    ax.semilogy(freqs[1:] * 60, power[1:], 'b-', linewidth=0.5)
    ax.set_xlabel('Frequency (cycles/hour)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectrum of slow drift')
    ax.grid(True, alpha=0.3)

    # (2,1) Power spectrum vs period
    ax = axes[2, 1]
    valid = periods_min[1:] <= 240  # up to 4 hours
    ax.semilogy(periods_min[1:][valid], power[1:][valid], 'b-', linewidth=0.5)
    ax.set_xlabel('Period (minutes)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectrum vs period')
    ax.grid(True, alpha=0.3)

    # (3,0) Autocorrelation
    ax = axes[3, 0]
    max_lag = min(n // 2, 240)  # up to 240 minutes
    lag_time = np.arange(max_lag) * dt_min
    ax.plot(lag_time, autocorr[:max_lag], 'b-', linewidth=1)
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.axhline(1.0 / np.e, color='r', linestyle='--', alpha=0.5,
               label='1/e')
    ax.set_xlabel('Lag (minutes)')
    ax.set_ylabel('Autocorrelation')
    ax.set_title('Autocorrelation of slow drift')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (3,1) Set-to-set changes histogram
    ax = axes[3, 1]
    ax.hist(diffs, bins=80, edgecolor='black', alpha=0.7)
    ax.axvline(0, color='r', linestyle='--', alpha=0.5)
    ax.set_xlabel('Set-to-set change (px/min)')
    ax.set_ylabel('Count')
    ax.set_title(f'Set-to-set changes (std={np.std(diffs):.3f} px/min)')

    plt.tight_layout()

    detail_plot = os.path.join(image_dir, "stripe_motion_detail.png")
    plt.savefig(detail_plot, dpi=150)
    print(f"Detail plot saved to: {detail_plot}")

    plt.show(block=True)

    print("\nDone.")

if __name__ == "__main__":
    main()
