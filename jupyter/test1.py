
# -*- coding: utf-8 -*-
"""
slider 3D numpy array

"""

import numpy
import pylab
from matplotlib.widgets import Slider


data = numpy.random.rand(100,256,256) #3d-array with 100 frames 256x256

ax = pylab.subplot(111)
pylab.subplots_adjust(left=0.25, bottom=0.25)

frame = 0
l = pylab.imshow(data[frame,:,:]) #shows 256x256 image, i.e. 0th frame

axcolor = 'lightgoldenrodyellow'
axframe = pylab.axes([0.25, 0.1, 0.65, 0.03], facecolor=axcolor)
sframe = Slider(axframe, 'Projection', 0, 100, valinit=50)

def update(val):
    print(val)
    frame = numpy.around(sframe.val)
    l.set_data(data[int(frame),:,:])

sframe.on_changed(update)
pylab.show()
