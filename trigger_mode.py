import os
import sys
import time
import argparse
from epics import PV
from datetime import datetime

EPSILON=0.01

import log

def wait_pv(epics_pv, wait_val, timeout=-1):
    """Wait on a pv to be a value until max_timeout (default forever)
       delay for pv to change
    """

    time.sleep(.01)
    start_time = time.time()
    while True:
        pv_val = epics_pv.get()
        if isinstance(pv_val, float):
            if abs(pv_val - wait_val) < EPSILON:
                return True
        if pv_val != wait_val:
            if timeout > -1:
                current_time = time.time()
                diff_time = current_time - start_time
                if diff_time >= timeout:
                    log.error('  *** ERROR: DROPPED IMAGES ***')
                    log.error('  *** wait_pv(%s, %d, %5.2f reached max timeout. Return False',
                          epics_pv.pvname, wait_val, timeout)
                    return False
            time.sleep(.01)
        else:
            return True

def set_pvs():
    epics_pvs = {}

    camera_prefix = '2bmSP2:cam1:'
    epics_pvs['CamManufacturer']      = PV(camera_prefix + 'Manufacturer_RBV')
    epics_pvs['CamModel']             = PV(camera_prefix + 'Model_RBV')
    epics_pvs['CamAcquire']           = PV(camera_prefix + 'Acquire')
    epics_pvs['CamAcquireBusy']       = PV(camera_prefix + 'AcquireBusy')
    epics_pvs['CamImageMode']         = PV(camera_prefix + 'ImageMode')
    epics_pvs['CamTriggerMode']       = PV(camera_prefix + 'TriggerMode')
    epics_pvs['CamNumImages']         = PV(camera_prefix + 'NumImages')
    epics_pvs['CamNumImagesCounter']  = PV(camera_prefix + 'NumImagesCounter_RBV')
    epics_pvs['CamAcquireTime']       = PV(camera_prefix + 'AcquireTime')
    epics_pvs['CamAcquireTimeRBV']    = PV(camera_prefix + 'AcquireTime_RBV')
    epics_pvs['CamBinX']              = PV(camera_prefix + 'BinX')
    epics_pvs['CamBinY']              = PV(camera_prefix + 'BinY')
    epics_pvs['CamWaitForPlugins']    = PV(camera_prefix + 'WaitForPlugins')
    epics_pvs['PortNameRBV']          = PV(camera_prefix + 'PortName_RBV')
    epics_pvs['CamExposureMode']      = PV(camera_prefix + 'ExposureMode')
    epics_pvs['CamTriggerOverlap']    = PV(camera_prefix + 'TriggerOverlap')
    epics_pvs['CamPixelFormat']       = PV(camera_prefix + 'PixelFormat')
    epics_pvs['CamArrayCallbacks']    = PV(camera_prefix + 'ArrayCallbacks')
    epics_pvs['CamFrameRateEnable']   = PV(camera_prefix + 'FrameRateEnable')
    epics_pvs['CamTriggerSource']     = PV(camera_prefix + 'TriggerSource')
    epics_pvs['CamImageSizeX']        = PV(camera_prefix + 'ArraySizeX_RBV')
    epics_pvs['CamImageSizeY']        = PV(camera_prefix + 'ArraySizeY_RBV')

    prefix = '2bma:PSOFly2:'
    epics_pvs['PSOscanDelta']       = PV(prefix + 'scanDelta')
    epics_pvs['PSOstartPos']        = PV(prefix + 'startPos')
    epics_pvs['PSOendPos']          = PV(prefix + 'endPos')
    epics_pvs['PSOslewSpeed']       = PV(prefix + 'slewSpeed')
    epics_pvs['PSOtaxi']            = PV(prefix + 'taxi')
    epics_pvs['PSOfly']             = PV(prefix + 'fly')
    epics_pvs['PSOscanControl']     = PV(prefix + 'scanControl')
    epics_pvs['PSOcalcProjections'] = PV(prefix + 'numTriggers')        
    epics_pvs['ThetaArray']         = PV(prefix + 'motorPos.AVAL')

    return epics_pvs

