
from epics import PV
import pvaccess as pva
import time
import numpy as np
import matplotlib.pyplot as plt


def streaming():
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

    ix = width//2
    iy = width//2
    iz = height//2
    
    # buffer is continuously update with monitoring
    # the detector pv (function addProjection), called inside pv monitor
    databuffer = np.zeros([10, height, width], dtype='float32')

    def addProjection(pv):
        curid = pv['uniqueId']
        print(curid)
        databuffer[np.mod(curid, 10)] = pv['value'][0]['ubyteValue'].reshape(
            height, width).astype('float32')

    pva_data.monitor(addProjection, '')
    
    while(True):
        datap = databuffer.copy()
        # print('new image')
if __name__ == "__main__":

    streaming()