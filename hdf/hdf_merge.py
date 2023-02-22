import os
import h5py

home_dir = '/data/2023-02/Jakes_rec/Absorptoin_EW_01_047_rec_00_parts/'
out_dir = '/data/2023-02/Jakes_rec/'

first = True

with h5py.File(out_dir + 'Absorptoin_EW_01_047_rec_00_nolinks.h5', 'a') as h5w:
    for entry in os.scandir(home_dir):
        fname = home_dir + entry.name

        with h5py.File(fname, 'r') as h5r:
            print('reading: ', fname)

            ds_arr = h5r['exchange/data'][:, :, :]
            if first:
                print ('exchange/data', ':', ds_arr.dtype, ds_arr.shape)
                print('create_dataset')
                # h5w.create_dataset('exchange/data', data=ds_arr)
                h5w.create_dataset('exchange/data', data=ds_arr, chunks=True, maxshape=(None,ds_arr.shape[1],ds_arr.shape[2]))
                first = False
            else:
                h5w['exchange/data'].resize((h5w['exchange/data'].shape[0] + h5r['exchange/data'].shape[0]), axis=0)
                h5w['exchange/data'][-ds_arr.shape[0]:] = ds_arr

print ('done')

# with h5py.File(out_dir + 'all.h5', 'a') as h5w:
#     fname = home_dir + 'p0005.h5'
#     with h5py.File(fname, 'r') as h5r:
#         print('reading: ', fname)
#         ds_arr = h5r['exchange/data'][...]
#         print ('exchange/data', ':', ds_arr.dtype, ds_arr.shape)
#         h5w.create_dataset('exchange/data', data=ds_arr[:])
