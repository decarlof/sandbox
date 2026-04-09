#!/usr/bin/env python3
"""
merge_intervals_interp.py — merge and flat-field-correct tomoscan interval
HDF5 files using per-projection linearly-interpolated flat fields.

Flat-field interpolation scheme
--------------------------------
Each scan interval produces one HDF5 file.  Flat fields were collected as:
  - Files 0 … N-2  :  FlatFieldMode = Start  → all flats at beginning
  - File  N-1      :  FlatFieldMode = Both   → flats at Start AND End
                       (stored in order: start flats, then end flats)

For every projection j in file i the flat is interpolated as:

    weight_j = j / (n_proj_i - 1)        # 0 at first proj, 1 at last
    flat_j   = (1 - weight_j) * flat_i_start  +  weight_j * flat_i_end

where the reference flats are:
  - flat_i_start = mean of all flat frames in file i
                   (or mean of the FIRST half, for the last file)
  - flat_i_end   = flat_(i+1)_start           (for files 0 … N-2)
                   mean of the SECOND half of flat frames (for the last file)

The dark field is taken as the mean of dark frames from the same file and
subtracted before dividing:

    corrected_j = clip( (proj_j - dark_mean_i) / (flat_j - dark_mean_i), 0, ∞ )

Output HDF5 contains:
  /exchange/data   — float32 corrected projections (all files concatenated)
  /exchange/theta  — float64 angles in degrees

Usage
-----
    # glob (sorted = scan order):
    python merge_intervals_interp.py --glob '/data/sample_*.h5' --output merged.h5

    # explicit order:
    python merge_intervals_interp.py a.h5 b.h5 c.h5 --output merged.h5

    # dry run — show plan without writing:
    python merge_intervals_interp.py --glob '*.h5' --output merged.h5 --dry-run
"""

import argparse
import glob as glob_module
import os
import sys

import h5py
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from scipy.ndimage import median_filter as cpu_median_filter

DS_PROJ  = '/exchange/data'
DS_FLAT  = '/exchange/data_white'
DS_DARK  = '/exchange/data_dark'
DS_THETA = '/exchange/theta'

DEFAULT_CHUNK     = 20   # projections per chunk (tune to available RAM)
DEZINGER_RADIUS   = 5
DEZINGER_THRESH   = 3.0  # sigma above local median to flag as zinger

# GPU support — present in the tomocupy conda environment
try:
    import cupy as cp
    from cupyx.scipy.ndimage import median_filter as gpu_median_filter
    HAS_CUPY = True
except ImportError:
    HAS_CUPY = False


# ---------------------------------------------------------------------------
# Dezinger  (tomocupy-style: median filter + threshold on residual)
# ---------------------------------------------------------------------------

def dezinger_chunk(chunk, radius=DEZINGER_RADIUS, threshold=DEZINGER_THRESH):
    """Dezinger a (N, H, W) float32 chunk.

    Algorithm (same as tomocupy remove_outlier):
        med   = median_filter(frame, 2*radius+1)
        mask  = (frame - med) > threshold * MAD_sigma
        frame[mask] = med[mask]

    Runs on GPU via cupy/cupyx when available; otherwise uses parallel
    CPU threads (scipy releases the GIL so ThreadPoolExecutor scales well).

    Returns (cleaned_chunk, total_zingers_replaced).
    """
    if HAS_CUPY:
        return _dezinger_gpu(chunk, radius, threshold)
    return _dezinger_cpu(chunk, radius, threshold)


def _dezinger_gpu(chunk, radius, threshold):
    window   = 2 * radius + 1
    n_zing   = 0
    data     = cp.asarray(chunk)          # single host→device transfer

    for k in range(data.shape[0]):
        frame = data[k]
        med   = gpu_median_filter(frame, size=window)
        diff  = frame - med
        mad   = float(cp.median(cp.abs(diff))) * 1.4826
        if mad > 0.0:
            mask    = diff > threshold * mad
            n_zing += int(mask.sum())
            frame[mask] = med[mask]

    return cp.asnumpy(data), n_zing       # single device→host transfer


def _dezinger_one_cpu(args):
    frame, radius, threshold = args
    window = 2 * radius + 1
    med    = cpu_median_filter(frame, size=window)
    diff   = frame - med
    mad    = np.median(np.abs(diff)) * 1.4826
    if mad == 0.0:
        return frame, 0
    mask   = diff > threshold * mad
    n      = int(mask.sum())
    if n:
        frame       = frame.copy()
        frame[mask] = med[mask]
    return frame, n


def _dezinger_cpu(chunk, radius, threshold):
    args = [(chunk[k], radius, threshold) for k in range(chunk.shape[0])]
    with ThreadPoolExecutor() as pool:
        results = list(pool.map(_dezinger_one_cpu, args))
    n_zing = 0
    for k, (frame, n) in enumerate(results):
        chunk[k] = frame
        n_zing  += n
    return chunk, n_zing


# ---------------------------------------------------------------------------
# Reference-flat helpers
# ---------------------------------------------------------------------------

