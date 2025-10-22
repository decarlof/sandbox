import time
import logging

import numpy as np
from epics import PV

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def init_global_PVs(detector_prefix):
    global_PVs = {}

    # detector pv's
    camera_prefix = detector_prefix + 'cam1:' 

    global_PVs['CamManufacturer_RBV']       = PV(camera_prefix + 'Manufacturer_RBV')
    global_PVs['CamModel']                  = PV(camera_prefix + 'Model_RBV')
    global_PVs['Cam1SerialNumber']          = PV(camera_prefix + 'SerialNumber_RBV')
    global_PVs['Cam1ImageMode']             = PV(camera_prefix + 'ImageMode')
    global_PVs['Cam1ArrayCallbacks']        = PV(camera_prefix + 'ArrayCallbacks')
    global_PVs['Cam1AcquirePeriod']         = PV(camera_prefix + 'AcquirePeriod')
    global_PVs['Cam1SoftwareTrigger']       = PV(camera_prefix + 'SoftwareTrigger') 
    global_PVs['Cam1AcquireTime']           = PV(camera_prefix + 'AcquireTime')
    global_PVs['Cam1AcquireTime_RBV']       = PV(camera_prefix + 'AcquireTime_RBV')
    global_PVs['Cam1FrameType']             = PV(camera_prefix + 'FrameType')
    global_PVs['Cam1AttributeFile']         = PV(camera_prefix + 'NDAttributesFile')
    global_PVs['Cam1SizeX']                 = PV(camera_prefix + 'SizeX')
    global_PVs['Cam1SizeY']                 = PV(camera_prefix + 'SizeY')
    global_PVs['Cam1NumImages']             = PV(camera_prefix + 'NumImages')
    global_PVs['Cam1TriggerMode']           = PV(camera_prefix + 'TriggerMode')
    global_PVs['Cam1Acquire']               = PV(camera_prefix + 'Acquire')
    global_PVs['Cam1SizeX_RBV']             = PV(camera_prefix + 'SizeX_RBV')
    global_PVs['Cam1SizeY_RBV']             = PV(camera_prefix + 'SizeY_RBV')
    global_PVs['Cam1MaxSizeX_RBV']          = PV(camera_prefix + 'MaxSizeX_RBV')
    global_PVs['Cam1MaxSizeY_RBV']          = PV(camera_prefix + 'MaxSizeY_RBV')
    global_PVs['Cam1PixelFormat_RBV']       = PV(camera_prefix + 'PixelFormat_RBV')
    global_PVs['ArrayRate_RBV']             = PV(camera_prefix + 'ArrayRate_RBV')

    image_prefix = detector_prefix + 'image1:'
    global_PVs['Image']                     = PV(image_prefix + 'ArrayData')
    global_PVs['Cam1Display']               = PV(image_prefix + 'EnableCallbacks')

    manufacturer = global_PVs['CamManufacturer_RBV'].get(as_string=True)
    model = global_PVs['CamModel'].get(as_string=True)

    if model in ('Oryx ORX-10G-51S5M', 'Oryx ORX-10G-310S9M'):
        logging.info('Detector %s model %s detected', manufacturer, model)
        global_PVs['Cam1AcquireTimeAuto']   = PV(detector_prefix + 'AcquireTimeAuto')
        global_PVs['Cam1FrameRateOnOff']    = PV(detector_prefix + 'FrameRateEnable')
        global_PVs['Cam1TriggerSource']     = PV(detector_prefix + 'TriggerSource')
        global_PVs['Cam1TriggerOverlap']    = PV(detector_prefix + 'TriggerOverlap')
        global_PVs['Cam1ExposureMode']      = PV(detector_prefix + 'ExposureMode')
        global_PVs['Cam1TriggerSelector']   = PV(detector_prefix + 'TriggerSelector')
        global_PVs['Cam1TriggerActivation'] = PV(detector_prefix + 'TriggerActivation')
    else:
        logging.error('Detector %s model %s is not supported', manufacturer, model)
        return None        

    # Aerotech Ensemble PSO
    tomoscan_prefix = '2bmb:TomoScan:'

    global_PVs['PSOControllerModel'] = PV(tomoscan_prefix + 'PSOControllerModel')
    global_PVs['PSOCountsPerRotation'] = PV(tomoscan_prefix + 'PSOCountsPerRotation')

    return global_PVs

