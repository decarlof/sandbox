import numpy as np
import matplotlib.pyplot as plt


def _bit_reverse(val: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (val & 1)
        val >>= 1
    return result


def _ensure_power_of_two(K: int):
    if K < 1 or (K & (K - 1)) != 0:
        raise ValueError(f"K={K} must be a power of two.")


def compute_equally_spaced_multiturn_angles(
    num_angles=180,
    K_interlace=3,
    rotation_start=0.0,
    rotation_stop=180.0,
    delta_theta=None,
    degrees=True,
):
    N = int(num_angles)
    K = int(K_interlace)

    if delta_theta is None:
        delta_theta = (rotation_stop - rotation_start) / N
    rotation_step = float(delta_theta)

    n = np.arange(N, dtype=float)
    angles_per_turn = []
    for k in range(K):
        theta_n = rotation_start + (n + k / K) * rotation_step + 360.0 * k
        angles_per_turn.append(theta_n)

    theta_interlaced = np.concatenate(angles_per_turn).astype(float)
    theta_monotonic = np.sort(theta_interlaced)

    return angles_per_turn, theta_interlaced, theta_monotonic


def compute_golden_angle_multiturn_angles(
    num_angles=180,
    K_interlace=3,
    rotation_start=0.0,
    degrees=True,
):
    N = int(num_angles)
    K = int(K_interlace)
    start_deg = float(rotation_start)

    if N <= 0 or K <= 0:
        raise ValueError("N and K must be > 0")

    golden_angle = 360.0 * (3.0 - np.sqrt(5.0)) / 2.0
    phi_inv = (np.sqrt(5.0) - 1.0) / 2.0

    base = np.array(
        [(start_deg + i * golden_angle) % 360.0 for i in range(N)],
        dtype=np.float64,
    )
    base.sort()

    angles_per_turn = []
    theta_list = []
    for k in range(K):
        if k == 0:
            block = base.copy()
        else:
            offset = (k / (N + 1.0)) * 360.0 * phi_inv
            block = np.sort((base + offset) % 360.0)

        unwrapped_block = start_deg + 360.0 * k + block
        angles_per_turn.append(unwrapped_block)
        theta_list.extend(unwrapped_block.tolist())

    theta_interlaced = np.asarray(theta_list, dtype=np.float64)
    theta_monotonic = np.sort(theta_interlaced)

    return angles_per_turn, theta_interlaced, theta_monotonic


def compute_corput_multiturn_angles(
    num_angles=180,
    K_interlace=4,
    rotation_start=0.0,
    rotation_stop=None,
    delta_theta=None,
    degrees=True,
):
    N = int(num_angles)
    K = int(K_interlace)
    start = float(rotation_start)

    if N <= 0 or K <= 0:
        raise ValueError("N and K must be > 0")

    if rotation_stop is None:
        rotation_stop = start + 360.0

    if delta_theta is not None:
        delta_theta = float(delta_theta)
    else:
        delta_theta = (float(rotation_stop) - start) / N

    base = start + np.arange(N, dtype=np.float64) * delta_theta

    bitsK = int(np.ceil(np.log2(K))) if K > 1 else 1
    MK = 1 << bitsK
    p_corput = np.array(
        [_bit_reverse(i, bitsK) for i in range(MK)], dtype=np.int64
    )
    p_corput = p_corput[p_corput < K]
    assert len(p_corput) == K
    offsets = (p_corput.astype(np.float64) / float(K)) * delta_theta

    bitsN = int(np.ceil(np.log2(N))) if N > 1 else 1
    MN = 1 << bitsN
    indices = np.array(
        [_bit_reverse(i, bitsN) for i in range(MN)], dtype=np.int64
    )
    indices = indices[indices < N]
    assert len(indices) == N

    angles_per_turn = []
    for k in range(K):
        offset = offsets[k]
        loop_angles = base[indices] + offset
        loop_angles_mod = np.mod(loop_angles - start, 360.0) + start
        loop_angles_mod = np.sort(loop_angles_mod)
        loop_angles_unwrapped = loop_angles_mod + 360.0 * k
        angles_per_turn.append(loop_angles_unwrapped)

    theta_unsorted = np.concatenate(angles_per_turn).astype(np.float64)
    theta_interlaced = np.sort(theta_unsorted)
    theta_monotonic = theta_interlaced.copy()

    return angles_per_turn, theta_interlaced, theta_monotonic


def compute_timbir_multiturn_angles(
    num_angles=180,
    K_interlace=4,
    rotation_start=0.0,
    degrees=True,
):
    N = int(num_angles)
    K = int(K_interlace)
    start_deg = float(rotation_start)

    _ensure_power_of_two(K)
    bits = int(np.log2(K))

    angles_per_turn = []
    for loop_turn in range(K):
        base_turn = 360.0 * loop_turn
        subloop = _bit_reverse(loop_turn, bits)
        turn_angles = []
        for i in range(N):
            idx = i * K + subloop
            angle_deg = idx * 360.0 / (N * K)
            turn_angles.append(start_deg + base_turn + angle_deg)
        angles_per_turn.append(np.asarray(turn_angles, dtype=np.float64))

    theta_interlaced = np.concatenate(angles_per_turn).astype(np.float64)
    theta_monotonic = np.sort(theta_interlaced)

    return angles_per_turn, theta_interlaced, theta_monotonic


def polar_plot_interlaced(
    angles_per_turn,
    theta_interlaced,
    theta_monotonic,
    title="Multi-turn acquisition angles (polar view)",
    degrees=True,
    show_monotonic=False,
    r0=1.0,
    dr=0.15,
    mono_offset=0.25,
    ax=None,
):
    K = len(angles_per_turn)
    N = len(angles_per_turn[0])

    if degrees:
        th_turns = [np.deg2rad(a % 360.0) for a in angles_per_turn]
        th_all = np.deg2rad(theta_interlaced % 360.0)
        th_mono = np.deg2rad(theta_monotonic % 360.0)
    else:
        th_turns = [a % (2 * np.pi) for a in angles_per_turn]
        th_all = theta_interlaced % (2 * np.pi)
        th_mono = theta_monotonic % (2 * np.pi)

    r_turns = [r0 + dr * k for k in range(K)]
    r_all = np.empty_like(th_all)
    for k in range(K):
        r_all[k * N : (k + 1) * N] = r_turns[k]

    standalone = ax is None
    if standalone:
        fig = plt.figure(figsize=(7, 7))
        ax = fig.add_subplot(111, projection="polar")

    for k in range(K):
        ax.scatter(
            th_turns[k],
            np.full(N, r_turns[k]),
            s=18,
            label=f"turn k={k}",
            alpha=0.9,
        )

    ax.plot(
        th_all, r_all, lw=1.0, alpha=0.35, color="k", label="acq order path"
    )

    if show_monotonic:
        ax.scatter(
            th_mono,
            np.full_like(th_mono, r0 - mono_offset),
            s=10,
            alpha=0.7,
            label="sorted (monotonic)",
        )

    ax.set_title(title, pad=20, fontsize=11)
    ax.set_rticks([])
    ax.set_ylim(r0 - mono_offset - 0.1, r0 + dr * (K - 1) + 0.2)
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.10), fontsize=7)

    if standalone:
        plt.tight_layout()
        plt.show()


