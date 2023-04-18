import tomopy
import dxchange


# Select the sinogram range to reconstruct.
start = 500
end = 502

# Set path to the data file
data_path = '/local/data/tomo_00097.h5'

# Read data
proj, flat, dark, theta = dxchange.read_aps_32id(data_path, sino=(start, end))

# Perform flat-field correction
proj = tomopy.normalize(proj, flat, dark)

# Set rotation center
# rot_center = tomopy.find_center(proj, theta, init=1024, ind=0, tol=0.5)

rot_center = 1267.5

proj = tomopy.minus_log(proj)

# Perform tomographic reconstruction
rec = tomopy.recon(proj, theta, center=rot_center, algorithm='gridrec')

# Mask each reconstructed slice with a circle.
recon = tomopy.circ_mask(rec, axis=0, ratio=0.95)

# Save reconstructed data as a stack of TIFF images
dxchange.write_tiff_stack(rec, fname='recon', dtype='float32', overwrite=True)