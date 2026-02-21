#!/usr/bin/env python
"""
Periodic image acquisition script.
- Configures camera for 10 images per trigger (Multiple mode).
- Triggers acquisition every 60 seconds.
- Stops on Ctrl-C or when APS current drops below 100 mA.
"""

import epics
import time
import signal
import sys

# --- Configuration ---
ACQUIRE_PV = "2bmSP1:cam1:Acquire"
IMAGE_MODE_PV = "2bmSP1:cam1:ImageMode"
NUM_IMAGES_PV = "2bmSP1:cam1:NumImages"
CURRENT_PV = "S-DCCT:CurrentM"
CURRENT_THRESHOLD = 100.0  # mA
ACQUISITION_INTERVAL = 60  # seconds
IMAGES_PER_SET = 10

# --- Global flag for clean shutdown ---
running = True


def signal_handler(sig, frame):
    """Handle Ctrl-C gracefully."""
    global running
    print("\n\nCtrl-C received. Stopping acquisition loop...")
    running = False


def main():
    global running

    # Register the Ctrl-C handler
    signal.signal(signal.SIGINT, signal_handler)

    # Connect to PVs
    print("Connecting to PVs...")
    pv_acquire = epics.PV(ACQUIRE_PV)
    pv_image_mode = epics.PV(IMAGE_MODE_PV)
    pv_num_images = epics.PV(NUM_IMAGES_PV)
    pv_current = epics.PV(CURRENT_PV)

    # Wait for connections
    if not pv_acquire.wait_for_connection(timeout=10):
        print(f"ERROR: Could not connect to {ACQUIRE_PV}")
        sys.exit(1)
    if not pv_image_mode.wait_for_connection(timeout=10):
        print(f"ERROR: Could not connect to {IMAGE_MODE_PV}")
        sys.exit(1)
    if not pv_num_images.wait_for_connection(timeout=10):
        print(f"ERROR: Could not connect to {NUM_IMAGES_PV}")
        sys.exit(1)
    if not pv_current.wait_for_connection(timeout=10):
        print(f"ERROR: Could not connect to {CURRENT_PV}")
        sys.exit(1)

    print(f"Connected to all PVs.")

    # --- Configure camera ---
    print("Configuring camera...")
    pv_image_mode.put(1, wait=True)       # Multiple mode
    pv_num_images.put(IMAGES_PER_SET, wait=True)  # 10 images per trigger
    time.sleep(0.5)

    # Verify settings
    mode = pv_image_mode.get()
    num = pv_num_images.get()
    print(f"  ImageMode:  {mode} (1 = Multiple)")
    print(f"  NumImages:  {num}")
    if mode != 1 or num != IMAGES_PER_SET:
        print("ERROR: Camera configuration did not apply correctly.")
        sys.exit(1)
    print("Camera configured successfully.\n")

    print(f"Acquisition interval: {ACQUISITION_INTERVAL} s")
    print(f"Current threshold:    {CURRENT_THRESHOLD} mA")
    print(f"Images per set:       {IMAGES_PER_SET}")
    print("Press Ctrl-C to stop.\n")

    set_number = 0

    while running:
        # --- Check beam current ---
        current = pv_current.get()
        if current is None:
            print("WARNING: Could not read beam current. Retrying in 5 s...")
            time.sleep(5)
            continue

        if current < CURRENT_THRESHOLD:
            print(f"Beam current is {current:.4f} mA (below {CURRENT_THRESHOLD} mA). "
                  f"Stopping acquisition.")
            break

        # --- Check that camera is not already acquiring ---
        acq_status = pv_acquire.get()
        if acq_status == 1:
            print("WARNING: Camera is still acquiring. Waiting for it to finish...")
            while pv_acquire.get() == 1 and running:
                time.sleep(0.5)
            if not running:
                break

        # --- Trigger acquisition ---
        file_start = set_number * IMAGES_PER_SET
        file_end = file_start + IMAGES_PER_SET - 1
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Set {set_number}: Triggering acquisition "
              f"(flat_{file_start:03d}.tiff - flat_{file_end:03d}.tiff) | "
              f"Current: {current:.4f} mA")

        pv_acquire.put(1)

        # Wait for acquisition to complete
        time.sleep(0.5)  # small delay to let the PV update
        while pv_acquire.get() == 1 and running:
            # Also check current while waiting
            current = pv_current.get()
            if current is not None and current < CURRENT_THRESHOLD:
                print(f"Beam current dropped to {current:.4f} mA during acquisition. "
                      f"Stopping.")
                running = False
                break
            time.sleep(0.5)

        if not running:
            break

        set_number += 1

        # --- Wait for the next acquisition interval ---
        # Use small sleep increments so we can respond to Ctrl-C promptly
        print(f"  Acquisition complete. Waiting {ACQUISITION_INTERVAL} s "
              f"until next trigger...")
        wait_start = time.time()
        while running and (time.time() - wait_start) < ACQUISITION_INTERVAL:
            # Check current during wait
            current = pv_current.get()
            if current is not None and current < CURRENT_THRESHOLD:
                print(f"Beam current dropped to {current:.4f} mA. Stopping.")
                running = False
                break
            time.sleep(1)

    print(f"\nFinished. Total sets acquired: {set_number}")
    print("Exiting.")


if __name__ == "__main__":
    main()

