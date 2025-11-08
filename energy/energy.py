from epics import PV


def main():
    energy_change_PVs = {}
    energy_change_PVs['Energy'] = PV('2bma:TomoScan:Energy.VAL')
    energy_change_PVs['Energy_Mode'] = PV('2bma:TomoScan:EnergyMode.VAL')

    mode = 'Mono'
    energy_value = 24.9
    energy_change_PVs['Energy_Mode'].put(mode, wait=True)
    energy_change_PVs['Energy'].put(energy_value, wait=True)


if __name__ == "__main__":
    main()