def polar_plot_interlaced_grid(
    datasets,
    degrees=True,
    show_monotonic=False,
    r0=1.0,
    dr=0.15,
    mono_offset=0.25,
    suptitle="Comparison of Multi-Turn Acquisition Schemes",
):
    n_plots = len(datasets)
    ncols = min(n_plots, 2)
    nrows = int(np.ceil(n_plots / ncols))

    fig = plt.figure(figsize=(7 * ncols, 7 * nrows))
    fig.suptitle(suptitle, fontsize=15, y=1.02)

    for idx, ds in enumerate(datasets):
        ax = fig.add_subplot(nrows, ncols, idx + 1, projection="polar")
        polar_plot_interlaced(
            ds["angles_per_turn"],
            ds["theta_interlaced"],
            ds["theta_monotonic"],
            title=ds["title"],
            degrees=degrees,
            show_monotonic=show_monotonic,
            r0=r0,
            dr=dr,
            mono_offset=mono_offset,
            ax=ax,
        )

    plt.tight_layout()
    plt.show()


def compute_delta_angles_acquisition_order(angles_per_turn):
    theta_acq = np.concatenate(angles_per_turn)
    delta_angles = np.diff(theta_acq)
    return delta_angles


def count_distinct_deltas(delta, decimals=6):
    return len(np.unique(np.round(delta, decimals=decimals)))


