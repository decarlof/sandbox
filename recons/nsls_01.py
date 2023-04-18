import h5py
import matplotlib.pyplot as plt
import numpy as np
with h5py.File('/data/2023-02/decarlo/HDF/NSLS/input_dx2_fixed_angles.h5','a') as fid:
    fid['/exchange/theta'][:] = np.float32(np.arange(899)*0.2)
#     data = fid['img_tomo']
#     dark = fid['img_dark']
#     flat = fid['img_bkg']
#     theta = fid['angle']
#     with h5py.File('/data/2023-02/decarlo/HDF/NSLS/fly_scan_id_2877_aps.h5','w') as fid_out:
#         fid_out.create_dataset('/exchange/data',data=data[:])
#         fid_out.create_dataset('/exchange/data_dark',data=dark[:])
#         fid_out.create_dataset('/exchange/data_white',data=flat[:])
#         fid_out.create_dataset('/exchange/theta',data=theta[:])
    # difs = theta[:-1:2]-theta[1::2]
    # for k,dif in enumerate(difs):
    #     print(k,dif)
    # print(theta)
    # print(len(theta))
    # # print(np.amin(theta[:-1:2]-theta[1::2]))
    # print(np.amax(theta[:-1:2]-theta[1::2]))
    # plt.plot(theta[:-1:2]-theta[1::2])
    # plt.show()
    
    