def set_pso(epics_pvs, rotation_start, num_angles, rotation_step):

    rotation_stop = rotation_start + (rotation_step * num_angles)

    log.info('set_pso')

    epics_pvs['PSOstartPos'].put(rotation_start, wait=True)
    wait_pv(epics_pvs['PSOstartPos'], rotation_start)
    epics_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(epics_pvs['PSOendPos'], rotation_stop)
    epics_pvs['PSOscanDelta'].put(rotation_step, wait=True)
    wait_pv(epics_pvs['PSOscanDelta'], rotation_step)

    calc_rotation_start = epics_pvs['PSOstartPos'].value
    calc_rotation_stop = epics_pvs['PSOendPos'].value
    calc_rotation_step = epics_pvs['PSOscanDelta'].value
    calc_num_angles = epics_pvs['PSOcalcProjections'].value

    log.info('start entered/calculated %s, %s', rotation_start, calc_rotation_start)
    log.info('stop entered/calculated %s, %s', rotation_stop, calc_rotation_stop)
    log.info('step entered/calculated %s, %s', rotation_step, calc_rotation_step)
    log.info('num_angles entered/calculated %s, %s', num_angles, calc_num_angles)

    # theta = []
    # theta = epics_pvs['ThetaArray'].get(count=int(num_angles))
    # log.info('theta = ', theta)

    return calc_num_angles, calc_rotation_step


def set_trigger_mode(epics_pvs, trigger_mode, num_images):
    """Sets the trigger mode SIS3820 and the camera.

    Parameters
    ----------
    trigger_mode : str
        Choices are: "FreeRun", "Internal", or "PSOExternal"

    num_images : int
        Number of images to collect.  Ignored if trigger_mode="FreeRun".
        This is used to set the ``NumImages`` PV of the camera.
    """

    epics_pvs['CamAcquire'].put('Done') ###
    wait_pv(epics_pvs['CamAcquire'], 0) ###
    log.info('set trigger mode: %s', trigger_mode)
    if trigger_mode == 'FreeRun':
        epics_pvs['CamImageMode'].put('Continuous', wait=True)
        epics_pvs['CamTriggerMode'].put('Off', wait=True)
        wait_pv(epics_pvs['CamTriggerMode'], 0)
    elif trigger_mode == 'Internal':
        epics_pvs['CamTriggerMode'].put('Off', wait=True)
        wait_pv(epics_pvs['CamTriggerMode'], 0)
        epics_pvs['CamImageMode'].put('Multiple')
        epics_pvs['CamNumImages'].put(num_images, wait=True)
    else: # set camera to external triggering
        # These are just in case the scan aborted with the camera in another state
        epics_pvs['CamTriggerMode'].put('Off', wait=True)
        epics_pvs['CamTriggerSource'].put('Line2', wait=True)
        epics_pvs['CamTriggerOverlap'].put('ReadOut', wait=True)
        epics_pvs['CamExposureMode'].put('Timed', wait=True)

        epics_pvs['CamImageMode'].put('Multiple')
        epics_pvs['CamArrayCallbacks'].put('Enable')
        epics_pvs['CamFrameRateEnable'].put(0)

        num_angles = num_images
        epics_pvs['CamNumImages'].put(num_angles, wait=True)
        epics_pvs['CamTriggerMode'].put('On', wait=True)
        wait_pv(epics_pvs['CamTriggerMode'], 1)


def compute_frame_time(epics_pvs):
    """Computes the time to collect and readout an image from the camera.

    This method is used to compute the time between triggers to the camera.
    This can be used, for example, to configure a trigger generator or to compute
    the speed of the rotation stage.

    The calculation is camera specific.  The result can depend on the actual exposure time
    of the camera, and on a variety of camera configuration settings (pixel binning,
    pixel bit depth, video mode, etc.)

    The current version only supports the Point Grey Grasshopper3 GS3-U3-23S6M.
    The logic for additional cameras should be added to this function in the future
    if the camera is expected to be used at more than one beamline.
    If the camera is only to be used at a single beamline then the code should be added
    to this method in the derived class

    Returns
    -------
    float
        The frame time, which is the minimum time allowed between triggers for the value of the
        ``ExposureTime`` PV.
    """
    # The readout time of the camera depends on the model, and things like the
    # PixelFormat, VideoMode, etc.
    # The measured times in ms with 100 microsecond exposure time and 1000 frames
    # without dropping
    camera_model = epics_pvs['CamModel'].get(as_string=True)
    pixel_format = epics_pvs['CamPixelFormat'].get(as_string=True)
    readout = None
    video_mode = None
    if camera_model == 'Grasshopper3 GS3-U3-23S6M':
        video_mode   = epics_pvs['CamVideoMode'].get(as_string=True)
        readout_times = {
            'Mono8':        {'Mode0': 6.2,  'Mode1': 6.2, 'Mode5': 6.2, 'Mode7': 7.9},
            'Mono12Packed': {'Mode0': 9.2,  'Mode1': 6.2, 'Mode5': 6.2, 'Mode7': 11.5},
            'Mono16':       {'Mode0': 12.2, 'Mode1': 6.2, 'Mode5': 6.2, 'Mode7': 12.2}
        }
        readout = readout_times[pixel_format][video_mode]/1000.
    if camera_model == 'Oryx ORX-10G-51S5M':
        # video_mode   = epics_pvs['CamVideoMode'].get(as_string=True)
        readout_times = {
            'Mono8': 6.18,
            'Mono12Packed': 8.20,
            'Mono16': 12.34
        }
        readout = readout_times[pixel_format]/1000.
    if camera_model == 'Oryx ORX-10G-310S9M':
        pixel_format = self.epics_pvs['CamPixelFormat'].get(as_string=True) 
        image_size_x = self.epics_pvs['ImageSizeX'].get() 
        image_size_y = self.epics_pvs['ImageSizeY'].get() 
        readout_times = {
            'Mono8': 30.0,
            'Mono12Packed': 30.0,
            'Mono16': 30.0
        }
        readout_margin = 1.2
        readout = readout_times[pixel_format]/1000.
        readout_estimate = estimate_readout_time(image_size_x, image_size_y, pixel_format, throughput_gbps=8.0):
        print(readout, readout_estimate)
        
    if readout is None:
        log.error('Unsupported combination of camera model, pixel format and video mode: %s %s %s',
                      camera_model, pixel_format, video_mode)
        return 0

    # We need to use the actual exposure time that the camera is using, not the requested time
    exposure = epics_pvs['CamAcquireTimeRBV'].value
    # Add 1 or 5 ms to exposure time for margin
    if exposure > 2.3:
        frame_time = exposure + .005
    elif exposure > 1.0:
        frame_time = exposure + .002
    else:
        frame_time = exposure + .001

    # If the time is less than the readout time then use the readout time
    if frame_time < readout:
        frame_time = readout
    return frame_time

