import time
from epics import PV


def onChanges(pvname=None, value=None, char_value=None, **kw):
    print('PV Changed! ', pvname, char_value, time.ctime())

def main():
    pvs = {}
    pvs['s_current']                = PV('S:SRcurrentAI')
    pvs['s_desired_mode']           = PV('S:DesiredMode')
    pvs['acis_shutter_permit']      = PV('ACIS:ShutterPermit')

    pvs['s_current'].add_callback(onChanges)
    pvs['s_desired_mode'].add_callback(onChanges)
    pvs['acis_shutter_permit'].add_callback(onChanges)

    print('Now wait for changes')

    t0 = time.time()
    while time.time() - t0 < 60.0:
        time.sleep(1.e-3)
    print('Done.')

if __name__ == "__main__":
    main()