#!/usr/bin/env python
"""
Periodic image acquisition script.
- Configures the TIFF plugin (enable, file name, counter, stream mode, capture).
- Configures camera for 10 images per trigger (Multiple mode).
- Triggers acquisition every 60 seconds.
- Stops on Ctrl-C or when APS current drops below 100 mA.
"""

import epics
import time
import signal
import sys

# --- Configuration ---
# Camera PVs
ACQUIRE_PV = "2bmSP1:cam1:Acquire"
IMAGE_MODE_PV = "2bmSP1:cam1:ImageMode"
NUM_IMAGES_PV = "2bmSP1:cam1:NumImages"

# TIFF plugin PVs
TIFF_PREFIX = "2bmSP1:TIFF1:"
TIFF_ENABLE_PV = TIFF_PREFIX + "EnableCallbacks"
TIFF_FILENAME_PV = TIFF_PREFIX + "FileName"
TIFF_FILE_NUMBER_PV = TIFF_PREFIX + "FileNumber"
TIFF_FILE_TEMPLATE_PV = TIFF_PREFIX + "FileTemplate"
TIFF_NUM_CAPTURE_PV = TIFF_PREFIX + "NumCapture"
TIFF_FILE_WRITE_MODE_PV = TIFF_PREFIX + "FileWriteMode"
TIFF_CAPTURE_PV = TIFF_PREFIX + "Capture"
TIFF_AUTO_INCREMENT_PV = TIFF_PREFIX + "AutoIncrement"
TIFF_AUTO_SAVE_PV = TIFF_PREFIX + "AutoSave"

# APS beam current PV
CURRENT_PV = "S-DCCT:CurrentM"

# Thresholds and timing
CURRENT_THRESHOLD = 100.0  # mA
ACQUISITION_INTERVAL = 60  # seconds
IMAGES_PER_SET = 10
TOTAL_CAPTURE_COUNT = 999999  # Very large number for NumCapture

# --- Global flag for clean shutdown ---
running = True


def signal_handler(sig, frame):
    """Handle Ctrl-C gracefully."""
    global running
    print("\n\nCtrl-C received. Stopping acquisition loop...")
    running = False


def connect_pv(pv_name, timeout=10):
    """Connect to a PV and exit on failure."""
    pv = epics.PV(pv_name)
    if not pv.wait_for_connection(timeout=timeout):
        print(f"ERROR: Could not connect to {pv_name}")
        sys.exit(1)
    return pv


def main():
    global running

    # Register the Ctrl-C handler
    signal.signal(signal.SIGINT, signal_handler)

    # =========================================================================
    # Connect to all PVs
    # =========================================================================
    print("Connecting to PVs...")

    # Camera PVs
    pv_acquire = connect_pv(ACQUIRE_PV)
    pv_image_mode = connect_pv(IMAGE_MODE_PV)
    pv_num_images = connect_pv(NUM_IMAGES_PV)

    # TIFF plugin PVs
    pv_tiff_enable = connect_pv(TIFF_ENABLE_PV)
    pv_tiff_filename = connect_pv(TIFF_FILENAME_PV)
    pv_tiff_file_number = connect_pv(TIFF_FILE_NUMBER_PV)
    pv_tiff_file_template = connect_pv(TIFF_FILE_TEMPLATE_PV)
    pv_tiff_num_capture = connect_pv(TIFF_NUM_CAPTURE_PV)
    pv_tiff_write_mode = connect_pv(TIFF_FILE_WRITE_MODE_PV)
    pv_tiff_capture = connect_pv(TIFF_CAPTURE_PV)
    pv_tiff_auto_increment = connect_pv(TIFF_AUTO_INCREMENT_PV)
    pv_tiff_auto_save = connect_pv(TIFF_AUTO_SAVE_PV)

    # Beam current PV
    pv_current = connect_pv(CURRENT_PV)

    print("Connected to all PVs.\n")

    # =========================================================================
    # Configure the TIFF plugin
    # =========================================================================
    print("Configuring TIFF plugin...")

    # 1. Enable the TIFF plugin callbacks
    #    0 = Disable, 1 = Enable
    pv_tiff_enable.put(1, wait=True)
    print(f"  EnableCallbacks:  1 (Enabled)")

    # 2. Set the file name to "flat"
    pv_tiff_filename.put("flat", wait=True)
    print(f"  FileName:         'flat'")

    # 3. Reset the file number counter to 0
    pv_tiff_file_number.put(0, wait=True)
    print(f"  FileNumber:       0")

    # 4. Use the default file template (e.g., "%s%s_%3.3d.tiff")
    #    This produces files like: <path>/flat_000.tiff, flat_001.tiff, ...
    default_template = "%s%s_%3.3d.tiff"
    pv_tiff_file_template.put(default_template, wait=True)
    print(f"  FileTemplate:     '{default_template}' (default)")

    # 5. Enable auto-increment so file number advances automatically
    pv_tiff_auto_increment.put(1, wait=True)
    print(f"  AutoIncrement:    1 (Yes)")

    # 6. Enable auto-save so each frame is written automatically
    pv_tiff_auto_save.put(1, wait=True)
    print(f"  AutoSave:         1 (Yes)")

    # 7. Set NumCapture to a very large number (total images across all sets)
    pv_tiff_num_capture.put(TOTAL_CAPTURE_COUNT, wait=True)
    print(f"  NumCapture:       {TOTAL_CAPTURE_COUNT}")

    # 8. Set FileWriteMode to Stream
    #    0 = Single, 1 = Capture, 2 = Stream
    pv_tiff_write_mode.put(2, wait=True)
    print(f"  FileWriteMode:    2 (Stream)")

    # 9. Press Capture to arm the TIFF plugin
    pv_tiff_capture.put(1, wait=True)
    print(f"  Capture:          1 (Armed)")

    time.sleep(0.5)
    print("TIFF plugin configured and armed.\n")

    # =========================================================================
    # Configure the camera
    # =========================================================================
    print("Configuring camera...")

    # Set ImageMode to Multiple (1)
    pv_image_mode.put(1, wait=True)
    # Set NumImages to 10
    pv_num_images.put(IMAGES_PER_SET, wait=True)
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

    # =========================================================================
    # Acquisition loop
    # =========================================================================
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

    # =========================================================================
    # Cleanup: stop the TIFF capture
    # =========================================================================
    print("\nDisarming TIFF plugin...")
    pv_tiff_capture.put(0, wait=True)
    print("TIFF plugin disarmed.")

    print(f"\nFinished. Total sets acquired: {set_number}")
    print("Exiting.")


if __name__ == "__main__":
    main()
