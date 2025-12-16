import numpy as np
from skimage.registration import phase_cross_correlation
import argparse
import h5py
import os
import glob
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from scipy.signal import detrend, windows


# ----------------------------------------------------------------------
# Primary method: position-based
# ----------------------------------------------------------------------
def extract_vibration_frequency_position(
    data,
    sampling_rate=162.0,
    upsample=100,
    max_frames=100,
    band_low=20.0,
    band_high=80.0,
):
    """
    Estimate vertical vibration frequency by tracking absolute vertical position
    of each frame relative to the first frame, then FFT-ing that 1D signal.
    """
    n_frames = data.shape[0]
    if max_frames is not None and n_frames > max_frames:
        data = data[:max_frames]
        n_frames = max_frames
        print(f"Using only first {n_frames} frames for POSITION analysis.")

    if n_frames < 3:
        raise ValueError("Need at least 3 frames to estimate vibration frequency.")

    ref = data[0]
    positions = np.zeros(n_frames, dtype=np.float64)

    # Estimate vertical shift of each frame relative to reference
    for k in range(1, n_frames):
        shift, _, _ = phase_cross_correlation(ref, data[k], upsample_factor=upsample)
        positions[k] = shift[0]  # vertical shift only

    # Remove mean
    positions -= np.mean(positions)

    # FFT of position signal
    N = len(positions)
    dt = 1.0 / sampling_rate
    freqs = np.fft.rfftfreq(N, d=dt)
    fft_vals = np.fft.rfft(positions)
    fft_mag = np.abs(fft_vals)

    # Apply band limit [band_low, band_high]
    valid = np.ones_like(freqs, dtype=bool)
    if band_low is not None:
        valid &= freqs >= band_low
    if band_high is not None:
        valid &= freqs <= band_high

    if np.any(valid):
        freqs_valid = freqs[valid]
        fft_mag_valid = fft_mag[valid]
        peak_idx = np.argmax(fft_mag_valid)
        peak_freq = freqs_valid[peak_idx]
    else:
        peak_idx = np.argmax(fft_mag)
        peak_freq = freqs[peak_idx]

    print("\n[POS DEBUG] N =", N)
    print("[POS DEBUG] dt =", dt)
    print("[POS DEBUG] freq resolution =", sampling_rate / N, "Hz")
    print("[POS DEBUG] band = [", band_low, ",", band_high, "] Hz")
    print("[POS DEBUG] peak_freq =", peak_freq, "Hz")

    return peak_freq, positions, freqs, fft_mag


# ----------------------------------------------------------------------
# Viewer (unchanged from your version)
# ----------------------------------------------------------------------
def view_images_with_slider(data):
    data = np.asarray(data)
    if data.ndim != 3:
        raise ValueError(f"Expected data with shape (N, Y, X), got {data.shape}")

    n_images = data.shape[0]
    idx0 = 0

    flat = data.reshape(-1)
    p1, p99 = np.percentile(flat, [1, 99])
    if p99 <= p1:
        p1 = float(np.min(flat))
        p99 = float(np.max(flat))

    global_min = p1
    global_max = p99
    global_mean = 0.5 * (global_min + global_max)
    global_range = global_max - global_min if global_max > global_min else 1.0

    state = {
        "scale": 1.0,
        "offset": 0.0,
    }

    def compute_clim():
        half_range = 0.5 * global_range / state["scale"]
        center = global_mean + state["offset"] * global_range
        vmin = center - half_range
        vmax = center + half_range
        return vmin, vmax

    fig, ax = plt.subplots()
    plt.subplots_adjust(bottom=0.25)

    im = ax.imshow(data[idx0], cmap="gray")
    ax.set_title(f"Image {idx0 + 1}/{n_images}")
    fig.colorbar(im, ax=ax)

    vmin, vmax = compute_clim()
    im.set_clim(vmin=vmin, vmax=vmax)

    ax_slider = plt.axes([0.15, 0.1, 0.7, 0.03])
    slider = Slider(
        ax=ax_slider,
        label="Frame",
        valmin=0,
        valmax=n_images - 1,
        valinit=idx0,
        valstep=1,
    )

    def update_frame(val):
        idx = int(slider.val)
        im.set_data(data[idx])
        ax.set_title(f"Image {idx + 1}/{n_images}")
        fig.canvas.draw_idle()

    slider.on_changed(update_frame)

    def apply_clim():
        vmin_, vmax_ = compute_clim()
        im.set_clim(vmin=vmin_, vmax=vmax_)
        fig.canvas.draw_idle()

    def on_key(event):
        if event.key == '+':
            state["scale"] *= 1.2
            apply_clim()
        elif event.key == '-':
            state["scale"] /= 1.2
            apply_clim()
        elif event.key == ']':
            state["offset"] += 0.05
            apply_clim()
        elif event.key == '[':
            state["offset"] -= 0.05
            apply_clim()
        elif event.key == 'r':
            state["scale"] = 1.0
            state["offset"] = 0.0
            apply_clim()

    fig.canvas.mpl_connect("key_press_event", on_key)
    plt.show()


