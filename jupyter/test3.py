
from types import SimpleNamespace

# parser = argparse.ArgumentParser(description='Processes parameters')
# parser.add_argument('rotation_axis_auto', metavar='rotation_axis_auto', default='auto', type=str)
# dict_args = {'rotation_axis_auto': 'auto', 'file_name': '/data/2022-12/Luxi_173.h5', 'dark_file_name': '/data/2022-12/Luxi_173.h5', 'flat_file_name': '/data/2022-12/Luxi_173.h5', 'rotation_axis_method': 'sift', 'binning': 0}

file_name = '/data/2022-12/Luxi_173.h5'
args = SimpleNamespace(rotation_axis_auto  = 'auto', 
					  file_name            =  file_name,
					  dark_file_name       =  file_name, 
					  flat_file_name       =  file_name, 
					  rotation_axis_method = 'sift',  
					  binning              = 0
					  )
# args = **dict_args
# args = parser.parse_args()

print(args.rotation_axis_auto)
# print('***************')
# print('parser', parser)