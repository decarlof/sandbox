from epics import PV

energy_choice_pv = PV('2bm:Energy:EnergyChoice')

energy_choice_index = energy_choice_pv.get()
# energy_choice       = energy_choice_pv.get(as_string=True)
energy_choice       = "Mono Br 13.374"
energy_choice       = "Pink  30.000"
energy_choice_list  = energy_choice.split(' ')
print("Energy: energy choice = %s" % energy_choice)
if energy_choice_list[0] == 'Pink':
	command = 'energy set --mode Pink --energy ' + energy_choice_list[2] + ' --force'
else: # Mono
    command = 'energy set --mode Mono --energy ' + energy_choice_list[2] + ' --force'

print(command)