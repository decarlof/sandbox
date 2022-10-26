import h5py
import sys
import meta

import numpy as np

infile = sys.argv[1]
outfile = f'{sys.argv[1][:-3]}_fixed.h5'


with h5py.File(infile,'r') as f:
    tree, meta_dict = meta.read_hdf(infile)
    with h5py.File(outfile,'a') as fout:
        for key, value in meta_dict.items():
            dset = fout.create_dataset(key, data=value[0], dtype=f[key].dtype, shape=(1,))
            print(key, value[0], f[key].dtype, )
            if value[1] is not None:
                s = value[1]
                utf8_type = h5py.string_dtype('utf-8', len(s)+1)
                dset.attrs['units'] =  np.array(s.encode("utf-8"), dtype=utf8_type)

