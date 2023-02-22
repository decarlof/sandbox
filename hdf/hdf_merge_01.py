import os
import sys
import h5py
from pathlib import Path


top = os.path.join('/data/2023-02/Jakes_rec/', '')
out_dir = os.path.join(top, 'no_links')

# make sure logs directory exists
if not os.path.exists(out_dir):
    os.makedirs(out_dir)

h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf', 'hdf5')), os.listdir(top)))
if (h5_file_list):
    h5_file_list.sort()
    print("Found: %s" % h5_file_list) 
    index=0
    for fname in h5_file_list:
        with h5py.File(os.path.join(out_dir, fname), 'a') as h5w:
            with h5py.File(fname, 'r') as h5r:
                print('Reading: ', fname)
                ds_arr = h5r['exchange/data'][...]
                print ('Saving', ':', ds_arr.dtype, ds_arr.shape, 'to: ', os.path.join(out_dir, fname))
                h5w.create_dataset('exchange/data', data=ds_arr[:])

