#!/usr/bin/env python3
"""
Generate an RST table summarizing runs and air handler status from a folder of HDF5 files.

Usage:
    python make_airhandler_table.py /path/to/folder > airhandler_table.rst
"""

import os
import sys

from meta.read_meta import Hdf5MetadataReader

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------
AIR_HANDLER_SUFFIXES = [
    "S01", "S03", "S05", "S07", "S09",
    "S11", "S13", "S15", "S17", "S19",
    "S21", "S23", "S25", "S27", "S29",
    "S31", "S33", "S35", "S37", "S39",
]

AIR_HANDLER_KEYS = [f"/air_handlers/AirHandler{s}" for s in AIR_HANDLER_SUFFIXES]

START_DATE_KEY = "/process/acquisition/start_date"


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def extract_run_and_fps_from_filename(fname: str):
    """
    From a file name like:
        S19-AHU509_1000frms_99fps_005.h5
    return:
        run = "S19-AHU509"
        fps_str = "99fps"
    """
    base = os.path.basename(fname)
    if base.lower().endswith(".h5"):
        base = base[:-3]

    parts = base.split("_")
    if len(parts) < 3:
        run = parts[0] if parts else base
        fps_str = "NA"
        return run, fps_str

    run = parts[0]

    fps_str = "NA"
    for p in parts:
        if "fps" in p:
            fps_str = p
            break

    return run, fps_str


def read_metadata(path: str):
    mp = Hdf5MetadataReader(path)
    meta_dict = mp.readMetadata()
    mp.close()
    return meta_dict


def get_meta_value(meta_dict, key, default=""):
    return meta_dict.get(key, default)


def _normalize_air_value(v):
    """
    Normalize an air handler metadata entry to a string "0"/"1" (or "" if unknown).

    Handles cases like:
        v = [np.int16(0), None]
        v = [0, None]
        v = np.int16(1)
        v = "0"
    """
    # If it's a list or tuple, take the first element
    if isinstance(v, (list, tuple)):
        if len(v) == 0:
            return ""
        v = v[0]

    if v is None:
        return ""

    try:
        # Try to coerce to int (works for np.int16, etc.)
        return str(int(v))
    except Exception:
        # Fallback: string representation
        return str(v).strip()


def _normalize_start_time(v):
    """
    Normalize start_time to a simple string.

    Handles cases like:
        v = ['2025-12-19T18:36:22-0600', None]
        v = '2025-12-19T18:36:22-0600'
    """
    if isinstance(v, (list, tuple)):
        if len(v) == 0:
            return ""
        v = v[0]
    if v is None:
        return ""
    return str(v).strip()


def collect_row_for_file(path: str):
    """
    Given the path to an HDF5 file, extract:
        - start_time
        - run (from file name)
        - fps_str (from file name)
        - air handler status list (in order of AIR_HANDLER_KEYS)
    """
    meta_dict = read_metadata(path)

    raw_start_time = get_meta_value(meta_dict, START_DATE_KEY, "")
    start_time = _normalize_start_time(raw_start_time)

    run, fps_str = extract_run_and_fps_from_filename(path)

    air_values = []
    for key in AIR_HANDLER_KEYS:
        v = get_meta_value(meta_dict, key, "")
        v_str = _normalize_air_value(v)
        air_values.append(v_str)

    return start_time, run, fps_str, air_values


# ----------------------------------------------------------------------
# RST table builders (each AH is its own column)
# ----------------------------------------------------------------------
def make_table_header():
    # Column names
    col_start = "start_time"
    col_run = "Run"
    col_fps = "Frame rate (name)"

    # Force widths so the borders match your desired example
    w_start = 24  # <- fixed to match "+------------------------+"
    w_run = max(len(col_run), 10)
    w_fps = max(len(col_fps), 18)
    w_ah = 3  # each air handler col width

    def border():
        parts = []
        parts.append("+" + "-" * w_start)
        parts.append("+" + "-" * w_run)
        parts.append("+" + "-" * w_fps)
        for _ in AIR_HANDLER_SUFFIXES:
            parts.append("+" + "-" * w_ah)
        parts.append("+")
        return "".join(parts)

    lines = []

    # Top border
    lines.append(border())
    # Header row with main titles
    header_cells = []
    header_cells.append("|" + col_start.center(w_start))
    header_cells.append("|" + col_run.center(w_run))
    header_cells.append("|" + col_fps.center(w_fps))
    for _ in AIR_HANDLER_SUFFIXES:
        header_cells.append("|" + "AH".center(w_ah))
    header_cells.append("|")
    lines.append("".join(header_cells))

    # Second header row with specific Sxx labels
    lines.append(border())
    label_cells = []
    label_cells.append("|" + " ".center(w_start))
    label_cells.append("|" + " ".center(w_run))
    label_cells.append("|" + " ".center(w_fps))
    for s in AIR_HANDLER_SUFFIXES:
        label_cells.append("|" + s.center(w_ah))
    label_cells.append("|")
    lines.append("".join(label_cells))

    # Header/data separator
    lines.append(border())

    return lines, w_start, w_run, w_fps, w_ah, border


def format_table_row(start_time, run, fps_str, air_values,
                     w_start, w_run, w_fps, w_ah):
    cells = []
    cells.append("|" + str(start_time).ljust(w_start))
    cells.append("|" + str(run).ljust(w_run))
    cells.append("|" + str(fps_str).ljust(w_fps))
    for v in air_values:
        cells.append("|" + str(v).center(w_ah))
    cells.append("|")
    return "".join(cells)


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------
def main(folder):
    files = [
        os.path.join(folder, f)
        for f in sorted(os.listdir(folder))
        if f.lower().endswith(".h5")
    ]

    if not files:
        print(f"No .h5 files found in {folder}", file=sys.stderr)
        sys.exit(1)

    header_lines, w_start, w_run, w_fps, w_ah, border = make_table_header()

    print("Vibration runs and air handler configuration")
    print("===========================================")
    print()
    print("The table below summarizes each run and the corresponding air handler status.")
    print("The frame rate is extracted from the file name (e.g. ``99fps``).")
    print()

    # Print header
    for line in header_lines:
        print(line)

    # Rows
    for path in files:
        try:
            start_time, run, fps_str, air_values = collect_row_for_file(path)
        except Exception as exc:
            print(f"# WARNING: could not read metadata for {path}: {exc}", file=sys.stderr)
            continue

        row = format_table_row(start_time, run, fps_str, air_values,
                               w_start, w_run, w_fps, w_ah)
        print(row)
        print(border())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python make_airhandler_table.py /path/to/folder", file=sys.stderr)
        sys.exit(1)

    main(sys.argv[1])