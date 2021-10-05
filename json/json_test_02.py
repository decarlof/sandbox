import json
import numpy as np


def write_array(fname, arr):
      
    # reshaping the array from 3D matrice to 2D matrice.
    arr_reshaped = arr.reshape(arr.shape[0], -1)
      
    # saving reshaped array to file.
    np.savetxt(fname, arr_reshaped)
      
def read_array(fname):
    # retrieving data from file.
    arr = np.loadtxt(fname)
      
    # This loadedArr is a 2D array, therefore
    # we need to convert it to the original
    # array shape.reshaping to get original
    # matrice with original shape.
    original_arr = arr.reshape(arr.shape[0], arr.shape[1] // 2, 2)

    return original_arr
  


def main():

    ntiles_v = 3
    ntiles_h = 4

    # shifts_h = np.zeros([ntiles_v,ntiles_h,2], dtype=np.float32)    

    shifts_h = np.zeros([ntiles_v,ntiles_h,2], dtype=np.float32)

    write_array('h.txt', shifts_h)
    load_original_arr = read_array('h.txt')

    # check if both arrays are same or not:
    if (load_original_arr == shifts_h).all():
        print("Yes, both the arrays are same")
    else:
        print("No, both the arrays are not same")

    # check the shapes:
    print("shape of shifts_h: ", shifts_h.shape)
    print("shape of load_original_arr: ", load_original_arr.shape)
  
    # print(shifts_h)
    # print(load_original_arr)

if __name__ == "__main__":
    main()