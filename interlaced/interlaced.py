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
        delta_theta = (rotation_stop - rotation_start) / (N - 1)
    rotation_step = float(delta_theta)

    n = np.arange(N, dtype=float)
    angles_per_turn = []
    for k in range(K):
        theta_n = rotation_start + (n + k / K) * rotation_step
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
        delta_theta = (float(rotation_stop) - start) / (N - 1)

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
    """
    Create a polar plot of interlaced multi-turn acquisition angles.

    If `ax` is provided, draws into that polar Axes (for use in subplots).
    If `ax` is None, creates a standalone figure and calls plt.show().
    """
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
    """
    Plot multiple acquisition schemes side-by-side in a single figure.

    Parameters
    ----------
    datasets : list of dict
        Each dict must contain:
            "angles_per_turn" : list of np.ndarray
            "theta_interlaced" : np.ndarray
            "theta_monotonic" : np.ndarray
            "title" : str
    """
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


def main():
    num_angles = 10
    K_interlace = 4
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


if __name__ == "__main__":
    main()
