import os
import sys
import h5py
from pathlib import Path
import meta

try:
    top = os.path.join(sys.argv[1], '')
    # Arguments passed
    if os.path.exists(top):
        print("\nPath: %s does exist" % top)
        out_dir = os.path.join(top, 'no_links')
        # make sure logs directory exists
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        h5_file_list = list(filter(lambda x: x.endswith(('.h5', '.hdf', 'hdf5')), os.listdir(top)))
        print(top, h5_file_list)
        # exit()
        if (h5_file_list):
            h5_file_list.sort()
            # print("Found: %s" % h5_file_list) 
            index=0
            for fname in h5_file_list:
                print("Found: %s" % fname)
                with h5py.File(os.path.join(out_dir, fname), 'a') as h5w:
                    with h5py.File(fname, 'r') as h5r:
                        try:  # trying to copy meta
                            tree, meta_dict = meta.read_hdf(fname)
                            print('Reading meta data: ', fname)
                            for key, value in meta_dict.items():
                                # print(key, value)
                                dset = h5w.create_dataset(key, data=value[0], dtype=h5r[key].dtype, shape=(1,))
                                if value[1] is not None:
                                    s = value[1]
                                    utf8_type = h5py.string_dtype('utf-8', len(s)+1)
                                    dset.attrs['units'] =  np.array(s.encode("utf-8"), dtype=utf8_type)
                        except:
                            print('ERROR: Skip copying meta')
                            pass

                        print('Reading data: ', fname)
                        ds_arr = h5r['exchange/data'][...]
                        print ('Saving', ':', ds_arr.dtype, ds_arr.shape, 'to: ', os.path.join(out_dir, fname))
                        h5w.create_dataset('exchange/data', data=ds_arr[:])
        else:
            print('ERROR: no hdf file found in %s' % top)
    else:
        print("Path: %s does not exist" % top)

except IndexError:
    print('ERROR: Enter a valid directory path')


