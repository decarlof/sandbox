import time
import re
import sys
import argparse
from epics import PV
from datetime import datetime

EPSILON = 0.1

DetectorIdle = 0
DetectorAcquire = 1

HDFIdle = 0
HDFCapture = 1

"""
This script:

- Configures an areadetector and HDF1 plugin once at startup:
  - Sets the number of images to acquire.
  - Sets the detector image mode to Multiple.
  - Sets the HDF1 plugin NumCapture to match the number of images.
  - Builds an HDF filename from a PV, e.g. OPS:message6 plus a timestamp.

- Then idles, monitoring a trigger PV e.g. OPS:message17.

- Each time the trigger PV changes to the string "start" (from any other value),
  the script starts exactly one data collection with the configured number of images.

- If the trigger PV remains "start", no additional collections are started.

- When the trigger PV changes to any value other than "start", the system re-arms
  and waits for the next transition to "start" to begin another collection.

- This cycle repeats indefinitely until the script is stopped (for example, with Ctrl-C).
"""

def wait_pv(pv, wait_val, max_timeout_sec=-1):

    # wait on a pv to be a value until max_timeout (default forever)
    # delay for pv to change
    time.sleep(.01)
    startTime = time.time()
    while True:
        pv_val = pv.get()
        if type(pv_val) == float:
            if abs(pv_val - wait_val) < EPSILON:
                return True
        if pv_val != wait_val:
            if max_timeout_sec > -1:
                curTime = time.time()
                diffTime = curTime - startTime
                if diffTime >= max_timeout_sec:
                    # log is not defined, so print to stderr
                    print('  *** ERROR: DROPPED IMAGES ***', file=sys.stderr)
                    print(
                        '  *** wait_pv(%s, %d, %5.2f) reached max timeout. Return False'
                        % (pv.pvname, wait_val, max_timeout_sec),
                        file=sys.stderr,
                    )
                    return False
            time.sleep(.01)
        else:
            return True


def init_general_PVs(aps_start_pv, aps_file_name_pv, detector_prefix):

    global_PVs = {}

    # aps PV
    global_PVs['APSStart']    = PV(aps_start_pv)
    global_PVs['APSFileName'] = PV(aps_file_name_pv)

    # detector pv's
    camera_prefix = detector_prefix + 'cam1:'

    global_PVs['CamManufacturer_RBV'] = PV(camera_prefix + 'Manufacturer_RBV')
    global_PVs['CamModel']            = PV(camera_prefix + 'Model_RBV')
    global_PVs['Cam1SerialNumber']    = PV(camera_prefix + 'SerialNumber_RBV')
    global_PVs['Cam1ImageMode']       = PV(camera_prefix + 'ImageMode')
    global_PVs['Cam1ArrayCallbacks']  = PV(camera_prefix + 'ArrayCallbacks')
    global_PVs['Cam1AcquirePeriod']   = PV(camera_prefix + 'AcquirePeriod')
    global_PVs['Cam1SoftwareTrigger'] = PV(camera_prefix + 'SoftwareTrigger')
    global_PVs['Cam1AcquireTime']     = PV(camera_prefix + 'AcquireTime')
    global_PVs['Cam1FrameType']       = PV(camera_prefix + 'FrameType')
    global_PVs['Cam1AttributeFile']   = PV(camera_prefix + 'NDAttributesFile')
    global_PVs['Cam1SizeX']           = PV(camera_prefix + 'SizeX')
    global_PVs['Cam1SizeY']           = PV(camera_prefix + 'SizeY')
    global_PVs['Cam1NumImages']       = PV(camera_prefix + 'NumImages')
    global_PVs['Cam1TriggerMode']     = PV(camera_prefix + 'TriggerMode')
    global_PVs['Cam1Acquire']         = PV(camera_prefix + 'Acquire')
    global_PVs['Cam1SizeX_RBV']       = PV(camera_prefix + 'SizeX_RBV')
    global_PVs['Cam1SizeY_RBV']       = PV(camera_prefix + 'SizeY_RBV')
    global_PVs['Cam1MaxSizeX_RBV']    = PV(camera_prefix + 'MaxSizeX_RBV')
    global_PVs['Cam1MaxSizeY_RBV']    = PV(camera_prefix + 'MaxSizeY_RBV')
    global_PVs['Cam1PixelFormat_RBV'] = PV(camera_prefix + 'PixelFormat_RBV')

    image_prefix = detector_prefix + 'image1:'
    global_PVs['Image']       = PV(image_prefix + 'ArrayData')
    global_PVs['Cam1Display'] = PV(image_prefix + 'EnableCallbacks')

    manufacturer = global_PVs['CamManufacturer_RBV'].get(as_string=True)
    model        = global_PVs['CamModel'].get(as_string=True)

    if model in ('Oryx ORX-10G-51S5M', 'Oryx ORX-10G-310S9M'):
        global_PVs['Cam1AcquireTimeAuto']   = PV(camera_prefix + 'AcquireTimeAuto')
        global_PVs['Cam1FrameRateOnOff']    = PV(camera_prefix + 'FrameRateEnable')
        global_PVs['Cam1TriggerSource']     = PV(camera_prefix + 'TriggerSource')
        global_PVs['Cam1TriggerOverlap']    = PV(camera_prefix + 'TriggerOverlap')
        global_PVs['Cam1ExposureMode']      = PV(camera_prefix + 'ExposureMode')
        global_PVs['Cam1TriggerSelector']   = PV(camera_prefix + 'TriggerSelector')
        global_PVs['Cam1TriggerActivation'] = PV(camera_prefix + 'TriggerActivation')
    else:
        print('Detector %s model %s is not supported' % (manufacturer, model),
              file=sys.stderr)
        return None

    hdf_plugin_prefix = detector_prefix + 'HDF1:'
    global_PVs['FPFullFileNameRBV'] = PV(hdf_plugin_prefix + 'FullFileName_RBV')
    global_PVs['FileName']          = PV(hdf_plugin_prefix + 'FileName')
    global_PVs['NumCapture']        = PV(hdf_plugin_prefix + 'NumCapture')
    global_PVs['Capture']           = PV(hdf_plugin_prefix + 'Capture')

    return global_PVs


