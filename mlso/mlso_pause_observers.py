import os
from datetime import datetime
import argparse
import numpy as np
from collections import defaultdict

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

TS_FORMAT = "%a %b %d %H:%M:%S GMT %Y"
TS_LEN = 28  # e.g. "Tue Nov 23 20:56:31 GMT 2021"


def read_log_file(filepath: str) -> str:
    with open(filepath, "r", encoding="windows-1252") as f:
        return f.read()


def extract_observer(log_content: str) -> str:
    for line in log_content.splitlines():
        if "Observer" not in line:
            continue

        if ":" in line:
            obs = line.split(":", 1)[1].strip()
            return obs if obs else "Unknown"
        if "=" in line:
            obs = line.split("=", 1)[1].strip()
            return obs if obs else "Unknown"

        tokens = line.split()
        if len(tokens) >= 2 and tokens[0].lower().startswith("observer"):
            obs = " ".join(tokens[1:]).strip()
            return obs if obs else "Unknown"

    return "Unknown"


def calculate_pauses_within_file(log_content: str):
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
        else:
            if pause_start is not None:
                hours = (t - pause_start).total_seconds() / 3600.0
                pauses.append((pause_start, t, hours))
                pause_start = None

    return pauses


def process_folder_group_by_observer(log_folder: str, max_pause_minutes: int):
    max_pause_h = max_pause_minutes / 60.0

    log_files = sorted(
        f for f in os.listdir(log_folder)
        if f.startswith("mlso.") and f.endswith(".olog")
    )

    durations_by_observer = defaultdict(list)
    no_pause_days_by_observer = defaultdict(int)

    for filename in log_files:
        filepath = os.path.join(log_folder, filename)
        log_content = read_log_file(filepath)
        observer = extract_observer(log_content)

        pauses = calculate_pauses_within_file(log_content)
        if not pauses:
            no_pause_days_by_observer[observer] += 1
            continue

        for _, __, hours in pauses:
            if hours < max_pause_h:
                durations_by_observer[observer].append(hours)

    return durations_by_observer, no_pause_days_by_observer


def plot_distributions_together(
    durations_by_obs,
    no_pause_by_obs,
    bin_minutes=1,
    x_tick_minutes=5,
    max_pause_minutes=30,
    title="Distribution of UCoMP pause lengths per observer",
):
    observers = sorted(set(durations_by_obs.keys()) | set(no_pause_by_obs.keys()))
    if not observers:
        print("Nothing to plot.")
        return

    # With 5 observers, a 2x3 grid works well
    n = len(observers)
    ncols = 3
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=(6 * ncols, 3.8 * nrows))
    axes = np.atleast_1d(axes).ravel()

    max_pause_h = max_pause_minutes / 60.0
    bin_w = bin_minutes / 60.0
    edges = np.arange(0, max_pause_h + bin_w, bin_w)

    step_hours = x_tick_minutes / 60.0

    def fmt_hours_as_hm(x, pos=None):
        total_minutes = int(round(x * 60))
        h, m = divmod(total_minutes, 60)
        if h == 0:
            return f"{m}m"
        if m == 0:
            return f"{h}h"
        return f"{h}h{m:02d}m"

    for i, obs in enumerate(observers):
        ax = axes[i]
        durs = [h for h in durations_by_obs.get(obs, []) if h < max_pause_h]
        no_pause = no_pause_by_obs.get(obs, 0)

        if durs:
            ax.hist(durs, bins=edges, edgecolor="black")

        # Optional: keep the same "no-pause days" indicator
        if no_pause > 0:
            ax.vlines(0, 0, no_pause, colors="red", linewidth=4)

        ax.set_title(f"{obs}\nN pauses<{max_pause_minutes}m={len(durs)}, no-pause days={no_pause}")
        ax.set_xlabel("Pause length")
        ax.set_ylabel("Count")
        ax.grid(axis="y", alpha=0.3)

        ax.set_xlim(0, max_pause_h)
        ax.xaxis.set_major_locator(mticker.MultipleLocator(step_hours))
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_hours_as_hm))

    for j in range(len(observers), len(axes)):
        axes[j].axis("off")

    fig.suptitle(title, y=1.02, fontsize=14)
    fig.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(
        description="Plot pause-length distributions for each observer in one multi-panel figure."
    )
    parser.add_argument("directory", type=str, help="Directory containing mlso.YYYYdDDD.olog files")
    parser.add_argument("--bin-min", type=int, default=1,
                        help="Histogram bin width in minutes (default: 1)")
    parser.add_argument("--xtick-min", type=int, default=5,
                        help="X tick spacing in minutes (default: 5)")
    parser.add_argument("--max-pause-min", type=int, default=30,
                        help="Only include pauses shorter than this (minutes). Default: 30")
    args = parser.parse_args()

    durations_by_obs, no_pause_by_obs = process_folder_group_by_observer(
        args.directory,
        max_pause_minutes=args.max_pause_min
    )

    plot_distributions_together(
        durations_by_obs,
        no_pause_by_obs,
        bin_minutes=args.bin_min,
        x_tick_minutes=args.xtick_min,
        max_pause_minutes=args.max_pause_min,
        title=f"Distribution of UCoMP pause lengths (<{args.max_pause_min} min) per observer",
    )


if __name__ == "__main__":
    main()
