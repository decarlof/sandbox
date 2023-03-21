import os
import six
import math
import h5py
import h5py as h5
import logging
import numpy as np

logger = logging.getLogger(__name__)

def read_nexus(fname, 
               proj=None, 
               sino=None, 
               dtype=None,
               data_path="/entry1/tomo_entry/data/", 
               angle_path="/entry1/tomo_entry/data/",
               image_key_path="/entry1/instrument/image_key/image_key"):
    """
    Read NeXus tomo HDF5 format.

    Parameters
    ----------
    fname : str
        Path to hdf5 file.

    proj : {sequence, int}, optional
        Specify projections to read. (start, end, step)

    sino : {sequence, int}, optional
        Specify sinograms to read. (start, end, step)

    dtype : numpy datatype, optional
        Convert data to this datatype on read if specified.

    data_path : string, optional
        hdf file path location of the data

    image_key_path : string, optional
        hdf file path location of the image type keys. 0 = projection, 1 = flat, 2 = dark

    Returns
    -------
    ndarray
        3D tomographic data.

    ndarray
        3D flat field data.

    ndarray
        3D dark field data.

    ndarray
        1D theta in radian.
    """


    # Get the indices of where the data, flat and dark are the dataset
    with h5.File(fname, "r") as file:
        data_indices  = []
        darks_indices = []
        flats_indices = []

        for i, key in enumerate(file[image_key_path]):
            if int(key) == 0:
                data_indices.append(i)
            elif int(key) == 1:
                flats_indices.append(i)
            elif int(key) == 2:
                darks_indices.append(i)

    dataset_grp = '/'.join([data_path, 'data'])
    theta_grp   = '/'.join([data_path, 'rotation_angle'])

    dataset = read_hdf5(fname, dataset_grp, slc=(proj, sino), dtype=dtype)
    angles  = read_hdf5(fname, theta_grp, slc=None)

    # Get the indices of where the data, flat and dark are the dataset
    with h5.File(fname, "r") as file:
        data_indices  = []
        darks_indices = []
        flats_indices = []

        tomo  = dataset[np.where(np.array(file[image_key_path][:]) == 0.0)[0]]
        dark  = dataset[np.where(np.array(file[image_key_path][:]) == 2.0)[0]]
        flat  = dataset[np.where(np.array(file[image_key_path][:]) == 1.0)[0]]
        theta = angles[np.where(np.array(file[image_key_path][:])  == 0.0)[0]]

    theta = np.deg2rad(theta)
    return tomo, flat, dark, theta
  

def read_hdf5(fname, dataset, slc=None, dtype=None, shared=False):
    """
    Read data from hdf5 file from a specific group.

    Parameters
    ----------
    fname : str
        String defining the path of file or file name.
    dataset : str
        Path to the dataset inside hdf5 file where data is located.
    slc : sequence of tuples, optional
        Range of values for slicing data in each axis.
        ((start_1, end_1, step_1), ... , (start_N, end_N, step_N))
        defines slicing parameters for each axis of the data matrix.
    dtype : numpy datatype (optional)
        Convert data to this datatype on read if specified.
    shared : bool (optional)
        If True, read data into shared memory location.  Defaults to True.

    Returns
    -------
    ndarray
        Data.
    """
    try:
        fname = _check_read(fname)
        with h5py.File(fname, "r") as f:
            try:
                data = f[dataset]
            except KeyError:
                # NOTE: I think it would be better to raise an exception here.
                logger.error('Unrecognized hdf5 dataset: "%s"' %
                             (str(dataset)))
                return None
            shape = _shape_after_slice(data.shape, slc)
            if dtype is None:
                dtype = data.dtype
            if shared:
                arr = empty_shared_array(shape, dtype)
            else:
                arr = np.empty(shape, dtype)
            data.read_direct(arr, _make_slice_object_a_tuple(slc))
    except KeyError:
        return None
    _log_imported_data(fname, arr)
    return arr

def _log_imported_data(fname, arr):
    logger.debug('Data shape & type: %s %s', arr.shape, arr.dtype)
    logger.info('Data successfully imported: %s', fname)

def _check_read(fname):
    known_extensions = ['.edf', '.tiff', '.tif', '.h5', '.hdf', '.npy', '.nc', '.xrm',
                        '.txrm', '.txm', '.xmt', '.nxs']
    if not isinstance(fname, six.string_types):
        logger.error('File name must be a string')
    else:
        if get_extension(fname) not in known_extensions:
            logger.error('Unknown file extension')
    return os.path.abspath(fname)

def get_extension(fname):
    """
    Get file extension.
    """
    return '.' + fname.split(".")[-1]

def _shape_after_slice(shape, slc):
    """
    Return the calculated shape of an array after it has been sliced.
    Only handles basic slicing (not advanced slicing).

    Parameters
    ----------
    shape : tuple of ints
        Tuple of ints defining the ndarray shape
    slc : tuple of slices
        Object representing a slice on the array.  Should be one slice per
        dimension in shape.

    """
    if slc is None:
        return shape
    new_shape = list(shape)
    slc = _make_slice_object_a_tuple(slc)
    for m, s in enumerate(slc):
        # indicies will perform wrapping and such for the shape
        start, stop, step = s.indices(shape[m])
        new_shape[m] = int(math.ceil((stop - start) / float(step)))
        if new_shape[m] < 0:
            new_shape[m] = 0
    return tuple(new_shape)


def _make_slice_object_a_tuple(slc):
    """
    Fix up a slc object to be tuple of slices.
    slc = None returns None
    slc is container and each element is converted into a slice object

    Parameters
    ----------
    slc : None or sequence of tuples
        Range of values for slicing data in each axis.
        ((start_1, end_1, step_1), ... , (start_N, end_N, step_N))
        defines slicing parameters for each axis of the data matrix.
    """
    if slc is None:
        return None  # need arr shape to create slice
    fixed_slc = list()
    for s in slc:
        if not isinstance(s, slice):
            # create slice object
            if s is None or isinstance(s, int):
                # slice(None) is equivalent to np.s_[:]
                # numpy will return an int when only an int is passed to
                # np.s_[]
                s = slice(s)
            else:
                s = slice(*s)
        fixed_slc.append(s)
    return tuple(fixed_slc)


def main():

    fname = '/local/data/HDF/DLS/110809.nxs'
    data, darks, flats, theta = read_nexus(fname)

if __name__ == '__main__':
    main()
