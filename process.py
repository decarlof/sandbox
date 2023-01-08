import os
import subprocess

data_path   = '/home/beams/USER2BMB/conda/anaconda/envs/ops/lib/python3.9/site-packages/mctoptics/data/'
energy_mode = "Mono"
energy      = "18.00"
file_name   = 'energy2bm_' + energy_mode +"_" + energy + ".conf"
full_file_name = os.path.join(data_path, file_name)

# command = '--testing --force --config %s' % (full_file_name)
# print('energy set %s'% command)
# # exit()
# subprocess.run(f"""
#     energy set -c command""",
#     shell=True, executable='/bin/bash', check=True)

command = 'energy set --testing --force --config %s' % (full_file_name)
print(command)
subprocess.Popen(command, shell=True)