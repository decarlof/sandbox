import numpy as np
import h5py
import sys
with h5py.File(sys.argv[1],'a') as fid:
# step = 2*(fid['exchange/theta'][1] - fid['exchange/theta'][0])
# print(step)
 fid['exchange/theta'][:]+=float(sys.argv[2])
 print( fid['exchange/theta'][:])
