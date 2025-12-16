import time
import re
import sys
import argparse
import logging

from epics import PV
from datetime import datetime

EPSILON = 0.1

DetectorIdle       = 0
DetectorAcquire    = 1

FilePluginIdle     = 0
WritePluginCapture = 1

StartCommand       = 'Acquire'


"""
This script:

- Configures an areadetector and write plugin once at startup:
  - Sets the number of images to acquire.
  - Sets the detector image mode to Multiple.
  - Sets the TIFF1/HDF1 plugin NumCapture to match the number of images.
  - Builds an TIFF/HDF filename from a PV, e.g. OPS:message6 plus a timestamp.

- Then idles, monitoring a trigger PV e.g. OPS:message17.

- Each time the trigger PV changes to the string "start" (from any other value),
  the script starts exactly one data collection with the configured number of images.

- If the trigger PV remains "start", no additional collections are started.

- When the trigger PV changes to any value other than "start", the system re-arms
  and waits for the next transition to "start" to begin another collection.

- This cycle repeats indefinitely until the script is stopped (for example, with Ctrl-C).
"""

logger = logging.getLogger(__name__)

def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)

def setup_custom_logger(lfname=None, stream_to_console=True):

    logger.setLevel(logging.DEBUG)

    if (lfname != None):
        fHandler = logging.FileHandler(lfname)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
        fHandler.setFormatter(file_formatter)
        logger.addHandler(fHandler)
    if stream_to_console:
        ch = logging.StreamHandler()
        ch.setFormatter(ColoredLogFormatter('%(asctime)s - %(message)s'))
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)

class ColoredLogFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None, style='%'):
        # Logging defines
        self.__GREEN = "\033[92m"
        self.__RED = '\033[91m'
        self.__YELLOW = '\033[33m'
        self.__ENDC = '\033[0m'
        super().__init__(fmt, datefmt, style)
    
    
    def formatMessage(self,record):
        if record.levelname=='INFO':
            record.message = self.__GREEN + record.message + self.__ENDC
        elif record.levelname == 'WARNING':
            record.message = self.__YELLOW + record.message + self.__ENDC
        elif record.levelname == 'ERROR':
            record.message = self.__RED + record.message + self.__ENDC
        return super().formatMessage(record)

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
                    error('ERROR: dropped images')
                    error(
                        'wait_pv(%s, %d, %5.2f) timed out; returning False'
                        % (pv.pvname, wait_val, max_timeout_sec)
                    )
                    return False
            time.sleep(.01)
        else:
            return True


def init_general_PVs(aps_start_pv, aps_file_name_pv, detector_prefix, file_format):

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
    global_PVs['Cam1ArrayRate_RBV']   = PV(camera_prefix + 'ArrayRate_RBV')

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
        error('Detector %s (model %s) is not supported' % (manufacturer, model))
        return None

    if file_format == "hdf":
        plugin_prefix = detector_prefix + 'HDF1:'
    else:
        plugin_prefix = detector_prefix + 'TIFF1:'

    global_PVs['FPFullFileNameRBV'] = PV(plugin_prefix + 'FullFileName_RBV')
    global_PVs['FileName']          = PV(plugin_prefix + 'FileName')
    global_PVs['NumCapture']        = PV(plugin_prefix + 'NumCapture')
    global_PVs['Capture']           = PV(plugin_prefix + 'Capture')

    return global_PVs


def sanitize_filename(name, max_length=255):
    name = name.strip()
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'[^A-Za-z0-9._-]', '', name)
    if not name:
        name = "unnamed"
    return name[:max_length]


def init_detector(global_PVs, n_images):
    info('')
    info('Init FLIR camera')
    info('  Setting detector to Idle')
    global_PVs['Cam1Acquire'].put(DetectorIdle)
    wait_pv(global_PVs['Cam1Acquire'], DetectorIdle, 2)
    info('  Detector is Idle')
    time.sleep(0.1)
    info('  Setting trigger mode to Off')
    global_PVs['Cam1TriggerMode'].put('Off', wait=True)
    info('  Trigger mode is Off')
    time.sleep(0.1)
    info('  Setting image mode to Multiple')
    global_PVs['Cam1ImageMode'].put('Multiple', wait=True)
    info('  Image mode is Multiple')
    time.sleep(0.1)
    info('  Setting number of images')
    global_PVs['Cam1NumImages'].put(n_images, wait=True)
    info('  Number of images set to %d' % n_images)
    time.sleep(0.1)
    info('Init write plugin')
    info('  Setting write plugin to Idle')
    global_PVs['Capture'].put(FilePluginIdle, wait=True)
    info('  Write plugin is Idle')
    time.sleep(0.1)
    info('  Setting NumCapture')
    global_PVs['NumCapture'].put(n_images, wait=True)
    info('  NumCapture set to %d' % n_images)
    time.sleep(0.1)

