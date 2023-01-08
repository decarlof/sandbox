import os
import subprocess

data_path   = '/home/beams/USER2BMB/conda/anaconda/envs/ops/lib/python3.9/site-packages/mctoptics/data/'
energy_mode = "Mono"
energy      = "18.00"
file_name   = 'energy2bm_' + energy_mode +"_" + energy + ".conf"
full_file_name = os.path.join(data_path, file_name)

command = 'energy set --config %s --testing' % (full_file_name)
subprocess.run(f"""energy -c command""", shell=True, executable='/bin/bash', check=True)