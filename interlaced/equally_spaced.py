import numpy as np
import matplotlib.pyplot as plt


def compute_equally_spaced_multiturn_angles(
    num_angles=180,
    K_interlace=3,
    rotation_start=0.0,
    rotation_stop=180.0,
    delta_theta=None,
    degrees=True,
):
    """
    Compute equally spaced interlaced multi-turn acquisition angles.

    Each of the K turns produces N uniformly spaced angles, offset by
    delta_theta / K from one turn to the next, so that the combined set
    of K*N angles is itself equally spaced over the rotation range.

    Parameters
    ----------
    num_angles : int
        Number of angles per turn (N).
    K_interlace : int
        Number of interlaced turns (K).
    rotation_start : float
        Starting angle of the acquisition range.
    rotation_stop : float
        Ending angle of the acquisition range.
    delta_theta : float or None
        Angular step within a single turn. If None, computed as
        (rotation_stop - rotation_start) / (N - 1).
    degrees : bool
        Whether angles are specified in degrees (True) or radians (False).

    Returns
    -------
    angles_per_turn : list of np.ndarray
        List of K arrays, each containing N angles for that turn.
    theta_interlaced : np.ndarray
        All K*N angles concatenated in acquisition order.
    theta_monotonic : np.ndarray
        All K*N angles sorted in ascending order.
    """
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


def polar_plot_interlaced(
    angles_per_turn,
    theta_interlaced,
    theta_monotonic,
    degrees=True,
    show_monotonic=False,
    r0=1.0,
    dr=0.15,
    mono_offset=0.25,
):
    """
    Create a polar plot of equally spaced interlaced multi-turn acquisition angles.

    Parameters
    ----------
    angles_per_turn : list of np.ndarray
        Per-turn angle arrays (from compute_equally_spaced_multiturn_angles).
    theta_interlaced : np.ndarray
        All angles in acquisition order.
    theta_monotonic : np.ndarray
        All angles sorted monotonically.
    degrees : bool
        Whether the input angles are in degrees.
    show_monotonic : bool
        Whether to overlay the sorted (monotonic) angles.
    r0 : float
        Base radius for the innermost turn.
    dr : float
        Radial separation between successive turns.
    mono_offset : float
        How far inside r0 to draw the monotonic ring.
    """
    K = len(angles_per_turn)
    N = len(angles_per_turn[0])

    # Convert to radians, wrapped to [0, 2π)
    if degrees:
        th_turns = [np.deg2rad(a % 360.0) for a in angles_per_turn]
        th_all = np.deg2rad(theta_interlaced % 360.0)
        th_mono = np.deg2rad(theta_monotonic % 360.0)
    else:
        th_turns = [a % (2 * np.pi) for a in angles_per_turn]
        th_all = theta_interlaced % (2 * np.pi)
        th_mono = theta_monotonic % (2 * np.pi)

    # Radii: separate each turn by dr
    r_turns = [r0 + dr * k for k in range(K)]
    r_all = np.empty_like(th_all)
    for k in range(K):
        r_all[k * N : (k + 1) * N] = r_turns[k]

    # --- Plot ---
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

    ax.set_title("Equally spaced multi-turn acquisition angles (polar view)")
    ax.set_rticks([])
    ax.set_ylim(r0 - mono_offset - 0.1, r0 + dr * (K - 1) + 0.2)
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10))

    plt.tight_layout()
    plt.show()


def main():
    # --- Parameters ---
    num_angles = 10
    K_interlace = 4
    rotation_start = 0.0
    rotation_stop = 360.0
    degrees = True
    show_monotonic = True
    dr = 0.25  # try 0.2–0.4

    # --- Compute equally spaced multi-turn angles ---
    angles_per_turn, theta_interlaced, theta_monotonic = (
        compute_equally_spaced_multiturn_angles(
            num_angles=num_angles,
            K_interlace=K_interlace,
            rotation_start=rotation_start,
            rotation_stop=rotation_stop,
            degrees=degrees,
        )
    )

    # --- Plot ---
    polar_plot_interlaced(
        angles_per_turn,
        theta_interlaced,
        theta_monotonic,
        degrees=degrees,
        show_monotonic=show_monotonic,
        dr=dr,
    )


if __name__ == "__main__":
    main()
