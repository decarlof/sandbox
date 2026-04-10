#!/usr/bin/env python3
"""
merge_intervals.py — flat-field-correct and merge tomoscan interval HDF5 files.

Each input file is corrected with its own dark and flat fields:

    corrected = (projection - dark_mean) / (flat_mean - dark_mean)

The corrected projections from all files are concatenated (in file order) into
a single output dataset along with the corresponding theta values.

Projections are processed in chunks so memory usage stays bounded even for
large (multi-GB) datasets.

Usage
-----
    # All files matching a glob, sorted by name:
    python merge_intervals.py --glob '/data/2024-10/sample_*.h5' --output merged.h5

    # Explicit file list (order matters):
    python merge_intervals.py file_001.h5 file_002.h5 file_003.h5 --output merged.h5

    # Dry run — print file inventory without writing:
    python merge_intervals.py --glob '*.h5' --output merged.h5 --dry-run
"""

import argparse
import glob as glob_module
import os
import sys
from datetime import datetime

import h5py
import numpy as np

# HDF5 exchange dataset paths (standard tomoscan layout)
DS_PROJ  = '/exchange/data'
DS_FLAT  = '/exchange/data_white'
DS_DARK  = '/exchange/data_dark'
DS_THETA = '/exchange/theta'

CHUNK_PROJ = 50   # projections processed at a time (tune for available RAM)


# ---------------------------------------------------------------------------
# Per-file helpers
# ---------------------------------------------------------------------------

def read_mean(f, path):
    """Return the mean image (float32) from an HDF5 dataset, or None if absent."""
    if path not in f:
        return None
    ds = f[path]
    if ds.shape[0] == 0:
        return None
    # read all frames and average
    return ds[:].astype(np.float32).mean(axis=0)


def file_inventory(path):
    """Return (n_proj, n_flat, n_dark, has_theta) for an HDF5 file."""
    with h5py.File(path, 'r') as f:
        n_proj  = f[DS_PROJ].shape[0]  if DS_PROJ  in f else 0
        n_flat  = f[DS_FLAT].shape[0]  if DS_FLAT  in f else 0
        n_dark  = f[DS_DARK].shape[0]  if DS_DARK  in f else 0
        has_th  = DS_THETA in f
    return n_proj, n_flat, n_dark, has_th


def correct_and_write(src_path, out_ds, theta_list, file_idx, n_files):
    """
    Open src_path, compute per-file dark/flat means, flat-field-correct all
    projections, and append them to the pre-allocated output dataset out_ds.

    theta_list  : list that will be extended with this file's theta values
    file_idx    : 0-based index of this file (used for offset into out_ds)
    Returns the number of projections written.
    """
    with h5py.File(src_path, 'r') as f:
        # --- dark and flat means ----------------------------------------
        dark_mean = read_mean(f, DS_DARK)
        flat_mean = read_mean(f, DS_FLAT)

        if flat_mean is None:
            print(f'  WARNING: no flat fields found in {src_path} — skipping correction')

        # --- theta ---------------------------------------------------------
        if DS_THETA in f:
            theta_list.extend(f[DS_THETA][:].tolist())
        else:
            print(f'  WARNING: no theta dataset in {src_path}')

        # --- projections (chunked) ----------------------------------------
        proj_ds = f[DS_PROJ]
        n_proj, height, width = proj_ds.shape
        offset = out_ds.attrs.get('_write_offset', 0)  # running write position

        for start in range(0, n_proj, CHUNK_PROJ):
            end   = min(start + CHUNK_PROJ, n_proj)
            chunk = proj_ds[start:end].astype(np.float32)

            if dark_mean is not None:
                chunk -= dark_mean

            if flat_mean is not None:
                denom = flat_mean if dark_mean is None else (flat_mean - dark_mean)
                # avoid division by zero
                denom = np.where(denom == 0, 1.0, denom)
                chunk /= denom

            np.clip(chunk, 0, None, out=chunk)
            out_ds[offset + start : offset + end] = chunk

        out_ds.attrs['_write_offset'] = offset + n_proj
        return n_proj


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('files', nargs='*',
                    help='Input HDF5 files (explicit list, in order)')
    ap.add_argument('--glob', metavar='PATTERN',
                    help='Glob pattern for input files (sorted by name)')
    ap.add_argument('--output', '-o', required=True,
                    help='Output HDF5 file path')
    ap.add_argument('--chunk-proj', type=int, default=CHUNK_PROJ,
                    help=f'Projections per processing chunk (default: {CHUNK_PROJ})')
    ap.add_argument('--dry-run', action='store_true',
                    help='Print inventory and exit without writing')
    args = ap.parse_args()

    global CHUNK_PROJ
    CHUNK_PROJ = args.chunk_proj

    # ---- collect input files -----------------------------------------------
    input_files = list(args.files)
    if args.glob:
        input_files += sorted(glob_module.glob(args.glob))

    if not input_files:
        ap.error('No input files specified (use positional args or --glob).')

    # deduplicate while preserving order
    seen = set()
    input_files = [p for p in input_files if not (p in seen or seen.add(p))]

    # ---- inventory ---------------------------------------------------------
    print(f'\n{"File":<60}  {"proj":>6}  {"flat":>6}  {"dark":>6}  {"theta"}')
    print('-' * 85)
    total_proj = 0
    first_shape = None
    for path in input_files:
        if not os.path.exists(path):
            print(f'ERROR: file not found: {path}', file=sys.stderr)
            sys.exit(1)
        n_proj, n_flat, n_dark, has_th = file_inventory(path)
        print(f'{path:<60}  {n_proj:>6}  {n_flat:>6}  {n_dark:>6}  {"yes" if has_th else "NO"}')
        total_proj += n_proj
        if first_shape is None and n_proj > 0:
            with h5py.File(path, 'r') as f:
                first_shape = f[DS_PROJ].shape[1:]   # (height, width)
    print('-' * 85)
    print(f'{"TOTAL":<60}  {total_proj:>6}  {"":>6}  {"":>6}')
    print(f'Image shape (height x width): {first_shape}')
    print(f'Output: {args.output}\n')

    if args.dry_run:
        print('Dry run — exiting without writing.')
        return

    if first_shape is None:
        print('ERROR: no projection data found in any input file.', file=sys.stderr)
        sys.exit(1)

    # ---- create output file ------------------------------------------------
    print(f'Creating output file: {args.output}')
    with h5py.File(args.output, 'w') as fout:
        # Pre-allocate the full projections dataset
        proj_out = fout.create_dataset(
            DS_PROJ,
            shape=(total_proj, *first_shape),
            dtype=np.float32,
            chunks=(1, *first_shape),
        )
        proj_out.attrs['_write_offset'] = 0

        theta_all = []
        n_files = len(input_files)

        for idx, path in enumerate(input_files):
            print(f'[{idx+1}/{n_files}] {os.path.basename(path)} ...', flush=True)
            n = correct_and_write(path, proj_out, theta_all, idx, n_files)
            print(f'         {n} projections written (running total: {proj_out.attrs["_write_offset"]})')

        # Remove internal write-offset attribute before closing
        del proj_out.attrs['_write_offset']

        # Write merged theta
        if theta_all:
            fout.create_dataset(DS_THETA, data=np.array(theta_all, dtype=np.float64))
            print(f'\nTheta dataset: {len(theta_all)} angles, '
                  f'{theta_all[0]:.3f} → {theta_all[-1]:.3f} deg')

    size_mb = os.path.getsize(args.output) / 1024**2
    print(f'\nDone. Output: {args.output}  ({size_mb:.1f} MB)')


if __name__ == '__main__':
    main()
