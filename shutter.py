import os
import sys
import time
import argparse
from epics import PV
from datetime import datetime

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
    epics_pvs['Energy'] = PV('2bma:TomoScan:Energy.VAL')
    epics_pvs['Energy_Mode'] = PV('2bma:TomoScan:EnergyMode.VAL')

    epics_pvs['CloseShutterPVName']   = PV('2bma:TomoScan:CloseShutterPVName')
    epics_pvs['CloseShutterValue']    = PV('2bma:TomoScan:CloseShutterValue')
    epics_pvs['OpenShutterPVName']    = PV('2bma:TomoScan:OpenShutterPVName')
    epics_pvs['OpenShutterValue']     = PV('2bma:TomoScan:OpenShutterValue')
    # epics_pvs['ShutterStatusPVName']  = PV('2bma:TomoScan:ShutterStatusPVName')

    epics_pvs['CloseShutter']        = PV(epics_pvs['CloseShutterPVName'].get(as_string=True))
    epics_pvs['OpenShutter']         = PV(epics_pvs['OpenShutterPVName'].get(as_string=True))
    epics_pvs['ShutterStatus']       = PV('PA:02BM:STA_A_FES_OPEN_PL')
    epics_pvs['BeamReady']           = PV('ACIS:ShutterPermit')

    return epics_pvs


def open_frontend_shutter(epics_pvs):
    """Opens the shutter to collect flat fields or projections.

    The value in the ``OpenShutterValue`` PV is written to the ``OpenShutter`` PV.
    """

    if not epics_pvs['OpenShutter'] is None:
        pv = epics_pvs['OpenShutter']
        value = epics_pvs['OpenShutterValue'].get(as_string=True)
        status = epics_pvs['ShutterStatus'].get(as_string=True)
        log.info('shutter status: %s', status)
        log.info('open shutter: %s, value: %s', pv, value)
        epics_pvs['OpenShutter'].put(value, wait=True)
        wait_pv(epics_pvs['ShutterStatus'], 1)
        status = epics_pvs['ShutterStatus'].get(as_string=True)
        log.info('shutter status: %s', status)

def close_frontend_shutter(epics_pvs):
    """Closes the shutter to collect dark fields.

    The value in the ``CloseShutterValue`` PV is written to the ``CloseShutter`` PV.
    """
    if not epics_pvs['CloseShutter'] is None:
        pv = epics_pvs['CloseShutter']
        value = epics_pvs['CloseShutterValue'].get(as_string=True)
        status = epics_pvs['ShutterStatus'].get(as_string=True)
        log.info('shutter status: %s', status)
        log.info('close shutter: %s, value: %s', pv, value)
        epics_pvs['CloseShutter'].put(value, wait=True)
        wait_pv(epics_pvs['ShutterStatus'], 0)
        status = epics_pvs['ShutterStatus'].get(as_string=True)
        log.info('shutter status: %s', status)


def main(arg):

    # set logs directory
    home = os.path.expanduser("~")
    logs_home = home + '/logs/'
    # make sure logs directory exists
    if not os.path.exists(logs_home):
        os.makedirs(logs_home)
    # setup logger
    lfname = logs_home + 'shutter_' + datetime.strftime(datetime.now(), "%Y-%m-%d_%H:%M:%S") + '.log'
    log.setup_custom_logger(lfname)


    parser = argparse.ArgumentParser()
    parser.add_argument("--open",action="store_true", help="Open the beamline shutter")

    args = parser.parse_args()

    epics_pvs = set_pvs()

    if args.open:
    	open_frontend_shutter(epics_pvs)
    else:
    	close_frontend_shutter(epics_pvs)


if __name__ == "__main__":
    main(sys.argv[1:])
