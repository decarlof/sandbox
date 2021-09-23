
from epics import PV
import pvaccess as pva
import time
import numpy as np
import matplotlib.pyplot as plt


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
print(image[0])