def wait_camera_done(epics_pvs, timeout):
    """Waits for the camera acquisition to complete, or for ``abort_scan()`` to be called.

    While waiting this method periodically updates the status PVs ``ImagesCollected``,
    ``ImagesSaved``, ``ElapsedTime``, and ``RemainingTime``.

    Parameters
    ----------
    timeout : float
        The maximum number of seconds to wait before raising a CameraTimeoutError exception.

    Raises
    ------
    ScanAbortError
        If ``abort_scan()`` is called
    CameraTimeoutError
        If acquisition has not completed within timeout value.
    """

    start_time = time.time()
    while True:
        if epics_pvs['CamAcquireBusy'].value == 0:
            return

def estimate_readout_time(width, height, pixel_format='Mono8', throughput_gbps=8.0):
    """
    Estimate readout time in milliseconds.

    Parameters:
    - width: ROI width in pixels
    - height: ROI height in pixels
    - bit_depth: bits per pixel (8, 10, 12, 16)
    - throughput_gbps: effective throughput of the interface (default 8 Gbps)

    Returns:
    - readout time in milliseconds
    """

    bit_depth = None
    if pixel_format == 'Mono8':
        bit_depth = 8
    elif pixel_format == 'Mono12Packed':
        bit_depth = 12
    elif pixel_format == 'Mono16':
        bit_depth = 16

    if bit_depth is not None:
        total_bits = width * height * bit_depth
        throughput_bps = throughput_gbps * 1e9
        readout_time_ms = (total_bits / throughput_bps) * 1000
        return round(readout_time_ms, 2)
    else:
        log.error('pixel format %s is not valid' % pixel_format)
        exit()

def main():

    # set logs directory
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'
    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)
    # setup logger
    lfname = logs_home + 'flir_' + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log.setup_custom_logger(lfname)

    epics_pvs = set_pvs()

    rotation_start = 0 
    num_angles = 100
    rotation_step = 0.1

    while (True):
        set_pso(epics_pvs, rotation_start, num_angles, rotation_step)
        log.info('taxi before starting capture')
        # Taxi before starting capture
        epics_pvs['PSOtaxi'].put(1, wait=True)
        wait_pv(epics_pvs['PSOtaxi'], 0)
        set_trigger_mode(epics_pvs, 'PSOExternal', num_angles)
        # Start the camera
        epics_pvs['CamAcquire'].put('Acquire')
        wait_pv(epics_pvs['CamAcquire'], 1)
        log.info('start fly scan')
        # Start fly scan
        epics_pvs['PSOfly'].put(1) #, wait=True)
        # wait for acquire to finish
        # wait_camera_done instead of the wait_pv enabled the counter update
        # self.wait_pv(epics_pvs['PSOfly'], 0)
        time_per_angle = compute_frame_time(epics_pvs)
        log.info('Time per angle: %s', time_per_angle)
        collection_time = num_angles * time_per_angle
        wait_camera_done(epics_pvs, collection_time + 60.)

        set_trigger_mode(epics_pvs, 'FreeRun', 1)
        epics_pvs['CamAcquire'].put('Acquire')
        wait_pv(epics_pvs['CamAcquire'], 1)

if __name__ == "__main__":
    main()
