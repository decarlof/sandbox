def init_epics_PVs():

    global_PVs = {}

    # detector pv's
    detector_prefix = '2bmSP1:'
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

    image_prefix = detector_prefix + 'image1:'
    global_PVs['Image']                     = PV(image_prefix + 'ArrayData')
    global_PVs['Cam1Display']               = PV(image_prefix + 'EnableCallbacks')

    manufacturer = global_PVs['CamManufacturer_RBV'].get(as_string=True)
    model = global_PVs['CamModel'].get(as_string=True)

    if model == 'Oryx ORX-10G-51S5M' or 'Oryx ORX-10G-310S9M':
        print('Detector %s model %s:' % (manufacturer, model))
        global_PVs['Cam1AcquireTimeAuto']   = PV(detector_prefix + 'AcquireTimeAuto')
        global_PVs['Cam1FrameRateOnOff']    = PV(detector_prefix + 'FrameRateEnable')
        global_PVs['Cam1TriggerSource']     = PV(detector_prefix + 'TriggerSource')
        global_PVs['Cam1TriggerOverlap']    = PV(detector_prefix + 'TriggerOverlap')
        global_PVs['Cam1ExposureMode']      = PV(detector_prefix + 'ExposureMode')
        global_PVs['Cam1TriggerSelector']   = PV(detector_prefix + 'TriggerSelector')
        global_PVs['Cam1TriggerActivation'] = PV(detector_prefix + 'TriggerActivation')
    else:
        log.error('Detector %s model %s is not supported' % (manufacturer, model))
        return None        

    return global_PVs



def main():

    global_PVs = init_epics_PVs()

    detector_sn = global_PVs['Cam1SerialNumber'].get()
    if ((detector_sn == None) or (detector_sn == 'Unknown')):
            log.error('*** The detector with EPICS IOC prefix %s is down' % params.detector_prefix)
            log.error('  *** Failed!')
        else:
            log.info('*** The detector with EPICS IOC prefix %s and serial number %s is on' \

if __name__ == '__main__':
    main()
