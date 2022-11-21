from epics import PV 
from datetime import datetime
import time

pv_flow = PV('ISCO1:A:FlowRate_RBV')
pv_pressure = PV('ISCO1:A:Pressure_RBV')
pv_volume = PV('ISCO1:A:VolumeRemaining_RBV')



while True:
	now = datetime.now()
	current_time = now.strftime("%H:%M:%S")
	current_flow = pv_flow.get()
	current_pressure = pv_pressure.get()
	current_volume = pv_volume.get()
	str = f"{current_time} {current_flow:.3f} {current_pressure:.3f} {current_volume:.3f}"
	print(str)
	with open("pump_log_nosample.txt", "a") as text_file:
		text_file.write(str+'\n')
		time.sleep(2)




