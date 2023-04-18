
from epics import PV
import time
import numpy as np

control_pvs = {}
config_pvs ={}
pv_prefixes = {}

def read_pv_file(pv_file_name, macros):
    """Reads a file containing a list of EPICS PVs to be used by TomoScan.


    Parameters
    ----------
    pv_file_name : str
      Name of the file to read
    macros: dict
      Dictionary of macro substitution to perform when reading the file
    """

    pv_file = open(pv_file_name)
    lines = pv_file.read()
    pv_file.close()
    lines = lines.splitlines()
    for line in lines:
        is_config_pv = True
        if line.find('#controlPV') != -1:
            line = line.replace('#controlPV', '')
            is_config_pv = False
        line = line.lstrip()
        # Skip lines starting with #
        if line.startswith('#'):
            continue
        # Skip blank lines
        if line == '':
            continue
        pvname = line
        # Do macro substitution on the pvName
        for key in macros:
            pvname = pvname.replace(key, macros[key])
        # Replace macros in dictionary key with nothing
        dictentry = line
        for key in macros:
            dictentry = dictentry.replace(key, '')
        epics_pv = PV(pvname)
        if is_config_pv:
            config_pvs[dictentry] = epics_pv
        else:
            control_pvs[dictentry] = epics_pv
        if dictentry.find('PVName') != -1:
            pvname = epics_pv.value
            key = dictentry.replace('PVName', '')
            control_pvs[key] = PV(pvname)
        if dictentry.find('PVPrefix') != -1:
            pvprefix = epics_pv.value
            key = dictentry.replace('PVPrefix', '')
            pv_prefixes[key] = pvprefix

def show_pvs():
    """Prints the current values of all EPICS PVs in use.

    The values are printed in three sections:

    - config_pvs : The PVs that are part of the scan configuration and
      are saved by save_configuration()

    - control_pvs : The PVs that are used for EPICS control and status,
      but are not saved by save_configuration()

    - pv_prefixes : The prefixes for PVs that are used for the areaDetector camera,
      file plugin, etc.
    """

    print('--------------------------------')
    print('configPVS::')
    for config_pv in config_pvs:
        print(config_pv, ':', config_pvs[config_pv].get(as_string=True))

    print('controlPVS::')
    for control_pv in control_pvs:
        print(control_pv, ':', control_pvs[control_pv].get(as_string=True))

    print('pv_prefixes::')
    for pv_prefix in pv_prefixes:
        print(pv_prefix, ':', pv_prefixes[pv_prefix])


def test():
    control_pvs = {}    

    tomostream_prefix = '2bma:TomoStream:'

    control_pvs['StreamOrthoX']       = PV(tomostream_prefix + 'OrthoX')
    print("%s / %s / %s" % (control_pvs['StreamOrthoX'].get(), control_pvs['StreamOrthoX'].upper_disp_limit, control_pvs['StreamOrthoX'].upper_ctrl_limit))

    control_pvs['StreamOrthoXlimit']  = PV(tomostream_prefix + 'OrthoX.DRVH')
    print(control_pvs['StreamOrthoXlimit'].get())
    control_pvs['StreamOrthoXlimit'].put(2000, wait=True)
    # IT WILL BE UPDATED ONLY FOR THE NEXT SCRIPT RUN  - NOT GOOD!
    print("1", control_pvs['StreamOrthoX'].upper_ctrl_limit)
    print(control_pvs['StreamOrthoXlimit'].get())

    # ALSO I NEED TO HAVE WRITE ACCESS, BUT THIS EVEN DOESNT WORK:
    # control_pvs['StreamOrthoX'].upper_disp_limit = 2000
    # control_pvs['StreamOrthoX'].upper_ctrl_limit = 2000

    # control_pvs['StreamOrthoXlimit']  = PV(tomostream_prefix + 'OrthoX.HOPR')
    # control_pvs['StreamOrthoXctrllimit']  = PV(tomostream_prefix + 'OrthoX.DRVH')
    # print("%s / %s / %s" % (control_pvs['StreamOrthoX'].get(), control_pvs['StreamOrthoXlimit'].get(),control_pvs['StreamOrthoXlimit'].get()))


def main():

    pv_files = ["/local/tomo/epics/synApps/support/tomostream/db/tomoStream_settings.req","/local/tomo/epics/synApps/support/tomostream/db/tomoStream_settings.req"]
    macros = {"$(P)":"2bma:", "$(R)":"TomoStream:"}

    if not isinstance(pv_files, list):
        pv_files = [pv_files]
    for pv_file in pv_files:
        read_pv_file(pv_file, macros)
        show_pvs()
    # print(config_pvs['OrthoX'])
    # print(config_pvs['OrthoX'].type)
    # print(config_pvs['OrthoX'].access)
    # print(config_pvs['OrthoX'].count)
    # print(config_pvs['OrthoX'].info)
    # print(config_pvs['OrthoX'].get())


if __name__ == "__main__":
    main()
