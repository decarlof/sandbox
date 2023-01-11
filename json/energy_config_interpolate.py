"""Demonstration of read an energy config file saved by 
https://github.com/xray-imaging/energy2bm in a dictionary

"""
import pickle
import json

import numpy as np
import yaml  # pyyaml package name
import toml

def main():

    full_file_name0 = 'energy2bm_18.conf'
    full_file_name1 = 'energy2bm_20.conf'
    interpolate_energy_config_files(full_file_name0, full_file_name1, 10)

def interpolate_energy_config_files(fname0, fname1, n):

    interp_energies_dict = {}

    pos_energy_start = read_energy_config(fname0)
    pos_energy_end   = read_energy_config(fname1)
    energies = merge(pos_energy_start, pos_energy_end)

    keys = list(energies.keys())
    interp_energies                 = np.linspace(float(keys[0]), float(keys[1]), n)
    interp_mirror_angle             = np.linspace(float(energies[keys[0]]['mirror-angle']),             float(energies[keys[0]]['mirror-angle']), n)
    interp_mirror_vertical_position = np.linspace(float(energies[keys[0]]['mirror-vertical-position']), float(energies[keys[1]]['mirror-vertical-position']), n)
    interp_dmm_usy_ob               = np.linspace(float(energies[keys[0]]['dmm-usy-ob']),               float(energies[keys[1]]['dmm-usy-ob']), n)
    interp_dmm_usy_ib               = np.linspace(float(energies[keys[0]]['dmm-usy-ib']),               float(energies[keys[1]]['dmm-usy-ib']), n)
    interp_dmm_dsy                  = np.linspace(float(energies[keys[0]]['dmm-dsy']),                  float(energies[keys[1]]['dmm-dsy']), n) 
    interp_dmm_us_arm               = np.linspace(float(energies[keys[0]]['dmm-us-arm']),               float(energies[keys[1]]['dmm-us-arm']), n)
    interp_dmm_ds_arm               = np.linspace(float(energies[keys[0]]['dmm-ds-arm']),               float(energies[keys[1]]['dmm-ds-arm']), n)
    interp_dmm_m2y                  = np.linspace(float(energies[keys[0]]['dmm-m2y']),                  float(energies[keys[1]]['dmm-m2y']), n)
    interp_dmm_usx                  = np.linspace(float(energies[keys[0]]['dmm-usx']),                  float(energies[keys[1]]['dmm-usx']), n)
    interp_dmm_dsx                  = np.linspace(float(energies[keys[0]]['dmm-dsx']),                  float(energies[keys[1]]['dmm-dsx']), n)
    interp_table_y                  = np.linspace(float(energies[keys[0]]['table-y']),                  float(energies[keys[1]]['table-y']), n)
    interp_flag                     = np.linspace(float(energies[keys[0]]['flag']),                     float(energies[keys[1]]['flag']), n) 
                 
    i = 0
    for energy in interp_energies:
        temp_dict = {}
        temp_dict['mirror-angle']             =  interp_mirror_angle[i]
        temp_dict['mirror-vertical-position'] =  interp_mirror_vertical_position[i]
        temp_dict['dmm-usy-ob']               =  interp_dmm_usy_ob[i]
        temp_dict['dmm-usy-ib']               =  interp_dmm_usy_ib[i]
        temp_dict['dmm-dsy']                  =  interp_dmm_dsy[i]
        temp_dict['dmm-us-arm']               =  interp_dmm_us_arm[i]
        temp_dict['dmm-ds-arm']               =  interp_dmm_ds_arm[i]
        temp_dict['dmm-m2y']                  =  interp_dmm_m2y[i]
        temp_dict['dmm-usx']                  =  interp_dmm_usx[i]
        temp_dict['dmm-dsx']                  =  interp_dmm_dsx[i]
        temp_dict['table-y']                  =  interp_table_y[i]
        temp_dict['flag']                     =  interp_flag[i]

        interp_energies_dict[str(energy)]     = temp_dict

        i += 1

    for key in  interp_energies_dict:
        file_name = 'energy2bm_interp_' + str(key) + '.conf'
        save_energy_config(file_name, str(key), interp_energies_dict[key])

    # demo_yaml(energy)

    # demo_toml(energy)

    # demo_pickle(energy)

