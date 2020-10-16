import numpy as np

detx = 2560
dety = 2160
resx = 6.5
resy = 6.5
lenses = np.array([1, 2, 5, 7.5, 10])

resx = resx/lenses
resy  = resy/lenses
objsizex = detx*resx
objsizey = dety*resy



for k in range(len(lenses)):
   print("%.1fx\t %.2fum x %.2fum\t %.2fmm x %.2fmm" % (lenses[k],resx[k],resy[k],objsizex[k]/1000,objsizey[k]/1000))

