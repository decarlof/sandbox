# import re
import json
import numpy as np


def write_array(fname, arr):
      
    # Write the array to disk
    header = '# Array shape: '
    with open(fname, 'w') as outfile:
        outfile.write(header + '{0}\n'.format(arr.shape))
        for data_slice in arr:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            # Writing out a break to indicate different slices...
            outfile.write('# New slice\n')


def read_array(fname):

    with open(fname) as f:
        firstline = f.readlines()[0].rstrip()

    header = '# Array shape: '
    fshape = firstline[len(header):]
    fshape = fshape.replace('(','').replace(')','')  
    shape = tuple(map(int, fshape.split(', ')))

    # Read the array from disk
    new_data = np.loadtxt(fname)
    new_data = new_data.reshape(shape)
    return new_data
  


def main():

    ntiles_h = 4
    ntiles_v = 3

    shifts_h = np.zeros([ntiles_v, ntiles_h, 2], dtype=np.float32)

    write_array('h.txt', shifts_h)
    new_data = read_array('h.txt')

    # Just to check that they're the same...
    # check if both arrays are same or not:
    if (new_data == shifts_h).all():
        print("Yes, both the arrays are same")
    else:
        print("No, both the arrays are not same")
if __name__ == "__main__":
    main()