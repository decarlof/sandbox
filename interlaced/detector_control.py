import time
import logging
from epics import PV

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def init_epics_PVs(detector_prefix):
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

    return global_PVs

def frame_rate():
    detector_prefix = '2bmSP1:'
    global_PVs = init_epics_PVs(detector_prefix)

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

def main():


    # # Current fly scan input parameters
    # start_angle = 
    # angle_step  =
    
    fps = frame_rate()
    if fps is not None:
        logging.info('Frame rate function returned: %.2f Hz', fps)
    else:
        logging.warning('Frame rate measurement failed.')

if __name__ == '__main__':
    main()