def sanitize_filename(name, max_length=255):
    name = name.strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^A-Za-z0-9._-]', '', name)
    if not name:
        name = "unnamed"
    return name[:max_length]


def init_detector(global_PVs, n_images):
    print(' ')
    print('  *** init FLIR camera')
    print('  *** *** set detector to idle')
    global_PVs['Cam1Acquire'].put(DetectorIdle)
    wait_pv(global_PVs['Cam1Acquire'], DetectorIdle, 2)
    print('  *** *** set detector to idle:  Done')
    time.sleep(0.1)
    print('  *** *** set trigger mode to Off')
    global_PVs['Cam1TriggerMode'].put('Off', wait=True)
    print('  *** *** set trigger mode to Off: done')
    time.sleep(0.1)
    print('  *** *** set image mode to Multiple')
    global_PVs['Cam1ImageMode'].put('Multiple', wait=True)
    print('  *** *** set image mode to Multiple: done')
    time.sleep(0.1)
    print('  *** *** set Cam1NumImages')
    global_PVs['Cam1NumImages'].put(n_images, wait=True)
    print('  *** *** set Cam1NumImage to %d' % n_images)
    time.sleep(0.1)
    print('  *** *** set cam display to 1')
    global_PVs['Cam1Display'].put(1)
    print('  *** *** set cam display to 1: done')
    time.sleep(0.1)
    print('  *** *** set cam acquire')


def arm_hdf_plugin(global_PVs, n_images):

    print(' ')
    print('  *** init HDF plugin')
    print('  *** *** set HDF plugin to Done')
    global_PVs['Capture'].put(HDFIdle, wait=True)
    print('  *** *** set HDF plugin to Done:  Done')
    time.sleep(0.1)
    print('  *** *** set HDF NumCapture')
    global_PVs['NumCapture'].put(n_images, wait=True)
    print('  *** *** set HDF NumCapture to %d' % n_images)
    time.sleep(0.1)

    raw_str = global_PVs['APSFileName'].get()
    base_filename = sanitize_filename(raw_str)
    now_str = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    filename = f"{base_filename}_{now_str}"
    global_PVs['FileName'].put(filename)
    time.sleep(0.1)
    print('  *** *** arm HDF plugin')
    global_PVs['Capture'].put(HDFCapture)
    wait_pv(global_PVs['Capture'], HDFCapture, 2)
    print('  *** *** HDF plugin: armed')


def parse_args():
    parser = argparse.ArgumentParser(
        description="Configure 2bmSP2 detector, HDF plugin, and start on APS start PV."
    )
    parser.add_argument(
        "--aps-start-pv",
        default="OPS:message17",
        help="PV to monitor for start command (default: OPS:message17)",
    )
    parser.add_argument(
        "--aps-filename-pv",
        default="OPS:message6",
        help="PV providing base filename (default: OPS:message6)",
    )
    parser.add_argument(
        "--detector-prefix",
        default="2bmSP2:",
        help="Detector prefix (default: 2bmSP2:)",
    )
    parser.add_argument(
        "--number-of-images",
        type=int,
        default=10,
        help="Number of images to acquire (default: 10)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    print("Using parameters:")
    print(f"  APS start PV     : {args.aps_start_pv}")
    print(f"  APS filename PV  : {args.aps_filename_pv}")
    print(f"  Detector prefix  : {args.detector_prefix}")
    print(f"  Number of images : {args.number_of_images}")

    pv = init_general_PVs(
        args.aps_start_pv,
        args.aps_filename_pv,
        args.detector_prefix,
    )
    if pv is None:
        sys.exit(1)

    # Initialize once at startup
    init_detector(pv, args.number_of_images)

    # Edge-triggered monitoring:
    # Only trigger when APSStart transitions from non-start -> start.
    print('  *** monitoring APSStart for start command ...')
    try:
        last_is_start = False
        while True:
            val = pv['APSStart'].get(as_string=True)
            if val is not None:
                val_str = str(val).strip()
                is_start = (val_str.lower() == 'start')

                # Detect rising edge: was not start, now is start
                if is_start and not last_is_start:
                    print('  *** APSStart changed to "start": arming HDF plugin')
                    arm_hdf_plugin(pv, args.number_of_images)
                    print('  *** APSStart changed to "start": starting acquisition')
                    pv['Cam1Acquire'].put(DetectorAcquire)
                    wait_pv(pv['Cam1Acquire'], DetectorAcquire, 2)
                    print('  *** *** set cam acquire: done')
                    print('  *** acquisition complete, returning to idle monitoring')

                last_is_start = is_start

            time.sleep(0.1)
    except KeyboardInterrupt:
        print('\n  *** monitoring stopped by user')


if __name__ == "__main__":
    main()
