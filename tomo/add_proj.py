import h5py 
import numpy as np

with h5py.File('/data/2021-12/Duchkov/mosaic/mosaic_2073.h5','r+') as fid:
    fid['/exchange/data'].resize([6000,2048,2448])
    fid['/exchange/data'][5999][:] = fid['/exchange/data'][5998]
    theta = fid['/exchange/theta'][:]
    # fid['/exchange/theta'][-1] = theta[-1]+theta[1] - theta[0]
    theta_new = np.concatenate((theta,[theta[-1]+theta[1] - theta[0]]))
    del fid['/exchange/theta']
    fid.create_dataset('/exchange/theta', (6000,), dtype='f')
    fid['/exchange/theta'][:] = theta_new