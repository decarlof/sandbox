import h5py
#flatfield_name = "/data/2022-10-Chawla-79064/flat_fields_Sn-58Bi_Sample1_Single_801_004_090.h5"
flatfield_name = "/data/2022-10-Chawla-79064/flat_fields.h5"

with h5py.File(flatfield_name, 'r') as flat_hdf:
  print(flat_hdf['/exchange/data_white'].shape)
