from hdf.object import Dataset
from hdf.object.h5 import H5File

# full_file_name = '/Users/decarlo/Downloads/data/ca9036_c_134.h5'
# dataFile = H5File(full_file_name, H5File.READ)
# fp = dataFile.get("/measurement/instrument/monochromator/energy")
# print(fp.getData()[0])
# fp = dataFile.get("/measurement/instrument/camera_motor_stack/setup/camera_distance")
# print(fp.getData()[0])
# fp = dataFile.get("/measurement/instrument/detection_system/objective/resoluxtion")
# print(fp.getData()[0])

def read_meta(file_name, hdf_path):
    
    dataFile = H5File(file_name, H5File.READ)
    fp = dataFile.get(hdf_path)

    if fp is not None:
    	return fp.getData()[0]
    else:
    	return fp


file_name = '/Users/decarlo/Downloads/data/ca9036_c_134.h5'

print(read_meta(file_name, "/measurement/instrument/monochromator/energy"))
print(read_meta(file_name, "/measurement/instrument/camera_motor_stack/setup/camera_distance"))
print(read_meta(file_name, "/measurement/instrument/detection_system/objective/resolution"))
