import dxchange
import sys

name = sys.argv[1]
f = dxchange.read_tiff_stack(f'{name}/r_00000.tiff',ind =np.arange(0,1780))[:,400:-400,400:-400]