def plot_delta_angle_distributions(
    datasets,
    degrees=True,
    suptitle=(
        r"$\Delta\theta$ between consecutive frames (acquisition order)"
        "\n— determines minimum detector exposure time at a given rotation speed —"
    ),
):
    n_plots = len(datasets)
    fig, axes = plt.subplots(
        3, n_plots, figsize=(5 * n_plots, 12),
        gridspec_kw={"height_ratios": [1, 1, 1]},
    )
    if n_plots == 1:
        axes = axes.reshape(-1, 1)

    fig.suptitle(suptitle, fontsize=13, y=1.03)

    colors = plt.cm.tab10.colors
    unit = "°" if degrees else "rad"

    all_deltas = []
    for ds in datasets:
        delta = compute_delta_angles_acquisition_order(ds["angles_per_turn"])
        all_deltas.append(delta)

    global_min = min(d.min() for d in all_deltas)
    global_max = max(d.max() for d in all_deltas)
    margin = (global_max - global_min) * 0.1
    if margin < 1e-10:
        margin = 0.1
    shared_xlim = (global_min - margin, global_max + margin)

    for col, (ds, delta) in enumerate(zip(datasets, all_deltas)):
        angles_per_turn = ds["angles_per_turn"]
        K = len(angles_per_turn)
        N = len(angles_per_turn[0])

        has_negative = np.any(delta < 0)
        n_negative = np.sum(delta < 0)

        unique_vals = np.unique(np.round(delta, decimals=6))
        n_unique = len(unique_vals)

        # --- Top row: distribution view ---
        ax_hist = axes[0, col]

        if n_unique <= 20:
            counts = {}
            for v in np.round(delta, decimals=6):
                counts[v] = counts.get(v, 0) + 1
            vals = np.array(sorted(counts.keys()))
            cnts = np.array([counts[v] for v in vals])

            markerline, stemlines, baseline = ax_hist.stem(
                vals, cnts, linefmt="-", markerfmt="o", basefmt=" ",
            )
            markerline.set_color(colors[col % len(colors)])
            markerline.set_markersize(6)
            stemlines.set_color(colors[col % len(colors)])
            stemlines.set_linewidth(2)

            for v, c in zip(vals, cnts):
                ax_hist.annotate(
                    f"{v:.3f}{unit}\n(n={c})",
                    xy=(v, c), xytext=(0, 8),
                    textcoords="offset points",
                    ha="center", fontsize=6,
                )

            # Add headroom so annotations don't overlap with title
            max_count = cnts.max()
            ax_hist.set_ylim(0, max_count * 1.35)
        else:
            ax_hist.hist(
                delta,
                bins="auto",
                color=colors[col % len(colors)],
                edgecolor="k",
                alpha=0.75,
            )
            # Add headroom for histogram too
            y_top = ax_hist.get_ylim()[1]
            ax_hist.set_ylim(0, y_top * 1.15)

        ax_hist.axvline(
            np.mean(delta), color="r", ls="--", lw=1.5,
            label=f"mean = {np.mean(delta):.3f}{unit}",
        )
        ax_hist.axvline(
            np.min(delta), color="green", ls=":", lw=1.5,
            label=f"min = {np.min(delta):.3f}{unit}",
        )
        ax_hist.axvline(
            np.max(delta), color="purple", ls=":", lw=1.5,
            label=f"max = {np.max(delta):.3f}{unit}",
        )

        title_str = ds["title"]
        title_str += f" ({n_unique} distinct values)"
        if has_negative:
            title_str += f"\n⚠ {n_negative} negative gaps"
        ax_hist.set_title(title_str, fontsize=11, fontweight="bold")
        ax_hist.set_xlabel(rf"$\Delta\theta$ ({unit})")
        ax_hist.set_ylabel("Count")
        ax_hist.set_xlim(shared_xlim)
        ax_hist.legend(fontsize=7)
        ax_hist.grid(True, alpha=0.3)

        # --- Middle row: delta vs acquisition index ---
        ax_stem = axes[1, col]
        base_color = colors[col % len(colors)]
        point_colors = [base_color if d >= 0 else "red" for d in delta]

        ax_stem.scatter(
            np.arange(len(delta)), delta,
            s=3, alpha=0.6, c=point_colors,
        )
        ax_stem.plot(
            np.arange(len(delta)), delta,
            lw=0.4, alpha=0.4, color=base_color,
        )
        ax_stem.axhline(
            np.mean(delta), color="r", ls="--", lw=1.2, alpha=0.8,
            label=f"mean = {np.mean(delta):.3f}{unit}",
        )
        if has_negative:
            ax_stem.axhline(0, color="k", ls="-", lw=0.8, alpha=0.5)
        for k in range(1, K):
            boundary = k * N - 1
            if boundary < len(delta):
                ax_stem.axvline(
                    boundary, color="gray", ls="--", lw=0.8, alpha=0.5,
                )
        ax_stem.set_xlabel("Acquisition index")
        ax_stem.set_ylabel(rf"$\Delta\theta$ ({unit})")
        ax_stem.set_title(r"$\Delta\theta$ vs. frame index", fontsize=10)
        ax_stem.legend(fontsize=7)
        ax_stem.grid(True, alpha=0.3)

        # --- Bottom row: per-turn breakdown ---
        ax_turn = axes[2, col]
        turn_colors = plt.cm.Set2.colors
        for k in range(K):
            turn_angles = angles_per_turn[k]
            delta_turn = np.diff(turn_angles)

            c = turn_colors[k % len(turn_colors)]
            ax_turn.plot(
                np.arange(len(delta_turn)),
                delta_turn,
                lw=0.8, alpha=0.8, color=c,
                label=f"turn {k} (mean={np.mean(delta_turn):.2f}{unit})",
            )
            ax_turn.scatter(
                np.arange(len(delta_turn)),
                delta_turn,
                s=6, alpha=0.6, color=c,
            )

        if has_negative:
            ax_turn.axhline(0, color="k", ls="-", lw=0.8, alpha=0.5)
        ax_turn.set_xlabel("Intra-turn frame index")
        ax_turn.set_ylabel(rf"$\Delta\theta$ ({unit})")
        ax_turn.set_title(r"$\Delta\theta$ per turn", fontsize=10)
        ax_turn.legend(fontsize=7)
        ax_turn.grid(True, alpha=0.3)

        fly_status = "✓ fly-scan OK" if not has_negative else f"✗ {n_negative} negative gaps"
        print(
            f"{ds['title']:>25s}:  "
            f"min={np.min(delta):8.3f}{unit}  "
            f"max={np.max(delta):8.3f}{unit}  "
            f"mean={np.mean(delta):8.3f}{unit}  "
            f"std={np.std(delta):8.3f}{unit}  "
            f"unique={n_unique:4d}  "
            f"[{fly_status}]"
        )

    plt.tight_layout()
    plt.show()


