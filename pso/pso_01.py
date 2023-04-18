import time

from epics import PV



rotation_start = 0
num_angles = 1500
rotation_step = 0.12
# rotation_start = 0
# num_angles = 1234
# rotation_step = 0.245
rotation_stop = rotation_start + (rotation_step * num_angles)

# print(rotation_start)
print(num_angles)
print(rotation_step)
# print(rotation_stop)

control_pvs = {}
prefix = '2bma:PSOFly2:'

control_pvs['PSOstartPos']        = PV(prefix + 'startPos')
control_pvs['PSOendPos']          = PV(prefix + 'endPos')
control_pvs['PSOscanDelta']       = PV(prefix + 'scanDelta')
control_pvs['PSOcalcProjections'] = PV(prefix + 'numTriggers')        
control_pvs['ThetaArray']         = PV(prefix + 'motorPos.AVAL')

control_pvs['PSOstartPos'].put(rotation_start, wait=True)
control_pvs['PSOendPos'].put(rotation_stop, wait=True)
control_pvs['PSOscanDelta'].put(rotation_step, wait=True)
# time.sleep(1)

calc_rotation_step = control_pvs['PSOscanDelta'].value
calc_num_proj = control_pvs['PSOcalcProjections'].value

print(int(calc_num_proj))
print(calc_rotation_step)

