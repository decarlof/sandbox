import argparse
import os
import csv
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def read_summary_csv(csv_path):
    """Read summary.csv and return a list of rows:
       (file, fps, start_date, vent_peak, res_peak)
    """
    rows = []
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fname = row.get("file", "")
            # fps may be missing or non-numeric
            fps_str = row.get("fps", "")
            try:
                fps = float(fps_str)
            except (TypeError, ValueError):
                fps = float("nan")

            start_date = row.get("start_date", "")
            vent_str = row.get("vent_peak", "")
            res_str = row.get("res_peak", "")

            try:
                vent_peak = float(vent_str)
            except (TypeError, ValueError):
                vent_peak = float("nan")

            try:
                res_peak = float(res_str)
            except (TypeError, ValueError):
                res_peak = float("nan")

            rows.append((fname, fps, start_date, vent_peak, res_peak))
    return rows


def print_summary_table(summary_rows):
    print("\n====================== Summary table ======================")
    print(
        "{:<40s} {:>10s} {:>22s} {:>18s} {:>22s}".format(
            "file",
            "fps",
            "start_date",
            "Peak [25.0, 35.0] Hz",
            "Peak [35.0,100.0] Hz",
        )
    )
    print("-" * 120)
    for fname, fps, start_date, vent_peak, res_peak in summary_rows:
        start_str = "" if start_date is None else str(start_date).strip()
        print(
            "{:<40s} {:>10.1f} {:>22s} {:>18.3f} {:>22.3f}".format(
                fname, fps, start_str, vent_peak, res_peak
            )
        )
    print("===========================================================\n")


def plot_peaks_vs_time(summary_rows, title_suffix=""):
    times = []
    vent_peaks = []
    res_peaks = []

    for _, fps, start_date, vent_peak, res_peak in summary_rows:
        start_str = str(start_date).strip()
        if not start_str:
            continue

        # Normalize timezone: '...-0600' -> '...-06:00'
        if len(start_str) >= 5 and start_str[-5] in ["+", "-"] and start_str[-3] != ":":
            start_str = start_str[:-2] + ":" + start_str[-2:]

        # Accept space instead of 'T'
        if "T" not in start_str and " " in start_str:
            start_str = start_str.replace(" ", "T")

        try:
            dt = datetime.fromisoformat(start_str)
        except ValueError:
            continue

        times.append(dt)
        vent_peaks.append(vent_peak)
        res_peaks.append(res_peak)

    if not times:
        print("No valid start_date values to plot.\n")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(times, vent_peaks, "-o", label="Peak [25.0, 35.0] Hz")
    ax.plot(times, res_peaks, "-o", label="Peak [35.0,100.0] Hz")

    ax.set_xlabel("Start date/time")
    ax.set_ylabel("Frequency [Hz]")
    base_title = "Vibration peaks vs acquisition start time"
    if title_suffix:
        ax.set_title(f"{base_title} ({title_suffix})")
    else:
        ax.set_title(base_title)
    ax.legend()

    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d\n%H:%M"))
    fig.autofmt_xdate()

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot vibration summary from a CSV file produced by frequency_folder.py"
    )
    parser.add_argument(
        "folder",
        type=str,
        help="Folder containing summary.csv (e.g. /path/to/test_01_partial).",
    )
    parser.add_argument(
        "--summary_csv",
        type=str,
        default="summary.csv",
        help="Name of the CSV file (default: summary.csv).",
    )
    parser.add_argument(
        "--no_table",
        action="store_true",
        help="Do not print the summary table, only plot.",
    )
    parser.add_argument(
        "--only_band",
        choices=["vent", "res", "both"],
        default="both",
        help="Future option: choose which band to plot (currently both).",
    )

    args = parser.parse_args()

    csv_path = os.path.join(args.folder, args.summary_csv)
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        return

    summary_rows = read_summary_csv(csv_path)

    if not args.no_table:
        print_summary_table(summary_rows)

    plot_peaks_vs_time(summary_rows)


if __name__ == "__main__":
    main()