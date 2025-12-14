import numpy as np
from skimage.registration import phase_cross_correlation
import argparse
import h5py
import os
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
# Secondary method: shift-based, detrended + windowed, SAME max_frames/band
# ----------------------------------------------------------------------
def extract_vibration_frequency_detrended(
    data,
    sampling_rate=162.0,
    upsample=100,
    max_frames=100,
    band_low=20.0,
    band_high=80.0,
):
    """
    Detrended + windowed shift-based method.
    """
    n_frames = data.shape[0]
    if max_frames is not None and n_frames > max_frames:
        data = data[:max_frames]
        n_frames = max_frames
        print(f"Using only first {n_frames} frames for DETRENDED analysis.")

    if n_frames < 3:
        raise ValueError("Need at least 3 frames to estimate vibration frequency.")

    shifts = np.zeros(n_frames - 1, dtype=np.float64)

    for i in range(n_frames - 1):
        shift, _, _ = phase_cross_correlation(
            data[i], data[i + 1], upsample_factor=upsample
        )
        shifts[i] = shift[0]

    # Detrend
    shifts_dt = detrend(shifts, type="linear")
    # Hann window
    win = windows.hann(len(shifts_dt))
    shifts_win = shifts_dt * win

    freqs = np.fft.rfftfreq(len(shifts_win), d=1.0 / sampling_rate)
    fft_vals = np.fft.rfft(shifts_win)
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

    print("\n[DET DEBUG] N =", len(shifts))
    print("[DET DEBUG] dt =", 1.0 / sampling_rate)
    print("[DET DEBUG] freq resolution =", sampling_rate / len(shifts), "Hz")
    print("[DET DEBUG] band = [", band_low, ",", band_high, "] Hz")
    print("[DET DEBUG] peak_freq =", peak_freq, "Hz")

    return peak_freq, shifts, freqs, fft_mag


# ----------------------------------------------------------------------
# Viewer
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
# Plot helper
# ----------------------------------------------------------------------
def plot_signals_and_spectra(
    positions,
    freqs_pos,
    fft_pos,
    shifts,
    freqs_shift,
    fft_shift,
    sampling_rate,
    band_low,
    band_high,
):
    t_pos = np.arange(len(positions)) / sampling_rate
    t_shift = np.arange(len(shifts)) / sampling_rate

    plt.figure(figsize=(10, 8))

    # Position signal
    plt.subplot(2, 2, 1)
    plt.plot(t_pos, positions, "-k")
    plt.xlabel("Time [s]")
    plt.ylabel("Position [px]")
    plt.title("Position vs time (position-based)")

    # Position spectrum
    plt.subplot(2, 2, 2)
    plt.plot(freqs_pos, fft_pos, "-b", label="|FFT|")
    if band_low is not None and band_high is not None:
        plt.axvspan(band_low, band_high, color="orange", alpha=0.2, label="Band")
    plt.xlim(0, sampling_rate / 2)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("|FFT(position)|")
    plt.title("Position spectrum")
    plt.legend()

    # Shift signal
    plt.subplot(2, 2, 3)
    plt.plot(t_shift, shifts, "-k")
    plt.xlabel("Time [s]")
    plt.ylabel("Shift [px]")
    plt.title("Frame-to-frame shift vs time (detrended method uses this)")

    # Shift spectrum
    plt.subplot(2, 2, 4)
    plt.plot(freqs_shift, fft_shift, "-g", label="|FFT|")
    if band_low is not None and band_high is not None:
        plt.axvspan(band_low, band_high, color="orange", alpha=0.2, label="Band")
    plt.xlim(0, sampling_rate / 2)
    plt.xlabel("Frequency [Hz]")
    plt.ylabel("|FFT(shift)|")
    plt.title("Shift spectrum (after detrend+window)")
    plt.legend()

    plt.tight_layout()
    plt.show()