# ----------------------------------------------------------------------
# Plot helper (uses position-based only here if needed)
# ----------------------------------------------------------------------
def plot_position_spectrum(positions, freqs, fft_mag, sampling_rate, band_low, band_high):
    t_pos = np.arange(len(positions)) / sampling_rate

    plt.figure(figsize=(10, 4))

    # Position signal
    plt.subplot(1, 2, 1)
    plt.plot(t_pos, positions, "-k")
    plt.xlabel("Time [s]")
    plt.ylabel("Position [px]")
    plt.title("Position vs time")

    # Position spectrum
    plt.subplot(1, 2, 2)
    plt.plot(freqs, fft_mag, "-b", label="|FFT|")
    if band_low is not None and band_high is not None:
        plt.axvspan(band_low, band_high, color="orange", alpha=0.2, label="Band")
    plt.xlim(0, sampling_rate / 2)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("|FFT(position)|")
    plt.title("Position spectrum")
    plt.legend()

    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Extract vertical vibration frequencies (dual band, position-based) from a set of HDF5 files."
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Folder containing HDF5 files (e.g. /path/to/DeCarlo).",
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.h5",
        help="Glob pattern to select files in folder (default: *.h5).",
    )
    parser.add_argument(
        "--sampling_rate",
        type=float,
        default=162.0,
        help="Acquisition rate in Hz (default: 162).",
    )
    parser.add_argument(
        "--upsample",
        type=int,
        default=100,
        help="Upsampling factor for phase_cross_correlation (default: 100).",
    )
    parser.add_argument(
        "--max_frames",
        type=int,
        default=648,
        help="Use only the first N frames for frequency estimation (default: 648).",
    )
    parser.add_argument(
        "--view",
        action="store_true",
        help="View images with slider for the first matching file instead of computing frequency.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot position signal and spectrum for each file (may be slow).",
    )

    args = parser.parse_args()

    folder = args.folder
    pattern = os.path.join(folder, args.pattern)

    files = sorted(glob.glob(pattern))
    if not files:
        print(f"No files found matching pattern: {pattern}")
        return

    # To store summary results
    summary_rows = []

    # Fixed dual bands
    vent_low, vent_high = 25.0, 35.0
    res_low, res_high = 35.0, 100.0

    print(f"Found {len(files)} files. Processing with max_frames={args.max_frames} ...")

    for path in files:
        fname = os.path.basename(path)
        print("\n===================================================")
        print(f"Processing file: {fname}")
        print("===================================================")

        # Load data
        ext = os.path.splitext(path)[1].lower()
        if ext in [".h5", ".hdf5"]:
            with h5py.File(path, "r") as f:
                data = f["/exchange/data"][:]
        else:
            # For completeness; your current data are .h5
            data = np.load(path)

        if args.view:
            # Just show this file and exit
            view_images_with_slider(data)
            return

        # Vent band [25, 35] Hz
        vent_freq, positions_v, freqs_v, fft_v = extract_vibration_frequency_position(
            data,
            sampling_rate=args.sampling_rate,
            upsample=args.upsample,
            max_frames=args.max_frames,
            band_low=vent_low,
            band_high=vent_high,
        )

        # Resonance band [35, 100] Hz
        res_freq, positions_r, freqs_r, fft_r = extract_vibration_frequency_position(
            data,
            sampling_rate=args.sampling_rate,
            upsample=args.upsample,
            max_frames=args.max_frames,
            band_low=res_low,
            band_high=res_high,
        )

        # Dual-band summary for this file
        print("=============== Dual-band (position-based) =================")
        print(
            f"Peak in the range     [{vent_low:.1f}, {vent_high:.1f}] Hz : {vent_freq:.3f} Hz"
        )
        print(
            f"Peak in the range  [{res_low:.1f}, {res_high:.1f}] Hz : {res_freq:.3f} Hz"
        )
        print("===========================================================\n")

        # Optionally plot for this file (for the resonance band by default)
        if args.plot:
            # Example: plot using the resonance-band spectrum
            plot_position_spectrum(
                positions_r,
                freqs_r,
                fft_r,
                sampling_rate=args.sampling_rate,
                band_low=res_low,
                band_high=res_high,
            )

        # Add to summary
        summary_rows.append((fname, vent_freq, res_freq))

    # Print summary table at the end
    print("\n====================== Summary table ======================")
    print("{:<40s} {:>18s} {:>22s}".format("file", "Peak [25.0, 35.0] Hz", "Peak [35.0,100.0] Hz"))
    print("-" * 82)
    for fname, vent_freq, res_freq in summary_rows:
        print("{:<40s} {:>18.3f} {:>22.3f}".format(fname, vent_freq, res_freq))
    print("===========================================================\n")


if __name__ == "__main__":
    main()