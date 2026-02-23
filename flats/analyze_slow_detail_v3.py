#!/usr/bin/env python
"""
Detailed slow motion analysis of flat field stripe drift (v3).

Focuses on characterizing intermittent jump behavior rather than
stable/unstable transition detection.

Loads results from analyze_stripe_motion.py and produces:
1. Jump detection and statistics
2. Quiet vs active period characterization
3. Spectral analysis
4. Practical flat field validity (overall and quiet periods only)

Usage:
    python analyze_slow_detail_v3.py /path/to/flat/images

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


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_slow_detail_v3.py /path/to/flat/images")
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
    # 1. Set-to-set changes and jump detection
    # =============================================
    print("=" * 60)
    print("1. SET-TO-SET CHANGES AND JUMP DETECTION")
    print("=" * 60)

    diffs = np.diff(slow_shifts)
    abs_diffs = np.abs(diffs)

    print(f"  Set-to-set change statistics (1-min intervals):")
    print(f"    Mean:              {np.mean(diffs):+.4f} px/min")
    print(f"    Std:               {np.std(diffs):.4f} px/min")
    print(f"    Median |change|:   {np.median(abs_diffs):.4f} px/min")
    print()

    print(f"  |Change| percentiles:")
    for p in [25, 50, 75, 80, 85, 90, 95, 97.5, 99, 99.5]:
        print(f"    {p:5.1f}th: {np.percentile(abs_diffs, p):.4f} px/min")
    print()

    # Define jumps using different thresholds
    print(f"  Jump detection at various thresholds:")
    print(f"    {'Threshold':>12s}  {'N jumps':>8s}  {'% of sets':>10s}  "
          f"{'Mean gap':>10s}  {'Mean |jump|':>12s}")

    thresholds = [0.5, 1.0, 2.0, 3.0, 5.0, 10.0, 15.0, 20.0]
    for thresh in thresholds:
        jump_mask = abs_diffs > thresh
        n_jumps = np.sum(jump_mask)
        pct = n_jumps / len(abs_diffs) * 100

        if n_jumps > 0:
            jump_indices = np.where(jump_mask)[0]
            if n_jumps > 1:
                gaps = np.diff(jump_indices)
                mean_gap = np.mean(gaps) * dt_min
            else:
                mean_gap = float('inf')
            mean_jump = np.mean(abs_diffs[jump_mask])
        else:
            mean_gap = float('inf')
            mean_jump = 0

        gap_str = f"{mean_gap:.1f} min" if mean_gap < 1000 else "N/A"
        print(f"    {thresh:9.1f} px  {n_jumps:8d}  {pct:9.1f}%  "
              f"{gap_str:>10s}  {mean_jump:12.3f}")
    print()

    # =============================================
    # 2. Classify quiet vs active minutes
    # =============================================
    print("=" * 60)
    print("2. QUIET vs ACTIVE PERIODS")
    print("=" * 60)

    # Use 2 px as the jump threshold (well above the median of 0.1 px)
    jump_threshold = 2.0
    is_jump = abs_diffs > jump_threshold

    # A set is "active" if it or its neighbors had a jump
    # Extend active periods by +/- 2 sets to capture the full event
    extend = 2
    is_active = np.zeros(n_sets, dtype=bool)
    jump_indices = np.where(is_jump)[0]
    for idx in jump_indices:
        start = max(0, idx - extend)
        end = min(n_sets, idx + extend + 2)  # +2 because diff shifts by 1
        is_active[start:end] = True

    is_quiet = ~is_active
    n_quiet = np.sum(is_quiet)
    n_active = np.sum(is_active)

    print(f"  Jump threshold: {jump_threshold} px")
    print(f"  Active sets:    {n_active} ({n_active / n_sets * 100:.1f}%)")
    print(f"  Quiet sets:     {n_quiet} ({n_quiet / n_sets * 100:.1f}%)")
    print()

    # Find quiet stretches
    quiet_stretches = []
    in_quiet = False
    start = 0
    for i in range(n_sets):
        if is_quiet[i] and not in_quiet:
            start = i
            in_quiet = True
        elif not is_quiet[i] and in_quiet:
            quiet_stretches.append((start, i - 1, i - start))
            in_quiet = False
    if in_quiet:
        quiet_stretches.append((start, n_sets - 1, n_sets - start))

    quiet_lengths = [s[2] for s in quiet_stretches]

    print(f"  Number of quiet stretches: {len(quiet_stretches)}")
    if quiet_lengths:
        print(f"  Quiet stretch duration (minutes):")
        print(f"    Mean:   {np.mean(quiet_lengths):.1f}")
        print(f"    Median: {np.median(quiet_lengths):.1f}")
        print(f"    Min:    {np.min(quiet_lengths)}")
        print(f"    Max:    {np.max(quiet_lengths)}")
        print(f"    Std:    {np.std(quiet_lengths):.1f}")
    print()

    # Statistics during quiet periods only
    quiet_shifts = slow_shifts[is_quiet]
    quiet_diffs_list = []
    for s_start, s_end, s_len in quiet_stretches:
        if s_len > 1:
            seg_diffs = np.diff(slow_shifts[s_start:s_end + 1])
            quiet_diffs_list.extend(seg_diffs)
    quiet_diffs = np.array(quiet_diffs_list) if quiet_diffs_list else np.array([0])
    quiet_abs_diffs = np.abs(quiet_diffs)

    print(f"  During QUIET periods:")
    print(f"    Set-to-set |change|:")
    print(f"      Mean:   {np.mean(quiet_abs_diffs):.4f} px/min")
    print(f"      Median: {np.median(quiet_abs_diffs):.4f} px/min")
    print(f"      Std:    {np.std(quiet_diffs):.4f} px/min")
    print(f"      90th:   {np.percentile(quiet_abs_diffs, 90):.4f} px/min")
    print(f"      Max:    {np.max(quiet_abs_diffs):.4f} px/min")
    print()

    # Find active events and characterize them
    active_events = []
    in_active = False
    for i in range(n_sets):
        if is_active[i] and not in_active:
            evt_start = i
            in_active = True
        elif not is_active[i] and in_active:
            evt_end = i - 1
            evt_shifts = slow_shifts[evt_start:evt_end + 1]
            evt_range = evt_shifts.max() - evt_shifts.min()
            active_events.append((evt_start, evt_end, evt_end - evt_start + 1,
                                  evt_range))
            in_active = False
    if in_active:
        evt_shifts = slow_shifts[evt_start:]
        evt_range = evt_shifts.max() - evt_shifts.min()
        active_events.append((evt_start, n_sets - 1, n_sets - evt_start,
                              evt_range))

    print(f"  Number of active events: {len(active_events)}")
    if active_events:
        print(f"  {'Event':>5s}  {'Start':>8s}  {'End':>8s}  {'Duration':>10s}  "
              f"{'Range (px)':>10s}  {'Time (h)':>10s}")
        for i, (es, ee, dur, rng) in enumerate(active_events):
            print(f"  {i:5d}  {es:8d}  {ee:8d}  {dur:7d} min  "
                  f"{rng:10.3f}  {time_hours[es]:8.2f}-{time_hours[ee]:.2f}")
    print()

    # =============================================
    # 3. Smoothed trend analysis
    # =============================================
    print("=" * 60)
    print("3. SLOW TREND (30-min smoothed)")
    print("=" * 60)

    slow_trend_30 = smooth(slow_shifts, 30)
    osc_30 = slow_shifts - slow_trend_30

    # Linear fit to trend
    trend_coeffs = np.polyfit(time_minutes, slow_trend_30, 1)
    trend_slope = trend_coeffs[0] * 60  # px/hr

    print(f"  Slow trend (30-min smoothed):")
    print(f"    Range:         {slow_trend_30.max() - slow_trend_30.min():.3f} px")
    print(f"    Std:           {np.std(slow_trend_30):.3f} px")
    print(f"    Linear trend:  {trend_slope:.4f} px/hr")
    print()
    print(f"  Oscillation (raw - 30-min smoothed):")
    print(f"    Std:           {np.std(osc_30):.3f} px")
    print(f"    Range:         {osc_30.max() - osc_30.min():.3f} px")
    print()

    # =============================================
    # 4. Spectral analysis
    # =============================================
    print("=" * 60)
    print("4. SPECTRAL ANALYSIS")
    print("=" * 60)

    n = len(slow_shifts)
    signal = slow_shifts - np.mean(slow_shifts)
    window = np.hanning(n)
    signal_windowed = signal * window

    fft_vals = np.fft.rfft(signal_windowed)
    power = np.abs(fft_vals) ** 2
    freqs = np.fft.rfftfreq(n, d=dt_min)

    power_no_dc = power.copy()
    power_no_dc[0] = 0
    n_peaks = min(15, len(power_no_dc) - 1)
    peak_indices = np.argsort(power_no_dc)[::-1][:n_peaks]

    print(f"  Top spectral peaks (raw signal):")
    print(f"    {'Rank':>4s}  {'Freq (cyc/min)':>14s}  {'Period (min)':>12s}  "
          f"{'Period (h)':>10s}  {'Power':>12s}")
    for rank, idx in enumerate(peak_indices):
        if idx == 0:
            continue
        f = freqs[idx]
        p_min = 1.0 / f if f > 0 else float('inf')
        p_hr = p_min / 60.0
        print(f"    {rank + 1:4d}  {f:14.6f}  {p_min:12.1f}  "
              f"{p_hr:10.2f}  {power_no_dc[idx]:12.1f}")
    print()

    # Power in bands
    print(f"  Power distribution by period band:")
    bands = [
        ("2-5 min", 2, 5),
        ("5-10 min", 5, 10),
        ("10-20 min", 10, 20),
        ("20-30 min", 20, 30),
        ("30-60 min", 30, 60),
        ("60-120 min", 60, 120),
        (">120 min", 120, 10000),
    ]
    total_power = np.sum(power_no_dc)
    for band_name, p_low, p_high in bands:
        f_low = 1.0 / p_high if p_high < 10000 else 0
        f_high = 1.0 / p_low
        band_mask = (freqs >= f_low) & (freqs <= f_high)
        band_mask[0] = False
        if np.any(band_mask):
            band_power = np.sum(power[band_mask])
            fraction = band_power / total_power * 100 if total_power > 0 else 0
            # Reconstruct band signal for amplitude
            band_fft = np.zeros_like(fft_vals)
            band_fft[band_mask] = fft_vals[band_mask]
            band_signal = np.fft.irfft(band_fft, n=n)
            band_rms = np.std(band_signal)
            band_pp = band_signal.max() - band_signal.min()
            print(f"    {band_name:>12s}: {fraction:5.1f}%  "
                  f"RMS={band_rms:.3f} px  peak-peak={band_pp:.3f} px")
    print()

    # =============================================
    # 5. Autocorrelation
    # =============================================
    print("=" * 60)
    print("5. AUTOCORRELATION")
    print("=" * 60)

    for label, sig in [("Raw signal", signal),
                       ("Quiet periods only", None)]:
        if label == "Quiet periods only":
            # Build a signal from quiet stretches only (longest one)
            if not quiet_stretches:
                continue
            longest = max(quiet_stretches, key=lambda x: x[2])
            ls, le, ll = longest
            if ll < 10:
                print(f"  {label}: longest quiet stretch too short ({ll} sets)")
                continue
            sig = slow_shifts[ls:le + 1]
            sig = sig - np.mean(sig)
            print(f"  {label} (longest quiet stretch: "
                  f"set {ls}-{le}, {ll} min, "
                  f"t={time_hours[ls]:.2f}-{time_hours[le]:.2f} h):")
        else:
            print(f"  {label}:")

        nn = len(sig)
        sig_std = np.std(sig)
        if sig_std > 0:
            sig_norm = sig / sig_std
        else:
            continue

        ac = np.correlate(sig_norm, sig_norm, mode='full')
        ac = ac[nn - 1:]
        ac = ac / ac[0]

        e_cross = np.where(ac < 1.0 / np.e)[0]
        e_time = e_cross[0] * dt_min if len(e_cross) > 0 else float('inf')

        zero_cross = np.where(np.diff(np.sign(ac)))[0]
        zero_time = zero_cross[0] * dt_min if len(zero_cross) > 0 else float('inf')

        print(f"    1/e decay time:      {e_time:.0f} min ({e_time / 60:.2f} h)")
        print(f"    First zero crossing: {zero_time:.0f} min ({zero_time / 60:.2f} h)")

        lag_list = [1, 2, 5, 10, 20, 30, 60]
        vals = []
        for lag_m in lag_list:
            lag_s = int(lag_m / dt_min)
            if lag_s < nn:
                vals.append(f"{lag_m}min:{ac[lag_s]:.3f}")
        print(f"    Autocorr: {', '.join(vals)}")
        print()

    # =============================================
    # 6. Flat field validity
    # =============================================
    print("=" * 60)
    print("6. FLAT FIELD VALIDITY ASSESSMENT")
    print("=" * 60)

    windows_min = [1, 2, 5, 10, 15, 20, 30, 60, 120, 180, 240]

    # Overall
    print(f"  ALL DATA: Expected drift for flat field N minutes away:")
    print(f"    {'Window':>10s}  {'Mean':>8s}  {'Median':>8s}  "
          f"{'75th':>8s}  {'90th':>8s}  {'95th':>8s}  {'Max':>8s}")

    for w in windows_min:
        w_sets = int(w / dt_min)
        if w_sets >= n_sets:
            continue
        drifts = np.abs(slow_shifts[w_sets:] - slow_shifts[:-w_sets])
        print(f"    {w:7d} min  {np.mean(drifts):8.3f}  "
              f"{np.median(drifts):8.3f}  "
              f"{np.percentile(drifts, 75):8.3f}  "
              f"{np.percentile(drifts, 90):8.3f}  "
              f"{np.percentile(drifts, 95):8.3f}  "
              f"{np.max(drifts):8.3f}")
    print()

    # Quiet periods only
    if quiet_stretches:
        print(f"  QUIET PERIODS ONLY (threshold={jump_threshold} px):")
        print(f"    {'Window':>10s}  {'Mean':>8s}  {'Median':>8s}  "
              f"{'75th':>8s}  {'90th':>8s}  {'95th':>8s}  {'Max':>8s}")

        for w in windows_min:
            w_sets = int(w / dt_min)
            all_quiet_drifts = []
            for s_start, s_end, s_len in quiet_stretches:
                if s_len <= w_sets:
                    continue
                seg = slow_shifts[s_start:s_end + 1]
                seg_drifts = np.abs(seg[w_sets:] - seg[:-w_sets])
                all_quiet_drifts.extend(seg_drifts)

            if len(all_quiet_drifts) > 0:
                qd = np.array(all_quiet_drifts)
                print(f"    {w:7d} min  {np.mean(qd):8.3f}  "
                      f"{np.median(qd):8.3f}  "
                      f"{np.percentile(qd, 75):8.3f}  "
                      f"{np.percentile(qd, 90):8.3f}  "
                      f"{np.percentile(qd, 95):8.3f}  "
                      f"{np.max(qd):8.3f}")
            else:
                print(f"    {w:7d} min  (no quiet stretches long enough)")
        print()

    # =============================================
    # 7. Summary
    # =============================================
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Duration:              {time_hours[-1]:.1f} hours ({n_sets} sets)")
    print(f"  Total drift range:     {slow_shifts.max() - slow_shifts.min():.1f} px")
    print()
    print(f"  BEHAVIOR TYPE: Intermittent jumps on a quiet background")
    print(f"    Quiet baseline:      median |change| = "
          f"{np.median(abs_diffs):.3f} px/min")
    print(f"    Jump events:         {np.sum(abs_diffs > jump_threshold)} of "
          f"{len(abs_diffs)} intervals exceed {jump_threshold} px")
    print(f"    Active time:         {n_active / n_sets * 100:.1f}% of total")
    print(f"    Quiet time:          {n_quiet / n_sets * 100:.1f}% of total")
    print()
    print(f"  SLOW TREND:")
    print(f"    30-min smoothed range: {slow_trend_30.max() - slow_trend_30.min():.1f} px")
    print(f"    Linear drift:          {trend_slope:.4f} px/hr")
    print()
    print(f"  DOMINANT OSCILLATIONS:")
    print(f"    Primary periods:     ~9-10 min and ~20-25 min")
    print(f"    Oscillation std:     {np.std(osc_30):.1f} px")
    print()
    print(f"  PRACTICAL GUIDANCE:")
    if len(quiet_diffs_list) > 0:
        print(f"    During quiet periods, flat field drift is "
              f"~{np.median(quiet_abs_diffs):.2f} px/min (median)")
    print(f"    However, {n_active / n_sets * 100:.0f}% of the time, large jumps "
          f"(>{jump_threshold} px) occur")
    print(f"    Recommend: acquire flat fields as close to scan time as possible")
    print()

    # =============================================
    # 8. Save plots
    # =============================================
    print("Starting plot generation...")
    fig, axes = plt.subplots(4, 2, figsize=(16, 20))
    fig.suptitle('Flat Field Stripe Motion Analysis — Feb 22, 2026 (00:00–08:03)',
                 fontsize=14, fontweight='bold', y=0.995)
    print("  Figure created")

    # (0,0) Raw signal with quiet/active coloring
    ax = axes[0, 0]
    ax.plot(time_hours, slow_shifts, 'b-', linewidth=0.3, alpha=0.3)
    for es, ee, dur, rng in active_events:
        ax.axvspan(time_hours[es], time_hours[ee], alpha=0.15, color='red')
    ax.plot(time_hours, slow_trend_30, 'r-', linewidth=2,
            label='30-min smoothed')
    ax.set_ylabel('Vertical shift (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title(f'Stripe drift (red shading = active events, '
                 f'{n_active / n_sets * 100:.0f}% of time)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    print("  Panel (0,0) done")

    # (0,1) Set-to-set changes
    ax = axes[0, 1]
    ax.plot(time_hours[1:], abs_diffs, 'b-', linewidth=0.3, alpha=0.5)
    ax.axhline(jump_threshold, color='r', linestyle='--',
               label=f'Jump threshold: {jump_threshold} px')
    ax.set_ylabel('|Set-to-set change| (px)')
    ax.set_xlabel('Hour of day (starting 00:00)')
    ax.set_title('Minute-to-minute changes')
    ax.set_yscale('log')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    print("  Panel (0,1) done")

    # (1,0) Histogram of set-to-set changes (log scale)
    ax = axes[1, 0]
    bins = np.logspace(np.log10(0.001), np.log10(50), 100)
    ax.hist(abs_diffs, bins=bins, edgecolor='black', alpha=0.7)
    ax.axvline(jump_threshold, color='r', linestyle='--',
               label=f'Threshold: {jump_threshold} px')
    ax.axvline(np.median(abs_diffs), color='green', linestyle='--',
               label=f'Median: {np.median(abs_diffs):.3f} px')
    ax.set_xscale('log')
    ax.set_xlabel('|Set-to-set change| (px)')
    ax.set_ylabel('Count')
    ax.set_title('Distribution of minute-to-minute changes')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    print("  Panel (1,0) done")

    # (1,1) Quiet stretch durations
    ax = axes[1, 1]
    if quiet_lengths:
        ax.hist(quiet_lengths, bins=30, edgecolor='black', alpha=0.7)
        ax.axvline(np.median(quiet_lengths), color='r', linestyle='--',
                   label=f'Median: {np.median(quiet_lengths):.0f} min')
        ax.set_xlabel('Quiet stretch duration (min)')
        ax.set_ylabel('Count')
        ax.set_title(f'Quiet stretch durations '
                     f'(n={len(quiet_stretches)})')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
    print("  Panel (1,1) done")

    # (2,0) Power spectrum
    ax = axes[2, 0]
    freq_cph = freqs[1:] * 60
    ax.semilogy(freq_cph, power[1:], 'b-', linewidth=0.5)
    ax.set_xlabel('Frequency (cycles/hour)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectrum')
    ax.grid(True, alpha=0.3)
    print("  Panel (2,0) done")

    # (2,1) Power spectrum vs period
    ax = axes[2, 1]
    periods = 1.0 / freqs[1:]
    valid = periods <= 120
    ax.semilogy(periods[valid], power[1:][valid], 'b-', linewidth=0.5)
    ax.set_xlabel('Period (minutes)')
    ax.set_ylabel('Power')
    ax.set_title('Power spectrum vs period')
    ax.axvline(10, color='r', linestyle=':', alpha=0.5, label='10 min')
    ax.axvline(23, color='g', linestyle=':', alpha=0.5, label='23 min')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    print("  Panel (2,1) done")

    # (3,0) Flat field validity - all data
    ax = axes[3, 0]
    validity_windows = list(range(1, min(121, n_sets)))
    mean_drifts = []
    median_drifts = []
    p90_drifts = []
    for w in validity_windows:
        d = np.abs(slow_shifts[w:] - slow_shifts[:-w])
        mean_drifts.append(np.mean(d))
        median_drifts.append(np.median(d))
        p90_drifts.append(np.percentile(d, 90))
    ax.plot(validity_windows, mean_drifts, 'b-', linewidth=1,
            label='Mean')
    ax.plot(validity_windows, median_drifts, 'g-', linewidth=1,
            label='Median')
    ax.plot(validity_windows, p90_drifts, 'r-', linewidth=1,
            label='90th pct')
    ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('Time gap (minutes)')
    ax.set_ylabel('Expected |drift| (px)')
    ax.set_title('Flat field validity (all data)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    print("  Panel (3,0) done")

    # (3,1) Flat field validity - quiet periods only
    ax = axes[3, 1]
    if quiet_stretches:
        q_mean = []
        q_median = []
        q_p90 = []
        q_windows = []
        for w in range(1, min(61, max(quiet_lengths))):
            all_qd = []
            for s_start, s_end, s_len in quiet_stretches:
                if s_len <= w:
                    continue
                seg = slow_shifts[s_start:s_end + 1]
                seg_d = np.abs(seg[w:] - seg[:-w])
                all_qd.extend(seg_d)
            if len(all_qd) > 0:
                qd = np.array(all_qd)
                q_windows.append(w)
                q_mean.append(np.mean(qd))
                q_median.append(np.median(qd))
                q_p90.append(np.percentile(qd, 90))

        if q_windows:
            ax.plot(q_windows, q_mean, 'b-', linewidth=1, label='Mean')
            ax.plot(q_windows, q_median, 'g-', linewidth=1, label='Median')
            ax.plot(q_windows, q_p90, 'r-', linewidth=1, label='90th pct')
            ax.axhline(1.0, color='gray', linestyle=':', alpha=0.5)
            ax.set_xlabel('Time gap (minutes)')
            ax.set_ylabel('Expected |drift| (px)')
            ax.set_title('Flat field validity (quiet periods only)')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
    print("  Panel (3,1) done")

    plt.tight_layout()

    detail_plot = os.path.join(image_dir, "stripe_motion_detail_v3.png")
    plt.savefig(detail_plot, dpi=150)
    print(f"Detail plot saved to: {detail_plot}")

    plt.show(block=True)

    print("\nDone.")

if __name__ == "__main__":
    main()