def mean_frames(ds, start=None, stop=None):
    """Return float32 mean image of ds[start:stop]."""
    sl = ds[start:stop]
    if sl.shape[0] == 0:
        return None
    return sl.astype(np.float32).mean(axis=0)


def load_flat_refs(path, is_last):
    """
    Return (flat_start, flat_end, dark_mean, n_proj) for one file.

    For the last file (is_last=True):
        flat_start = mean of first half of data_white
        flat_end   = mean of second half of data_white
    For all other files:
        flat_start = mean of all data_white
        flat_end   = None  (filled in by the caller from the next file)
    """
    with h5py.File(path, 'r') as f:
        n_proj = f[DS_PROJ].shape[0] if DS_PROJ in f else 0

        # dark mean
        dark_mean = None
        if DS_DARK in f and f[DS_DARK].shape[0] > 0:
            dark_mean = mean_frames(f[DS_DARK])

        # flat references
        if DS_FLAT not in f or f[DS_FLAT].shape[0] == 0:
            return None, None, dark_mean, n_proj

        n_flat = f[DS_FLAT].shape[0]

        if is_last:
            mid = n_flat // 2
            flat_start = mean_frames(f[DS_FLAT], 0, mid)
            flat_end   = mean_frames(f[DS_FLAT], mid, n_flat)
        else:
            flat_start = mean_frames(f[DS_FLAT])
            flat_end   = None   # set later from next file's flat_start

    return flat_start, flat_end, dark_mean, n_proj


# ---------------------------------------------------------------------------
# Per-file correction with interpolated flats (chunked)
# ---------------------------------------------------------------------------

