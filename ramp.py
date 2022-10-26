from epics import PV
import sys
import numpy as np
import time
temp_goal = float(sys.argv[1]) # deg
ramp_rate = float(sys.argv[2]) # deg/min
#change_rate = float(sys.argv[3]) # deg/min

temp_set = PV('2bmb:ET2k:1:WriteSetPoint')
temp_read = PV('2bmb:ET2k:1:Temperature')

temp_cur = temp_read.get()
temp = np.arange(temp_cur,temp_goal,ramp_rate/60)

# print(temp)

for t in temp:
    print(f'set temp to {t:0.2f} deg {temp_read.get():0.2f}')
    temp_set.put(t,wait=True)
    while (np.abs(temp_read.get()-t)>1):
        print(f'wait on {temp_read.get():0.2f} to reach {t:0.2}')
        # pass
        time.sleep(1)
    time.sleep(1)



