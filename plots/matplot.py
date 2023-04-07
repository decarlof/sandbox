import h5py
import matplotlib.pyplot as plt
import numpy as np

import dxchange as dx


# proj, flat, dark, theta = dx.read_aps_tomoscan_hdf5('/local/data/tomo_00097.h5')


# images = proj[:1]
# images = (images - np.min(images)) * 256 / (np.max(images) - np.min(images))

# for i, image in enumerate(images):
#     plt.figure()
#     plt.imshow(image, cmap='gray')
#     plt.title(f"Image {i + 1}")
#     plt.axis("off")

# plt.show()

# exit()

with h5py.File('/local/data/tomo_00097.h5', 'r') as h5:
    data = h5['exchange/data']

    images = data[:1]
    images = (images - np.min(images)) * 256 / (np.max(images) - np.min(images))

    for i, image in enumerate(images):

        plt.figure()
        plt.imshow(image, cmap='gray')
        plt.title(f"Image {i + 1}")
        plt.axis("off")

plt.show()