def plot_distinct_deltas_vs_N_K(
    N_values=None,
    K_values=None,
):
    if N_values is None:
        N_values = [10, 20, 50, 100, 200, 500, 1000]
    if K_values is None:
        K_values = [1, 2, 3, 4, 5, 6, 8, 10, 16]

    schemes = {
        "Equally Spaced": lambda N, K: compute_equally_spaced_multiturn_angles(
            num_angles=N, K_interlace=K, rotation_start=0.0, rotation_stop=360.0,
        ),
        "Golden Angle": lambda N, K: compute_golden_angle_multiturn_angles(
            num_angles=N, K_interlace=K, rotation_start=0.0,
        ),
        "Van der Corput": lambda N, K: compute_corput_multiturn_angles(
            num_angles=N, K_interlace=K, rotation_start=0.0, rotation_stop=360.0,
        ),
        "TIMBIR": lambda N, K: compute_timbir_multiturn_angles(
            num_angles=N, K_interlace=K, rotation_start=0.0,
        ),
    }

    markers = ["o", "s", "D", "^", "v", "P", "*", "X", "h"]
    fig, axes = plt.subplots(1, len(schemes), figsize=(5 * len(schemes), 5))
    fig.suptitle(
        "Number of distinct $\\Delta\\theta$ values vs. N (angles per turn)\n"
        "for different K (number of turns)",
        fontsize=13, y=1.03,
    )

    colors_K = plt.cm.viridis(np.linspace(0.2, 0.9, len(K_values)))

    n_K = len(K_values)
    jitter_offsets = np.linspace(-0.15, 0.15, n_K)

    for ax, (scheme_name, scheme_fn) in zip(axes, schemes.items()):
        ax.set_title(scheme_name, fontsize=11, fontweight="bold")

        for ki, K in enumerate(K_values):
            n_distinct_list = []
            valid_N = []
            for N in N_values:
                try:
                    angles_per_turn, _, _ = scheme_fn(N, K)
                    delta = compute_delta_angles_acquisition_order(angles_per_turn)
                    n_dist = count_distinct_deltas(delta)
                    n_distinct_list.append(n_dist)
                    valid_N.append(N)
                except (ValueError, AssertionError):
                    continue

            if valid_N:
                jittered = [v + jitter_offsets[ki] for v in n_distinct_list]
                is_pow2 = K >= 1 and (K & (K - 1)) == 0
                label = f"K={K}" if is_pow2 else f"K={K} (non-2ⁿ)"
                ax.plot(
                    valid_N, jittered,
                    linestyle="-" if is_pow2 else "--",
                    color=colors_K[ki], lw=1.5,
                    marker=markers[ki % len(markers)], ms=7,
                    label=label,
                    alpha=0.85,
                )

        ax.set_xlabel("N (angles per turn)")
        ax.set_ylabel("# distinct $\\Delta\\theta$ values")
        ax.set_xscale("log")
        ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Print table
    print(f"\n{'Scheme':>20s} {'K':>4s} {'N':>6s} {'#distinct':>10s} {'note':>12s}")
    print("-" * 58)
    for scheme_name, scheme_fn in schemes.items():
        for K in K_values:
            for N in N_values:
                try:
                    angles_per_turn, _, _ = scheme_fn(N, K)
                    delta = compute_delta_angles_acquisition_order(angles_per_turn)
                    n_dist = count_distinct_deltas(delta)
                    is_pow2 = K >= 1 and (K & (K - 1)) == 0
                    note = "" if is_pow2 else "non-2^n"
                    print(f"{scheme_name:>20s} {K:4d} {N:6d} {n_dist:10d} {note:>12s}")
                except (ValueError, AssertionError):
                    pass