def frame_rate():
    detector_prefix = '2bmSP1:'
    global_PVs = init_global_PVs(detector_prefix)

    if global_PVs is None:
        logging.error('Failed to initialize PVs for %s', detector_prefix)
        return None

    detector_sn = global_PVs['Cam1SerialNumber'].get()
    if detector_sn in (None, 'Unknown'):
        logging.error('Detector with EPICS IOC prefix %s is down', detector_prefix)
        return None
    else:
        logging.info('Detector with EPICS IOC prefix %s and serial number %s is on', detector_prefix, detector_sn)

        global_PVs['Cam1ImageMode'].put(2, wait=True)  # set Continuous
        logging.info('ImageMode set to %s', global_PVs['Cam1ImageMode'].get(as_string=True))

        global_PVs['Cam1Acquire'].put(1)
        time.sleep(3)

        fr = global_PVs['ArrayRate_RBV'].get()
        logging.info('Measured frame rate: %.2f Hz', fr)

        global_PVs['Cam1Acquire'].put(0)

    return fr


def compute_frame_time(detector_prefix):
    """Computes the time to collect and readout an image from the camera.

    This method is used to compute the time between triggers to the camera.
    This can be used, for example, to configure a trigger generator or to compute
    the speed of the rotation stage.

    The calculation is camera specific.  The result can depend on the actual exposure time
    of the camera, and on a variety of camera configuration settings (pixel binning,
    pixel bit depth, video mode, etc.)


    Returns
    -------
    float
        The frame time, which is the minimum time allowed between triggers for the value of the
        ``ExposureTime`` PV.
    """

    global_PVs = init_global_PVs(detector_prefix)
    # The readout time of the camera depends on the model, and things like the
    # PixelFormat, VideoMode, etc.
    # The measured times in ms with 100 microsecond exposure time and 1000 frames
    # without dropping
    camera_model = global_PVs['CamModel'].get(as_string=True)
    readout = None
    video_mode = None
    # Adding 1% read out margin to the exposure time, and at least 1 ms seems to work for FLIR cameras
    # This is empirical and if needed should adjusted for each camera
    readout_margin = 1.01
    if camera_model == 'Grasshopper3 GS3-U3-51S5M':
        pixel_format = global_PVs['Cam1PixelFormat_RBV'].get(as_string=True) 
        readout_times = {
            'Mono8': 6.18,
            'Mono12Packed': 8.20,
            'Mono12p': 8.20,
            'Mono16': 12.34
        }
        readout = readout_times[pixel_format]/1000.            
    if camera_model == 'Oryx ORX-10G-51S5M':
        pixel_format = global_PVs['Cam1PixelFormat_RBV'].get(as_string=True) 
        readout_margin = 1.05
        readout_times = {
            'Mono8': 6.18,
            'Mono12Packed': 8.20,
            'Mono16': 12.34
        }
        readout = readout_times[pixel_format]/1000.
    if camera_model == 'Oryx ORX-10G-310S9M':
        pixel_format = global_PVs['Cam1PixelFormat_RBV'].get(as_string=True) 
        readout_times = {
            'Mono8': 30.0,
            'Mono12Packed': 30.0,
            'Mono16': 30.0
        }
        readout_margin = 1.2
        readout = readout_times[pixel_format]/1000.

    if readout is None:
        log.error('Unsupported combination of camera model, pixel format and video mode: %s %s %s',
                      camera_model, pixel_format, video_mode)            
        return 0

    # We need to use the actual exposure time that the camera is using, not the requested time
    exposure = global_PVs['Cam1AcquireTime_RBV'].value
    # Add some extra time to exposure time for margin.

    frame_time = exposure * readout_margin   
    # If the time is less than the readout time then use the readout time plus 1 ms.
    if frame_time < readout:
        frame_time = readout + .001

    return frame_time

