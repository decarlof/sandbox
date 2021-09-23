
from epics import PV
import pvaccess as pva
import time
import numpy as np
import matplotlib.pyplot as plt


def streaming(theta, nthetap):
    PVA_prefix = '2bmbPG1:Pva1:'

	pva_data      = pva.Channel(PVA_prefix + 'Image')
	pva_data_type = pva.Channel(PVA_prefix + 'DataType_RBV')
	pva_image     = pva_data.get('')
	pva_data_dict = pva_image.getStructureDict()     

	image     = pva_image['value']
	width     = pva_image['dimension'][0]['size']
	height    = pva_image['dimension'][1]['size']

	print(image[0]['ubyteValue'])
	image_np = np.reshape(image[0]['ubyteValue'], (width, height))
	print(width, height)
	print(image_np.shape)

	# plt.imshow(image_np)
	# plt.show()

    print(pva_data_dict)


    # buffer is continuously update with monitoring
    # the detector pv (function addProjection), called inside pv monitor
    databuffer = np.zeros([nthetap, nz, n], dtype='float32')

    def addProjection(pv):
        curid = pv['uniqueId']
        print(curid)
        databuffer[np.mod(curid, nthetap)] = pv['value'][0]['ubyteValue'].reshape(
            nz, n).astype('float32')
        thetabuffer[np.mod(curid, nthetap)] = theta[np.mod(
            curid, ntheta)]  # take some theta with respect to id

    pva_data.monitor(addProjection, '')


if __name__ == "__main__":

    streaming()