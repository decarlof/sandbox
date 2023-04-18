import time

from epics import PV

EPSILON = .001

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


def set_pso_not_ok(rotation_start, num_angles, rotation_step):

    rotation_stop = rotation_start + (rotation_step * num_angles)

    control_pvs = {}
    prefix = '2bma:PSOFly2:'

    control_pvs['PSOstartPos']        = PV(prefix + 'startPos')
    control_pvs['PSOendPos']          = PV(prefix + 'endPos')
    control_pvs['PSOscanDelta']       = PV(prefix + 'scanDelta')
    control_pvs['PSOcalcProjections'] = PV(prefix + 'numTriggers')        
    control_pvs['ThetaArray']         = PV(prefix + 'motorPos.AVAL')

    control_pvs['PSOstartPos'].put(rotation_start, wait=True)
    wait_pv(control_pvs['PSOstartPos'], rotation_start)
    control_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop)
    control_pvs['PSOscanDelta'].put(rotation_step, wait=True)
    wait_pv(control_pvs['PSOscanDelta'], rotation_step)
    control_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop)
    time.sleep(1) # Per Tim suggestion
    control_pvs['PSOcalcProjections'].put(num_angles, wait=True)
    wait_pv(control_pvs['PSOcalcProjections'], num_angles)


    calc_rotation_start = control_pvs['PSOstartPos'].value
    calc_rotation_stop = control_pvs['PSOendPos'].value
    calc_rotation_step = control_pvs['PSOscanDelta'].value
    calc_num_angles = control_pvs['PSOcalcProjections'].value

    print('start entered/calculated', rotation_start, calc_rotation_start)
    print('stop entered/calculated', rotation_stop, calc_rotation_stop)
    print('step entered/calculated', rotation_step, calc_rotation_step)
    print('num_angles entered/calculated', num_angles, calc_num_angles)

    theta = []
    theta = control_pvs['ThetaArray'].get(count=int(num_angles))
    print('theta = ', theta)

def set_pso_ok(rotation_start, num_angles, rotation_step):

    rotation_stop = rotation_start + (rotation_step * num_angles)

    control_pvs = {}
    prefix = '2bma:PSOFly2:'

    control_pvs['PSOstartPos']        = PV(prefix + 'startPos')
    control_pvs['PSOendPos']          = PV(prefix + 'endPos')
    control_pvs['PSOscanDelta']       = PV(prefix + 'scanDelta')
    control_pvs['PSOcalcProjections'] = PV(prefix + 'numTriggers')        
    control_pvs['ThetaArray']         = PV(prefix + 'motorPos.AVAL')

    control_pvs['PSOstartPos'].put(rotation_start, wait=True)
    wait_pv(control_pvs['PSOstartPos'], rotation_start)
    control_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop)
    control_pvs['PSOscanDelta'].put(rotation_step, wait=True)
    wait_pv(control_pvs['PSOscanDelta'], rotation_step)
    control_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop)

    # why I need to add this? 
    control_pvs['PSOendPos'].put(rotation_stop+1, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop+1)
    control_pvs['PSOendPos'].put(rotation_stop, wait=True)
    wait_pv(control_pvs['PSOendPos'], rotation_stop)

    calc_rotation_start = control_pvs['PSOstartPos'].value
    calc_rotation_stop = control_pvs['PSOendPos'].value
    calc_rotation_step = control_pvs['PSOscanDelta'].value
    calc_num_angles = control_pvs['PSOcalcProjections'].value

    print('start entered/calculated', rotation_start, calc_rotation_start)
    print('stop entered/calculated', rotation_stop, calc_rotation_stop)
    print('step entered/calculated', rotation_step, calc_rotation_step)
    print('num_angles entered/calculated', num_angles, calc_num_angles)

    theta = []
    theta = control_pvs['ThetaArray'].get(count=int(num_angles))
    print('theta = ', theta)



def main():
    rotation_start = 0.0
    num_angles = 1500
    rotation_step = 0.12
    print('1')
    set_pso_not_ok(rotation_start, num_angles, rotation_step)
    rotation_start = 0
    num_angles = 1234
    rotation_step = 0.245
    print('2')
    set_pso_not_ok(rotation_start, num_angles, rotation_step)
    rotation_start = 0.0
    num_angles = 1500
    rotation_step = 0.12
    print('3')
    set_pso_not_ok(rotation_start, num_angles, rotation_step)

    rotation_start = 0.0
    num_angles = 1500
    rotation_step = 0.12
    print('4')
    set_pso_ok(rotation_start, num_angles, rotation_step)
    rotation_start = 0
    num_angles = 1234
    rotation_step = 0.245
    print('5')
    set_pso_ok(rotation_start, num_angles, rotation_step)
    rotation_start = 0.0
    num_angles = 1500
    rotation_step = 0.12
    print('6')
    set_pso_ok(rotation_start, num_angles, rotation_step)


if __name__ == "__main__":
    main()