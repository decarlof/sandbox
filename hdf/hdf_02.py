import meta
import h5py

file_name_raw = '/data/2022-04/Tekawade/PE6_1011_157.h5'
file_name_rec = '/data/2022-04/Tekawade_rec/test_rec.h5'

tree, meta_dict = meta.read_hdf(file_name_raw)

hf = h5py.File(file_name_rec, 'w')
for key, value in meta_dict.items():
    # print(key, value)
    dset = hf.create_dataset(key, data=value[0])
    if value[1] is not None:
        dset.attrs['units'] = value[1]

hf.close()