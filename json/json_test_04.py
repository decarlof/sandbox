# import re
import json
import numpy as np


def write_array(fname, arr):
      
    # Write the array to disk
    with open(fname, 'w') as outfile:
        outfile.write('# Array shape: {0}\n'.format(arr.shape))
        for data_slice in arr:
            np.savetxt(outfile, data_slice, fmt='%-7.2f')
            # Writing out a break to indicate different slices...
            outfile.write('# New slice\n')


def read_array(fname):

    with open(fname) as f:
        firstline = f.readlines()[0].rstrip()

    fshape = firstline[15:]
    fshape = fshape.replace('(','').replace(')','')  
    shape = tuple(map(int, fshape.split(', ')))

    # Read the array from disk
    new_data = np.loadtxt(fname)
    new_data = new_data.reshape(shape)
    return new_data
  
def write_json(fname, alist):
    with open(fname, 'w') as fp:
        json.dump(alist, fp, indent=4, sort_keys=True)

def read_json(fname):
    with open(fname, 'r') as fp:
        alist = json.load(fp)
    return alist

def main():

    ntiles_h = 4
    ntiles_v = 3

    shifts_h = np.zeros([ntiles_v, ntiles_h, 2], dtype=np.float32)

    write_json('list.txt', shifts_h.tolist())
    new_data1 = np.array(read_json('list.txt'))

    # # Just to check that they're the same...
    # # check if both arrays are same or not:
    if (new_data1 == shifts_h).all():
        print("Yes, both the arrays are same")
    else:
        print("No, both the arrays are not same")

    write_array('text.txt', shifts_h)
    new_data2 = read_array('text.txt')

    # # Just to check that they're the same...
    # # check if both arrays are same or not:
    if (new_data2 == shifts_h).all():
        print("Yes, both the arrays are same")
    else:
        print("No, both the arrays are not same")

if __name__ == "__main__":
    main()