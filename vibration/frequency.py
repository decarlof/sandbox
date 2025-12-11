import numpy as np
from skimage.registration import phase_cross_correlation
import argparse

def extract_vibration_frequency(data, sampling_rate=1000, upsample=100):
    """
    Estimate the vibration frequency from a stack of flat-field images.

    Parameters
    ----------
    data : np.ndarray
        3D array of shape (n, y, x) with images acquired at constant rate.
    sampling_rate : float
        Acquisition rate in Hz (default = 1000 Hz for 1 kHz).
    upsample : int
        Subpixel upsampling factor for phase correlation.

    Returns
    -------
    peak_freq : float
        Dominant vibration frequency in Hz.
    shifts : np.ndarray
        Array of vertical shifts (in pixels) for each time frame.
    freqs : np.ndarray
        Frequencies corresponding to FFT.
    fft_mag : np.ndarray
        Magnitude spectrum of the shift signal.
    """

    n_frames = data.shape[0]
    shifts = np.zeros(n_frames - 1)

    # --- Compute vertical shift per frame (subpixel precision) ---
    for i in range(n_frames - 1):
        shift, _, _ = phase_cross_correlation(data[i], data[i+1],
                                              upsample_factor=upsample)
        shifts[i] = shift[0]  # vertical shift

    # --- FFT of the shift signal ---
    freqs = np.fft.rfftfreq(len(shifts), d=1.0 / sampling_rate)
    fft_mag = np.abs(np.fft.rfft(shifts))

    # --- Dominant frequency ---
    peak_freq = freqs[np.argmax(fft_mag)]

    return peak_freq, shifts, freqs, fft_mag


def main():
    parser = argparse.ArgumentParser(description="Extract vibration frequency from a stack of images.")
    parser.add_argument("file", type=str, help="Path to .npy file containing the 3D data array (n, y, x).")
    parser.add_argument("--sampling_rate", type=float, default=1000.0,
                        help="Acquisition sampling rate in Hz (default: 1000 Hz).")
    parser.add_argument("--upsample", type=int, default=100,
                        help="Upsampling factor for subpixel phase correlation (default: 100).")

    args = parser.parse_args()

    # Load data
    print(f"Loading data from {args.file} ...")
    data = np.load(args.file)

    # Compute frequency
    peak_freq, shifts, freqs, fft_mag = extract_vibration_frequency(
        data,
        sampling_rate=args.sampling_rate,
        upsample=args.upsample
    )

    print(f"\nDominant vibration frequency: {peak_freq:.3f} Hz")
    print(f"Total frames processed: {data.shape[0]}")
    print(f"Shift signal length: {len(shifts)} frames")

if __name__ == "__main__":
    main()

