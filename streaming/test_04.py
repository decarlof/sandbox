# takes Pva from AD and extracts the NTNDArray structure then
# creates a new pv that uses the same structure and hosts a random image.
# these new pv is them served as 'AdImage'. 
# run it with: 
# 
# python -i test_03.py
# 
# then from a terminal you can get the image with:
# pvget AdImage | more

import pvaccess as pva
import numpy as np

c = pva.Channel('2bmbSP1:Pva1:Image')
pv1 = c.get('')
pv1d = pv1.getStructureDict()
print(pv1d)
# pv1['descriptor'] = 'test'

print(pv1['descriptor'])
# print(pv1d['timeStamp.secondsPastEpoch'])
print(pv1['uniqueId'])
print(pv1['display.limitLow'])