def main():
    num_angles = 100
    K_interlace = 1
    rotation_start = 0.0
    rotation_stop = 360.0
    degrees = True
    show_monotonic = True
    dr = 0.25

    angles_eq, theta_eq, theta_eq_mono = compute_equally_spaced_multiturn_angles(
        num_angles=num_angles,
        K_interlace=K_interlace,
        rotation_start=rotation_start,
        rotation_stop=rotation_stop,
        degrees=degrees,
    )

    angles_ga, theta_ga, theta_ga_mono = compute_golden_angle_multiturn_angles(
        num_angles=num_angles,
        K_interlace=K_interlace,
        rotation_start=rotation_start,
        degrees=degrees,
    )

    angles_vc, theta_vc, theta_vc_mono = compute_corput_multiturn_angles(
        num_angles=num_angles,
        K_interlace=K_interlace,
        rotation_start=rotation_start,
        rotation_stop=rotation_stop,
        degrees=degrees,
    )
    angles_tb, theta_tb, theta_tb_mono = compute_timbir_multiturn_angles(
        num_angles=num_angles,
        K_interlace=K_interlace,
        rotation_start=rotation_start,
        degrees=degrees,
    )

    datasets = [
        {
            "angles_per_turn": angles_eq,
            "theta_interlaced": theta_eq,
            "theta_monotonic": theta_eq_mono,
            "title": "Equally Spaced",
        },
        {
            "angles_per_turn": angles_ga,
            "theta_interlaced": theta_ga,
            "theta_monotonic": theta_ga_mono,
            "title": "Golden Angle",
        },
        {
            "angles_per_turn": angles_vc,
            "theta_interlaced": theta_vc,
            "theta_monotonic": theta_vc_mono,
            "title": "Van der Corput",
        },
        {
            "angles_per_turn": angles_tb,
            "theta_interlaced": theta_tb,
            "theta_monotonic": theta_tb_mono,
            "title": "TIMBIR",
        },
    ]

    polar_plot_interlaced_grid(
        datasets,
        degrees=degrees,
        show_monotonic=show_monotonic,
        dr=dr,
    )

    plot_delta_angle_distributions(
        datasets,
        degrees=degrees,
    )

    plot_distinct_deltas_vs_N_K()


if __name__ == "__main__":
    main()
