# # open numpy array in imagej
# ######################################################################################
# # Installation:

# # 1. conda create -n pyimagej -c conda-forge pyimagej openjdk=8 
# # 2. conda activate pyimagej
# #######################################################################################

import imagej
import numpy as np

ij = imagej.init('/home/beams/FAST/Software/Fiji.app', mode='interactive')
ij.ui().showUI()
from jpype import JClass
WindowManager = JClass('ij.WindowManager')

a = np.random.random([5,128,128]).astype('float32')
ij.ui().show('recon', ij.py.to_dataset(a))

while True:
   pass