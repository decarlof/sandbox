from epics import PV, caget, caput
import re
import sys
import time
from datetime import datetime

# Globals
OPS_MESSAGE6_VALUE = None
DET_PVS = {}       # name -> PV
IMAGE_MODE_ENUMS = None  # list of enum strings for ImageMode


def sanitize_filename(name, max_length=255):
    name = name.strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^A-Za-z0-9._-]', '', name)
    if not name:
        name = "unnamed"
    return name[:max_length]


def read_ops_message6_once():
    global OPS_MESSAGE6_VALUE
    name_pv = "OPS:message6"

    val = caget(name_pv, timeout=5.0)
    print(f"[INIT] caget({name_pv!r}) -> {repr(val)}")

    if val is None:
        print(f"[INIT] WARNING: PV {name_pv} did not return a value; using 'unnamed'.",
              file=sys.stderr)
        OPS_MESSAGE6_VALUE = "unnamed"
    else:
        OPS_MESSAGE6_VALUE = str(val)


def connect_detector_pvs_once():
    """
    Create PV objects for detector/HDF, wait for connection,
    and load enum strings for ImageMode.
    """
    global DET_PVS, IMAGE_MODE_ENUMS

    detector_prefix = "2bmSP2:cam1:"
    hdf_prefix = "2bmSP2:HDF1:"

    pv_names = [
        detector_prefix + "NumImages",
        detector_prefix + "AcquireTime",
        detector_prefix + "ImageMode",
        detector_prefix + "Acquire",
        hdf_prefix + "FileName",
        hdf_prefix + "NumCapture",
        hdf_prefix + "Capture",
    ]

    DET_PVS = {name: PV(name) for name in pv_names}

    # Wait for connections (as in test_pv_connect.py)
    for i in range(20):  # ~2 seconds
        if all(pv.connected for pv in DET_PVS.values()):
            break
        time.sleep(0.1)

    print("[INIT] Detector/HDF PV connection status:")
    for name, pv in DET_PVS.items():
        print(f"  {name}: connected={pv.connected}")

    if not all(pv.connected for pv in DET_PVS.values()):
        print("[INIT] ERROR: one or more detector/HDF PVs are not connected.",
              file=sys.stderr)
        # Optionally abort here
        # sys.exit(1)

    # Fetch enum strings for ImageMode
    image_mode_pv = DET_PVS[detector_prefix + "ImageMode"]
    # Force a get of full control info (which includes enum strings)
    _ = image_mode_pv.get(as_string=True, timeout=2.0)
    IMAGE_MODE_ENUMS = image_mode_pv.enum_strs
    print("[INIT] ImageMode enum strings:", IMAGE_MODE_ENUMS)


def configure_and_arm_detector():
    """Configure camera + HDF plugin using cached OPS:message6, then arm and start."""
    if OPS_MESSAGE6_VALUE is None:
        print("Error: OPS_MESSAGE6_VALUE is not set; did init read fail?", file=sys.stderr)
        return

    if not DET_PVS:
        print("Error: DET_PVS is empty; did connect_detector_pvs_once() run?", file=sys.stderr)
        return

    if not all(pv.connected for pv in DET_PVS.values()):
        print("Error: some detector/HDF PVs are currently disconnected; aborting configure.",
              file=sys.stderr)
        for name, pv in DET_PVS.items():
            print(f"  {name}: connected={pv.connected}")
        return

    detector_prefix = "2bmSP2:cam1:"
    hdf_prefix = "2bmSP2:HDF1:"

    num_images = 1000
    acquire_time = 0.2

    raw_str = OPS_MESSAGE6_VALUE
    base_filename = sanitize_filename(raw_str)

    now_str = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    filename = f"{base_filename}_{now_str}"

    print("Using cached OPS:message6:", raw_str)
    print("Sanitized base name:      ", base_filename)
    print("Final filename:           ", filename)

    # PV names
    num_images_pv_name   = detector_prefix + "NumImages"
    acquire_time_pv_name = detector_prefix + "AcquireTime"
    image_mode_pv_name   = detector_prefix + "ImageMode"
    acquire_pv_name      = detector_prefix + "Acquire"
    hdf_filename_pv_name    = hdf_prefix + "FileName"
    hdf_num_capture_pv_name = hdf_prefix + "NumCapture"
    hdf_capture_pv_name     = hdf_prefix + "Capture"


    # Use same style as working interactive test
    caput(num_images_pv_name,   num_images,   wait=True, timeout=2)
    caput(acquire_time_pv_name, acquire_time, wait=True, timeout=2)
    caput(image_mode_pv_name,   "Multiple",   wait=True, timeout=2)

    caput(hdf_filename_pv_name,    filename,   wait=True, timeout=2)
    caput(hdf_num_capture_pv_name, num_images, wait=True, timeout=2)

    caput(hdf_capture_pv_name, 1, wait=True, timeout=2)  # Arm HDF
    caput(acquire_pv_name,     "Acquire", wait=True, timeout=2)  # Start acquisition

    print(f"Set {num_images_pv_name}      = {num_images}")
    print(f"Set {acquire_time_pv_name}    = {acquire_time}")
    print(f"Set {image_mode_pv_name}      = 'Multiple' (index {mode_index})")
    print(f"Set {hdf_filename_pv_name}    = '{filename}'")
    print(f"Set {hdf_num_capture_pv_name} = {num_images}")
    print(f"Armed {hdf_capture_pv_name}   = 1")
    print(f"Started {acquire_pv_name}     = 1")


def message_callback(pvname=None, value=None, **kwargs):
    if value is None:
        return

    val_str = str(value).strip()
    print(f"Monitor: {pvname} changed to '{val_str}'")

    if val_str.lower() == "start":
        print("Detected 'start' on trigger PV, configuring detector and starting acquisition...")
        configure_and_arm_detector()


def main():
    trigger_pv_name = "2bmb:TomoScan:UserBadge"

    read_ops_message6_once()
    connect_detector_pvs_once()

    def conn_callback(pvname=None, conn=None, **kws):
        print(f"Connection change: {pvname} connected={conn}")

    msg_pv = PV(trigger_pv_name,
                callback=message_callback,
                connection_callback=conn_callback)

    for _ in range(20):
        if msg_pv.connected:
            break
        time.sleep(0.1)

    if not msg_pv.connected:
        print(f"Error: could not connect to {trigger_pv_name}", file=sys.stderr)
        sys.exit(1)

    print(f"Connected to {trigger_pv_name}, monitoring for value 'start'...")
    print("Press Ctrl+C to exit.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nExiting monitor.")


if __name__ == "__main__":
    main()
