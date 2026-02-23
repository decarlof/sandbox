#!/usr/bin/env python
"""
Detailed slow motion analysis of flat field stripe drift (v2).

Loads results from analyze_stripe_motion.py and produces:
1. Smoothed drift to separate slow trend from oscillations
2. Time-segmented statistics using smoothed signal
3. Oscillation characterization
4. Spectral analysis on stable vs unstable segments
5. Practical flat field validity assessment

Usage:
    python analyze_slow_detail_v2.py /path/to/flat/images

Requires stripe_motion_results.npz from analyze_stripe_motion.py
"""

import os
import sys
import numpy as np
import matplotlib.pyplot as plt


def smooth(signal, window):
    """Simple moving average smoothing."""
    if window <= 1:
        return signal.copy()
    kernel = np.ones(window) / window
    padded = np.pad(signal, (window // 2, window // 2), mode='edge')
    smoothed = np.convolve(padded, kernel, mode='valid')
    return smoothed[:len(signal)]


def find_transition(rolling_std, time_hours, baseline_fraction=0.25,
                    threshold_factor=3.0, min_consecutive=5):
    """
    Find transition point where rolling std consistently exceeds threshold.
    Requires min_consecutive sets above threshold to avoid false triggers.
    """
    n = len(rolling_std)
    baseline_end = int(n * baseline_fraction)
    baseline_std = np.median(rolling_std[:baseline_end])
    threshold = threshold_factor * baseline_std

    count = 0
    for i in range(n):
        if rolling_std[i] > threshold:
            count += 1
            if count >= min_consecutive:
                return i - min_consecutive + 1, baseline_std, threshold
        else:
            count = 0

    return n, baseline_std, threshold


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_slow_detail_v2.py /path/to/flat/images")
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
    fast_ranges = data['fast_ranges']

    n_sets = len(slow_shifts)
    dt_min = time_minutes[1] - time_minutes[0] if n_sets > 1 else 1.0

    print(f"Loaded {n_sets} sets, duration {time_hours[-1]:.1f} hours")
    print()

    # =============================================
    # 1. Separate slow trend from oscillations
    # =============================================
    print("=" * 60)
    print("1. SEPARATING SLOW TREND FROM OSCILLATIONS")
    print("=" * 60)

    smooth_windows = [5, 15, 30, 60]
    smoothed = {}
    oscillation = {}

    for w in smooth_windows:
        s = smooth(slow_shifts, w)
        smoothed[w] = s
        oscillation[w] = slow_shifts - s

        osc = oscillation[w]
        print(f"  Smoothing window = {w} min:")
        print(f"    Smoothed range:    {s.max() - s.min():.3f} px")
        print(f"    Smoothed std:      {np.std(s):.3f} px")
        print(f"    Oscillation std:   {np.std(osc):.3f} px")
        print(f"    Oscillation range: {osc.max() - osc.min():.3f} px")
        print()

    slow_trend_30 = smoothed[30]
    osc_30 = oscillation[30]

    print(f"  Using 30-min smoothing as primary slow trend separator")
    print()

    # =============================================
    # 2. Improved transition detection
    # =============================================
    print("=" * 60)
    print("2. TRANSITION DETECTION")
    print("=" * 60)

    window_roll = 30
    rolling_std_smooth = np.array([
        np.std(slow_trend_30[max(0, i - window_roll):i + 1])
        for i in range(n_sets)
    ])

    rolling_range = np.array([
        np.ptp(slow_shifts[max(0, i - window_roll):i + 1])
        for i in range(n_sets)
    ])

    trans_set, baseline_val, threshold_val = find_transition(
        rolling_std_smooth, time_hours,
        baseline_fraction=0.4,
        threshold_factor=3.0,
        min_consecutive=10
    )

    if trans_set < n_sets:
        trans_time = time_hours[trans_set]
        print(f"  Transition detected at set {trans_set} (t = {trans_time:.2f} h)")
    else:
        trans_time = time_hours[-1]
        print(f"  No clear transition detected")

    print(f"  Baseline rolling std (smoothed): {baseline_val:.3f} px")
    print(f"  Threshold:                       {threshold_val:.3f} px")
    print()

    # =============================================
    # 3. Segmented analysis
    # =============================================
    print("=" * 60)
    print("3. SEGMENTED ANALYSIS")
    print("=" * 60)

    split = trans_set
    split_time = trans_time

    for label, idx_start, idx_end in [
        ("STABLE", 0, split),
        ("UNSTABLE", split, n_sets)
    ]:
        seg = slow_shifts[idx_start:idx_end]
        seg_time = time_hours[idx_start:idx_end]
        seg_trend = slow_trend_30[idx_start:idx_end]
        seg_osc = osc_30[idx_start:idx_end]

        if len(seg) < 2:
            print(f"  {label} PERIOD: too few sets ({len(seg)}), skipping")
            print()
            continue

        t_start = seg_time[0]
        t_end = seg_time[-1]
        duration = t_end - t_start

        seg_minutes = time_minutes[idx_start:idx_end]
        seg_coeffs = np.polyfit(seg_minutes, seg, 1)
        seg_linear_trend = seg_coeffs[0] * 60

        diffs = np.diff(seg)
        abs_diffs = np.abs(diffs)

        print(f"  {label} PERIOD ({t_start:.2f} - {t_end:.2f} h, "
              f"duration {duration:.2f} h, {len(seg)} sets):")
        print(f"    Raw signal:")
        print(f"      Range:           {seg.max() - seg.min():.3f} px")
        print(f"      Std:             {np.std(seg):.3f} px")
        print(f"      Linear trend:    {seg_linear_trend:.4f} px/hr")
        print(f"    Slow trend (30-min smoothed):")
        print(f"      Range:           {seg_trend.max() - seg_trend.min():.3f} px")
        print(f"      Std:             {np.std(seg_trend):.3f} px")
        print(f"    Oscillation (raw - smoothed):")
        print(f"      Std:             {np.std(seg_osc):.3f} px")
        print(f"      Range:           {seg_osc.max() - seg_osc.min():.3f} px")
        print(f"    Set-to-set changes:")
        print(f"      Std:             {np.std(diffs):.4f} px/min")
        print(f"      Median |change|: {np.median(abs_diffs):.4f} px/min")
        print(f"      90th pct:        {np.percentile(abs_diffs, 90):.4f} px/min")
        print(f"      Max |change|:    {np.max(abs_diffs):.4f} px/min")
        print()

    # =============================================
    # 4. Oscillation characterization
    # =============================================
    print("=" * 60)
    print("4. OSCILLATION CHARACTERIZATION")
    print("=" * 60)

    osc_signal = osc_30 - np.mean(osc_30)
    n = len(osc_signal)
    window = np.hanning(n)
    osc_windowed = osc_signal * window

    fft_osc = np.fft.rfft(osc_windowed)
    power_osc = np.abs(fft_osc) ** 2
    freqs = np.fft.rfftfreq(n, d=dt_min)

    trend_signal = slow_trend_30 - np.mean(slow_trend_30)
    trend_windowed = trend_signal * window
    fft_trend = np.fft.rfft(trend_windowed)
    power_trend = np.abs(fft_trend) ** 2

    power_osc_no_dc = power_osc.copy()
    power_osc_no_dc[0] = 0
    n_peaks = min(10, len(power_osc_no_dc) - 1)
    peak_indices = np.argsort(power_osc_no_dc)[::-1][:n_peaks]

    print(f"  Oscillation spectrum (after removing 30-min trend):")
    print(f"    {'Rank':>4s}  {'Freq (cyc/min)':>14s}  {'Period (min)':>12s}  "
          f"{'Period (h)':>10s}  {'Power':>12s}")
    for rank, idx in enumerate(peak_indices):
        if idx == 0:
            continue
        f = freqs[idx]
        p_min = 1.0 / f if f > 0 else float('inf')
        p_hr = p_min / 60.0
        print(f"    {rank + 1:4d}  {f:14.6f}  {p_min:12.1f}  "
              f"{p_hr:10.2f}  {power_osc_no_dc[idx]:12.1f}")
    print()

    print(f"  Dominant oscillation bands:")
    bands = [
        ("2-5 min", 2, 5),
        ("5-15 min", 5, 15),
        ("15-30 min", 15, 30),
        ("30-60 min", 30, 60),
        ("60-120 min", 60, 120),
    ]
    for band_name, p_low, p_high in bands:
        f_low = 1.0 / p_high
        f_high = 1.0 / p_low
        band_mask = (freqs >= f_low) & (freqs <= f_high)
        if np.any(band_mask):
            band_power = np.sum(power_osc[band_mask])
            total_power = np.sum(power_osc[1:])
            fraction = band_power / total_power * 100 if total_power > 0 else 0
            band_fft = np.zeros_like(fft_osc)
            band_fft[band_mask] = fft_osc[band_mask]
            band_signal = np.fft.irfft(band_fft, n=n)
            band_rms = np.std(band_signal)
            band_pp = band_signal.max() - band_signal.min()
            print(f"    {band_name:>12s}: {fraction:5.1f}% of power, "
                  f"RMS={band_rms:.3f} px, peak-peak={band_pp:.3f} px")
    print()

    # =============================================
    # 5. Autocorrelation of components
    # =============================================
    print("=" * 60)
    print("5. AUTOCORRELATION ANALYSIS")
    print("=" * 60)

    for label, sig in [("Raw signal", slow_shifts - np.mean(slow_shifts)),
                       ("Slow trend (30-min)", trend_signal),
                       ("Oscillation", osc_signal)]:
        sig_std = np.std(sig)
        if sig_std > 0:
            sig_norm = sig / sig_std
        else:
            continue

        ac = np.correlate(sig_norm, sig_norm, mode='full')
        ac = ac[n - 1:]
        ac = ac / ac[0]

        e_cross = np.where(ac < 1.0 / np.e)[0]
        e_time = e_cross[0] * dt_min if len(e_cross) > 0 else float('inf')

        zero_cross = np.where(np.diff(np.sign(ac)))[0]
        zero_time = zero_cross[0] * dt_min if len(zero_cross) > 0 else float('inf')

        print(f"  {label}:")
        print(f"    1/e decay time:      {e_time:.0f} min ({e_time / 60:.2f} h)")
        print(f"    First zero crossing: {zero_time:.0f} min ({zero_time / 60:.2f} h)")

        lag_list = [1, 2, 5, 10, 20, 30, 60]
        vals = []
        for lag_m in lag_list:
            lag_s = int(lag_m / dt_min)
            if lag_s < n:
                vals.append(f"{lag_m}min:{ac[lag_s]:.3f}")
        print(f"    Autocorr: {', '.join(vals)}")
        print()

    # =============================================
    # 6. Practical flat field validity
    # =============================================
    print("=" * 60)
    print("6. FLAT FIELD VALIDITY ASSESSMENT")
    print("=" * 60)

    windows_min = [1, 2, 5, 10, 15, 20, 30, 60, 120, 180, 240]

    print(f"  Expected stripe drift for a flat field acquired N minutes before/after:")
    print(f"    {'Window':>10s}  {'Mean |drift|':>12s}  {'Median |drift|':>14s}  "
          f"{'90th pct':>10s}  {'95th pct':>10s}  {'Max |drift|':>12s}")

    for w in windows_min:
        w_sets = int(w / dt_min)
        if w_sets >= n_sets:
            continue
        drifts = slow_shifts[w_sets:] - slow_shifts[:-w_sets]
        abs_drifts = np.abs(drifts)

        print(f"    {w:7d} min  {np.mean(abs_drifts):12.3f}  "
              f"{np.median(abs_drifts):14.3f}  "
              f"{np.percentile(abs_drifts, 90):10.3f}  "
              f"{np.percentile(abs_drifts, 95):10.3f}  "
              f"{np.max(abs_drifts):12.3f}")
    print()

    if trans_set > 10:
        print(f"  Same analysis for STABLE period only "
              f"(0 - {split_time:.2f} h):")
        print(f"    {'Window':>10s}  {'Mean |drift|':>12s}  {'Median |drift|':>14s}  "
              f"{'90th pct':>10s}  {'95th pct':>10s}  {'Max |drift|':>12s}")

        stable_shifts = slow_shifts[:trans_set]
        for w in windows_min:
            w_sets = int(w / dt_min)
            if w_sets >= len(stable_shifts):
                continue
            drifts = stable_shifts[w_sets:] - stable_shifts[:-w_sets]
            abs_drifts = np.abs(drifts)

            print(f"    {w:7d} min  {np.mean(abs_drifts):12.3f}  "
                  f"{np.median(abs_drifts):14.3f}  "
                  f"{np.percentile(abs_drifts, 90):10.3f}  "
                  f"{np.percentile(abs_drifts, 95):10.3f}  "
                  f"{np.max(abs_drifts):12.3f}")
        print()

    # =============================================
    # 7. Save plots
    # =============================================
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    fig.suptitle('Flat Field Stripe Motion Analysis — Feb 22, 2026 (00:00–08:03)',
                 fontsize=14, fontweight='bold', y=0.995)

    # (0,0) Raw + smoothed
    ax = axes[0, 0]
    ax.plot(time_hours, slow_shifts, 'b-', linewidth=0.3, alpha=0.5,
            label='Raw')
    ax.plot(time_hours, slow_trend_30, 'r-', linewidth=2,
            label='30-min smoothed')
    if trans_set < n_sets:
        ax.axvline(split_time, color='green', linestyle='--', linewidth=2,
                   label=f'Transition: {split_time:.2f} h')
    ax.set_ylabel('Vertical shift (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title('Raw signal and slow trend')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (0,1) Oscillation component
    ax = axes[0, 1]
    ax.plot(time_hours, osc_30, 'g-', linewidth=0.3, alpha=0.7)
    ax.set_ylabel('Oscillation (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Oscillation component (std={np.std(osc_30):.3f} px)')
    ax.grid(True, alpha=0.3)

    # (1,0) Rolling std of smoothed signal
    ax = axes[1, 0]
    ax.plot(time_hours, rolling_std_smooth, 'b-', linewidth=1)
    ax.axhline(threshold_val, color='r', linestyle='--',
               label=f'Threshold: {threshold_val:.2f} px')
    if trans_set < n_sets:
        ax.axvline(split_time, color='green', linestyle='--', linewidth=2)
    ax.set_ylabel('Rolling std (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title('Rolling std of 30-min smoothed signal (30-set window)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (1,1) Rolling range of raw signal
    ax = axes[1, 1]
    ax.plot(time_hours, rolling_range, 'orange', linewidth=0.5)
    if trans_set < n_sets:
        ax.axvline(split_time, color='green', linestyle='--', linewidth=2)
    ax.set_ylabel('Rolling range (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title('Rolling range of raw signal (30-set window)')
    ax.grid(True, alpha=0.3)

    # (2,0) Oscillation power spectrum
    ax = axes[2, 0]
    freq_cph = freqs[1:] * 60
    ax.semilogy(freq_cph, power_osc[1:], 'g-', linewidth=0.5,
                label='Oscillation')
    ax.semilogy(freq_cph, power_trend[1:], 'r-', linewidth=0.5,
                alpha=0.5, label='Slow trend')
    ax.set_xlabel('Frequency (cycles/hour)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectra')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (2,1) Power spectrum vs period
    ax = axes[2, 1]
    periods = 1.0 / freqs[1:]
    valid = periods <= 120
    ax.semilogy(periods[valid], power_osc[1:][valid], 'g-', linewidth=0.5,
                label='Oscillation')
    ax.semilogy(periods[valid], power_trend[1:][valid], 'r-', linewidth=0.5,
                alpha=0.5, label='Slow trend')
    ax.set_xlabel('Period (minutes)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectra vs period')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (3,0) Flat field validity
    ax = axes[3, 0]
    validity_windows = list(range(1, min(121, n_sets)))
    mean_drifts = []
    p90_drifts = []
    for w in validity_windows:
        drifts = np.abs(slow_shifts[w:] - slow_shifts[:-w])
        mean_drifts.append(np.mean(drifts))
        p90_drifts.append(np.percentile(drifts, 90))
    ax.plot(validity_windows, mean_drifts, 'b-', linewidth=1,
            label='Mean |drift|')
    ax.plot(validity_windows, p90_drifts, 'r-', linewidth=1,
            label='90th pct |drift|')
    ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5,
               label='1 pixel')
    ax.set_xlabel('Time gap (minutes)')
    ax.set_ylabel('Expected drift (px)')
    ax.set_title('Flat field validity: drift vs time gap')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # (3,1) Set-to-set change over time
    ax = axes[3, 1]
    diffs = np.diff(slow_shifts)
    ax.plot(time_hours[1:], np.abs(diffs), 'b-', linewidth=0.3, alpha=0.5)
    ax.plot(time_hours[1:], smooth(np.abs(diffs), 30), 'r-', linewidth=2,
            label='30-min smoothed')
    if trans_set < n_sets:
        ax.axvline(split_time, color='green', linestyle='--', linewidth=2)
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_ylabel('|Set-to-set change| (px)')
    ax.set_title('Minute-to-minute variability')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    detail_plot = os.path.join(image_dir, "stripe_motion_detail_v2.png")
    plt.savefig(detail_plot, dpi=150)
    print(f"Detail plot saved to: {detail_plot}")

    plt.show(block=True)

    print("\nDone.")


if __name__ == "__main__":
    main()
