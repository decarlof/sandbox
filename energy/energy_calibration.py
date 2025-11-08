from epics import PV
import pvaccess as pva
import numpy as np
from time import sleep

data_pv = pva.Channel('2bmbSP2:Pva1:Image')
n = data_pv.get('')['dimension'][0]['size']
nz = data_pv.get('')['dimension'][1]['size']
# exp_pv = PV('2bmbSP1:cam1:AcquireTime')
crystal1 = PV('2bma:m30')
crystal2 = PV('2bma:m31')
# init_value_c1 = 1.955
# init_value_c2 = 2.02737
init_value_c1 = 1.905-0.03
init_value_c2 = 1.97737-0.03

karray = np.arange(-0.0,0.07,0.001)
arr = np.zeros(len(karray))
for k in np.arange(len(karray)):
	crystal1.put(init_value_c1+karray[k],wait=True)
	crystal2.put(init_value_c2+karray[k],wait=True)
	sleep(4)
	data = list(data_pv.get()['value'][0].values())[0].reshape(nz,n).copy()    
	arr[k] = np.sum(data[nz//2-512:nz//2+512,n//2-512:n//2+512])
	print(init_value_c1+karray[k],arr[k])
np.save('with_filter',arr)

# import matplotlib.pyplot as plt
# nf = np.load('no_filter.npy')
# wf = np.load('with_filter.npy')
# # plt.subplot(1,3,1)
# # plt.plot(wf,'.')
# # plt.subplot(1,3,2)
# # plt.plot(nf,'.')
# # plt.subplot(1,3,3)
# plt.figure(figsize=(12,6))
# plt.plot(energies,wf/nf,'.')
# plt.xticks(energies[::2])
# plt.grid()
# plt.show()