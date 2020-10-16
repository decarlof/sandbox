import os
import sys
import time
import argparse
from epics import PV
from datetime import datetime

import log

def wait_frontend_shutter_open(epics_pvs, timeout=-1):
    """Waits for the front end shutter to open, or for ``abort_scan()`` to be called.

    While waiting this method periodically tries to open the shutter..

    Parameters
    ----------
    timeout : float
        The maximum number of seconds to wait before raising a ShutterTimeoutError exception.

    Raises
    ------
    ScanAbortError
        If ``abort_scan()`` is called
    ShutterTimeoutError
        If the open shutter has not completed within timeout value.
    """

    start_time = time.time()
    pv = epics_pvs['OpenShutter']
    value = epics_pvs['OpenShutterValue'].get(as_string = True)
    log.info('open shutter: %s, value: %s', pv, value)
    elapsed_time = 0
    while True:
        if epics_pvs['ShutterStatus'].get() == int(value):
            log.warning("Shutter is open in %f s", elapsed_time)
            return
        # if not self.scan_is_running:
        #     raise ScanAbortError
        value = epics_pvs['OpenShutterValue'].get()
        time.sleep(1.0)
        current_time = time.time()
        elapsed_time = current_time - start_time
        log.warning("Waiting on shutter to open: %f s", elapsed_time)
        epics_pvs['OpenShutter'].put(value, wait=True)
        if timeout > 0:
            if elapsed_time >= timeout:
                raise ShutterTimeoutError()

def set_pvs():
    epics_pvs = {}
    epics_pvs['Energy'] = PV('2bma:TomoScan:Energy.VAL')
    epics_pvs['Energy_Mode'] = PV('2bma:TomoScan:EnergyMode.VAL')

    epics_pvs['CloseShutterPVName']   = PV('2bma:TomoScan:CloseShutterPVName')
    epics_pvs['CloseShutterValue']    = PV('2bma:TomoScan:CloseShutterValue')
    epics_pvs['OpenShutterPVName']    = PV('2bma:TomoScan:OpenShutterPVName')
    epics_pvs['OpenShutterValue']     = PV('2bma:TomoScan:OpenShutterValue')
    epics_pvs['ShutterStatusPVName']  = PV('2bma:TomoScan:ShutterStatusPVName')
    epics_pvs['BeamReadyPVName']      = PV('2bma:TomoScan:BeamReadyPVName')

    epics_pvs['CloseShutter']        = PV(epics_pvs['CloseShutterPVName'].get(as_string=True))
    epics_pvs['OpenShutter']         = PV(epics_pvs['OpenShutterPVName'].get(as_string=True))
    epics_pvs['ShutterStatus']       = PV(epics_pvs['ShutterStatusPVName'].get(as_string=True))
    epics_pvs['BeamReady']           = PV(epics_pvs['BeamReadyPVName'].get(as_string=True))

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
        wait_frontend_shutter_open(epics_pvs)
        # wait_pv(epics_pvs['ShutterStatus'], 1)
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