def arm_write_plugin(global_PVs, n_images, fps):

    raw_str = global_PVs['APSFileName'].get()
    base_filename = sanitize_filename(raw_str)
    now_str = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    # filename = f"{base_filename}_{now_str}"
    filename = f"{base_filename}_{n_images}frms_{fps}fps"
    global_PVs['FileName'].put(filename, wait=True)
    time.sleep(0.1)
    info('  Arming write plugin')
    global_PVs['Capture'].put(WritePluginCapture)
    # wait_pv(global_PVs['Capture'], WritePluginCapture, 5)
    info('  Write plugin armed')

def measure_fps(global_PVs):

    info('  Setting image mode to Continuous')
    global_PVs['Cam1ImageMode'].put('Continuous', wait=True)
    time.sleep(0.1)
    global_PVs['Cam1Acquire'].put(DetectorAcquire)
    time.sleep(2)
    fps = global_PVs['Cam1ArrayRate_RBV'].get()
    global_PVs['Cam1Acquire'].put(DetectorIdle)
    info('  Setting image mode to Multiple')
    global_PVs['Cam1ImageMode'].put('Multiple', wait=True)
    info('  Image mode is Multiple')
    time.sleep(0.1)
    warning('  Frame rate: %d' % fps)
    return int(fps)

def parse_args():

    default_aps_start_pv    = "OPS:message8"
    default_aps_filename_pv = "OPS:message7"
    default_detector_prefix = "2bmSP1:"
    default_file_format     = "hdf"
    default_num_images      = 1000

    parser = argparse.ArgumentParser(
        description="Configure 2bmSP1 detector, write plugin, and start on APS start PV."
    )

    parser.add_argument(
        "--aps-start-pv",
        default=default_aps_start_pv,
        help=f"PV to monitor for start command (default: {default_aps_start_pv})",
    )
    parser.add_argument(
        "--aps-filename-pv",
        default=default_aps_filename_pv,
        help=f"PV providing base filename (default: {default_aps_filename_pv})",
    )
    parser.add_argument(
        "--detector-prefix",
        default=default_detector_prefix,
        help=f"Detector prefix (default: {default_detector_prefix})",
    )
    parser.add_argument(
        "--file-format",
        default=default_file_format,
        choices=["tiff", "hdf"],
        help=f"Detector plugin used (options: tiff, hdf; default: {default_file_format})",
    )
    parser.add_argument(
        "--number-of-images",
        type=int,
        default=default_num_images,
        help=f"Number of images to acquire (default: {default_num_images})",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # This is just to print nice logger messages
    setup_custom_logger()

    info("Parameters:")
    info(f"  APS start PV     : {args.aps_start_pv}")
    info(f"  APS filename PV  : {args.aps_filename_pv}")
    info(f"  Detector prefix  : {args.detector_prefix}")
    info(f"  Number of images : {args.number_of_images}")

    pv = init_general_PVs(
        args.aps_start_pv,
        args.aps_filename_pv,
        args.detector_prefix,
        args.file_format
    )
    if pv is None:
        sys.exit(1)

    # Initialize once at startup
    init_detector(pv, args.number_of_images)

    fps = measure_fps(pv)

    # Edge-triggered monitoring:
    # Only trigger when APSStart transitions from non-start -> start.
    info('Monitoring APSStart for "start" command')
    try:
        last_is_start = False
        while True:
            val = pv['APSStart'].get(as_string=True)
            if val is not None:
                val_str = str(val).strip()
                # is_start = (val_str.lower() == StartCommand.lower())
                is_start = val_str.lower().startswith(StartCommand.lower())
                # Detect rising edge: was not start, now is start
                if is_start and not last_is_start:
                    info('APSStart changed to "Acquire": arming write plugin')
                    arm_write_plugin(pv, args.number_of_images, fps)
                    time.sleep(1)
                    info('APSStart changed to "Acquire": starting acquisition')
                    pv['Cam1Acquire'].put(DetectorAcquire)
                    wait_pv(pv['Cam1Acquire'], DetectorAcquire, 2)
                    info('Acquisition complete; returning to monitoring')

                last_is_start = is_start

            time.sleep(0.1)
    except KeyboardInterrupt:
        info('\nMonitoring stopped by user')


if __name__ == "__main__":
    main()
