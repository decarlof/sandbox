#!/usr/bin/env python3
"""
scan_intervals.py — scan projections over a sequence of angular intervals.

Splits [--start, --stop] into sub-scans of --interval degrees each.
For every sub-scan the script sets RotationStart / RotationStep / NumAngles
in the tomoscan IOC and then triggers StartScan (busy record), waiting for
completion before moving to the next interval.

Example — 3600 projections over 0–360° in 100° chunks:

    python scan_intervals.py

    python scan_intervals.py --prefix 2bmb:TomoScanFPGA: \\
                             --start 0 --stop 360 --total-angles 3600 \\
                             --interval 100

    python scan_intervals.py --dry-run   # print plan, no scans
"""

import argparse
import os
import time
from datetime import datetime

import epics
from tomoscan import log


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_PREFIX        = '2bmb:TomoScan:'
DEFAULT_TOTAL_ANGLES  = 7200
DEFAULT_START         = 0.0
DEFAULT_STOP          = 360.0
DEFAULT_INTERVAL      = 18.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def init_pvs(prefix):
    """Return a dict of connected epics.PV objects for the tomoscan IOC."""
    pvs = {
        'RotationStart'  : epics.PV(prefix + 'RotationStart'),
        'RotationStep'   : epics.PV(prefix + 'RotationStep'),
        'NumAngles'      : epics.PV(prefix + 'NumAngles'),
        'StartScan'      : epics.PV(prefix + 'StartScan'),
        'ScanStatus'     : epics.PV(prefix + 'ScanStatus'),
        'ServerRunning'  : epics.PV(prefix + 'ServerRunning'),
        'FlatFieldMode'  : epics.PV(prefix + 'FlatFieldMode'),
    }
    time.sleep(0.5)   # allow CA connections to establish
    return pvs


def build_intervals(total_start, total_stop, interval_size, total_angles):
    """Return (step_deg, list of (seg_start, seg_stop, n_angles)).

    The angular step is kept constant across all intervals so that the
    combined dataset has uniform angular sampling.
    """
    total_range = total_stop - total_start
    step = total_range / total_angles          # deg / projection

    intervals = []
    seg_start = total_start
    while seg_start < total_stop - 1e-9:
        seg_stop  = min(seg_start + interval_size, total_stop)
        n_angles  = round((seg_stop - seg_start) / step)
        intervals.append((seg_start, seg_stop, n_angles))
        seg_start = seg_stop

    return step, intervals


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument('--prefix',
                    default=DEFAULT_PREFIX,
                    help='Tomoscan IOC PV prefix  (default: %(default)s)')
    ap.add_argument('--total-angles', type=int,   default=DEFAULT_TOTAL_ANGLES,
                    help='Total projections across the full range  (default: %(default)s)')
    ap.add_argument('--start',        type=float, default=DEFAULT_START,
                    help='Full-range start angle in deg  (default: %(default)s)')
    ap.add_argument('--stop',         type=float, default=DEFAULT_STOP,
                    help='Full-range stop angle in deg   (default: %(default)s)')
    ap.add_argument('--interval',     type=float, default=DEFAULT_INTERVAL,
                    help='Angular size of each sub-scan in deg  (default: %(default)s)')
    ap.add_argument('--dry-run', action='store_true',
                    help='Print the interval plan and exit without running any scans')
    args = ap.parse_args()

    # ---- logging -----------------------------------------------------------
    logs_home = os.path.join(os.path.expanduser('~'), 'logs')
    os.makedirs(logs_home, exist_ok=True)
    lfname = os.path.join(
        logs_home,
        'scan_intervals_' + datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S') + '.log',
    )
    log.setup_custom_logger(lfname)

    # ---- build plan --------------------------------------------------------
    step, intervals = build_intervals(args.start, args.stop, args.interval, args.total_angles)

    log.info('Prefix        : %s', args.prefix)
    log.info('Full range    : [%.2f, %.2f] deg', args.start, args.stop)
    log.info('Total angles  : %d', args.total_angles)
    log.info('Angular step  : %.4f deg/proj', step)
    log.info('Interval size : %.2f deg', args.interval)
    log.info('Sub-scans     : %d', len(intervals))
    for i, (s, e, n) in enumerate(intervals):
        log.info('  [%d/%d]  start=%.3f  stop=%.3f  n_angles=%d',
                 i + 1, len(intervals), s, e, n)

    if args.dry_run:
        log.warning('Dry run — exiting without triggering any scans.')
        return

    # ---- connect PVs -------------------------------------------------------
    pvs = init_pvs(args.prefix)

    if not pvs['ServerRunning'].get():
        log.error('Server %s is not running. Aborting.', args.prefix)
        return

    status = pvs['ScanStatus'].get(as_string=True)
    if status != 'Scan complete':
        log.error('Server is busy (%s). Aborting.', status)
        return

    # ---- set step once — constant across all intervals ---------------------
    pvs['RotationStep'].put(step, wait=True)
    time.sleep(0.2)

    # ---- scan loop ---------------------------------------------------------
    tic_total = time.time()

    n_intervals = len(intervals)
    for idx, (seg_start, seg_stop, n_angles) in enumerate(intervals):
        is_last = (idx == n_intervals - 1)
        flat_mode = 'Both' if is_last else 'Start'

        log.warning('Interval %d/%d  [%.3f → %.3f] deg  %d angles  FlatFieldMode=%s',
                    idx + 1, n_intervals, seg_start, seg_stop, n_angles, flat_mode)

        pvs['FlatFieldMode'].put(flat_mode, wait=True)
        pvs['RotationStart'].put(seg_start, wait=True)
        pvs['NumAngles'].put(n_angles, wait=True)
        time.sleep(0.5)   # let RotationStop calc record settle

        log.info('  Triggering StartScan ...')
        tic = time.time()
        pvs['StartScan'].put(1, wait=True, timeout=360000)
        elapsed = (time.time() - tic) / 60.
        log.info('  Interval done in %.2f min', elapsed)

    total_elapsed = (time.time() - tic_total) / 60.
    log.warning('All %d intervals complete in %.2f min.', n_intervals, total_elapsed)


if __name__ == '__main__':
    main()
