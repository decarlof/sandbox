import numpy as np
from mpi4py import MPI
import h5py as h5
import argparse

from datetime import datetime
import os

import load_h5 as load_h5


# Load Diamond and ESRF raw data. Default parameters are for Diamond.
# To load a NeXus file from the ESRF:
# python nexus.py /HDF/ESRF/align/align_0001/align_0001_1_1_0000.nx /HDF/ESRF/ --path /entry0000/data/data/ --path_angle /entry0000/data/rotation_angle/ --image_key_path /entry0000/data/image_key/

def __option_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("in_file", help="Input data file.")
    parser.add_argument("out_folder", help="Output folder.")
    parser.add_argument("-p", "--path", default="/entry1/tomo_entry/data/data", help="Data path.")
    parser.add_argument("-pan", "--path_angle", default="/entry1/tomo_entry/data/rotation_angle", help="Rotation angle path.")
    parser.add_argument("-ikp", "--image_key_path", default="/entry1/tomo_entry/instrument/detector/image_key", help="Image key path.")
    parser.add_argument("-c", "--csv", default=None, help="Write results to specified csv file.")
    parser.add_argument("-r", "--repeat", type=int, default=1, help="Number of repeats.")
    parser.add_argument("-d", "--dimension", type=int, choices=[1, 2, 3], default=1,
                        help="Which dimension to slice through (usually 1 = projections, 2 = sinograms).")
    parser.add_argument("-cr", "--crop", type=int, choices=range(1, 101), default=100,
                        help="Percentage of data to process. 10 will take the middle 10% of data in the second dimension.")    
    parser.add_argument("-rec", "--reconstruction", default="gridrec", help="The reconstruction method (from tomopy) to apply.")
    parser.add_argument("-rings", "--stripe", default=None, help="The stripes removal method to apply.")
    parser.add_argument("-nc", "--ncore", type=int, default=1, help="The number of cores.")
    parser.add_argument("-pa", "--pad", type=int, default=0, help="The number of slices to pad each chunk with.")
    args = parser.parse_args()
    return args

def read_nexus(args):
    with h5.File(args.in_file, "r") as in_file:
        dataset = in_file[args.path]
        shape = dataset.shape
    print(f"Dataset shape is {shape}")

    angles_degrees = load_h5.get_angles(args.in_file, path=args.path_angle)
    data_indices = load_h5.get_data_indices(args.in_file,
                                            image_key_path=args.image_key_path)
    angles_radians = np.deg2rad(angles_degrees[data_indices])

    # preview to prepare to crop the data from the middle when --crop is used to avoid loading the whole volume.
    # and crop out darks and flats when loading data.
    preview = [f"{data_indices[0]}: {data_indices[-1] + 1}", ":", ":"]
    if args.crop != 100:
        new_length = int(round(shape[1] * args.crop / 100))
        offset = int((shape[1] - new_length) / 2)
        preview[1] = f"{offset}: {offset + new_length}"
        cropped_shape = (data_indices[-1] + 1 - data_indices[0], new_length, shape[2])
    else:
        cropped_shape = (data_indices[-1] + 1 - data_indices[0], shape[1], shape[2])
    preview = ", ".join(preview)

    print(f"Cropped data shape is {cropped_shape}")

    dim = args.dimension
    pad_values = load_h5.get_pad_values(args.pad, dim, shape[dim - 1], data_indices=data_indices, preview=preview)
    print(f"pad values are {pad_values}.")
    data = load_h5.load_data(args.in_file, dim, args.path, preview=preview, pad=pad_values)

    darks, flats = load_h5.get_darks_flats(args.in_file, args.path,
                                           image_key_path=args.image_key_path,
                                           preview=preview, dim=args.dimension)

    (angles_total, detector_y, detector_x) = np.shape(data)
    print(f"data shape is {(angles_total, detector_y, detector_x)}")

    return data, darks, flats, angles_radians

def main():
    args = __option_parser()

    data, darks, flats, theta = read_nexus(args)

if __name__ == '__main__':
    main()
