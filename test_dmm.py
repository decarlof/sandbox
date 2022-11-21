from epics import PV

pv1 = PV('2bma:m30')
pv2 = PV('2bma:m31')

for k in range(4):
	pv1.put(1.4,wait=False)
	pv2.put(1.4,wait=True)

	pv1.put(0.9,wait=False)
	pv2.put(0.9,wait=True)
	
