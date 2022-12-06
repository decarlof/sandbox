import numpy as np 
import h5py
import dxchange
import sys

fname = sys.argv[1]
fid = h5py.File(fname,'r')
data = fid['exchange/data']
white = fid['exchange/data_white']


proj = data[0]/np.mean(white,axis=0)
print('/local/data/2021-02/Nooduin/extracts/proj'+fname[-6:-3]+'.tiff')
# dxchange.write_tiff(proj,'/local/data/2021-02/Nooduin/extracts/proj'+fname[-6:-3]+'.tiff',overwrite=True)
