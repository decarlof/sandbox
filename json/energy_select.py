import os
import json
import numpy as np

def main():

    energy_select = np.around(33.2, decimals=2)

    data_path = '/home/beams/USER2BMB/epics/synApps/support/mctoptics/mctoptics/data'
    with open(os.path.join(data_path, 'energy.json')) as json_file:
        energy_lookup = json.load(json_file)

    energy_list = []

    for value in energy_lookup.values():
        if value['mode'] == 'Mono':
            energy_list.append(value['energy'])

    energies_str = np.array(energy_list)
    energies_flt = [float(i) for i in  energies_str]
    energy_max = np.max(energies_flt)
    energy_min = np.min(energies_flt)

    print(energies_flt)
    if energy_select < energy_max and energy_select >= energy_min:
        energy_calibrated = find_nearest(energies_flt, energy_select)
        
        print(energy_select, energy_calibrated)
        # print(energies_str)

        energy_closer_index  = np.where(energies_str == str(energy_calibrated))[0][0]

        if energy_select >= float(energy_calibrated):
            energy_low  = np.around(float(energies_str[energy_closer_index]), decimals=2)
            energy_high = np.around(float(energies_str[energy_closer_index+1]), decimals=2)
        else:
            energy_low  = np.around(float(energies_str[energy_closer_index-1]), decimals=2)
            energy_high = np.around(float(energies_str[energy_closer_index]), decimals=2)
           
        print("Select %4.2f: [%4.2f, %4.2f]" % (energy_select, energy_low, energy_high))
        n = int(100*(energy_high-energy_low))
        print("Range: %4.2f; N = %d" % ((energy_high-energy_low), n))
        interp_energies = np.linspace(energy_low, energy_high, n).round(decimals=2)
        print(interp_energies)
        # print('Interpolation: %4.2f' % interp_energies)
    else:
        print('Error: energy selected %4.2f is outside the calibrated range [%4.2f, %4.2f]' %(energy_select, energy_min, energy_max))

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    value = "{0:4.2f}".format(array[idx])

    return value

    
if __name__ == '__main__':
    main()