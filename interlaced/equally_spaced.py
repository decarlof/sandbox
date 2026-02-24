import numpy as np
import matplotlib.pyplot as plt

def polar_plot_interlaced(
    num_angles=180,
    K_interlace=3,
    rotation_start=0.0,
    rotation_stop=180.0,
    delta_theta=None,
    degrees=True,
    show_monotonic=False,
    r0=1.0,
    dr=0.15,          # <-- increase this to separate turns more
    mono_offset=0.25, # <-- how far inside to draw the monotonic ring
):
    N = int(num_angles)
    K = int(K_interlace)

    if delta_theta is None:
        delta_theta = (rotation_stop - rotation_start) / (N - 1)
    rotation_step = float(delta_theta)

    n = np.arange(N, dtype=float)
    angles_all = []
    for k in range(K):
        theta_n = rotation_start + (n + k / K) * rotation_step
        angles_all.append(theta_n)

    theta_interlaced = np.concatenate(angles_all).astype(float)
    theta_monotonic = np.sort(theta_interlaced)

    if degrees:
        th_all = np.deg2rad(theta_interlaced % 360.0)
        th_turns = [np.deg2rad(a % 360.0) for a in angles_all]
        th_mono = np.deg2rad(theta_monotonic % 360.0)
    else:
        th_all = theta_interlaced % (2 * np.pi)
        th_turns = [a % (2 * np.pi) for a in angles_all]
        th_mono = theta_monotonic % (2 * np.pi)

    # Radii: separate each turn by dr
    r_turns = [r0 + dr * k for k in range(K)]
    r_all = np.empty_like(th_all)
    for k in range(K):
        r_all[k * N : (k + 1) * N] = r_turns[k]

    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="polar")

    for k in range(K):
        ax.scatter(th_turns[k], np.full(N, r_turns[k]), s=18, label=f"turn k={k}", alpha=0.9)

    ax.plot(th_all, r_all, lw=1.0, alpha=0.35, color="k", label="acq order path")

    if show_monotonic:
        ax.scatter(th_mono, np.full_like(th_mono, r0 - mono_offset), s=10, alpha=0.7,
                   label="sorted (monotonic)")

    ax.set_title("Interlaced multi-turn acquisition angles (polar view)")
    ax.set_rticks([])
    ax.set_ylim(r0 - mono_offset - 0.1, r0 + dr * (K - 1) + 0.2)
    ax.grid(True)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.10))

    plt.tight_layout()
    plt.show()

    return angles_all, theta_interlaced, theta_monotonic

# Example
angles_all, theta_interlaced, theta_monotonic = polar_plot_interlaced(
    num_angles=10,
    K_interlace=4,
    rotation_start=0.0,
    rotation_stop=360.0,
    degrees=True,
    show_monotonic=True,
    dr=0.25,          # try 0.2–0.4
)
