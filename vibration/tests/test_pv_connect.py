# test_pv_connect.py
from epics import PV
import time

pv_names = [
    "2bmSP2:cam1:NumImages",
    "2bmSP2:cam1:AcquireTime",
    "2bmSP2:cam1:ImageMode",
    "2bmSP2:HDF1:FileName",
    "2bmSP2:HDF1:NumCapture",
    "2bmSP2:HDF1:Capture",
    "2bmSP2:cam1:Acquire",
]

pvs = {name: PV(name) for name in pv_names}

for i in range(20):  # up to ~2 seconds
    print(f"Iteration {i}:")
    for name, pv in pvs.items():
        print(f"  {name}: connected={pv.connected}")
    if all(pv.connected for pv in pvs.values()):
        break
    time.sleep(0.1)