def save_energy_config(file_name, energy, pos_energy):   
    
    with open(file_name, 'w') as f:
        f.write('[general]\n')
        f.write('logs-home = /home/beams/USER2BMB/logs\n')
        f.write('verbose = False\n')
        f.write('testing = False\n')
        f.write('\n')
        f.write('[energy]\n')
        f.write('energy-value = %s\n' % energy)
        f.write('mode = Mono\n')
        f.write('\n')
        f.write('[mirror-vertical-positions]\n')
        f.write('mirror-angle = %s\n' % pos_energy['mirror-angle'])
        f.write('mirror-vertical-position = %s\n' % pos_energy['mirror-vertical-position'])
        f.write('\n')
        f.write('[dmm-motor-positions]\n')
        f.write('dmm-usy-ob = %s\n' % pos_energy['dmm-usy-ob'])
        f.write('dmm-usy-ib = %s\n' % pos_energy['dmm-usy-ib'])
        f.write('dmm-dsy = %s\n' % pos_energy['dmm-dsy'])
        f.write('dmm-us-arm = %s\n' % pos_energy['dmm-us-arm'])
        f.write('dmm-ds-arm = %s\n' % pos_energy['dmm-ds-arm'])
        f.write('dmm-m2y = %s\n' % pos_energy['dmm-m2y'])
        f.write('dmm-usx = %s\n' % pos_energy['dmm-usx'])
        f.write('dmm-dsx = %s\n' % pos_energy['dmm-dsx'])
        f.write('\n')
        f.write('[filter-selector]\n')
        f.write('filter = 4\n')
        f.write('\n')
        f.write('[tabley-flag]\n')
        f.write('table-y = %s\n' % pos_energy['table-y'])
        f.write('flag = %s\n' % pos_energy['flag'])
        f.write('\n')
        f.write('[energyioc]\n')
        f.write('energyioc-prefix = 2bm:MCTOptics:\n')

def merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

def read_energy_config(file_name):   
    
    energy_dict = {}
    energy      = {}

    with open(file_name) as f:
        for line in f:
            if line.find('=') != -1:
                words = line.split('=')
                if words[0].strip() == 'energy-value':
                    key = words[1].strip()
                else:    
                    energy[words[0].strip()] = words[1].strip()
        energy_dict[key] = energy
    
    return energy_dict

def demo_json(parameters):
    """JavaScript Object Notation

    Pros
    ----
    - JSON is part of the standard library.
    - Very old and well known.

    Gotchas
    -------
    - No numpy arrays; it only takes built-in data structures. Use toList().
    - Dictionary keys must be strings; non-string keys will be converted on
      write.
    """
    with open('energy_dict_data.json', 'w') as f:
        json.dump(parameters, f, indent=4)

    with open('energy_dict_data.json', 'r') as f:
        loaded_parameters = json.load(f)

    print(loaded_parameters)


def demo_yaml(parameters):
    """YAML Ain't Markup Language

    Pros
    ----
    - Keys do not need to be strings.
    - The syntax is also less verbose because it doesn't use brackets.

    Gotchas
    -------
    - YAML is not part of the standard library.
    - Syntax for storing NumPy arrays is verbose!
    """

    with open('energy_data.yaml', 'w') as f:
        # Can use yaml.CDumper for faster dump/load if available
        yaml.dump(parameters, f, indent=4, Dumper=yaml.Dumper)

    with open('energy_data.yaml', 'r') as f:
        loaded_parameters = yaml.load(f, Loader=yaml.Loader)

    print(loaded_parameters)


def demo_toml(parameters):
    """Tom's Obvious, Minimal Language

    Pros
    ----
    - Syntax is flatter than YAML, JSON

    Gotchas
    -------
    - TOML is not part of the standard library.
    - Keys must be strings
    - No numpy arrays; arrays automatically converted to lists of STRING!
    """

    with open('energy_data.toml', 'w') as f:
        toml.dump(parameters, f)

    with open('energy_data.toml', 'r') as f:
        loaded_parameters = toml.load(f)

    print(loaded_parameters)


def demo_pickle(parameters):
    """Pickle saves and load exactly as it was, but is not human readable."""
    with open('energy_data.pickle', 'wb') as f:
        pickle.dump(parameters, f)

    with open('energy_data.pickle', 'rb') as f:
        loaded_parameters = pickle.load(f)

    print(loaded_parameters)

if __name__ == '__main__':
    main()