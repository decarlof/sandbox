import h5py


with h5py.File('/data/2023-02/decarlo/HDF/NSLS/fly_scan_id_2877.h5','r') as fid:
    data = fid['img_tomo']
    dark = fid['img_dark']
    flat = fid['img_bkg']
    theta = fid['angle']
    with h5py.File('/data/2023-02/decarlo/HDF/NSLS/fly_scan_id_2877_aps.h5','w') as fid_out:
        fid_out.create_dataset('/exchange/data',data=data[:])
        fid_out.create_dataset('/exchange/data_dark',data=dark[:])
        fid_out.create_dataset('/exchange/data_white',data=flat[:])
        fid_out.create_dataset('/exchange/theta',data=theta[:])
    print(theta[:-1:2]-theta[1::2])
    
    