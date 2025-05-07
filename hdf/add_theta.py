import dxfile.dxtomo as dx
import numpy as np

n_proj = 512 # enter the correct number of projections
fname = '/local/dataraid/test.h5'

# Theta
theta_step = np.pi / n_proj
theta_step_deg = theta_step * 180./np.pi
theta = np.arange(0, 180., 180. / n_proj)

f = dx.File(fname, mode='w')
f.add_entry(dx.Entry.data(theta={'value': theta, 'units':'degrees'}))

f.close()