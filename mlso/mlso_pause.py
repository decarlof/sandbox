import os
from datetime import datetime
import argparse
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

TS_FORMAT = "%a %b %d %H:%M:%S GMT %Y"
TS_LEN = 28  # e.g. "Tue Nov 23 20:56:31 GMT 2021"


def read_log_file(filepath: str) -> str:
    with open(filepath, "r", encoding="windows-1252") as f:
        return f.read()


def calculate_pauses_within_file(log_content: str):
    """
    Return list of (pause_start_dt, pause_end_dt, duration_hours) for pairs
    found within the same file. Unclosed end-of-file pauses are ignored.
    """
    pause_start = None
    pauses = []

    for line in log_content.splitlines():
        if len(line) < TS_LEN:
            continue

        is_pause = "Paused for clouds" in line
        is_restart = "Restarted from pause" in line
        if not (is_pause or is_restart):
            continue

        try:
            t = datetime.strptime(line[:TS_LEN], TS_FORMAT)
        except ValueError:
            continue

        if is_pause:
            if pause_start is None:
                pause_start = t
        else:  # restart
            if pause_start is not None:
                hours = (t - pause_start).total_seconds() / 3600.0
                pauses.append((pause_start, t, hours))
                pause_start = None

    # discard any unclosed pause_start (end-of-day with no restart)
    return pauses


def plot_distribution(durations_hours, days_without_pauses, bin_minutes=10, x_tick_minutes=30):
    if not durations_hours and days_without_pauses == 0:
        print("Nothing to plot.")
        return

    fig, ax = plt.subplots(figsize=(9, 5))

    # Histogram with fixed 10-min bins
    if durations_hours:
        bin_w = bin_minutes / 60.0  # hours
        max_h = max(durations_hours)
        edges = np.arange(0, max_h + bin_w, bin_w)
        ax.hist(durations_hours, bins=edges, edgecolor="black")

    # Red "line" at 0 minutes = number of no-pause days
    if days_without_pauses > 0:
        ax.vlines(0, 0, days_without_pauses, colors="red", linewidth=4,
                  label=f"No-pause days (N={days_without_pauses})")

    ax.set_xlabel("Pause length")
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of UCoMP pause lengths (pause intervals N={len(durations_hours)})")
    ax.grid(axis="y", alpha=0.3)

    # ticks in minutes (same formatter you already have)
    step_hours = x_tick_minutes / 60.0
    ax.xaxis.set_major_locator(mticker.MultipleLocator(step_hours))

    def fmt_hours_as_hm(x, pos=None):
        total_minutes = int(round(x * 60))
        h, m = divmod(total_minutes, 60)
        if h == 0:
            return f"{m}m"
        if m == 0:
            return f"{h}h"
        return f"{h}h{m:02d}m"

    ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_hours_as_hm))

    ax.legend(loc="upper right")
    fig.tight_layout()
    plt.show()

def process_folder_print_and_collect(log_folder: str):
    log_files = sorted(
        f for f in os.listdir(log_folder)
        if f.startswith("mlso.") and f.endswith(".olog")
    )

    all_durations = []
    days_without_pauses = 0

    for filename in log_files:
        filepath = os.path.join(log_folder, filename)

        # Parse filename date: mlso.YYYYdDDD.olog
        try:
            year = int(filename[5:9])
            doy = int(filename[10:13])
            file_date = datetime.strptime(f"{year} {doy:03d}", "%Y %j").date()
        except Exception:
            continue

        log_content = read_log_file(filepath)
        pauses = calculate_pauses_within_file(log_content)

        if not pauses:
            days_without_pauses += 1
            continue

        print(f"\n{filename} ({file_date})")
        for start_dt, end_dt, hours in pauses:
            print(f"  UCoMP pause: {start_dt} -> {end_dt} ({hours:.2f} hours)")
            all_durations.append(hours)

    return all_durations, days_without_pauses


def main():
    parser = argparse.ArgumentParser(
        description="Print UCoMP pause intervals and plot the distribution of pause lengths."
    )
    parser.add_argument("directory", type=str, help="Directory containing mlso.YYYYdDDD.olog files")
    parser.add_argument("--bins", type=int, default=50, help="Histogram bins (default: 50)")
    parser.add_argument("--xtick-min", type=int, default=30, help="X tick spacing in minutes (default: 30)")
    args = parser.parse_args()

    durations, days_without_pauses = process_folder_print_and_collect(args.directory)
    print(f"\nFound {len(durations)} pause durations total.")
    print(f"Days (files) with zero pauses: {days_without_pauses}")

    plot_distribution(
        durations,
        days_without_pauses=days_without_pauses,
        bin_minutes=10,
        x_tick_minutes=args.xtick_min,
    )


if __name__ == "__main__":
    main()