def motor_speed(rotation_start, rotation_step, num_angles):

    detector_prefix = '2bmSP1:'
    global_PVs = init_global_PVs(detector_prefix)



    # Computes several parameters describing the fly scan motion.
    # Computes the spacing between points, ensuring it is an integer number
    # of encoder counts.
    # Uses this spacing to recalculate the end of the scan, if necessary.
    # Computes the taxi distance at the beginning and end of scan to allow
    # the stage to accelerate to speed.
    # Assign the fly scan angular position to theta[]
    # Compute the actual delta to keep each interval an integer number of encoder counts
    encoder_multiply = float(global_PVs['PSOCountsPerRotation'].get()) / 360.
    raw_delta_encoder_counts = rotation_step * encoder_multiply
    delta_encoder_counts = round(raw_delta_encoder_counts)
    if abs(raw_delta_encoder_counts - delta_encoder_counts) > 1e-4:
        logging.warning('  *** *** *** Requested scan would have used a non-integer number of encoder counts.')
        logging.warning('  *** *** *** Calculated # of encoder counts per step = {0:9.4f}'.format(raw_delta_encoder_counts))
        logging.warning('  *** *** *** Instead, using {0:d}'.format(delta_encoder_counts))
        new_rotation_step = delta_encoder_counts / encoder_multiply

        logging.warning('  *** *** *** new rotation_step = %.7f° instead of %.7f°' % (new_rotation_step, rotation_step))
        rotation_stop     = rotation_start + num_angles * rotation_step
        new_rotation_stop = rotation_start + num_angles * new_rotation_step
        logging.warning('  *** *** *** new rotation_step = %.7f° instead of %.7f°' % (new_rotation_stop, rotation_stop))

    # In the regular fly scan we compute the time to collect each frame which is the exposure time plus the readout time plus a margin
    # then we use this time as the time to travel a rotation step
    detector_prefix = '2bmSP1:'
    time_per_angle_step = compute_frame_time(detector_prefix)
    logging.info('Time per angular step %f s', time_per_angle_step)

    motor_speed = np.abs(new_rotation_step) / time_per_angle_step
    logging.info('Rotary stage speed: %f °/s', motor_speed)

    return motor_speed

def main():

    # In a standard fly scan, the configuration parameters (rotation_start, rotation_step, and num_angles)
    # are used to compute the rotation motor speed. Projection images are acquired continuously as the sample rotates.
    # The rotation speed is set to ensure there is no motion blur during each exposure.
    logging.info('******** ******** ********')
    logging.info('******** ******** ********')
    logging.info('******** FLY SCAN ********')
    logging.info('******** ******** ********')
    logging.info('******** ******** ********')
    rotation_start       = 0
    rotation_step        = 0.12
    num_angles           = 1500
    rotation_speed = motor_speed(rotation_start, rotation_step, num_angles)


    # In an interlaced scan, the goal is instead to define the total time required for a full rotation,
    # and use the measured camera frame rate to acquire projection images at predefined angular positions.
    # Below is how to measure the detector frame rate
    logging.info('******** *************** ********')
    logging.info('******** *************** ********')
    logging.info('******** INTERLACED SCAN ********')
    logging.info('******** *************** ********')
    logging.info('******** *************** ********')
    fps = frame_rate()
    if fps is not None:
        logging.info('Frame rate function returned: %.2f Hz', fps)
    else:
        logging.warning('Frame rate measurement failed.')

if __name__ == '__main__':
    main()