# ----------------------------------------------------------------------
# main
# ----------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Extract vertical vibration frequency from a stack of images."
    )
    parser.add_argument("file", type=str, help="Path to .npy or .h5/.hdf5 file.")
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
        default=100,
        help="Use only the first N frames for frequency estimation (default: 100).",
    )
    parser.add_argument(
        "--band",
        type=float,
        nargs=2,
        metavar=("F_MIN", "F_MAX"),
        default=[20.0, 80.0],
        help="Restrict peak search to frequency band [F_MIN, F_MAX] Hz (default: 20 80).",
    )
    parser.add_argument(
        "--view",
        action="store_true",
        help="View images with slider instead of computing frequency.",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Plot time signals and spectra for both methods.",
    )
    parser.add_argument(
        "--dual_band",
        action="store_true",
        help="Additionally report vent line (25–35 Hz) and dominant resonance (35–100 Hz) using position-based method.",
    )

    args = parser.parse_args()

    print(f"Loading data from {args.file} ...")
    ext = os.path.splitext(args.file)[1].lower()
    if ext in [".h5", ".hdf5"]:
        with h5py.File(args.file, "r") as f:
            data = f["/exchange/data"][:]
    else:
        data = np.load(args.file)

    if args.view:
        view_images_with_slider(data)
        return

    band_low, band_high = args.band

    # Run both methods on the same data with the same window and band
    freq_pos, positions, freqs_pos, fft_pos = extract_vibration_frequency_position(
        data,
        sampling_rate=args.sampling_rate,
        upsample=args.upsample,
        max_frames=args.max_frames,
        band_low=band_low,
        band_high=band_high,
    )

    freq_det, shifts_det, freqs_det, fft_det = extract_vibration_frequency_detrended(
        data,
        sampling_rate=args.sampling_rate,
        upsample=args.upsample,
        max_frames=args.max_frames,
        band_low=band_low,
        band_high=band_high,
    )

    # Summary for current band
    print("\n==================== Summary (current band) ====================")
    print(f"Total frames loaded: {data.shape[0]}")
    print(f"Frames used for analysis: {len(positions)}")
    print(f"Sampling rate: {args.sampling_rate} Hz")
    print(f"Band: [{band_low}, {band_high}] Hz\n")
    print("{:<30s} {:>10s}".format("Method", "Freq [Hz]"))
    print("-" * 42)
    print("{:<30s} {:>10.3f}".format("Position-based", freq_pos))
    print("{:<30s} {:>10.3f}".format("Shift-based (detrended)", freq_det))
    print("===============================================================\n")

    # Dual-band report: vent line and resonance using position-based method
    if args.dual_band:
        vent_low, vent_high = 25.0, 35.0
        res_low, res_high = 35.0, 100.0

        vent_freq, _, _, _ = extract_vibration_frequency_position(
            data,
            sampling_rate=args.sampling_rate,
            upsample=args.upsample,
            max_frames=args.max_frames,
            band_low=vent_low,
            band_high=vent_high,
        )

        res_freq, _, _, _ = extract_vibration_frequency_position(
            data,
            sampling_rate=args.sampling_rate,
            upsample=args.upsample,
            max_frames=args.max_frames,
            band_low=res_low,
            band_high=res_high,
        )

        print("=============== Dual-band (position-based) =================")
        print(f"Vent line      [{vent_low:.1f}, {vent_high:.1f}] Hz : {vent_freq:.3f} Hz")
        print(f"Resonance mode [{res_low:.1f}, {res_high:.1f}] Hz : {res_freq:.3f} Hz")
        print("===========================================================\n")

    # Optional plots for the current band
    if args.plot:
        plot_signals_and_spectra(
            positions=positions,
            freqs_pos=freqs_pos,
            fft_pos=fft_pos,
            shifts=shifts_det,
            freqs_shift=freqs_det,
            fft_shift=fft_det,
            sampling_rate=args.sampling_rate,
            band_low=band_low,
            band_high=band_high,
        )


if __name__ == "__main__":
    main()