def correct_and_append(path, flat_start, flat_end, dark_mean,
                        out_ds, write_offset, theta_list, chunk_size,
                        dezinger_threshold=DEZINGER_THRESH):
    """
    Read projections from path, apply per-projection interpolated flat
    correction, NaN/Inf sanitisation, and dezingering, then write to
    out_ds starting at write_offset.

    Returns (n_proj, total_nan_inf_replaced, total_zingers_replaced).
    """
    total_bad   = 0
    total_zing  = 0

    with h5py.File(path, 'r') as f:
        proj_ds = f[DS_PROJ]
        n_proj, height, width = proj_ds.shape

        # theta
        if DS_THETA in f:
            theta_list.extend(f[DS_THETA][:].tolist())
        else:
            print(f'  WARNING: no theta in {path}')

        # interpolation weights: 0 at first projection, 1 at last
        weights = np.linspace(0.0, 1.0, n_proj, dtype=np.float32) if n_proj > 1 \
                  else np.zeros(1, dtype=np.float32)

        for chunk_start in range(0, n_proj, chunk_size):
            chunk_end  = min(chunk_start + chunk_size, n_proj)

            proj_chunk = proj_ds[chunk_start:chunk_end].astype(np.float32)
            w3         = weights[chunk_start:chunk_end, np.newaxis, np.newaxis]

            # per-projection interpolated flat  (chunk, H, W)
            flat_interp = (1.0 - w3) * flat_start + w3 * flat_end

            # subtract dark
            if dark_mean is not None:
                proj_chunk  -= dark_mean
                flat_interp -= dark_mean

            # safe divide — replace zero denominator with 1 to avoid ±Inf
            denom     = np.where(flat_interp == 0.0, 1.0, flat_interp)
            corrected = proj_chunk / denom

            # --- NaN / Inf sanitisation ------------------------------------
            bad_mask = ~np.isfinite(corrected)
            n_bad    = int(bad_mask.sum())
            if n_bad:
                corrected[bad_mask] = 0.0
                total_bad += n_bad

            # clip to [0, ∞)
            np.clip(corrected, 0.0, None, out=corrected)

            # --- dezinger the whole chunk at once --------------------------
            if dezinger_threshold is not None:
                corrected, n_zing = dezinger_chunk(
                    corrected, radius=DEZINGER_RADIUS, threshold=dezinger_threshold
                )
                total_zing += n_zing

            out_ds[write_offset + chunk_start : write_offset + chunk_end] = corrected

    return n_proj, total_bad, total_zing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('files', nargs='*',
                    help='Input HDF5 files in scan order (positional)')
    ap.add_argument('--glob', metavar='PATTERN',
                    help='Glob pattern for input files (sorted by name)')
    ap.add_argument('--output', '-o', required=True,
                    help='Output HDF5 file')
    ap.add_argument('--chunk', type=int, default=DEFAULT_CHUNK,
                    help=f'Projections per processing chunk (default: {DEFAULT_CHUNK})')
    ap.add_argument('--dezinger-threshold', type=float, default=DEZINGER_THRESH,
                    metavar='SIGMA',
                    help='MAD-sigma threshold for zinger detection '
                         f'(default: {DEZINGER_THRESH}; higher = less aggressive)')
    ap.add_argument('--no-dezinger', action='store_true',
                    help='Disable dezingering')
    ap.add_argument('--dry-run', action='store_true',
                    help='Print plan and exit without writing')
    args = ap.parse_args()

    # ---- collect files -----------------------------------------------------
    input_files = list(args.files)
    if args.glob:
        input_files += sorted(glob_module.glob(args.glob))
    seen = set()
    input_files = [p for p in input_files if not (p in seen or seen.add(p))]

    if len(input_files) < 1:
        ap.error('No input files specified.')

    for p in input_files:
        if not os.path.exists(p):
            print(f'ERROR: not found: {p}', file=sys.stderr)
            sys.exit(1)

    n_files = len(input_files)

    # ---- load all reference flats and darks --------------------------------
    print('\nLoading flat/dark references ...')
    flat_starts = []
    flat_ends   = []
    dark_means  = []
    n_projs     = []

    for i, path in enumerate(input_files):
        is_last = (i == n_files - 1)
        
        fs, fe, dm, np_ = load_flat_refs(path, is_last)
        flat_starts.append(fs)
        flat_ends.append(fe)
        dark_means.append(dm)
        n_projs.append(np_)

    # Fill in flat_end for non-last files: flat_end[i] = flat_start[i+1]
    for i in range(n_files - 1):
        if flat_starts[i + 1] is None:
            print(f'WARNING: file {i+1} has no flat fields — '
                  f'using flat_start of file {i} for extrapolation')
            flat_ends[i] = flat_starts[i]
        else:
            flat_ends[i] = flat_starts[i + 1]

    # ---- inventory ---------------------------------------------------------
    print(f'\n{"#":<4} {"File":<55} {"proj":>6} {"n_flat ref":>12}')
    print('-' * 80)
    total_proj   = 0
    first_shape  = None
    for i, path in enumerate(input_files):
        is_last = (i == n_files - 1)
        mode = 'Both (split)' if is_last else 'Start→next'
        print(f'{i:<4} {os.path.basename(path):<55} {n_projs[i]:>6}  {mode}')
        total_proj += n_projs[i]
        if first_shape is None and n_projs[i] > 0:
            with h5py.File(path, 'r') as f:
                first_shape = f[DS_PROJ].shape[1:]

    print('-' * 80)
    print(f'     {"TOTAL":<55} {total_proj:>6}')
    print(f'Image shape  : {first_shape}')
    print(f'Output       : {args.output}')
    print(f'Chunk size   : {args.chunk} projections')
    dezinger_info = 'disabled' if args.no_dezinger else f'radius={DEZINGER_RADIUS}, threshold={args.dezinger_threshold} sigma'
    print(f'Dezinger     : {dezinger_info}\n')

    if args.dry_run:
        print('Dry run — exiting without writing.')
        return

    if first_shape is None:
        print('ERROR: no projection data found.', file=sys.stderr)
        sys.exit(1)

    # Sanity check: ensure every file has both reference flats
    for i in range(n_files):
        if flat_starts[i] is None or flat_ends[i] is None:
            print(f'ERROR: file {i} ({input_files[i]}) is missing flat field data.',
                  file=sys.stderr)
            sys.exit(1)

    # ---- create output file ------------------------------------------------
    print(f'Creating {args.output} ...')
    with h5py.File(args.output, 'w') as fout:
        proj_out = fout.create_dataset(
            DS_PROJ,
            shape=(total_proj, *first_shape),
            dtype=np.float32,
            chunks=(1, *first_shape),
        )

        theta_all    = []
        write_offset = 0

        for i, path in enumerate(input_files):
            print(f'[{i+1}/{n_files}] {os.path.basename(path)} '
                  f'({n_projs[i]} proj) ...', flush=True)
            n, n_bad, n_zing = correct_and_append(
                path,
                flat_start          = flat_starts[i],
                flat_end            = flat_ends[i],
                dark_mean           = dark_means[i],
                out_ds              = proj_out,
                write_offset        = write_offset,
                theta_list          = theta_all,
                chunk_size          = args.chunk,
                dezinger_threshold  = None if args.no_dezinger else args.dezinger_threshold,
            )
            write_offset += n
            warn_bad  = f'  *** {n_bad} NaN/Inf pixels replaced with 0' if n_bad  else ''
            warn_zing = f'  *** {n_zing} zinger pixels replaced'         if n_zing else ''
            print(f'         done  (running total: {write_offset}){warn_bad}{warn_zing}')

        # theta
        if theta_all:
            fout.create_dataset(DS_THETA,
                                data=np.array(theta_all, dtype=np.float64))
            print(f'\nTheta: {len(theta_all)} angles, '
                  f'{theta_all[0]:.3f} → {theta_all[-1]:.3f} deg')

        # dummy flat (ones) and dark (zeros) — data is already corrected
        fout.create_dataset(DS_FLAT, data=np.ones((1, *first_shape), dtype=np.float32))
        fout.create_dataset(DS_DARK, data=np.zeros((1, *first_shape), dtype=np.float32))

    size_mb = os.path.getsize(args.output) / 1024 ** 2
    print(f'\nDone. {args.output}  ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()
